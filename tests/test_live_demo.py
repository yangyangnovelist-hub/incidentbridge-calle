import argparse
import json
from pathlib import Path

import calle
import pytest

from incidentbridge import live_demo
from incidentbridge.models import parse_request
from incidentbridge.policy import simulated_result

PHONE = "+15555550123"


def provider_result(*, acknowledged: bool = True):
    request = parse_request(live_demo.synthetic_request(PHONE))
    structured = simulated_result(request, "acknowledged")["structured_result"]
    return {
        "id": "call_consent_001",
        "status": "completed",
        "task_completed": acknowledged,
        "completion_confidence": {"score": 0.96, "label": "high"},
        "structured_result": structured,
        "evidence": ["Synthetic consenting recipient supplied a vendor ticket."],
        "metadata": {
            "workflow_id": request.workflow_id,
            "workflow_type": "vendor_incident_support",
            "incident_id": request.incident_id,
        },
        "recipients": [
            {
                "phone": request.support_phone,
                "attempts": [
                    {
                        "transcript_turns": [
                            {
                                "speaker": "recipient",
                                "text": f"Ticket {structured['ticket_id']}.",
                            }
                        ]
                    }
                ],
            }
        ],
    }


class FakeClient:
    response = provider_result()

    def __init__(self, *, api_key, base_url):
        assert api_key == "calle_test_key"
        assert base_url == "http://127.0.0.1:8123"
        self.calls = self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def create(self, **kwargs):
        assert kwargs["idempotency_key"].startswith("incidentbridge-")
        return {"id": "call_consent_001"}

    def wait_for_result(self, call_id, *, timeout_seconds, interval_seconds):
        assert call_id == "call_consent_001"
        assert timeout_seconds == 5
        assert interval_seconds == 2
        return self.response


def args(tmp_path: Path, *, confirm: str = live_demo.CONSENT_PHRASE):
    return argparse.Namespace(
        phone=PHONE,
        confirm_consent=confirm,
        timeout_seconds=5,
        base_url="http://127.0.0.1:8123",
        database=tmp_path / "ledger.sqlite3",
        public_output=tmp_path / "public.json",
        failure_output=tmp_path / "private-failure.json",
    )


def test_consent_live_demo_emits_public_safe_success(tmp_path, monkeypatch):
    FakeClient.response = provider_result()
    monkeypatch.setattr(calle, "CalleClient", FakeClient)
    monkeypatch.setenv("CALLE_LIVE_CALLS_ENABLED", "true")
    monkeypatch.setenv("CALLE_API_KEY", "calle_test_key")

    proof = live_demo.run(args(tmp_path))
    assert proof["evidence_type"] == "consented_live_success_synthetic_scenario"
    assert proof["call_id"] == "call_consent_001"
    assert proof["decision"]["route"] == "vendor_acknowledged"
    assert proof["decision"]["incident_closed"] == "false"
    assert proof["corroboration"]["ticket_supported_by_recipient_evidence"] is True

    rendered = (tmp_path / "public.json").read_text(encoding="utf-8")
    assert PHONE not in rendered
    assert "transcript_turns" not in rendered
    assert "recipient_identity" not in rendered
    assert json.loads(rendered)["privacy"]["transcript_published"] is False


def test_consent_live_demo_failure_stays_local_and_no_blind_retry(tmp_path, monkeypatch):
    FakeClient.response = provider_result(acknowledged=False)
    monkeypatch.setattr(calle, "CalleClient", FakeClient)
    monkeypatch.setenv("CALLE_LIVE_CALLS_ENABLED", "true")
    monkeypatch.setenv("CALLE_API_KEY", "calle_test_key")

    with pytest.raises(RuntimeError, match="Do not blindly retry"):
        live_demo.run(args(tmp_path))
    assert not (tmp_path / "public.json").exists()
    failure = json.loads((tmp_path / "private-failure.json").read_text(encoding="utf-8"))
    assert failure["decision"]["route"] == "needs_human"


def test_consent_live_demo_requires_exact_consent_and_fresh_public_output(tmp_path):
    with pytest.raises(ValueError, match="I HAVE EXPLICIT CONSENT"):
        live_demo.run(args(tmp_path, confirm="yes"))

    public = tmp_path / "public.json"
    public.write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="refusing to overwrite"):
        live_demo.run(args(tmp_path))


def test_public_proof_rejects_non_success():
    with pytest.raises(ValueError, match="vendor_acknowledged"):
        live_demo.public_proof(
            {
                "decision": {"route": "needs_human", "incident_closed": "false"},
                "structured_result": {},
            }
        )
