# IncidentBridge — Judge Guide

IncidentBridge is a consent-first CALL-E agent for one bounded real-world task: contact an authorized vendor support line during an incident, collect ticket/status/ETA/workaround facts, and return structured evidence without allowing the phone agent to close the incident.

**Fast path for judges**

- Live evidence console: https://yangyangnovelist-hub.github.io/incidentbridge-calle/
- Official CALL-E contribution: https://github.com/CALLE-AI/awesome-phone-call-agents/pull/132 — **merged**
- Official merged app: https://github.com/CALLE-AI/awesome-phone-call-agents/tree/main/apps/python/incidentbridge
- Safe reproduction path: `TESTING.md`
- Core safety regression tests: `tests/test_policy.py`
- Runtime integration: `tests/test_sdk_runtime.py`

## 1. Real World Impact

The phone-work problem is specific: during a SaaS or data-platform incident, an operator often has to stop diagnosing the failure, wait on a vendor support line, repeat incident context, then manually carry ticket/status/ETA/workaround facts back into the incident workflow.

IncidentBridge removes that bounded phone task without replacing the part that should remain human-owned. CALL-E can collect vendor evidence; local health checks and the human incident commander retain recovery authority.

This is useful beyond the demo because the same pattern applies anywhere an operations team must contact an external provider during an incident while preserving an auditable separation between **what the vendor said** and **whether the system is actually recovered**.

### Why this is not another incident-alerting agent

Incident notification and on-call escalation answer an internal question: **who on our side knows about the incident and owns the next action?**

IncidentBridge starts after that. It answers the external-dependency question: **what does the vendor know, what ticket did they open, what status/ETA/workaround did they give us, and can we trust that those facts came from the exact authorized call?**

That distinction changes the data contract and the safety model:

| Internal incident escalation | IncidentBridge |
|---|---|
| calls an on-call responder | calls an authorized external vendor-support destination |
| asks for acknowledgment / ownership / next action | asks for vendor ticket / status / ETA / workaround / callback window |
| proves a human on our side has been reached | proves vendor evidence is bound to the exact approved call and corroborated by recipient transcript |
| may change internal ownership state | **never** changes recovery state or closes the incident |

The product therefore complements PagerDuty-style alerting and internal voice escalation instead of competing with them.

## 2. Quality of the Idea

The non-obvious design choice is not “AI makes a support call.” It is the authority boundary around a real-world side effect.

IncidentBridge treats phone automation as a safety-critical state machine:

1. validate a non-secret incident briefing;
2. preview the exact task without creating a call;
3. require exact recipient authorization;
4. reserve the call durably before dispatch to prevent ambiguous retries;
5. require a strict structured result;
6. bind a successful result to workflow + incident + call ID + destination;
7. corroborate the returned ticket against recipient transcript evidence; and
8. keep `incident_closed: "false"` until human/local recovery verification.

The contribution is reusable: the official CALL-E repository accepted IncidentBridge as a community app after maintainer review, so the safety pattern is available to other builders rather than existing only as a competition-specific demo.

## 3. Technical Implementation

- Published `calle-ai==0.2.0` SDK is imported and exercised at runtime.
- Strict structured-result schema for support-desk consent, incident acknowledgment, ticket, status, ETA, workaround and escalation state.
- Exact E.164 authorization gate plus explicit live-call confirmation.
- Durable SQLite reservation prevents duplicate or ambiguous retries.
- Every free-text field entering the spoken task is screened for credentials, secrets and personal contact data.
- Unbound, incomplete, low-confidence or uncorroborated results fail closed to `needs_human`.
- Ticket corroboration rejects blank/`unknown` IDs and prefix/sub-string false matches while tolerating punctuation differences such as `SUP-4821` vs `SUP 4821`.
- **GitHub Actions verified Ruff plus 21 passing tests at 92.37% coverage**, above the enforced 90% gate.
- Integration tests exercise the actual SDK request/poll boundary through loopback HTTP rather than replacing the SDK with an internal mock.

### Independent upstream review

CALL-E maintainers reviewed IncidentBridge in `CALLE-AI/awesome-phone-call-agents` PR #132. The review identified two substantive security blockers:

1. privacy validation did not cover every free-text field entering the spoken task; and
2. a high-confidence structured result was not sufficiently bound to the approved request or corroborated by recipient evidence.

Both were fixed and regression-tested. The contribution was merged into the official CALL-E repository on August 17, 2026.

## 4. Product Experience & Demo

The public judge console intentionally distinguishes three states instead of presenting every path as “live”:

- **Public live-provider boundary:** a real CALL-E call reaches an unavailable voicemail and correctly fails closed without automatic retry.
- **Authorization preview:** shows the exact task, masked destination and decision boundary while creating no phone call.
- **Deterministic acknowledged simulation:** makes the complete success route inspectable without misrepresenting simulated data as a live call.

Successful live-call behavior has additionally been validated privately through direct testing, packaged external testing, and testing with randomly selected users. Those call materials are not published because they contain real participant and conversation data.

The demo narration is reproducible locally using an Apache-2.0 Kokoro-82M voice; no real person is cloned.

## What `vendor_acknowledged` actually means

A successful route requires all of the following:

- the call completed reliably;
- the destination matches the exact authorized number;
- the provider result is bound to the correct workflow and incident;
- the correct support desk consented after AI disclosure;
- the vendor acknowledged the incident;
- a meaningful ticket identifier was supplied; and
- recipient transcript evidence corroborates that ticket without accepting a shorter prefix as proof.

Even then, `incident_closed` remains `false`.

## Why the upstream merge matters

The official merge is not presented as a prize signal. It is independent evidence that the contribution was useful enough for CALL-E maintainers to review in detail, identify real flaws, require fixes, and accept the corrected implementation into their public community repository.