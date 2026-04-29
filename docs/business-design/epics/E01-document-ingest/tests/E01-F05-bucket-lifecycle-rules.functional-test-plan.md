# E01-F05 — Bucket Lifecycle Rules: Functional Test Plan

## Scope
Verifies prefix-scoped lifecycle rules, opt-in 7-day mode, audio cache
exemption, and observable lifecycle actions.

## Source User Stories
| Story ID | Title | Priority |
|----------|-------|---------|
| E01-F05-S01 | Default 24h TTL on confidential prefixes | Critical |
| E01-F05-S02 | Opt-in 7-day retention | High |

## Functional Objects Under Test
| Object | Type | Related Story | Expected Behaviour |
|--------|------|--------------|-------------------|
| Lifecycle rule set | infra | S01 | prefix → AGE > 24h → DELETE |
| Audio cache rule | infra | S01 | NO rule on `audio/` |
| `Document.retention_mode` | value object | S02 | 24h \| 7d |

---

## Test Scenarios

### FT-050: 24h rule deletes within tolerance
**Input:** PDF uploaded at T
**Expected:** at T+25h, object gone (lifecycle runs every ~24h; tolerance 1h)
**Priority:** Critical

### FT-051: Audio cache exempt
**Input:** audio object aged 30 days
**Expected:** still present
**Priority:** Critical

### FT-052: Opt-in 7-day retention applied
**Input:** doc with `retention_mode=7d`
**Expected:** at T+25h still present; at T+7d+1h gone
**Priority:** High

### FT-053: Mixed-mode within bucket
**Input:** doc A (24h), doc B (7d) in same bucket
**Expected:** A deleted at 24h; B preserved
**Priority:** High

### FT-054: Lifecycle action observable in audit log
**Input:** wait for lifecycle sweep
**Expected:** Cloud Logging shows `OBJECT_DELETE` events with prefix counts
**Priority:** Medium

### FT-055: Rule change requires ADR
**Input:** TF plan modifies TTL
**Expected:** plan diff flags ADR requirement; CI gate halts
**Priority:** High

## Negative Tests
- Lifecycle rule misconfigured to delete `audio/`: TF lint catches before apply.
- Object metadata `retention=7d` set but rule lacks the predicate; rule still
  deletes — pre-deploy validation catches.

## Boundary Tests
- 24h exact (sweep runs 23h59m after upload): may extend to next sweep; UI
  documents the 24h ± 1h tolerance.
- 7d exact: same tolerance window.

## Permission and Role Tests
- Lifecycle SA can delete; runtime SA cannot.

## Integration Tests
- E11-F01 (privacy) reads same lifecycle config; both must agree.
- E01-F04 (cascade) idempotent against lifecycle-already-removed objects.

## Audit and Traceability Tests
- Lifecycle events archived; quarterly audit dashboard reads from logs.

## Regression Risks
- New prefix (`corrections/`, `mos-panel/`) added without lifecycle rule.

## Open Questions
- Should opt-in 7d for minors require parental re-consent?
