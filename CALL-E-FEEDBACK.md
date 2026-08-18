# CALL-E Platform Feedback from IncidentBridge

This feedback comes from building and hardening IncidentBridge, a consent-first vendor incident-support coordinator using the published Python SDK. The project was reviewed and merged into `CALLE-AI/awesome-phone-call-agents` as PR #132.

The suggestions below are intentionally implementation-specific: each one maps to code IncidentBridge had to add around a real phone-call workflow.

## 1. Publish an authorization-bound success pattern, not only a result-reading pattern

The quickstart correctly shows that a terminal call can expose `status`, `task_completed`, `completion_confidence`, `evidence`, and `structured_result`. For workflows that trigger downstream state, builders also need a canonical pattern for proving that the result belongs to the exact action a human approved.

IncidentBridge had to add its own success-binding rule across:

- expected call ID;
- workflow ID;
- incident ID;
- exact authorized destination;
- structured ticket ID; and
- recipient transcript evidence corroborating that ticket.

**Suggestion:** add an official “before you act on a result” recipe showing how to bind a terminal result to the original approved request and how to fail closed when any binding is missing.

## 2. Make recipient evidence a documented, stable contract for downstream verification

A structured result is useful, but consequential workflows sometimes need to verify that a field is supported by what the recipient actually said. IncidentBridge currently walks recipient attempts and transcript turns, filters to recipient-side speakers, and checks that the returned ticket identifier appears in recipient evidence.

**Suggestion:** document a stable recipient-evidence surface (including transcript-turn speaker semantics) or provide an SDK helper such as `call.recipient_evidence()` / `call.corroborates(field, value)` so every integration does not invent a subtly different parser.

## 3. Add a first-class reconciliation recipe for ambiguous call creation and polling

A phone call is a real-world side effect. If the client loses certainty after dispatch, “try again” is not a harmless retry. IncidentBridge writes a durable reservation before provider dispatch and preserves ambiguous outcomes for reconciliation rather than redialing.

**Suggestion:** make this an explicit SDK/docs pattern:

1. derive an idempotency key from the authorized call intent;
2. persist intent before create;
3. persist call ID as soon as creation is acknowledged;
4. on timeout/transport uncertainty, reconcile the same intent/call instead of creating a new one; and
5. treat unresolved state as a first-class outcome.

A small reference implementation would prevent duplicate calls across many apps.

## 4. Provide a no-call request/schema preflight

Result schemas and task wording are part of the call contract, but discovering a preventable contract problem at live-create time spends developer attention on a side-effect boundary.

**Suggestion:** expose an official validation/preflight helper that can check request shape, supported schema subset, metadata shape, region/locale compatibility where possible, and task size without creating a call or spending credit.

This would make CI safer and would give builders a canonical alternative to custom local validators.

## 5. Add privacy/redaction primitives to the SDK

Phone workflows routinely return text that can contain phone numbers, email addresses, credentials accidentally spoken or copied into summaries, and other identifiers. IncidentBridge recursively redacts phone-, email-, and credential-like strings before exposing free text.

**Suggestion:** ship a conservative SDK redaction helper with documented limits, for example:

```text
redact_call_result(result, policy="basic_pii")
```

It should be opt-in and should never imply full compliance, but a shared baseline would be safer than dozens of incompatible regex implementations.

## 6. Expand the quickstart with a fail-closed terminal-result example

A terminal transport status is not the same thing as business success. IncidentBridge deliberately checks `status`, exact `task_completed`, confidence, complete schema, request binding, consent, escalation state, and corroboration before returning `vendor_acknowledged`.

**Suggestion:** add a second quickstart example where the call reaches a terminal state but the application must **not** act because `task_completed` is false, `structured_result` is null/incomplete, or evidence is insufficient. Showing the negative branch early would establish the correct mental model for new integrations.

## 7. Make metadata provenance guidance explicit

Metadata is extremely useful for tying a phone task back to an application workflow. IncidentBridge uses it for `workflow_id`, `workflow_type`, and `incident_id`, then checks the returned metadata before accepting a result.

**Suggestion:** document metadata as correlation data rather than authorization by itself, and recommend pairing it with call ID + destination + application-side state. That would help prevent builders from treating a user-controlled metadata echo as sufficient proof.

## What worked particularly well

- The Python SDK made the real call boundary small and easy to isolate.
- Native `result_schema` support made the post-call contract substantially safer than parsing prose.
- `task_completed`, confidence, evidence, and structured results expose enough information to build conservative application-level routing rather than treating “call ended” as “task succeeded.”
- The official community-repository review process materially improved IncidentBridge: maintainers found two substantive safety flaws before merge, and both became permanent regression tests.

## Bottom line

CALL-E already makes the transport side of real-world phone automation accessible. The highest-leverage next layer would be **reference primitives for trustworthy downstream action**: request binding, recipient-evidence corroboration, ambiguous-outcome reconciliation, preflight validation, and baseline redaction.

Those primitives would let builders spend less time rebuilding safety plumbing and more time on the actual phone-work problem.