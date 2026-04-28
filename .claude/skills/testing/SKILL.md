---
name: testing
description: Run quality gates — unit tests, linting, SAST, SCA, complexity, coverage. Use when running tests, checking code quality, or validating before commit.
argument-hint: "[scope or test-path]"
allowed-tools: Read, Glob, Grep, Bash
---

Run quality gates for $ARGUMENTS:

## When to Use

- Running tests before commit
- Pre-merge validation
- Quality gate checks during workflow step 5

## When NOT to Use

- Writing tests (use `@tdd-workflow`)
- Implementing code changes

## Primary Runner

```bash
make gate
```

To auto-fix formatting and lint issues first:

```bash
make gate-fix
```

## Quality Gates (12 gates, cheapest/fastest first)

| # | Gate | Command | Threshold | Mode |
|---|------|---------|-----------|------|
| 1 | Formatting | `ruff format --check` | 0 diffs | blocking |
| 2 | Lint | `ruff check` | 0 errors | blocking |
| 3 | Dead code | `vulture` | 90% confidence | blocking |
| 4 | Complexity (CC) | `radon` | CC <= 5 | blocking |
| 5 | Complexity (cognitive) | `complexipy` | cognitive <= 8 | blocking |
| 6 | Type check | `mypy` | 0 errors | warn |
| 7 | SAST | `bandit` | 0 high severity | blocking |
| 8 | SCA | `pip-audit` | 0 known CVEs | blocking |
| 9 | Unit tests | `pytest tests/unit/` | 0 failures | blocking |
| 10 | Integration tests | `pytest tests/integration/` | 0 failures | warn |
| 11 | Coverage | `pytest --cov` | >= 80% | blocking |
| 12 | Bash syntax | `bash -n` | 0 errors | blocking |

### Gate Ordering Rationale

Gates are ordered cheapest-first to maximize fail-fast efficiency:

1. **Static checks (1-5)**: Instant, catch trivial issues before investing in heavier analysis.
2. **Type checking (6)**: Moderate cost — catches type errors that static linters miss.
3. **Security (7-8)**: Run before tests to avoid executing slow test suites on insecure code.
4. **Tests (9-11)**: Slowest gates last. Gate 9 runs unit-only for fast feedback.
5. **Bash syntax (12)**: Validates shell scripts in hooks and scripts.

## Output

The script prints a summary table:

```
Gate                  Status   Duration
----                  ------   --------
Formatting            PASS     0.3s
Lint                  PASS     0.8s
Dead code             PASS     0.5s
...
```

- Exit code 0: all gates passed
- Exit code 1: first failure stops execution (fail-fast)

## Cross-References

- `@tdd-workflow` — Writing tests (Three Laws TDD)
- `@feature-completion` — Pre-commit validation sequence
- `@code-review` — Also invokes quality gates
