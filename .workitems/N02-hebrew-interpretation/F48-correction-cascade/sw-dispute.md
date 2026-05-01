# sw-dispute.md — F48 open questions and workarounds

TDD run. Any design question that required a workaround is logged here
for user review. Medium/Low code-review findings are tagged [GH-ISSUE-NEEDED].

---

## [DISPUTE-02] httpx not installed; used urllib.request instead (ADR-029)
- **Task:** T-04a
- **Question:** ADR-029 designates `adapters/ollama.py` as "the ONLY file allowed to import httpx",
  but `httpx` is not installed in the project or the pytest tool environment.
- **Workaround:** Implemented `_http_post()` using `urllib.request` (stdlib). The monkeypatch
  target is the same module-level function. No functional difference for the unit tests.
- **Impact if wrong:** Low for unit tests. Medium for production: `urllib.request` lacks
  httpx's connection pooling and async support. If httpx is added as a dependency later,
  replace `_http_post` body; the interface and tests stay unchanged.

## [DISPUTE-01] pyyaml not available in pytest tool environment
- **Task:** T-03
- **Question:** `confusion_pairs.yaml` loader was intended to use `pyyaml`, but the
  pytest tool's isolated Python (`/root/.local/share/uv/tools/pytest/bin/python`)
  does not have pyyaml installed, causing `ModuleNotFoundError` at collection time.
- **Workaround:** Replaced `yaml.safe_load` with a 12-line stdlib-only line parser
  (`_parse_table_line` + `_load_table`). Supports the exact format used by
  confusion_pairs.yaml (`key:\n  - value`). YAML comments and blank lines handled.
- **Impact if wrong:** Low — the custom parser is narrower than full YAML but sufficient
  for the flat string→list format. If the confusion table ever uses anchors, multi-line
  values, or nested dicts, the parser must be replaced with pyyaml.

## [REVIEW-01] pytest.mark.slow not registered in pyproject.toml [GH-ISSUE-NEEDED]
- **Task:** T-02
- **Finding:** `@pytest.mark.slow` on `test_p95_under_5ms_for_1000_token_loop` produces a
  `PytestUnknownMarkWarning`. The mark needs registering in `pyproject.toml`
  under `[tool.pytest.ini_options] markers`.
- **Impact:** Low — warning only, tests still pass. pyproject.toml is a protected path;
  defer to user after run.
