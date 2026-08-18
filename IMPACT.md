# IncidentBridge — Real-World Impact Model

IncidentBridge is designed to remove one bounded source of incident-response toil: the external vendor-support phone call.

This document deliberately separates **measured product facts** from **illustrative operating assumptions**. It does not claim that IncidentBridge shortens outage duration by a specific percentage. The impact claim is narrower and auditable: when a vendor call can be delegated safely, the on-call operator can avoid spending active attention on queueing, repeating incident context, and manually transcribing the vendor response.

## The unit of impact

The primary unit is **operator minutes returned to incident diagnosis and coordination**.

For one vendor-support interaction:

```text
manual_operator_minutes
  = queue_or_hold_minutes
  + briefing_and_routing_minutes
  + conversation_minutes
  + transcription_minutes

incidentbridge_operator_minutes
  = approval_and_review_minutes
  + exception_handling_minutes

operator_minutes_reclaimed
  = max(0, manual_operator_minutes - incidentbridge_operator_minutes)
```

For a team over one year:

```text
annual_operator_hours_reclaimed
  = vendor_calls_per_week
  × operator_minutes_reclaimed
  × 52
  ÷ 60
```

The model intentionally excludes speculative secondary effects such as reduced MTTR, avoided revenue loss, or fewer SLA penalties unless a real deployment measures them.

## Interactive calculator

Use the public calculator with your own assumptions:

https://yangyangnovelist-hub.github.io/incidentbridge-calle/impact-calculator.html

The calculator runs entirely in the browser and sends no data anywhere.

## Example only — not field-measured

If a team handles 2 external vendor-support calls per week, each call consumes 25 operator minutes, and IncidentBridge reduces the human approval/review burden to 3 minutes, the model yields:

```text
22 reclaimed minutes/call
× 2 calls/week
× 52 weeks
÷ 60
= 38.1 operator hours/year
```

That example is an illustration of the formula, not a claim about average vendor queues or a measured IncidentBridge customer deployment.

## Why operator attention matters during an incident

IncidentBridge does not assume that every minute reclaimed becomes one minute of lower MTTR. The safer claim is that vendor phone work competes for the same operator attention used for diagnosis, mitigation, stakeholder coordination, and recovery verification.

The product therefore delegates only the conversation that can be bounded and audited:

- contact one explicitly authorized vendor-support destination;
- disclose that the caller is an AI agent;
- collect ticket, status, ETA, workaround, callback, and escalation facts;
- bind those facts to the exact approved call; and
- return them as evidence while leaving recovery authority with local health checks and the incident commander.

## What a real pilot should measure

A production pilot should collect these fields without recording sensitive call content:

| Metric | Definition |
|---|---|
| Vendor calls per incident | Number of external support calls required during an incident |
| Manual operator minutes | Active operator time spent queueing, briefing, speaking, and transcribing |
| IncidentBridge review minutes | Human time spent approving the call and reviewing returned evidence |
| Exception rate | Share of calls that route to `needs_human` |
| Duplicate-call rate | Calls repeated because of ambiguous provider outcomes |
| Evidence completeness | Share of completed calls returning the required ticket/status/ETA fields |
| Unauthorized-call rate | Must remain zero |
| False-success rate | Must remain zero |

The first business KPI is **operator minutes reclaimed per delegated call**. The first safety KPIs are **unauthorized-call rate** and **false-success rate**.

## Current evidence boundary

Publicly reproducible evidence currently shows:

- a real CALL-E provider call ID on an authorized fail-closed path;
- deterministic inspection of the complete acknowledged route;
- runtime use of the published CALL-E Python SDK;
- 21 automated tests at 92.37% coverage with a 90% CI gate; and
- independent CALL-E maintainer review followed by merge into the official community repository.

Successful live-call behavior has also been tested privately, but private participant/conversation materials are not used as public impact statistics.

## What IncidentBridge does not claim

IncidentBridge does **not** claim that:

- a vendor phone call proves service recovery;
- a terminal provider status is business success;
- every incident needs a vendor phone call;
- every delegated call saves the same amount of time; or
- the illustrative calculator assumptions are measured customer results.

A phone call may create evidence. A phone call may not create recovery truth.
