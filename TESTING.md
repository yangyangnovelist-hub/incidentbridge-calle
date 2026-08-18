# IncidentBridge — Fast Judge Testing

This path is intentionally safe: the first three checks do **not** place a phone call and do not require a CALL-E API key.

## 1. Inspect the live product surface

Open:

https://yangyangnovelist-hub.github.io/incidentbridge-calle/

The page exposes three clearly labeled states:

- a redacted **real CALL-E provider boundary** that failed closed when the destination could not complete the conversation;
- a **no-call authorization preview**; and
- a **deterministic success-path simulation** that shows the complete `vendor_acknowledged` route without representing simulated data as a live call.

## 2. Install

Requires Python 3.12+ and `uv`.

```bash
uv venv --python 3.12 .venv
uv sync --extra dev
```

## 3. Run the no-call product paths

Preview the exact task, destination mask, result schema and decision boundary:

```bash
.venv/bin/incidentbridge --request examples/incident.json
```

Exercise the acknowledged route without placing a phone call:

```bash
.venv/bin/incidentbridge --request examples/incident.json --simulate acknowledged
```

Exercise two fail-closed paths:

```bash
.venv/bin/incidentbridge --request examples/incident.json --simulate wrong-desk
.venv/bin/incidentbridge --request examples/incident.json --simulate eta-unknown
```

Expected invariant: the phone workflow never sets `incident_closed` to true.

## 4. Run the technical proof

```bash
uv run ruff check .
uv run pytest --cov=src/incidentbridge --cov-report=term-missing --cov-fail-under=90
```

Expected result: 19 tests pass and the enforced coverage gate remains above 90%.

The SDK integration test uses the published `calle-ai==0.2.0` package against a loopback HTTP capture server. It verifies that the real SDK performs the create-call request and result poll, including bearer auth, idempotency and the strict result schema, without creating an external phone call during the test suite.

## 5. Inspect the two upstream-review security fixes

The highest-value regression cases are in `tests/test_policy.py`:

- secret/contact data is rejected from every free-text field that can enter the spoken task;
- mismatched workflow/incident metadata fails closed;
- mismatched destination fails closed;
- mismatched call ID fails closed;
- missing recipient transcript evidence fails closed; and
- a returned ticket that is not corroborated by recipient transcript evidence fails closed.

## 6. Verify independent upstream acceptance

CALL-E maintainers reviewed the contribution and merged it into the official repository:

- PR: https://github.com/CALLE-AI/awesome-phone-call-agents/pull/132
- Official app: https://github.com/CALLE-AI/awesome-phone-call-agents/tree/main/apps/python/incidentbridge

## Optional live execution

A live call should only be made to a business number the tester owns or is explicitly authorized to call. Live mode additionally requires an exact-number allowlist, an explicit authorization flag, `CALLE_LIVE_CALLS_ENABLED=true`, and a valid CALL-E API key.

The repository does not include real phone numbers, credentials, recordings or private participant transcripts.