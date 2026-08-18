# IncidentBridge

![IncidentBridge incident-to-call-to-evidence workflow](assets/incidentbridge-cover.png)

[![CI](https://github.com/yangyangnovelist-hub/incidentbridge-calle/actions/workflows/ci.yml/badge.svg)](https://github.com/yangyangnovelist-hub/incidentbridge-calle/actions/workflows/ci.yml)

**A consent-first CALL-E agent that turns a vendor-support phone call into structured incident
evidence without pretending the service recovered.**

[Open the live evidence console](https://yangyangnovelist-hub.github.io/incidentbridge-calle/) ·
[Model operator-time impact](https://yangyangnovelist-hub.github.io/incidentbridge-calle/impact-calculator.html) ·
[Run the local operator console](OPERATOR-CONSOLE.md) ·
[Review the official CALL-E contribution](https://github.com/CALLE-AI/awesome-phone-call-agents/pull/132) ·
[Read the judge guide](JUDGING.md)

## Judge in 90 seconds

1. Open the [evidence console](https://yangyangnovelist-hub.github.io/incidentbridge-calle/) and switch between the real fail-closed provider run, zero-call authorization preview, and deterministic acknowledged path.
2. Open [PR #132](https://github.com/CALLE-AI/awesome-phone-call-agents/pull/132) to verify that CALL-E maintainers reviewed the implementation, found two substantive safety blockers, and merged the corrected app.
3. Open the [impact calculator](https://yangyangnovelist-hub.github.io/incidentbridge-calle/impact-calculator.html) and use your own assumptions to estimate operator attention returned by delegating bounded vendor-support phone work.
4. Run `uv run incidentbridge-web` and open `http://127.0.0.1:8766/` for the local operator surface. Live execution is disabled by default.
5. Run the safe local reproduction in [`TESTING.md`](TESTING.md). No CALL-E key or external phone call is required for the preview, simulations, operator console, or SDK boundary test.

## Official CALL-E acceptance

IncidentBridge was reviewed by CALL-E maintainers and merged into the official
[`CALLE-AI/awesome-phone-call-agents`](https://github.com/CALLE-AI/awesome-phone-call-agents)
repository through [PR #132](https://github.com/CALLE-AI/awesome-phone-call-agents/pull/132) on
August 17, 2026.

The upstream review identified two security blockers before merge: every free-text field entering
the spoken task needed secret/privacy validation, and a successful terminal result needed to be
bound to the approved workflow, incident, call and destination and corroborated by recipient
transcript evidence. Both requirements are implemented in the current code and locked in by
regression tests in `tests/test_policy.py`.

## Real-world impact boundary

The product makes one deliberately narrow impact claim: **when an external vendor-support call can
be delegated safely, the on-call operator can avoid spending active attention on queueing, repeating
incident context, and manually transcribing the vendor response.**

IncidentBridge does not invent a universal MTTR reduction. Instead, [`IMPACT.md`](IMPACT.md) defines
a transparent operator-time model and a public browser calculator that lets a team use its own
call volume and time assumptions:

```text
operator_minutes_reclaimed
  = manual_operator_minutes - approval_and_review_minutes
```

The first business KPI for a real pilot is operator minutes reclaimed per delegated call. The first
safety KPIs are unauthorized-call rate and false-success rate, both of which should remain zero.

[Open the transparent impact calculator](https://yangyangnovelist-hub.github.io/incidentbridge-calle/impact-calculator.html).

## Validation status

The public repository contains a redacted real-provider boundary run plus deterministic simulation
and SDK-integration tests. In addition, successful live-call behavior has been validated privately
through direct testing, packaged external testing, and testing with randomly selected users. Those
private call materials are intentionally not published because they contain real participant and
conversation data.

Current reproducible checks:

- GitHub Actions verifies Ruff plus **27 automated tests at 93.14% coverage**, above the enforced 90% gate.
- The local operator console itself is 95% covered and reuses the same guarded execution path as the CLI.
- The published `calle-ai==0.2.0` SDK is exercised at runtime through the integration suite.
- A real CALL-E provider call ID is preserved in the redacted public fail-closed artifact.
- The implementation has completed upstream maintainer review and is merged into CALL-E's official
  phone-agent repository.

For an additional public success-path proof without exposing private participants, the repository
also includes a [`consented live success protocol`](LIVE-SUCCESS-DEMO.md) that uses a synthetic
incident and a phone number owned by or explicitly authorized by the tester.

When a critical SaaS or data dependency fails, operators often lose time waiting on a support line,
repeating context, and manually copying a ticket number and ETA into an incident channel.
IncidentBridge places one explicitly authorized phone call, discloses that it is AI, gathers a strict
result, and returns either `vendor_acknowledged` or `needs_human`.

The phone result can never close the incident. Local health checks and a human incident commander
retain recovery authority.

## Local operator console

IncidentBridge now ships a browser operator surface around the same policy and execution path:

```bash
uv sync --extra dev
uv run incidentbridge-web
```

Then open `http://127.0.0.1:8766/`.

By default the browser can preview the exact task and inspect deterministic routes but **cannot
place a phone call**. Live mode must be armed server-side with an explicit exact-number allowlist,
the separate CALL-E environment gates, a human authorization checkbox, and the typed phrase
`CALL AUTHORIZED`. The live server is loopback-only and rejects non-loopback Host headers.

See [`OPERATOR-CONSOLE.md`](OPERATOR-CONSOLE.md) for the full safe and live paths.

## Safety model

```text
incident → validated, non-secret briefing → masked preview → exact phone allowlist
         → durable reservation → CALL-E SDK → strict result schema
         → vendor acknowledged / needs human → local recovery verification
```

- Preview is the default and never calls anyone.
- Live mode requires an authorized business contact in the request, the exact E.164 phone number in
  `--allow`, `--confirm-authorized-recipient`, `CALLE_LIVE_CALLS_ENABLED=true`, and a server-side
  `CALLE_API_KEY`.
- The browser operator surface adds its own loopback-only, typed-confirmation, and server-side live-UI gates without bypassing the CLI execution policy.
- A SQLite reservation is written before provider dispatch. Any repeat or ambiguous outcome is
  locked for reconciliation instead of redialed.
- The task requests no credentials, authentication codes, personal data, payment data, or contract
  changes.
- Wrong desk, declined AI disclosure, low confidence, incomplete schema, uncertain provider state,
  or requested escalation all fail closed to `needs_human`.
- `vendor_acknowledged` additionally requires the terminal call ID, workflow, incident, and exact
  approved destination to match, plus recipient transcript evidence containing the returned ticket.
- Phone numbers, email addresses, and credential-like strings are redacted from returned free text.

## Install

```bash
uv venv --python 3.12 .venv
uv sync --extra dev
```

## Preview — no phone call

```bash
.venv/bin/incidentbridge --request examples/incident.json
```

The output includes the masked recipient, exact CALL-E task, strict JSON Schema, stable idempotency
key, and decision boundary.

## Simulate the complete result path — no phone call

```bash
.venv/bin/incidentbridge --request examples/incident.json --simulate acknowledged
.venv/bin/incidentbridge --request examples/incident.json --simulate wrong-desk
.venv/bin/incidentbridge --request examples/incident.json --simulate eta-unknown
```

## Execute one real CALL-E call

Use a phone number you own or have documented authorization to call. Replace the reserved example
number and keep credentials in the environment:

```bash
export CALLE_API_KEY="<CALL_E_API_KEY>"
export CALLE_LIVE_CALLS_ENABLED="true"

.venv/bin/incidentbridge \
  --request your-authorized-incident.json \
  --execute \
  --confirm-authorized-recipient \
  --allow +15555550100 \
  --database data/incidentbridge.sqlite3 \
  --output artifacts/live-result.json
```

The output path uses exclusive creation and will not overwrite an earlier audit result. If the SDK
accepts the call but polling fails, the reservation becomes `outcome_unknown`; inspect it before any
new call attempt.

## Structured output

CALL-E is asked for:

- correct support desk and consent after AI disclosure;
- incident acknowledgment and vendor ticket identifier;
- `investigating`, `identified`, `monitoring`, `resolved`, or `unknown` vendor status;
- ETA in minutes, a bounded workaround summary, and callback window; and
- explicit human-escalation need plus a short evidence summary.

Even when the vendor says `resolved`, IncidentBridge returns `incident_closed: "false"`.

## Test the real SDK boundary

```bash
.venv/bin/ruff check .
.venv/bin/pytest --cov=src/incidentbridge --cov-report=term-missing --cov-fail-under=90
```

The integration test runs the published `calle-ai==0.2.0` SDK against a loopback capture server and
asserts the observed `POST /v1/calls`, bearer authentication, idempotency header, strict schema, and
`GET /v1/calls/{id}` poll. It proves CALL-E is imported and called at runtime without placing a real
phone call during tests.

The current CI run reports **27 passed, 93.14% total coverage**, with the operator console module at
95% coverage.

## Verified public live boundary

An authorized live CALL-E run reached an unavailable voicemail, returned `task_completed: false`
with 0.85 confidence, and produced a real provider call ID. IncidentBridge treats that result as
`needs_human`, keeps `incident_closed: "false"`, and does not auto-retry. The redacted evidence is in
[`artifacts/calle-live-no-answer.json`](artifacts/calle-live-no-answer.json).

## Rebuild the demo video

The judge-focused V2 demo source is designed to stay under three minutes and now includes the
upstream merge, current CI proof, and transparent impact calculator. Build it with:

```bash
bash scripts/build-demo-v2.sh
```

The narration uses the Apache-2.0-licensed Kokoro-82M `bm_george` voice and does not clone a real
person. See [`video/DEMO-V2.md`](video/DEMO-V2.md) for the review and upload checklist.

## Scope

IncidentBridge coordinates a single business support conversation. It is not emergency response,
medical or legal advice, a recovery verifier, a contract agent, an auto-retry system, or a general
outbound campaign tool.

See [`THIRD_PARTY.md`](THIRD_PARTY.md) for the reuse boundary and
[`ADR-0001`](docs/architecture/adr-0001-official-calle-sdk.md) for the integration decision.

MIT licensed.