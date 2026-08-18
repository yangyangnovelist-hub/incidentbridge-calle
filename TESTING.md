# IncidentBridge — Fast Judge Testing

This path is intentionally safe: the default checks do **not** place a phone call and do not require a CALL-E API key.

## 0. Ninety-second judge path

If you only have ninety seconds:

1. Open the evidence console: https://yangyangnovelist-hub.github.io/incidentbridge-calle/
2. Click all three scenarios and verify the route changes while `incident_closed` never becomes true.
3. Open the impact calculator: https://yangyangnovelist-hub.github.io/incidentbridge-calle/impact-calculator.html and change the assumptions.
4. Run `uv run incidentbridge-web`, open `http://127.0.0.1:8766/`, and click **Preview — no call**. Live calling is disabled by default.
5. Verify official upstream acceptance: https://github.com/CALLE-AI/awesome-phone-call-agents/pull/132
6. Inspect `tests/test_sdk_runtime.py`, `tests/test_policy.py`, `tests/test_web.py`, and `tests/test_live_demo.py` for the runtime, policy, operator-surface, and public-live-proof boundaries.

## 1. Inspect the public evidence surface

Open:

https://yangyangnovelist-hub.github.io/incidentbridge-calle/

The page exposes three clearly labeled states:

- a redacted **real CALL-E provider boundary** that failed closed when the destination could not complete the conversation;
- a **no-call authorization preview**; and
- a **deterministic success-path simulation** that shows the complete `vendor_acknowledged` route without representing simulated data as a live call.

The separate impact calculator runs entirely in the browser and lets a judge test the real-world value proposition with their own assumptions rather than relying on a fabricated ROI claim:

https://yangyangnovelist-hub.github.io/incidentbridge-calle/impact-calculator.html

## 2. Install

Requires Python 3.12+ and `uv`.

```bash
uv venv --python 3.12 .venv
uv sync --extra dev
```

## 3. Run the local operator console — live disabled by default

```bash
uv run incidentbridge-web
```

Open:

```text
http://127.0.0.1:8766/
```

The default server supports preview and deterministic simulation but has no live-call permission. The browser can edit the synthetic incident, preview the exact CALL-E task, and inspect the returned evidence boundary.

Live execution is not merely hidden in the UI; it is disabled server-side unless the process is deliberately restarted with `--enable-live-ui` and an exact server-side `--allow` number. Additional environment and human-confirmation gates still apply.

See `OPERATOR-CONSOLE.md` for the complete safe/live model.

## 4. Run the CLI no-call product paths

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

## 5. Run the technical proof

```bash
uv run ruff check .
uv run pytest --cov=src/incidentbridge --cov-report=term-missing --cov-fail-under=90
```

Final award-sprint GitHub Actions result:

```text
33 passed
93.80% total coverage
99% coverage for src/incidentbridge/live_demo.py
95% coverage for src/incidentbridge/web.py
Ruff: all checks passed
Demo JS/Bash source syntax: passed
```

The enforced repository gate remains 90%. The GitHub Actions workflow runs lint, the full regression suite, coverage, and demo-source syntax checks on pushes to `main` and on pull requests.

The SDK integration test uses the published `calle-ai==0.2.0` package against a loopback HTTP capture server. It verifies that the real SDK performs the create-call request and result poll, including bearer auth, idempotency and the strict result schema, without creating an external phone call during the test suite.

The operator-console tests verify disabled-by-default live behavior, server-side exact-number allowlisting, human confirmation, duplicate-call reconciliation, loopback-only live binding, and browser/server startup behavior.

The consented-live-runner tests verify that the synthetic public proof path requires exact consent, refuses stale/overwritten public proof, emits no phone/transcript/participant identity, creates a public artifact only on `vendor_acknowledged`, and preserves failed results only in an ignored local data path with an explicit no-blind-retry error.

## 6. Inspect the upstream-review and adversarial security fixes

The highest-value regression cases are in `tests/test_policy.py`:

- secret/contact data is rejected from every free-text field that can enter the spoken task;
- mismatched workflow/incident metadata fails closed;
- mismatched destination fails closed;
- mismatched call ID fails closed;
- missing recipient transcript evidence fails closed;
- a returned ticket that is not corroborated by recipient transcript evidence fails closed;
- blank and case-variant `unknown` ticket IDs fail closed;
- a short ticket cannot be "corroborated" merely because it is a substring/prefix of a longer ticket; and
- punctuation differences such as `SUP-4821` vs `SUP 4821` are tolerated without weakening token equality.

## 7. Verify independent upstream acceptance

CALL-E maintainers reviewed the contribution and merged it into the official repository:

- PR: https://github.com/CALLE-AI/awesome-phone-call-agents/pull/132
- Official app: https://github.com/CALLE-AI/awesome-phone-call-agents/tree/main/apps/python/incidentbridge

A follow-up hardening branch for ticket corroboration is maintained in the contributor fork so the official app can receive the same adversarial fix.

## 8. Inspect the impact methodology and prior-art boundary

Read `IMPACT.md` for the transparent model. It intentionally measures operator attention returned to incident work rather than claiming an unmeasured universal MTTR reduction.

Read `PRIOR-ART.md` for direct official CALL-E references showing why IncidentBridge is distinct from internal incident paging and phone-line synthetic monitoring.

The recommended production-pilot metrics include:

- manual operator minutes per vendor-support interaction;
- approval/review minutes after delegation;
- exception rate;
- evidence completeness;
- duplicate-call rate;
- unauthorized-call rate; and
- false-success rate.

## Optional public live success validation

A live call should only be made to a phone number the tester owns or a consenting adult has explicitly authorized for this synthetic test.

The one-shot runner fixes the incident to synthetic data and uses the same guarded runtime:

```bash
export CALLE_API_KEY="<CALL_E_API_KEY>"
export CALLE_LIVE_CALLS_ENABLED="true"

uv run incidentbridge-consented-live-demo \
  --phone +<AUTHORIZED_E164_NUMBER> \
  --confirm-consent "I HAVE EXPLICIT CONSENT"
```

On a true success path, it creates `artifacts/consented-live-success.json`. On a failed or ambiguous path, it creates no public success artifact, stores the result under ignored `data/`, and tells the operator not to blindly retry.

See `LIVE-SUCCESS-DEMO.md` for the exact recipient script, fixed synthetic scenario, and public claim boundary.

The repository does not include real phone numbers, credentials, recordings or private participant transcripts.