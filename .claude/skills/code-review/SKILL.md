---
name: code-review
description: 2-phase code review — Phase 1 automated quality gates, Phase 2 three-agent parallel manual review with master synthesis. Use when reviewing PRs, inspecting code, or auditing a module.
allowed-tools: Read, Glob, Grep, Bash
argument-hint: "[scope or file-path]"
context: fork
agent: reviewer
---

Review code for $ARGUMENTS:

## When to Use

- Code review (workflow step 4)
- Security audit
- Code inspection before commit

## When NOT to Use

- Writing or fixing code (read-only skill)
- Running tests (use `@testing`)

## Phase 1: Automated Quality Gates

Run the automated quality gate pipeline **before** any manual review. This pre-screens for issues that tooling can catch deterministically.

**Invoke the gate script:**

```bash
bash .claude/scripts/quality-gate.sh 2>&1 | tee /tmp/acm-gate-results.txt
```

Capture the full stdout as `$GATE_RESULTS` (the contents of `/tmp/acm-gate-results.txt`).

**On failure (any gate FAIL):**
1. Output the gate results table showing which gates failed
2. List the fix commands for each failed gate (e.g., `uv run ruff format --fix`)
3. **Stop here — do not proceed to Phase 2.** Block all manual review until gates pass.

**On success (all gates PASS or WARN):**
1. Store the gate results path (`/tmp/acm-gate-results.txt`) for Phase 2 agents
2. Proceed to Phase 2 with `$GATE_RESULTS` available as context

## Phase 2: Manual Review (3-Agent Parallel)

Launch three specialized review passes in parallel. Each agent receives the `$GATE_RESULTS` preamble from Phase 1 as context before starting their review.

### Agent 1: Architecture Reviewer

**Gate results preamble:** Read `$GATE_RESULTS` before starting. The automated gates have already verified formatting, lint, dead code, complexity, type checking, SAST, SCA, tests, and coverage.

**Skip list — do not review these (covered by automated gates):**
- Import ordering and formatting issues (covered by ruff gate)
- Complexity score numbers (covered by radon and complexipy gates)

**Focus areas (manual-only):**
- Design coherence with `design.md` specifications
- Schema compliance: new nodes/edges use `schema.py` types
- Backend interface: methods defined in `db/base.py` first
- ID conventions: `{type}:{context}:{name}` kebab-case
- No circular imports between modules
- Ingestion accepts `GraphBackend` parameter

### Agent 2: Code Quality + Security Reviewer

**Gate results preamble:** Read `$GATE_RESULTS` before starting. The automated gates have already verified formatting, lint, dead code, complexity, type checking, SAST, SCA, tests, and coverage.

**Skip list — do not review these (covered by automated gates):**
- Lint violations (covered by ruff gate)
- Complexity threshold violations (covered by radon and complexipy gates)
- Known CVEs in dependencies (covered by pip-audit gate)
- SAST basics like hardcoded secrets, injection patterns (covered by bandit gate)

**Focus areas (manual-only):**
- **Logic correctness** — Does the logic match the specification? Are edge cases handled?
- **Domain security** — Authorization, data boundaries, domain-specific attack vectors
- **Naming** — Clear, consistent naming that follows project conventions
- Invokes `@security-review` checklist for manual-only security concerns (not the automated SAST/SCA already gated)

### Agent 3: Test Coverage Reviewer

**Gate results preamble:** Read `$GATE_RESULTS` before starting. The automated gates have already verified formatting, lint, dead code, complexity, type checking, SAST, SCA, tests, and coverage.

**Skip list — do not review these (covered by automated gates):**
- Test pass/fail status (covered by pytest gate)
- Overall coverage percentage (covered by coverage gate)

**Focus areas (manual-only):**
- Coverage gaps — untested code paths, missing edge cases
- Assertion quality — meaningful assertions, not just "runs without error"
- Test isolation — no shared state, no order dependencies
- Boundary testing — off-by-one, empty input, max values
- Mock appropriateness — mocking at right boundaries

## Master Synthesis

After all three Phase 2 agents complete:

1. Collect results: 10 automated gate results + manual findings from 3 agents
2. **Deduplicate:** For each manual finding, check if it overlaps with a gate category (same file + same category as a gate). If overlap is found, keep the manual finding but annotate it with "also caught by gate N" to indicate redundancy
3. Assign severity: Critical / High / Medium / Low
4. Create GitHub issues for Critical/High findings

```bash
gh issue create --title "Review: <finding>" --label "code-review,<severity>"
```

Critical and High issues must be resolved before commit. Medium/Low tracked for follow-up.

## Output Format

Present the final review output in three sections:

### Section 1: Gate Results Table

| Gate | Status | Details |
|------|--------|---------|
| Formatting | PASS/FAIL | ruff format check |
| Lint | PASS/FAIL | ruff check |
| Dead code | PASS/FAIL | vulture |
| Complexity (radon) | PASS/FAIL | radon cc |
| Complexity (complexipy) | PASS/FAIL | complexipy |
| Type check (mypy) | PASS/WARN | mypy |
| SAST (bandit) | PASS/FAIL | bandit |
| SCA (pip-audit) | PASS/FAIL | pip-audit |
| Unit tests | PASS/FAIL | pytest |
| Coverage | PASS/FAIL | pytest --cov |

### Section 2: Manual Findings Table

| # | Finding | Agent | Severity | File | Source |
|---|---------|-------|----------|------|--------|
| 1 | Description | Architecture/Quality/Tests | Critical/High/Medium/Low | path/to/file.py | Manual |

If a finding overlaps with a gate, add "(also caught by gate N)" to the Source column.

### Section 3: Verdict

- **PASS** — All gates passed and no Critical/High manual findings
- **FAIL** — Any gate failed OR Critical/High manual findings exist
- Summary of key issues and created GitHub issue links

## Cross-References

- `@security-review` — Dedicated security analysis (invoked by Agent 2)
- `@testing` — Run quality gates after review fixes
- `@feature-completion` — Final validation after review
- `@design-pipeline` — Design pipeline (uses `@design-review` for design validation)
- `@design-review` — Sibling review skill for design artifacts
