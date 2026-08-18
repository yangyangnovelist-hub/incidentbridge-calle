import argparse
import json
import threading
from contextlib import contextmanager
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import calle
import pytest

from incidentbridge.web import CONFIRM_PHRASE, WebConfig, build_server
from tests.test_policy import RAW
from tests.test_runtime import FakeCalls, completed_response


@contextmanager
def running_server(config: WebConfig):
    args = argparse.Namespace(
        host="127.0.0.1",
        port=0,
        allow=list(config.allow),
        enable_live_ui=config.enable_live_ui,
        timeout_seconds=config.timeout_seconds,
        base_url=config.base_url,
        database=config.database,
    )
    server = build_server(args)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def get_json(base: str, path: str):
    with urlopen(f"{base}{path}", timeout=3) as response:  # noqa: S310
        return response.status, json.load(response)


def post_json(base: str, path: str, payload: dict):
    request = Request(  # noqa: S310
        f"{base}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=3) as response:  # noqa: S310
        return response.status, json.load(response)


def error_json(base: str, path: str, payload: dict):
    request = Request(  # noqa: S310
        f"{base}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with pytest.raises(HTTPError) as captured:
        urlopen(request, timeout=3)  # noqa: S310
    return captured.value.code, json.load(captured.value)


def test_web_preview_simulation_and_capabilities(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("CALLE_LIVE_CALLS_ENABLED", raising=False)
    monkeypatch.delenv("CALLE_API_KEY", raising=False)
    config = WebConfig(database=tmp_path / "web.sqlite3")
    with running_server(config) as base:
        status, capabilities = get_json(base, "/api/capabilities")
        assert status == 200
        assert capabilities["live_ui_enabled"] is False
        assert capabilities["live_environment_ready"] is False

        status, result = post_json(base, "/api/preview", {"request": RAW})
        assert status == 200
        assert result["mode"] == "preview"

        status, result = post_json(
            base,
            "/api/simulate",
            {"request": RAW, "scenario": "acknowledged"},
        )
        assert status == 200
        assert result["decision"]["route"] == "vendor_acknowledged"
        assert result["decision"]["incident_closed"] == "false"


def test_web_live_requires_server_and_human_gates(tmp_path: Path):
    disabled = WebConfig(database=tmp_path / "disabled.sqlite3")
    with running_server(disabled) as base:
        status, body = error_json(
            base,
            "/api/execute",
            {
                "request": RAW,
                "confirm_authorized_recipient": True,
                "confirm_phrase": CONFIRM_PHRASE,
            },
        )
        assert status == 400
        assert "disabled" in body["error"]

    enabled = WebConfig(
        allow=(RAW["support_phone"],),
        enable_live_ui=True,
        database=tmp_path / "enabled.sqlite3",
    )
    with running_server(enabled) as base:
        status, body = error_json(
            base,
            "/api/execute",
            {"request": RAW, "confirm_authorized_recipient": False, "confirm_phrase": ""},
        )
        assert status == 400
        assert "authorization" in body["error"]

        status, body = error_json(
            base,
            "/api/execute",
            {
                "request": RAW,
                "confirm_authorized_recipient": True,
                "confirm_phrase": "yes",
            },
        )
        assert status == 400
        assert CONFIRM_PHRASE in body["error"]


def test_web_live_success_and_duplicate_reconciliation(tmp_path: Path, monkeypatch):
    class FakeClient:
        def __init__(self, *, api_key, base_url):
            assert api_key == "calle_test_key"
            assert base_url == "http://127.0.0.1:8123"
            self.calls = FakeCalls(completed_response())

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

    monkeypatch.setattr(calle, "CalleClient", FakeClient)
    monkeypatch.setenv("CALLE_LIVE_CALLS_ENABLED", "true")
    monkeypatch.setenv("CALLE_API_KEY", "calle_test_key")
    config = WebConfig(
        allow=(RAW["support_phone"],),
        enable_live_ui=True,
        timeout_seconds=5,
        base_url="http://127.0.0.1:8123",
        database=tmp_path / "ledger.sqlite3",
    )
    payload = {
        "request": RAW,
        "confirm_authorized_recipient": True,
        "confirm_phrase": CONFIRM_PHRASE,
    }
    with running_server(config) as base:
        status, result = post_json(base, "/api/execute", payload)
        assert status == 200
        assert result["decision"]["route"] == "vendor_acknowledged"
        assert result["decision"]["incident_closed"] == "false"

        status, body = error_json(base, "/api/execute", payload)
        assert status == 409
        assert "already reserved" in body["error"]


def test_live_ui_must_bind_loopback_and_have_allowlist(tmp_path: Path):
    base = {
        "port": 0,
        "timeout_seconds": 5,
        "base_url": "http://127.0.0.1:8123",
        "database": tmp_path / "ledger.sqlite3",
        "enable_live_ui": True,
    }
    with pytest.raises(ValueError, match="loopback"):
        build_server(argparse.Namespace(host="0.0.0.0", allow=[RAW["support_phone"]], **base))
    with pytest.raises(ValueError, match="at least one exact"):
        build_server(argparse.Namespace(host="127.0.0.1", allow=[], **base))
