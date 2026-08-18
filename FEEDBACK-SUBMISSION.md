# CALL-E Feedback Survey — Submission Draft

This file maps directly to the current Devpost CALL-E Feedback Survey fields. It is written from the actual IncidentBridge build experience and avoids presenting app-level bugs as CALL-E platform bugs.

## Identity

**First Name**
Yang

**Last Name**
Yang

**Devpost Username**
yangyangnovelist-hub

**Email associated with your CALL-E account**
yangyangnovelist@gmail.com

**Did you start a project for this hackathon after July 23, 2026?**
Yes

**If you didn't finish and submit your project, why not?**
N/A — IncidentBridge was completed and submitted.

**Which CALL-E interfaces did you use?**
SDK

## What is a calling-related problem you face on a regular basis?

During operational incidents involving an external SaaS or data-platform dependency, the phone work creates a separate coordination tax: someone has to stop diagnosing the incident, wait on the vendor support line, repeat known context, then manually carry the vendor ticket, status, ETA, workaround, and callback information back into the incident workflow. The hard part is not simply making the call; it is getting structured facts back without accidentally treating “the vendor says resolved” as proof that the service has actually recovered.

## On a scale of 1 to 10, how painful would you rank this problem?

**Suggested: 8**

Reasoning: during a serious incident the interruption is expensive because it consumes the attention of the same operator who should be diagnosing and restoring the service. The frequency varies by team, but when it occurs the impact is high.

## What bugs or issues did you run into while using CALL-E, if any?

I did not find a core SDK bug that I can responsibly claim from this build. The main friction was that several safety-critical application patterns were left to each integrator to design independently:

1. **Binding a terminal result to the exact approved action.** A high-confidence structured result is not enough for a consequential workflow. IncidentBridge had to bind the result to the expected call ID, workflow ID, incident ID, exact authorized destination, and recipient evidence before allowing a `vendor_acknowledged` route.

2. **Corroborating structured output with recipient evidence.** We needed to verify that a returned vendor ticket was actually supported by recipient-side transcript evidence. This required application-specific parsing of `recipients -> attempts -> transcript_turns` and careful speaker filtering.

3. **Ambiguous create/poll outcomes.** A phone call is a real-world side effect, so “retry after uncertainty” can create a duplicate call. We implemented a durable reservation before dispatch, persisted the provider call ID as soon as it existed, and route ambiguous outcomes to reconciliation rather than automatically redialing.

4. **No-call preflight.** It would be useful to validate the request, result schema, metadata shape, and other supported contract details without spending a call or reaching the side-effect boundary.

5. **Baseline output redaction.** Phone results can contain phone numbers, emails, or credential-like strings. We implemented recursive redaction locally; a conservative SDK helper would give integrations a safer common baseline.

These are mostly missing reference patterns / primitives rather than transport failures.

## What would have given you a better experience with our CALL-E documentation?

The biggest improvement would be a second quickstart called something like **“Before you act on a call result.”** The current happy path makes call creation and structured results easy to understand; the next layer should show how to consume those results safely in a real application.

I would include one end-to-end example covering:

- derive and persist an idempotency key from the human-approved call intent;
- create the call and persist the call ID immediately;
- distinguish terminal transport state from business success;
- validate the complete structured-result schema;
- bind the result back to application metadata, call ID, and destination;
- inspect recipient-side evidence for claims that trigger downstream actions;
- fail closed on low confidence, incomplete results, mismatched context, or missing evidence; and
- reconcile an uncertain create/poll outcome instead of simply issuing another call.

I would also document the intended stability and speaker semantics of recipient transcript/evidence fields, because those become part of the trust boundary once an application acts on structured results.

## How likely are you to use CALL-E in the future?

**Suggested: 9 / 10**

The SDK made the actual phone-call boundary small and straightforward, and `result_schema` is especially valuable. The main reason I would not select 10 yet is that consequential workflows still need substantial application-side safety plumbing around authorization binding, evidence corroboration, ambiguous retries, and privacy handling.

## Is there any other feedback you'd like to provide?

The highest-leverage roadmap opportunity I see is to make **trustworthy downstream action** a first-class CALL-E pattern, not only successful call transport.

Concrete suggestions:

1. Add an official `before you act on a result` recipe for request/call/destination binding.
2. Document a stable recipient-evidence contract or add an SDK helper for recipient-side evidence extraction/corroboration.
3. Publish an idempotent reconciliation pattern for ambiguous create/poll outcomes so integrations do not accidentally redial.
4. Add a no-call request/schema preflight helper for CI and local validation.
5. Provide an opt-in conservative redaction helper for common phone/email/credential-like data, with clear documentation that it is a baseline rather than a compliance guarantee.
6. Add a fail-closed quickstart where the call reaches a terminal state but the application correctly refuses to act because `task_completed`, schema completeness, confidence, or evidence is insufficient.
7. Clarify that metadata is useful correlation context but should not be treated as authorization/provenance by itself; pair it with provider call identity, authorized destination, and application-side state.

What worked particularly well: the Python SDK was easy to isolate behind a small runtime boundary; native structured-result schemas made the integration much safer than parsing prose; and the official `awesome-phone-call-agents` review process materially improved our app. In IncidentBridge PR #132, maintainers found two substantive safety problems before merge, and those review comments became permanent regression tests. That review loop is worth preserving as the ecosystem grows.

## Are you open to being contacted by the CALL-E team?

Yes

**Contact email:**
yangyangnovelist@gmail.com

---

# Discord #support version

The survey strongly encourages sharing feedback in CALL-E Discord. This is a shorter version suitable for one post:

> Built IncidentBridge with the CALL-E Python SDK and wanted to share the highest-leverage gaps I hit around consequential phone workflows. The SDK makes the call boundary easy, but I had to build several trust primitives application-side: (1) bind a terminal result back to the exact approved call/workflow/incident/destination, (2) corroborate action-driving structured fields against recipient-side transcript evidence, (3) persist call intent/idempotency before dispatch and reconcile uncertain outcomes rather than blindly redial, (4) recursively redact phone/email/credential-like output, and (5) validate as much of the call contract as possible before reaching the side-effect boundary. I’d love to see an official “before you act on a call result” quickstart plus a stable recipient-evidence contract/helper, a reconciliation recipe, no-call preflight, and an opt-in baseline redaction helper. One thing that worked especially well: the upstream review process. CALL-E maintainers found two real safety blockers in IncidentBridge PR #132; after fixing them, we converted both into regression tests and the app was merged. That kind of review loop is extremely valuable for a platform that triggers real-world side effects.

After posting it manually, paste the Discord message URL into the survey field **“Please share a link to your feedback posted on Discord.”**