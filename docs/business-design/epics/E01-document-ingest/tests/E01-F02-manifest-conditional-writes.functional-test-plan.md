# E01-F02 — Manifest With Conditional Writes: Functional Test Plan

## Scope
Verifies manifest schema, atomic update under generation precondition, and
projection consistency.

## Source User Stories
| Story ID | Title | Priority |
|----------|-------|---------|
| E01-F02-S01 | Atomic per-document state | Critical |
| E01-F02-S02 | Browser polls manifest for live status | Critical |

## Functional Objects Under Test
| Object | Type | Related Story | Expected Behaviour |
|--------|------|--------------|-------------------|
| `Manifest` | aggregate | S01 | atomic single-object update |
| Manifest projection | API view | S02 | denormalized status JSON |

---

## Test Scenarios

### FT-034: Concurrent stage writers
**Input:** 5 simulated stage completions update the same manifest in 100 ms window
**Expected:** all 5 reflected in final manifest; no lost writes
**Priority:** Critical

### FT-035: Stale generation triggers retry
**Input:** writer A reads gen 5, writer B reads gen 5; both write
**Expected:** A succeeds (gen 6), B gets 412, retries (re-read gen 6, write gen 7)
**Priority:** Critical

### FT-036: Projection round-trip
**Input:** manifest gen 7 with 3 stages done
**Expected:** API GET returns projection within 50 ms with the same stage states
**Priority:** High

### FT-037: Manifest absent from `/documents/{id}` for unrelated session
**Input:** request from another session
**Expected:** 404
**Priority:** Critical

### FT-038: Schema migration is forward-compatible
**Input:** old manifest (v1) read by new code
**Expected:** new code accepts v1 + applies default for v2 fields
**Priority:** High

## Negative Tests
- GCS unavailable: writer enqueues retry with backoff.
- Manifest accidentally deleted: API returns 410 with "document gone" code.

## Boundary Tests
- Document with 1 page: manifest has 1 page entry.
- Document with 50 pages (max practical): manifest still single-object atomic.

## Permission and Role Tests
- Manifests writeable only by worker SA; readable by API SA.

## Integration Tests
- Worker → manifest → API → browser polling round-trip.
- Lifecycle (E01-F05) sees manifest age and removes it on TTL boundary.

## Audit and Traceability Tests
- Manifest carries `created_at`, `updated_at`, `generation_history` (last N).

## Regression Risks
- Stage rename breaking historical manifests; needs rename-plan ADR.

## Open Questions
- Per-stage shard manifests for very long documents — defer until > 50 pages
  becomes common.
