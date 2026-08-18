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
- the final route becomes `vendor_acknowledged` while `incident_closed` remains `false`.

It does **not** prove that a real external vendor has adopted IncidentBridge or that a synthetic call reduced production MTTR.

## Recipient requirements

Use only a phone number that:

1. you own, or the recipient has explicitly authorized you to call with CALL-E;
2. is safe to use for a synthetic test; and
3. will be answered by a consenting adult who understands that an AI phone agent will call.

Do not call an emergency service, medical provider, government office, random business, or uninvolved third party for this validation.

## Fixed synthetic incident

The one-shot runner creates the incident internally. It does **not** accept arbitrary production incident text, which reduces the chance of accidentally sending credentials or customer data into the public validation.

The fixed scenario is:

- provider: `ExampleCloud`
- affected service: `managed ingestion endpoint`
- incident: synthetic elevated `503` responses
- incident id: `INC-2026-0810`
- expected ticket for the recipient to return: `SUP-4821`
- vendor status: `investigating`
- ETA: `30 minutes`
- workaround: `retry through the secondary endpoint`
- callback window: `within 45 minutes`

## Recipient script

The consenting recipient should answer naturally, but the following facts should be available if the agent asks:

> Yes, this is the ExampleCloud support desk for this synthetic test. I understand that I am speaking with an AI agent and I consent to continue. I acknowledge incident INC-2026-0810. The support ticket is SUP-4821. The current status is investigating. The estimated time to the next update is 30 minutes. The temporary workaround is to retry through the secondary endpoint. We can call back within 45 minutes. Human escalation is not required right now.

The recipient does not need to read this as one monologue. Natural question-and-answer behavior is preferable.

## One guarded command

Install current `main` first:

```bash
uv sync --extra dev
```

Export the same two live CALL-E gates used by IncidentBridge:

```bash
export CALLE_API_KEY="<CALL_E_API_KEY>"
export CALLE_LIVE_CALLS_ENABLED="true"
```

Then place **exactly one** call to the consenting number:

```bash
uv run incidentbridge-consented-live-demo \
  --phone +<AUTHORIZED_E164_NUMBER> \
  --confirm-consent "I HAVE EXPLICIT CONSENT"
```

The command deliberately fixes the synthetic incident and internally sets the exact phone allowlist to the same number supplied on the command line. It then uses the normal `execute_once` path, including the durable reservation and all result-binding/corroboration checks.

### If the call succeeds

The runner writes:

```text
artifacts/consented-live-success.json
```

only if the final route is actually `vendor_acknowledged` and `incident_closed` remains `false`.

The public artifact contains the real CALL-E call ID, status, completion confidence, redacted structured result, final decision, and a statement that ticket corroboration succeeded. It deliberately contains **no real phone number, participant identity, transcript, or recording**.

The repository `.gitignore` allows this one public artifact to be committed after review.

### If the call does not succeed

No public success artifact is created. The result is written only to:

```text
data/consented-live-last-result.json
```

which is ignored by Git.

Do **not** immediately redial. The same durable reservation prevents a blind duplicate call. Inspect the result and ledger first.

## Public claim boundary

The generated artifact labels itself as:

**`consented_live_success_synthetic_scenario`**

and explicitly states:

> Real CALL-E transport and IncidentBridge success routing; synthetic incident with a consenting authorized test recipient, not a real vendor deployment.

That is the strongest accurate claim. Do not rename it to imply a customer deployment or a real vendor incident.

## Review before commit

Even though the runner is designed to emit only public-safe fields, inspect the file once before `git add`:

```bash
cat artifacts/consented-live-success.json
```

Check that it contains:

- a real CALL-E `call_id`;
- `task_completed: true`;
- ticket `SUP-4821`;
- `decision.route: vendor_acknowledged`;
- `decision.incident_closed: "false"`;
- `ticket_supported_by_recipient_evidence: true`; and
- no real phone number, name, transcript, recording, email, API key, or other participant identifier.

Then the artifact can be committed as public evidence.

## What to capture for the final demo video

If the run succeeds, the highest-value sequence is:

1. show the local operator preview / authorization boundary;
2. show that exactly one real CALL-E call was initiated;
3. show the generated public artifact with the real call ID;
4. show `ticket_id = SUP-4821` and the corroboration result;
5. show `route = vendor_acknowledged`; and
6. end on `incident_closed = false`.

That sequence demonstrates the project's central thesis in one real side-effect path: **the call can succeed without gaining recovery authority**.
