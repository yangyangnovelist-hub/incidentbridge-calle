"""Run one consented synthetic CALL-E success-path validation and emit public-safe proof."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from incidentbridge.cli import execute_once
from incidentbridge.models import parse_request
from incidentbridge.runtime import DEFAULT_BASE_URL

CONSENT_PHRASE = "I HAVE EXPLICIT CONSENT"
DEFAULT_DATABASE = Path("data/consented-live-demo.sqlite3")
DEFAULT_FAILURE_OUTPUT = Path("data/consented-live-last-result.json")
DEFAULT_PUBLIC_OUTPUT = Path("artifacts/consented-live-success.json")


def synthetic_request(phone: str) -> dict[str, Any]:
    """Return the fixed non-production scenario used for public live validation."""
    return {
        "workflow_id": "wf-consented-live-demo-001",
        "incident_id": "INC-2026-0810",
        "support_phone": phone,
        "authorized_support_contact": True,
        "caller_business_name": "Acme Data Operations",
        "provider_name": "ExampleCloud",
        "affected_service": "managed ingestion endpoint",
        "incident_summary": (
            "Synthetic test: elevated 503 responses on the managed ingestion endpoint."
        ),
        "severity": "outage",
        "observed_at_utc": "2026-08-10T01:20:00Z",
        "region": "US",
        "locale": "en-US",
    }


def public_proof(result: dict[str, Any]) -> dict[str, Any]:
    """Reduce a successful runtime result to the minimum public evidence artifact."""
    decision = result.get("decision")
    structured = result.get("structured_result")
    if not isinstance(decision, dict) or decision.get("route") != "vendor_acknowledged":
        raise ValueError("public success proof requires route=vendor_acknowledged")
    if decision.get("incident_closed") != "false":
        raise ValueError("public success proof requires incident_closed=false")
    if not isinstance(structured, dict):
        raise ValueError("public success proof requires a structured result")

    return {
        "evidence_type": "consented_live_success_synthetic_scenario",
        "provider": "CALL-E",
        "scenario": "synthetic ExampleCloud vendor-support incident",
        "recipient": "redacted consenting authorized test recipient",
        "call_id": result.get("call_id"),
        "status": result.get("status"),
        "task_completed": result.get("task_completed"),
        "completion_confidence": result.get("completion_confidence"),
        "structured_result": structured,
        "decision": decision,
        "corroboration": {
            "ticket_supported_by_recipient_evidence": True,
            "basis": (
                "vendor_acknowledged is reachable only after the runtime policy binds the "
                "result to the approved call/workflow/incident/destination and corroborates "
                "the returned ticket against recipient-side evidence"
            ),
        },
        "privacy": {
            "real_phone_number_published": False,
            "participant_identity_published": False,
            "transcript_published": False,
            "recording_published": False,
        },
        "claim_boundary": (
            "Real CALL-E transport and IncidentBridge success routing; synthetic incident "
            "with a consenting authorized test recipient, not a real vendor deployment."
        ),
    }


def write_exclusive(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def write_replace(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phone", required=True, help="Owned or explicitly authorized E.164 number")
    parser.add_argument(
        "--confirm-consent",
        required=True,
        help=f"Must equal: {CONSENT_PHRASE}",
    )
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument(
        "--base-url",
        default=os.environ.get("CALLE_BASE_URL", DEFAULT_BASE_URL),
    )
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--public-output", type=Path, default=DEFAULT_PUBLIC_OUTPUT)
    parser.add_argument("--failure-output", type=Path, default=DEFAULT_FAILURE_OUTPUT)
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.confirm_consent != CONSENT_PHRASE:
        raise ValueError(f"--confirm-consent must equal: {CONSENT_PHRASE}")
    if args.timeout_seconds <= 0:
        raise ValueError("--timeout-seconds must be positive")
    if args.public_output.exists():
        raise ValueError(
            f"refusing to overwrite existing public proof: {args.public_output}"
        )

    request = parse_request(synthetic_request(args.phone))
    execute_args = argparse.Namespace(
        confirm_authorized_recipient=True,
        allow=[args.phone],
        timeout_seconds=args.timeout_seconds,
        base_url=args.base_url,
        database=args.database,
    )
    result = execute_once(request, execute_args)

    if result.get("decision", {}).get("route") != "vendor_acknowledged":
        write_replace(args.failure_output, result)
        raise RuntimeError(
            "CALL-E call completed but did not reach vendor_acknowledged; "
            f"inspect ignored local result at {args.failure_output}. Do not blindly retry."
        )

    proof = public_proof(result)
    write_exclusive(args.public_output, proof)
    return proof


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        proof = run(args)
        sys.stdout.write(
            "Consented live success proof created: "
            f"{args.public_output}\ncall_id={proof.get('call_id')}\n"
        )
        sys.stdout.write(
            "Review the public artifact before git add. It contains no phone number, "
            "participant identity, transcript, or recording.\n"
        )
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
