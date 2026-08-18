# IncidentBridge Operator Console

IncidentBridge now includes a local browser operator surface that reuses the same preview, policy, durable reservation, and CALL-E execution path as the CLI.

The browser UI is intentionally local-first. The CALL-E API key never enters browser JavaScript, and live calling is disabled unless the server is explicitly armed with a server-side exact-number allowlist.

## Safe judge path — no phone call

Install the project and start the console:

```bash
uv sync --extra dev
uv run incidentbridge-web
```

Open:

```text
http://127.0.0.1:8766/
```

With the default command:

- preview works;
- deterministic simulations work;
- the browser can inspect structured evidence; and
- **live execution is disabled server-side**.

A judge can paste or edit an incident request, click **Preview — no call**, and inspect the exact CALL-E task/result boundary without a CALL-E credential or phone side effect.

## Live mode — only for an authorized destination

Use a number you own or have explicit permission to call. Keep the CALL-E key in the server environment:

```bash
export CALLE_API_KEY="<CALL_E_API_KEY>"
export CALLE_LIVE_CALLS_ENABLED="true"

uv run incidentbridge-web \
  --enable-live-ui \
  --allow +<AUTHORIZED_E164_NUMBER> \
  --database data/operator-console.sqlite3
```

Then open `http://127.0.0.1:8766/`.

The **Place one authorized CALL-E call** button remains disabled until the operator:

1. starts the server with `--enable-live-ui`;
2. starts it with at least one exact server-side `--allow` number;
3. supplies the separate `CALLE_LIVE_CALLS_ENABLED=true` environment gate;
4. keeps a valid `CALLE_API_KEY` server-side;
5. checks the recipient-authorization confirmation box; and
6. types the exact phrase `CALL AUTHORIZED`.

The server also rejects live execution if the HTTP `Host` header is not loopback, which reduces the localhost DNS-rebinding attack surface.

## Duplicate prevention still applies

The web UI calls the same `execute_once` path as the CLI. Before CALL-E dispatch, IncidentBridge claims a durable SQLite reservation keyed to the approved call intent.

If a call is already reserved, or an accepted provider call has an ambiguous outcome, the operator console does not blindly redial. The workflow routes to reconciliation.

## Recovery authority does not change

The browser UI does not add a new authority path. A completed CALL-E call can return structured vendor evidence and route to `vendor_acknowledged`, but it still cannot set `incident_closed=true`.

Local service health and the human incident commander remain the recovery authority.

## Automated verification

`tests/test_web.py` exercises:

- the packaged browser surface;
- preview and acknowledged simulation;
- live-UI disabled-by-default behavior;
- explicit human confirmation gates;
- exact server-side allowlisting;
- live success through the same mocked CALL-E SDK boundary used by the existing suite;
- duplicate reservation rejection;
- loopback-only live server binding; and
- startup/error behavior.

This is a product surface around the existing safety model, not a second implementation of the call policy.
