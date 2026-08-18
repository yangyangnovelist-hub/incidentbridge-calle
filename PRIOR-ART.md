# IncidentBridge — Prior Art and Product Boundary

IncidentBridge intentionally sits next to, rather than duplicates, other CALL-E operational phone patterns.

Two adjacent patterns already exist in the official `CALLE-AI/awesome-phone-call-agents` repository. They help make the product boundary concrete.

## 1. Internal incident paging: Zapier incident-escalation recipe

Official reference:

https://github.com/CALLE-AI/awesome-phone-call-agents/blob/main/plugins/zapier-calle/examples/incident-escalation.md

That workflow solves an **internal ownership problem**:

> call the primary on-call engineer, ask whether they are taking the incident, and escalate to the backup when acknowledgment is missing or ambiguous.

Its key output is whether an internal responder accepted responsibility.

IncidentBridge begins after that layer. It solves an **external dependency evidence problem**:

> call the authorized external vendor support destination, obtain the vendor ticket/status/ETA/workaround/callback facts, prove those facts came from the exact approved call, and return them to the incident workflow without granting the phone result recovery authority.

| Internal incident paging | IncidentBridge |
|---|---|
| recipient is primary/backup responder | recipient is external vendor support |
| asks who owns the incident internally | asks what the vendor knows externally |
| output is acknowledgment / responder ETA | output is vendor ticket / status / ETA / workaround / callback |
| escalation may intentionally create another internal page | ambiguous vendor-call outcome is reconciled rather than blindly redialed |
| changes internal ownership state | never changes recovery state |

The two workflows compose naturally: an organization can page its responder first, then delegate the external vendor-support coordination without taking that responder away from diagnosis.

## 2. Phone-system reliability: LineCanary

Official reference:

https://github.com/CALLE-AI/awesome-phone-call-agents/tree/main/apps/typescript/linecanary

LineCanary solves a different operational problem: **synthetic monitoring and regression testing of phone lines and deployed voice agents**. It calls lines the user owns, exercises the caller journey, compares structured results to assertions/baselines, and can gate CI when the phone experience regresses.

IncidentBridge is not phone-line monitoring. The phone network is a transport for a one-off incident workflow; the system under investigation is the external SaaS/cloud/data dependency.

| LineCanary | IncidentBridge |
|---|---|
| system under test is a phone line / voice agent | system under incident is an external technical dependency |
| recurrent synthetic check | bounded incident-triggered vendor-support call |
| assertions detect phone regression | evidence captures vendor acknowledgment and support facts |
| calls lines owned/controlled for monitoring | calls one explicitly authorized vendor-support destination |
| CI/status-page product | incident evidence/coordination product |

## 3. Why the authority boundary is the differentiator

The commodity capability is “an AI agent can place a phone call.” IncidentBridge's product contribution is the trust boundary required before a real phone result can safely enter an incident workflow.

A successful result must be:

- bound to the exact workflow and incident;
- bound to the real CALL-E call ID;
- bound to the exact authorized destination;
- complete and high-confidence;
- from the correct support desk after AI disclosure/consent; and
- corroborated by recipient-side evidence for the returned ticket.

Even after all of those checks pass, the result can only create `vendor_acknowledged`. It cannot set `incident_closed=true`.

That makes the product complementary to internal paging and phone monitoring while preserving a distinct, reusable operational primitive:

**external vendor evidence without external recovery authority.**
