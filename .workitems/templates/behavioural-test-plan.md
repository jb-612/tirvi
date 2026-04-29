# <Feature Name> Behavioural Test Plan

## Behavioural Scope
Describe which human behaviour patterns, persona types, and interaction modes
are covered by this plan.

## Human Behaviour Patterns Covered
| Behaviour | Persona | Risk | Test Method |
|-----------|---------|------|------------|

---

## Behavioural Scenarios

### BT-<N>: <Scenario Name>
**Persona:**
**Intent:**
**Human behaviour simulated:**
**System expectation:**
**Agent expectation (if relevant):**
**Collaboration expectation:**
**Escalation path:**
**Acceptance criteria:**

---

## Edge Behaviour
Scenarios involving unusual but valid human actions: fast repeated clicks,
long pauses, session abandonment, back-navigation during a multi-step flow,
duplicate submissions.

## Misuse Behaviour
Scenarios where users attempt to work around intended flows: skipping required
steps, entering unexpected characters, submitting before all fields are ready,
copy-pasting from external systems.

## Recovery Behaviour
Scenarios where something fails mid-flow and the user must recover: network
loss, validation error, timeout, expired session. Verify the system preserves
partial progress where expected.

## Collaboration Breakdown Tests
Scenarios where a handoff fails: an approver is unavailable, a downstream system
is down, an expected notification was not received. Verify escalation paths and
fallback messages.

## Open Questions
-
