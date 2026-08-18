# IncidentBridge — Threat Model

IncidentBridge creates a real-world side effect: an AI system places a phone call to an external vendor. The primary safety goal is therefore narrower than “the model says the right thing.” The system must prevent an unapproved call, prevent a weak or mismatched result from becoming trusted incident state, and preserve human authority over recovery.

## Security invariants

These are the properties the implementation is designed to preserve even when inputs, provider results, or network outcomes are imperfect:

1. **No implicit live call.** Preview is the default. A live call requires explicit execute intent, confirmation that the recipient is authorized, an exact E.164 allowlist match, `CALLE_LIVE_CALLS_ENABLED=true`, and a server-side API key.
2. **No blind duplicate call.** Intent is durably reserved before dispatch. An ambiguous provider outcome is reconciled rather than automatically redialed.
3. **No secret-bearing spoken briefing.** Every free-text field that can enter the spoken task is screened for credential-, phone-, and email-like content before the task is created.
4. **No success from transport status alone.** Terminal status, `task_completed`, confidence, complete schema, consent, escalation state, request binding, and evidence all participate in routing.
5. **No cross-call result acceptance.** `vendor_acknowledged` requires the expected call ID, workflow ID, incident ID, and exact authorized destination to match.
6. **No ticket claim without recipient corroboration.** A meaningful vendor ticket must be supported by recipient-side transcript evidence. Blank, `unknown`, and prefix/sub-string false matches fail closed.
7. **No phone-based recovery declaration.** `incident_closed` remains `false`, including when the vendor reports its own status as `resolved`.
8. **No raw common contact/credential strings in returned free text.** Recursive output redaction removes phone-, email-, and common credential-like values before application output is persisted or displayed.

## Threats and controls

| Threat | Failure mode | Control | Failure route |
|---|---|---|---|
| Unauthorized destination | Agent calls an unapproved number | request-level authorization + exact E.164 `--allow` gate + explicit live confirmation | call is not created |
| Secret leakage in task | API key/email/phone appears in spoken briefing | validation across every spoken free-text field | request rejected |
| Duplicate side effect | network uncertainty causes a second call | stable idempotency identity + durable SQLite reservation + ambiguous-outcome reconciliation | no blind retry |
| Wrong support desk | unrelated recipient hears incident details | AI disclosure + correct-desk/consent gate before incident detail | `needs_human` |
| Low-quality provider result | terminal call is mistaken for task success | terminal status + exact `task_completed` + confidence threshold + complete schema | `needs_human` |
| Cross-workflow result mix-up | result from another incident/call is accepted | workflow + incident + call ID + destination binding | `needs_human` |
| Structured ticket hallucination | result contains a ticket the recipient never supplied | recipient-side transcript corroboration using token-sequence equality | `needs_human` |
| Prefix evidence confusion | `SUP-48` is accepted because transcript contains `SUP-4821` | exact normalized token-sequence matching | `needs_human` |
| Vendor says “resolved” | external statement becomes internal recovery state | hard-coded human/local-health recovery boundary | `incident_closed=false` |
| Sensitive data in returned text | phone/email/credential-like values leak into artifacts | recursive redaction before returned output | sensitive pattern replaced |

## Trust boundaries

### CALL-E / telephony provider

IncidentBridge trusts CALL-E to execute the authorized call and return the provider call object, recipient attempts, transcript turns, metadata, and structured result according to the SDK/API contract. Application-side binding reduces accidental result mix-ups; it does not cryptographically attest the telephony provider itself.

### Recipient transcript evidence

The application treats recipient-side transcript evidence as corroboration for the vendor ticket identifier. It does **not** currently require every informational field such as ETA or workaround text to be independently transcript-matched before displaying it. Those fields remain operational context, not authority to close or mutate recovery state.

### Human authorization

The application can enforce that a caller asserted recipient authorization and matched an exact allowlist. It cannot independently prove the legal or organizational authority of the person supplying that configuration. Deployment policy remains responsible for who is allowed to authorize real calls.

## Residual risks

- Regex-based secret/privacy screening is a conservative baseline, not a DLP or compliance certification. Novel secret formats can evade pattern matching.
- ASR/transcript quality can affect corroboration. The ticket matcher tolerates punctuation differences but intentionally fails closed when a meaningful normalized ticket sequence is absent.
- A legitimately authorized vendor representative can still provide incorrect facts. IncidentBridge records vendor evidence; it does not certify that the vendor's statement is true.
- The provider-side transcript/result objects are trusted inputs from CALL-E. IncidentBridge currently provides application-level correlation rather than cryptographic provenance.
- Private successful live-call tests are not published because they contain real participant/conversation data; the public repository exposes a redacted real fail-closed provider boundary plus deterministic success-path simulation and SDK integration tests.

## Verification

The threat controls above are exercised by the automated suite, including adversarial cases for unauthorized input, secret-bearing spoken fields, wrong desk, low confidence, incomplete results, mismatched metadata/destination/call ID, missing recipient evidence, wrong ticket, blank ticket, case-variant `unknown`, prefix false matches, punctuation-tolerant legitimate ticket matching, recursive redaction, idempotency, durable reservation, and the real SDK HTTP boundary.

GitHub Actions currently verifies Ruff plus **21 passing tests at 92.37% coverage**, with a 90% coverage gate.

## Deliberate non-goal

IncidentBridge is not a recovery verifier. The strongest invariant in the system is intentionally simple:

```text
A phone call may create evidence.
A phone call may not create recovery truth.
```