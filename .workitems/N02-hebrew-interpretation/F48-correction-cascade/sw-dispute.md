# sw-dispute.md — F48 open questions and workarounds

TDD run. Any design question that required a workaround is logged here
for user review. Medium/Low code-review findings are tagged [GH-ISSUE-NEEDED].

---

## [REVIEW-01] pytest.mark.slow not registered in pyproject.toml [GH-ISSUE-NEEDED]
- **Task:** T-02
- **Finding:** `@pytest.mark.slow` on `test_p95_under_5ms_for_1000_token_loop` produces a
  `PytestUnknownMarkWarning`. The mark needs registering in `pyproject.toml`
  under `[tool.pytest.ini_options] markers`.
- **Impact:** Low — warning only, tests still pass. pyproject.toml is a protected path;
  defer to user after run.
