# E00-F05 — Dev Resource Floor: Functional Test Plan

## Scope
Verifies `make doctor` and compose-profile gating produce predictable resource
behaviour across 8 GB and 16 GB hosts.

## Source User Stories
| Story ID | Title | Priority |
|----------|-------|---------|
| E00-F05-S01 | `make doctor` reports dev resource health | High |
| E00-F05-S02 | `--profile models` opt-in keeps light workflows light | High |

## Functional Objects Under Test
| Object | Type | Related Story | Expected Behaviour |
|--------|------|--------------|-------------------|
| `make doctor` | DX tool | S01 | reports PASS/FAIL with reasons |
| compose profile resolver | platform | S02 | gates `models` service |
| fixture-fallback `api` | platform | S02 | serves canned responses without `models` |

---

## Test Scenarios

### FT-023: Doctor PASSes on 16 GB host
**Input:** 16 GB host, Docker 24, 20 GB free disk
**Expected:** `make doctor` exits 0; outputs PASS lines
**Priority:** High

### FT-024: Doctor FAILs on 8 GB host with actionable hint
**Input:** 8 GB host
**Expected:** FAIL on memory; recommends `--profile lite`
**Priority:** High

### FT-025: Default profile excludes `models`
**Input:** `docker compose up`
**Expected:** `models` service not in `docker compose ps`
**Priority:** Critical

### FT-026: `--profile models` includes `models`
**Input:** `docker compose --profile models up`
**Expected:** `models` healthy; NLP endpoints functional
**Priority:** Critical

### FT-027: API fixture fallback returns canned responses
**Input:** default profile; call `/disambiguate`
**Expected:** fixture body returned; logs note `models profile inactive`
**Priority:** High

## Negative Tests
- Doctor on Apple Silicon with x86 emulation: warns; not a hard fail.
- Compose profile typo: explicit error from compose, not a silent miss.

## Boundary Tests
- 16 GB exact: PASS but warns about narrow margin.
- 12 GB: FAIL on memory; recommends lite.

## Permission and Role Tests
- Doctor reads /proc; on macOS uses `vm_stat`; no root required.

## Integration Tests
- Doctor results compared against compose profile actually selected; mismatch
  produces warning line.

## Audit and Traceability Tests
- Doctor logs decision to `~/.tirvi/doctor-history.log` (opt-in).

## Regression Risks
- Compose profile renamed; doctor advice goes stale; CI lint catches.

## Open Questions
- Should doctor be wired into `docker compose up` as a pre-hook?
