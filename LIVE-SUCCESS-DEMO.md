# IncidentBridge — Consented Live Success Validation

This protocol creates a **real CALL-E phone call on a synthetic incident scenario** without pretending that a consenting tester is a real vendor or publishing private participant data.

The goal is to make the complete `vendor_acknowledged` path publicly inspectable while preserving the product's consent, privacy, and authority boundaries.

## What this proves

A successful run can prove that:

- the published CALL-E SDK places the real phone call;
- the recipient hears the bounded support task and AI disclosure;
- CALL-E returns structured support facts;
- IncidentBridge binds the result to the exact approved call/workflow/incident/destination;
- the returned ticket is corroborated against recipient-side evidence; and
- the final route can become `vendor_acknowledged` while `incident_closed` remains `false`.

It does **not** prove that a real external vendor has adopted IncidentBridge or that a synthetic call reduced production MTTR.

## Recipient requirements

Use only a phone number that:

1. you own, or the recipient has explicitly authorized you to call with CALL-E;
2. is safe to use for a synthetic test; and
3. will be answered by a consenting adult who understands that an AI phone agent will call.

Do not call an emergency service, medical provider, government office, random business, or uninvolved third party for this validation.

## Synthetic incident

Copy `examples/incident.json` to a temporary file and change only the phone number to the authorized recipient's real E.164 number.

Keep the fictional provider and incident content. Do not put real credentials, customer data, personal data, or production incident secrets into the test.

Suggested scenario:

- provider: `ExampleCloud`
- affected service: `managed ingestion endpoint`
- incident: elevated synthetic `503` responses
- ticket to return: `SUP-4821`
- vendor status: `investigating`
- ETA: `30 minutes`
- workaround: `retry through the secondary endpoint`
- callback window: `within 45 minutes`

## Recipient script

The consenting recipient should answer naturally, but the following facts should be available if the agent asks:

> Yes, this is the ExampleCloud support desk for this synthetic test. I understand that I am speaking with an AI agent and I consent to continue. I acknowledge incident INC-2026-0810. The support ticket is SUP-4821. The current status is investigating. The estimated time to the next update is 30 minutes. The temporary workaround is to retry through the secondary endpoint. We can call back within 45 minutes. Human escalation is not required right now.

The recipient does not need to read this as one monologue. Natural question-and-answer behavior is preferable.

## Run the preview first

```bash
.venv/bin/incidentbridge --request /path/to/consented-live-incident.json
```

Confirm that:

- the destination is masked in preview output;
- the task contains only synthetic, non-secret information;
- the expected result schema is correct; and
- the decision boundary still says the phone result cannot close the incident.

## Place exactly one authorized call

```bash
export CALLE_API_KEY="<CALL_E_API_KEY>"
export CALLE_LIVE_CALLS_ENABLED="true"

.venv/bin/incidentbridge \
  --request /path/to/consented-live-incident.json \
  --execute \
  --confirm-authorized-recipient \
  --allow +<AUTHORIZED_E164_NUMBER> \
  --database data/consented-live-demo.sqlite3 \
  --output artifacts/consented-live-success-private.json
```

Do not blindly retry if the provider outcome is ambiguous. Inspect the durable reservation first.

## Public artifact boundary

Before publishing anything, remove or mask:

- the real phone number;
- participant name or identity;
- email addresses;
- recordings;
- unnecessary transcript text;
- CALL-E credentials or tokens; and
- any other personally identifying information.

A public artifact should contain only the minimum proof needed, for example:

```json
{
  "evidence_type": "consented_live_success_synthetic_scenario",
  "provider": "CALL-E",
  "scenario": "synthetic ExampleCloud support desk",
  "recipient": "redacted consenting test number",
  "call_id": "<real CALL-E call id>",
  "status": "COMPLETED",
  "task_completed": true,
  "ticket_id": "SUP-4821",
  "vendor_status": "investigating",
  "eta_minutes": 30,
  "decision": {
    "route": "vendor_acknowledged",
    "incident_closed": "false",
    "automatic_retry": false
  },
  "corroboration": {
    "ticket_supported_by_recipient_evidence": true
  }
}
```

Label it explicitly as a **consented live CALL-E success-path validation using a synthetic incident scenario**. Do not label it as a real vendor incident.

## What to capture for the new demo video

If the run succeeds, the highest-value video sequence is:

1. show the safe preview and exact authorization gates;
2. show the CALL-E call being initiated once;
3. briefly show the redacted terminal result with the real call ID;
4. show `ticket_id = SUP-4821` corroborated by recipient evidence;
5. show `route = vendor_acknowledged`; and
6. end on `incident_closed = false`.

That sequence demonstrates the project's central thesis in one real side-effect path: **the call can succeed without gaining recovery authority**.
