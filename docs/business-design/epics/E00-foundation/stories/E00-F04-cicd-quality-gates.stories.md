# E00-F04 — CI/CD With TDD, Complexity, and Security Gates

## Source Basis
- PRD: §7.3 Reliability, §7.4 Cost
- HLD: §7 Deployment topology
- Research: src-003 §10 Phase 0 F0.4 (TDD gate, complexity ≤ 5, security scan)
- CLAUDE.md: protected paths, TDD discipline, CC ≤ 5
- Assumptions: ASM07 (no auth in MVP CI gates)

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P04 SRE | maintains CI | gates block bad merges | flaky tests | green CI ⇒ deployable |
| P08 Backend Dev | submits PRs | fast feedback | long CI | PR feedback ≤ 8 min |
| P12 Security Reviewer | scans deps | catch CVEs | missed transitive | SBOM + vuln report on every PR |

## Collaboration Model
1. Primary: backend dev pushing a branch.
2. Supporting: SRE tuning gate thresholds; security reviewer triaging findings.
3. System actors: GitHub Actions / Cloud Build; Trivy / OSV-Scanner; ruff / mypy; pytest; gocyclo.
4. Approvals: gate threshold changes require team-lead sign-off.
5. Handoff: green pipeline → deploy job (E00-F02 outputs).
6. Failure recovery: dev fixes locally; rebases; CI re-runs.

## Behavioural Model
- Hesitation: dev unsure whether a CC-6 helper is worth refactoring.
- Rework: vuln scan flags transitive CVE; dev pins dep.
- Partial info: test added but not registered; gate catches missing coverage.
- Abandoned flow: CI infra outage; dev re-runs after status page recovers.

---

## User Stories

### Story 1: TDD gate enforces test-before-code

**As a** team
**I want** CI to fail when a production change lands without a corresponding test commit
**So that** TDD discipline holds without manual reviewer policing.

#### Preconditions
- CLAUDE.md TDD discipline is canonical.

#### Main Flow
1. CI computes diff: production file change without a same-PR test file change → fail.
2. Override label (`chore:scaffolding`) skips gate but records justification in PR body.

#### Edge Cases
- Pure refactor of test code only — gate passes.
- Generated code (e.g., proto stubs) — gate sees label `generated:true`.

#### Acceptance Criteria
```gherkin
Given a PR modifies a *.py file under domain/ without changing any tests/
When CI runs
Then the TDD gate fails with a message naming the missing test directory
And the dev can label `chore:scaffolding` only with a one-line justification
```

#### Dependencies
- DEP-INT to E00-F03 (fakes used by tests)

#### Non-Functional Considerations
- Reliability: gate runs offline (no network).
- Performance: gate adds ≤ 30 s.

#### Open Questions
- Is the gate per-bounded-context or repo-wide?

---

### Story 2: Complexity gate (CC ≤ 5) blocks merges

**As a** code reviewer
**I want** functions with cyclomatic complexity > 5 to fail CI
**So that** complex helpers are split before they land.

#### Preconditions
- Per-language complexity tool wired (gocyclo, radon, dart-code-metrics).

#### Main Flow
1. CI runs complexity tool on changed files.
2. Functions with CC ≥ 6 produce warning; CC ≥ 8 produce hard fail.
3. Allowed waiver via `# noqa: complexity` with reviewer comment.

#### Edge Cases
- Generated code skipped via path allow-list.
- Test fixtures with long match statements waived as data, not logic.

#### Acceptance Criteria
```gherkin
Given a function has cyclomatic complexity 7
When CI runs the complexity gate
Then the build fails and the function name and CC value are surfaced
```

#### Non-Functional Considerations
- Reliability: gate runs offline.
- DX: pre-commit hook surfaces issue before push.

---

### Story 3: Security scan (SBOM + CVE) on every PR

**As a** security reviewer
**I want** SBOM and CVE scan results on every PR
**So that** new vulnerabilities are caught before merge.

#### Preconditions
- Trivy / OSV-Scanner / pip-audit configured.

#### Main Flow
1. CI generates SBOM (CycloneDX format).
2. Scanner runs against current dependency tree.
3. PR comment posts new vulnerabilities introduced by the change.

#### Edge Cases
- Vendor-pinned dep with known CVE; waiver requires ADR or risk acceptance note.
- Transitive dep CVE not yet patched; dev sets ignore-until-date with reviewer approval.

#### Acceptance Criteria
```gherkin
Given a PR adds a dependency with a Critical CVE
When CI runs the security scan
Then the PR is blocked and the CVE ID + remediation are posted as a comment
```

#### Non-Functional Considerations
- Compliance: SBOM stored as CI artifact (≥ 90-day retention).
- Privacy: scan results tagged `internal-only`.

#### Open Questions
- Should we additionally run a SAST (semgrep / bandit) on every PR or weekly?
