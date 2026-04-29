# <Feature Name> Functional Test Plan

## Scope
Describe what business behaviour is under test and what is explicitly out of scope.

## Source User Stories
| Story ID | Title | Priority |
|----------|-------|---------|

## Functional Objects Under Test
| Object | Type | Related Story | Expected Behaviour |
|--------|------|--------------|-------------------|

---

## Test Scenarios

### FT-<N>: <Scenario Name>
**Related stories:**
**Related business objects:**
**Preconditions:**
**Input:**
**Expected output:**
**Validation method:**
**Failure mode:**
**Priority:** Critical | High | Medium | Low

---

## Negative Tests
Scenarios where invalid input, missing data, or unauthorized access must be
handled gracefully. Include expected error messages or fallback behaviour.

## Boundary Tests
Scenarios at the edges of valid input ranges, quota limits, date boundaries,
character limits, or numeric overflow.

## Permission and Role Tests
Scenarios where different personas (with different roles or permissions) attempt
the same action and receive different outcomes.

## Integration Tests
Scenarios that cross a system or bounded context boundary. Identify the
integration point, the contract being tested, and the failure mode if the
contract breaks.

## Audit and Traceability Tests
Scenarios that verify audit records are created, traceability links are
maintained, and compliance-relevant events are logged.

## Regression Risks
List stories or scenarios from neighbouring features that could break if this
feature is modified.

## Open Questions
-
