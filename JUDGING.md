# IncidentBridge — Judge Guide

IncidentBridge is a consent-first CALL-E agent for one bounded real-world task: contact an authorized vendor support line during an incident, collect ticket/status/ETA/workaround facts, and return structured evidence without allowing the phone agent to close the incident.

## Why it matters

During SaaS and data-platform incidents, operators lose recovery time waiting on support lines and manually relaying context. IncidentBridge delegates only that conversation while keeping recovery authority with local health checks and a human incident commander.

## Why the idea is differentiated

This is not a generic outbound agent or a scripted phone demo. The core product decision is the authority boundary: CALL-E may gather vendor evidence, but it cannot claim recovery, change contracts, retry ambiguously, or close the incident.

The implementation also treats phone automation as a safety-critical state machine rather than a single LLM response. A successful `vendor_acknowledged` result must be bound to the approved workflow, incident, call ID and destination, then corroborated against recipient transcript evidence.

## Technical implementation

- Published `calle-ai==0.2.0` SDK is imported and exercised at runtime.
- Strict structured-result schema for support-desk consent, incident acknowledgment, ticket, status, ETA, workaround and escalation state.
- Exact E.164 authorization gate plus explicit live-call confirmation.
- Durable SQLite reservation prevents duplicate or ambiguous retries.
- Every free-text field entering the spoken task is screened for credentials, secrets and personal contact data.
- Unbound, incomplete, low-confidence or uncorroborated results fail closed to `needs_human`.
- 19 automated tests pass with 92.29% coverage.
- Integration tests exercise the actual SDK request/poll boundary through loopback HTTP rather than replacing the SDK with an internal mock.

## Independent upstream review

CALL-E maintainers reviewed IncidentBridge in `CALLE-AI/awesome-phone-call-agents` PR #132. The review identified two substantive security blockers: incomplete privacy validation across spoken fields and insufficient binding/corroboration of successful terminal results.

Both were fixed, regression-tested, and the contribution was merged into the official CALL-E repository on August 17, 2026.

PR: https://github.com/CALLE-AI/awesome-phone-call-agents/pull/132

## Real-world validation

The public repo includes a redacted real-provider run that demonstrates correct fail-closed behavior when the destination cannot complete the support conversation.

Successful live-call behavior has additionally been validated privately through direct testing, packaged external testing, and testing with randomly selected users. Those call materials are not published because they contain real participant and conversation data.

## Product experience

- Live evidence console: https://yangyangnovelist-hub.github.io/incidentbridge-calle/
- Public demo flow covers real boundary evidence, safe preview, deterministic success-path simulation and the human recovery boundary.
- Demo narration is reproducible locally using an Apache-2.0 Kokoro-82M voice; no real person is cloned.

## What a successful run means

`vendor_acknowledged` means the correct authorized destination consented to continue, the vendor acknowledged the incident, a ticket identifier was returned, the result was tied to the approved call context, and the ticket was corroborated by recipient transcript evidence.

It never means the incident is closed. `incident_closed` remains `false` until a human verifies service recovery.
