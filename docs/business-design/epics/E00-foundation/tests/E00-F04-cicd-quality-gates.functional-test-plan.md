# E00-F04 — CI/CD Quality Gates: Functional Test Plan

## Scope
Verifies TDD, complexity, and security gates run on every PR and block on
violations. Out of scope: deploy job (covered by E00-F02).

## Source User Stories
| Story ID | Title | Priority |
|----------|-------|---------|
| E00-F04-S01 | TDD gate enforces test-before-code | Critical |
| E00-F04-S02 | Complexity gate (CC ≤ 5) | High |
| E00-F04-S03 | Security scan + SBOM | Critical |

## Functional Objects Under Test
| Object | Type | Related Story | Expected Behaviour |
|--------|------|--------------|-------------------|
| TDD gate script | quality | S01 | scans diff; pass/fail per rule |
| Complexity gate | quality | S02 | reports per-function CC; warn ≥6 / fail ≥8 |
| Vuln scanner | quality | S03 | new CVEs blocked; SBOM artifact |

---

## Test Scenarios

### FT-017: PR with prod change & no tests fails TDD gate
**Input:** PR adds `domain/foo.py`; no `tests/**` change
**Expected:** TDD gate fails; PR comment names missing test
**Priority:** Critical

### FT-018: PR labeled `chore:scaffolding` skips TDD gate
**Input:** label applied; description has justification
**Expected:** gate skipped; reviewer reads justification
**Priority:** High

### FT-019: Complexity gate reports per-function CC
**Input:** PR introduces a function with CC=7
**Expected:** gate fails with `function name + CC value`
**Priority:** High

### FT-020: SBOM generated on every PR
**Input:** PR adds a dependency
**Expected:** SBOM CycloneDX uploaded as CI artifact
**Priority:** Critical

### FT-021: New Critical CVE blocks merge
**Input:** PR introduces a dep with Critical CVE
**Expected:** vuln scanner emits PR comment; merge blocked
**Priority:** Critical

### FT-022: Pipeline ≤ 8 minutes total
**Input:** typical PR
**Expected:** total CI time ≤ 8 min (parallel jobs)
**Priority:** High

## Negative Tests
- Gate config invalid → CI fails fast with config error, not a silent skip.
- Vuln database unreachable → scan emits warning + retries; merge held.

## Boundary Tests
- Function with CC=5 passes warning threshold.
- Function with CC=6 emits warning, no block.
- Function with CC=8 hard-fails.

## Permission and Role Tests
- Only repo owners may add `chore:scaffolding` label (configurable).
- Only security reviewer may approve CVE waiver.

## Integration Tests
- TDD gate inspects E00-F03 fake registry to identify production vs test paths.

## Audit and Traceability Tests
- SBOM stored as CI artifact ≥ 90 days.
- Gate decisions logged to PR comment with timestamp + rule ID.

## Regression Risks
- Gate logic regression silently skips a category — periodic synthetic PR
  catches missed coverage.

## Open Questions
- Do we add SAST (semgrep) on every PR or weekly?
