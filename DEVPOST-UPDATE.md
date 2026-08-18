# IncidentBridge — Devpost Submission Update

Use this copy to tighten the current Devpost Story before the submission deadline. The first section is deliberately judge-first because CALL-E rules allow judges to score from the submission text, images, and video without running the project.

## Short description / opening

**IncidentBridge removes one expensive interruption from incident response: the external vendor-support call.**

When a SaaS or data dependency fails, the same operator diagnosing the outage often has to wait on a support line, repeat incident context, then manually copy a vendor ticket, status, ETA, and workaround back into the incident workflow. IncidentBridge delegates exactly that bounded conversation to CALL-E.

The key safety decision is that **calls become evidence, never authority**. CALL-E can collect vendor facts, but it can never declare the service recovered. `incident_closed` stays false until local health checks and a human incident commander verify recovery.

This is a real CALL-E integration, not a mock transport. The published `calle-ai==0.2.0` SDK is imported and called at runtime. The implementation has been independently reviewed by CALL-E maintainers and merged into the official `CALLE-AI/awesome-phone-call-agents` repository as PR #132 after two substantive security blockers were identified, fixed, and regression-tested.

Current GitHub Actions verification: **21 passing tests, 92.37% coverage, Ruff clean, 90% coverage gate enforced.**

## Inspiration

Incident-response automation usually focuses on what happens inside the company: detect the incident, page the on-call engineer, assign ownership, or propose a fix. But a large class of outages also creates an external dependency: someone must contact a cloud/SaaS/data vendor and find out what the vendor actually knows.

That phone work is awkward to automate because a call is a real-world side effect. A useful system needs more than “AI can dial a number.” It needs an explicit authority boundary around who may be called, what may be disclosed, whether a result belongs to the approved call, and what downstream state the result is allowed to change.

IncidentBridge was built around that boundary.

## What it does

IncidentBridge coordinates one explicitly authorized vendor-support conversation:

1. validates a bounded, non-secret incident briefing;
2. previews the exact CALL-E task without creating a call;
3. requires an authorized business destination, explicit live-call confirmation, and an exact E.164 allowlist match;
4. writes a durable reservation before dispatch so an ambiguous provider outcome cannot become a blind duplicate call;
5. calls the vendor through the published CALL-E Python SDK;
6. requests a strict structured result: support-desk consent, incident acknowledgment, ticket ID, status, ETA, workaround, callback window, and escalation state;
7. binds any success result to the exact workflow, incident, call ID, and destination;
8. corroborates the returned ticket against recipient-side transcript evidence; and
9. returns either `vendor_acknowledged` or `needs_human` while always keeping `incident_closed=false`.

## Why it is different from incident-alerting agents

Internal escalation asks: **Who on our side knows about the incident and owns the next action?**

IncidentBridge answers a different question: **What does the external vendor know, what ticket did they create, what status/ETA/workaround did they give us, and can we trust that those facts came from the exact authorized call?**

It therefore complements PagerDuty-style alerting and internal voice escalation rather than duplicating them.

## How we built it

The application is a Python package around the published `calle-ai==0.2.0` SDK.

The runtime boundary is intentionally small. CALL-E owns call creation and polling; IncidentBridge owns the authorization, state, evidence, and incident-routing policy around that call.

Key implementation pieces:

- strict validated `IncidentRequest` input model;
- privacy screening across every free-text field that can enter the spoken task;
- exact E.164 destination authorization and explicit execute gates;
- deterministic idempotency identity;
- durable SQLite reservation and reconciliation state;
- strict CALL-E `result_schema`;
- fail-closed routing on non-terminal / incomplete / low-confidence / mismatched results;
- call/workflow/incident/destination binding;
- recipient-side transcript corroboration for ticket IDs;
- token-sequence corroboration that tolerates punctuation differences such as `SUP-4821` vs `SUP 4821` without accepting shorter prefix matches such as `SUP-48` vs `SUP-4821`;
- recursive phone/email/common-credential redaction;
- integration tests that exercise the real published SDK through loopback HTTP instead of replacing the SDK with an internal mock.

## Independent upstream review

The official CALL-E contribution is PR #132:

https://github.com/CALLE-AI/awesome-phone-call-agents/pull/132

CALL-E maintainers found two substantive blockers before merge:

1. privacy validation originally covered only the incident summary, while other free-text fields could also enter the spoken task; and
2. a high-confidence structured result was not sufficiently bound to the exact approved workflow/incident/call/destination or corroborated by recipient evidence.

Both issues were fixed and converted into regression tests. The contribution was then merged into the official CALL-E repository on August 17, 2026.

That review is important evidence for the project, but it is not presented as a prize signal: it shows that an external maintainer inspected the actual safety boundary, found real defects, and accepted the corrected implementation.

## What is real, what is simulated

The public evidence console labels the three paths explicitly:

- **Real provider boundary:** an authorized real CALL-E run reached an unavailable voicemail. CALL-E returned `task_completed=false`; IncidentBridge correctly returned `needs_human`, kept `incident_closed=false`, and did not automatically retry. A redacted real provider call ID is preserved in the public artifact.
- **No-call preview:** displays the exact task, masked recipient, schema, idempotency identity, and decision boundary without creating a phone call.
- **Deterministic acknowledged simulation:** exposes the complete success routing path without pretending the simulated result is a live call.

Successful live-call behavior has also been validated privately through direct testing, packaged external testing, and testing with randomly selected users. Those call materials are not public because they contain real participant and conversation data.

## Verification

GitHub Actions currently enforces:

```bash
uv run ruff check .
uv run pytest --cov=src/incidentbridge --cov-report=term-missing --cov-fail-under=90
```

Verified result:

- **21 tests passed**
- **92.37% total coverage**
- **90% minimum coverage gate**
- **Ruff clean**

The adversarial suite includes secret-bearing spoken inputs, wrong support desk, low confidence, incomplete schema, mismatched workflow/incident metadata, mismatched destination, mismatched call ID, missing recipient evidence, wrong ticket, blank ticket, case-variant `unknown`, prefix false matches, punctuation-tolerant valid ticket matching, recursive redaction, idempotency, durable reservation, and the real SDK HTTP boundary.

## Product / demo links

**Live evidence console**  
https://yangyangnovelist-hub.github.io/incidentbridge-calle/

**Source**  
https://github.com/yangyangnovelist-hub/incidentbridge-calle

**Official merged CALL-E contribution**  
https://github.com/CALLE-AI/awesome-phone-call-agents/pull/132

**Official merged app**  
https://github.com/CALLE-AI/awesome-phone-call-agents/tree/main/apps/python/incidentbridge

## Challenges we ran into

The hardest problem was deciding when a phone result is trustworthy enough to influence application state.

A structured JSON object with high confidence still might belong to the wrong workflow, wrong recipient, or wrong call; and a returned ticket ID still might not have been said by the recipient. That led to the request-binding and transcript-corroboration layer.

A second challenge was retries. A failed HTTP request is normally safe to retry; a phone call is not. The client can lose certainty after a call has already been dispatched. IncidentBridge therefore reserves intent durably and treats ambiguity as reconciliation rather than permission to dial again.

A third challenge was privacy. The maintainer review caught that protecting only the incident summary was insufficient because several other fields also enter the spoken task. The fix moved privacy validation to every spoken free-text field.

## Accomplishments

- Built a real runtime integration on the published CALL-E SDK.
- Completed a real provider call and preserved a redacted fail-closed evidence artifact.
- Kept live-call success testing separate from public artifacts to protect real participant/conversation data.
- Passed independent CALL-E maintainer review after fixing two substantive security blockers.
- Merged IncidentBridge into the official CALL-E community repository.
- Hardened ticket evidence against blank IDs, `unknown`, and substring/prefix false corroboration.
- Added continuous GitHub Actions verification: 21 tests, 92.37% coverage, Ruff clean.
- Published an impact-first evidence console and a safe judge reproduction path.

## What we learned

For an AI agent that creates a real-world side effect, “the model completed the task” is not a sufficient trust boundary.

The application needs to distinguish:

- authorization from intent;
- call completion from business success;
- structured output from corroborated evidence;
- external vendor status from internal recovery truth; and
- network retry semantics from physical-world retry semantics.

CALL-E made the telephony transport boundary straightforward. Most of the engineering effort went into making the result safe to consume.

## What's next

The next useful layer is integration into an incident-management system so a `vendor_acknowledged` result can attach a structured vendor-evidence receipt to the incident timeline while still leaving recovery/closure authority with local health checks and the incident commander.

The architecture deliberately does not need to become a general autonomous incident agent. The product is strongest when it stays narrow: **outsource the vendor conversation, not the recovery decision.**