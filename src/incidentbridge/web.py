"""Local operator console for previewing and authorizing one IncidentBridge call."""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
import sys
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from incidentbridge.cli import execute_once
from incidentbridge.models import parse_request
from incidentbridge.policy import preview, simulated_result
from incidentbridge.runtime import DEFAULT_BASE_URL

MAX_BODY_BYTES = 64 * 1024
CONFIRM_PHRASE = "CALL AUTHORIZED"

EXAMPLE_REQUEST = {
    "workflow_id": "wf-acme-vendor-outage-001",
    "incident_id": "INC-2026-0810",
    "support_phone": "+15555550100",
    "authorized_support_contact": True,
    "caller_business_name": "Acme Data Operations",
    "provider_name": "ExampleCloud",
    "affected_service": "managed ingestion endpoint",
    "incident_summary": (
        "Requests return elevated 503 responses and the public status page has no incident entry."
    ),
    "severity": "outage",
    "observed_at_utc": "2026-08-10T01:20:00Z",
    "region": "US",
    "locale": "en-US",
}

OPERATOR_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IncidentBridge Operator Console</title>
<style>
:root{--ink:#11100e;--paper:#f4efe3;--muted:#6d675d;--orange:#ff4d19;--green:#a3ed72;--line:#24221f;--white:#fff9ee}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:Inter,system-ui,sans-serif}.wrap{width:min(1180px,calc(100% - 32px));margin:auto}header{padding:36px 0 24px;border-bottom:2px solid var(--line)}.eyebrow{font:700 11px/1.4 ui-monospace,monospace;letter-spacing:.1em;text-transform:uppercase;color:var(--orange)}h1{font-size:clamp(42px,6vw,78px);line-height:.92;letter-spacing:-.055em;margin:12px 0 18px}.lead{max-width:800px;font-size:19px;line-height:1.5;color:#443f38}.badge{display:inline-block;border:2px solid var(--line);padding:8px 11px;font-weight:800;margin-right:8px}.badge.safe{background:var(--green)}main{display:grid;grid-template-columns:1fr 1fr;gap:18px;padding:30px 0 55px}.card{border:2px solid var(--line);background:var(--white);padding:22px}.card h2{font-size:28px;margin:0 0 16px;letter-spacing:-.035em}textarea{width:100%;min-height:440px;resize:vertical;border:2px solid var(--line);background:white;padding:14px;font:13px/1.55 ui-monospace,monospace}.actions{display:flex;flex-wrap:wrap;gap:9px;margin-top:14px}button{border:2px solid var(--line);padding:12px 14px;font-weight:850;background:var(--green);cursor:pointer}button.secondary{background:white}button.live{background:var(--orange)}button:disabled{opacity:.38;cursor:not-allowed}.livebox{margin-top:18px;border-top:2px solid var(--line);padding-top:16px}.livebox label{display:block;font-weight:750;margin:9px 0}.livebox input[type=text]{width:100%;padding:11px;border:2px solid var(--line);font:700 14px ui-monospace,monospace}.hint{font-size:13px;line-height:1.5;color:var(--muted)}.result{background:var(--ink);color:white}.result pre{white-space:pre-wrap;word-break:break-word;min-height:520px;max-height:720px;overflow:auto;margin:0;padding:18px;background:#1d1b18;border-left:5px solid #35d3ca;color:#ded9d0;font:12px/1.6 ui-monospace,monospace}.status{display:flex;justify-content:space-between;gap:12px;align-items:center;margin-bottom:14px}.status strong{color:var(--green)}.warning{border:2px solid var(--orange);padding:12px;margin-top:12px;line-height:1.45}@media(max-width:850px){main{grid-template-columns:1fr}textarea{min-height:360px}}
</style>
</head>
<body>
<header><div class="wrap"><div class="eyebrow">IncidentBridge · local operator surface</div><h1>Approve the phone task. Never approve recovery.</h1><p class="lead">Preview and simulate locally. Live execution stays disabled unless the server was started with an explicit allowlist and live-UI flag, and the CALL-E environment is also enabled.</p><span class="badge safe">Preview-first</span><span class="badge">Server-side key only</span><span class="badge">Exact-number allowlist</span></div></header>
<main class="wrap">
<section class="card"><h2>Incident request</h2><textarea id="request"></textarea><div class="actions"><button id="preview">Preview — no call</button><button id="simulate" class="secondary">Simulate acknowledged</button></div><div class="livebox"><h2>Live authorization</h2><p class="hint" id="capability">Checking server capability…</p><label><input id="consent" type="checkbox"> I confirm this business recipient is authorized to receive this AI call.</label><label for="phrase">Type <code>CALL AUTHORIZED</code></label><input id="phrase" type="text" autocomplete="off" placeholder="CALL AUTHORIZED"><div class="actions"><button id="execute" class="live" disabled>Place one authorized CALL-E call</button></div><div class="warning">A terminal phone result is evidence only. IncidentBridge never sets <code>incident_closed</code> to true.</div></div></section>
<section class="card result"><div class="status"><h2>Evidence output</h2><strong id="status">Ready</strong></div><pre id="output">Choose Preview first. No external phone call is created by preview or simulation.</pre></section>
</main>
<script>
const example = __EXAMPLE__;
const requestBox=document.querySelector('#request');const output=document.querySelector('#output');const status=document.querySelector('#status');const execute=document.querySelector('#execute');const consent=document.querySelector('#consent');const phrase=document.querySelector('#phrase');let liveServer=false;
requestBox.value=JSON.stringify(example,null,2);
function body(){return JSON.parse(requestBox.value)}
async function post(path,payload){status.textContent='Working…';const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const data=await r.json();output.textContent=JSON.stringify(data,null,2);status.textContent=r.ok?'Verified output':'Blocked';if(!r.ok)throw new Error(data.error||'request failed');return data}
fetch('/api/capabilities').then(r=>r.json()).then(c=>{liveServer=c.live_ui_enabled;document.querySelector('#capability').textContent=liveServer?`Live UI armed server-side · ${c.allowlist_count} allowlisted destination(s). CALL-E environment is ${c.live_environment_ready?'ready':'not ready'}.`:'Live UI is disabled on this server. Preview and simulation remain available.';sync()}).catch(()=>{document.querySelector('#capability').textContent='Could not read server capability.'});
function sync(){execute.disabled=!(liveServer&&consent.checked&&phrase.value===`CALL AUTHORIZED`)}consent.addEventListener('change',sync);phrase.addEventListener('input',sync);
document.querySelector('#preview').onclick=()=>post('/api/preview',{request:body()}).catch(()=>{});
document.querySelector('#simulate').onclick=()=>post('/api/simulate',{request:body(),scenario:'acknowledged'}).catch(()=>{});
execute.onclick=()=>{if(!window.confirm('Place exactly one authorized CALL-E phone call? Ambiguous outcomes will not be blindly retried.'))return;post('/api/execute',{request:body(),confirm_authorized_recipient:consent.checked,confirm_phrase:phrase.value}).catch(()=>{})};
</script>
</body></html>""".replace("__EXAMPLE__", json.dumps(EXAMPLE_REQUEST))


@dataclass(frozen=True)
class WebConfig:
    """Server-side live-call controls. Client input cannot expand these permissions."""

    allow: tuple[str, ...] = ()
    enable_live_ui: bool = False
    timeout_seconds: int = 600
    base_url: str = DEFAULT_BASE_URL
    database: Path = Path("data/incidentbridge-web.sqlite3")

    def capabilities(self) -> dict[str, Any]:
        return {
            "live_ui_enabled": self.enable_live_ui,
            "allowlist_count": len(self.allow),
            "live_environment_ready": (
                os.environ.get("CALLE_LIVE_CALLS_ENABLED", "").lower() == "true"
                and bool(os.environ.get("CALLE_API_KEY"))
            ),
            "recovery_authority": "human_and_local_health_checks_only",
        }


class OperatorServer(ThreadingHTTPServer):
    """HTTP server carrying immutable server-side execution policy."""

    daemon_threads = True

    def __init__(self, server_address: tuple[str, int], config: WebConfig):
        self.config = config
        super().__init__(server_address, OperatorHandler)


class OperatorHandler(BaseHTTPRequestHandler):
    server: OperatorServer

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        sys.stderr.write("incidentbridge-web: " + (format % args) + "\n")

    def _json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        data = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _html(self) -> None:
        data = OPERATOR_HTML.encode()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(data)

    def _payload(self) -> dict[str, Any]:
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            raise ValueError("Content-Type must be application/json")
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("invalid Content-Length") from exc
        if length <= 0 or length > MAX_BODY_BYTES:
            raise ValueError("request body must be between 1 byte and 64 KiB")
        value = json.loads(self.rfile.read(length))
        if not isinstance(value, dict):
            raise ValueError("request body must be a JSON object")
        return value

    @staticmethod
    def _request(payload: dict[str, Any]):
        raw = payload.get("request")
        if not isinstance(raw, dict):
            raise ValueError("request must be a JSON object")
        return parse_request(raw)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/":
            self._html()
        elif self.path == "/api/capabilities":
            self._json(HTTPStatus.OK, self.server.config.capabilities())
        else:
            self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        try:
            payload = self._payload()
            request = self._request(payload)
            if self.path == "/api/preview":
                result = preview(request)
            elif self.path == "/api/simulate":
                scenario = payload.get("scenario", "acknowledged")
                if scenario not in {"acknowledged", "wrong-desk", "eta-unknown"}:
                    raise ValueError("unsupported simulation scenario")
                result = simulated_result(request, scenario)
            elif self.path == "/api/execute":
                result = self._execute(request, payload)
            else:
                self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
                return
            self._json(HTTPStatus.OK, result)
        except json.JSONDecodeError:
            self._json(HTTPStatus.BAD_REQUEST, {"error": "invalid JSON"})
        except ValueError as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except RuntimeError as exc:
            self._json(HTTPStatus.CONFLICT, {"error": str(exc)})
        except OSError as exc:
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": type(exc).__name__})

    def _execute(self, request, payload: dict[str, Any]) -> dict[str, Any]:
        config = self.server.config
        if not config.enable_live_ui:
            raise ValueError("live execution is disabled on this operator server")
        if payload.get("confirm_authorized_recipient") is not True:
            raise ValueError("live execution requires recipient authorization confirmation")
        if payload.get("confirm_phrase") != CONFIRM_PHRASE:
            raise ValueError(f"live execution requires typing {CONFIRM_PHRASE}")
        if request.support_phone not in config.allow:
            raise ValueError("destination is not in the server-side exact-number allowlist")

        args = argparse.Namespace(
            confirm_authorized_recipient=True,
            allow=list(config.allow),
            timeout_seconds=config.timeout_seconds,
            base_url=config.base_url,
            database=config.database,
        )
        return execute_once(request, args)


def is_loopback_host(host: str) -> bool:
    """Return true only for localhost or a literal loopback IP address."""
    if host.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--allow", action="append", default=[])
    parser.add_argument("--enable-live-ui", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--base-url", default=os.environ.get("CALLE_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument(
        "--database",
        type=Path,
        default=Path(os.environ.get("INCIDENTBRIDGE_WEB_DB_PATH", "data/incidentbridge-web.sqlite3")),
    )
    return parser.parse_args(argv)


def build_server(args: argparse.Namespace) -> OperatorServer:
    if args.port < 0 or args.port > 65535:
        raise ValueError("port must be between 0 and 65535")
    if args.timeout_seconds <= 0:
        raise ValueError("timeout-seconds must be positive")
    if args.enable_live_ui and not is_loopback_host(args.host):
        raise ValueError("live operator UI may only bind to a loopback host")
    if args.enable_live_ui and not args.allow:
        raise ValueError("live operator UI requires at least one exact --allow destination")
    config = WebConfig(
        allow=tuple(dict.fromkeys(args.allow)),
        enable_live_ui=args.enable_live_ui,
        timeout_seconds=args.timeout_seconds,
        base_url=args.base_url,
        database=args.database,
    )
    return OperatorServer((args.host, args.port), config)


def main(argv: list[str] | None = None) -> int:
    try:
        server = build_server(parse_args(argv))
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    host, port = server.server_address[:2]
    sys.stdout.write(f"IncidentBridge operator console: http://{host}:{port}/\n")
    if not server.config.enable_live_ui:
        sys.stdout.write("Live execution is disabled; preview and simulation only.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
