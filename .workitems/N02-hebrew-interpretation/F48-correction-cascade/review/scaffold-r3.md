# Scaffold Review — Gate 3 (L4 Behaviour + L5 TDD shells)

**Verdict**: PASS

## Scope
- Layers: L4 (behaviour shells), L5 (TDD shells + fakes).
- Files: `tirvi/correction/{service,log,health,feedback_aggregator}.py`,
  `tests/unit/conftest.py`, 10 `tests/unit/test_*.py` skeletons.

## L4 — Behaviour shell checks

| Module | Class | Port impl | Methods (all NotImplemented) |
|---|---|---|---|
| `service.py` | `CorrectionCascadeService` | orchestrator (DE-05) | `run_page`, `_publish` |
| `service.py` | `EventListener` | runtime_checkable Protocol | 4 `on_*` callbacks |
| `service.py` | `PageCorrections` | frozen DTO | n/a (data) |
| `log.py` | `CorrectionLog` | DE-06 writer | `write_page`, `_entries_for_page`, `_record_audit_gap` |
| `log.py` | `CorrectionLogEntry` | BO55 frozen DTO | n/a |
| `health.py` | `HealthProbe` | DE-07 selector | `run`, `select_mode`, `_deprecated_known_fixes_lookup` |
| `feedback_aggregator.py` | `FeedbackAggregator` | DE-08 CLI | `run`, `_emit_rule_promoted` |

- All bodies raise `NotImplementedError("AC-... / TDD T-NN fills")`.
- No business logic anywhere.
- `service.EventListener` is a Protocol — no broker, no infra (ADR-033).
- `log.CorrectionLog` carves out `CHUNKING_PAGE_THRESHOLD = 50` constant
  per ADR-035.
- `health._deprecated_known_fixes_lookup` is the explicit bridge to
  `tirvi/normalize/ocr_corrections.py::_KNOWN_OCR_FIXES`; not deleted
  (T-09 deprecate-and-redirect is TDD's job).

## L5 — TDD shell checks

- 10 test files match `tasks.md` `test_file:` fields exactly.
- Every file declares `pytestmark = pytest.mark.skip(reason="scaffold — /tdd fills")`.
- 109 cascade-specific tests skipped cleanly + 5 in `test_pipeline.py`
  (T-09 wiring) = **114 new tests** (`850 - 736` baseline).
- `tests/unit/conftest.py` provides 4 fakes (`FakeNakdanWordList`,
  `FakeLLMClient`, `FakeFeedbackReader`, `FakeCascadeStage`) plus 4
  fixtures. All in-memory, deterministic, no business logic — they
  store inputs and return canned outputs. Become `@test-mock-registry`
  seed in TDD.
- Test class structure walks the AC matrix per file (AC-01..AC-04 of
  the relevant story); GWT comments included.

## Anti-pattern checks (clean)

- ✅ No real Ollama / Nakdan / DictaBERT calls in fakes.
- ✅ No `_KNOWN_OCR_FIXES` deletion — kept for `no_mlm` mode bridge.
- ✅ `mlm_correction.py` in `tirvi/normalize/` untouched (T-09 deprecates).
- ✅ All tests collect without import errors (verified via `pytest --collect-only`).
- ✅ `pytest.mark.slow` warning is informational; FT-317 perf gate
  marker can be registered in `pyproject.toml` at TDD time.

## Findings
None blocking. Proceeding to L6/L7.
