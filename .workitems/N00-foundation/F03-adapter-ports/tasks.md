---
feature_id: N00/F03
status: ready
total_estimate_hours: 9.5
---

# Tasks: N00/F03 — Adapter Ports & In-Memory Fakes

## T-01: Scaffold tirvi Python package

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.5h
- test_file: tests/unit/test_package_structure.py
- dependencies: []
- hints: pyproject.toml (if absent), tirvi/__init__.py, ports.py, results.py, fakes.py, contracts.py stubs; basic import test goes red first

## T-02: Define result dataclasses (OCR, NLP, Diacritization, G2P, TTS)

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-011, FT-012, FT-013]
- estimate: 1h
- test_file: tests/unit/test_results.py
- dependencies: [T-01]
- hints: frozen @dataclass; provider: str; confidence: float | None; payload fields per domain stage; OCRResult has pages list

## T-03: Define WordTimingResult with Literal source field

- design_element: DE-01, DE-03
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-014]
- estimate: 0.5h
- test_file: tests/unit/test_results.py
- dependencies: [T-01]
- hints: source: Literal["tts-marks", "forced-alignment"]; frozen; provider field same as siblings

## T-04: Define 6 port Protocols (tirvi/ports.py)

- design_element: DE-02
- acceptance_criteria: [US-01/AC-01, US-02/AC-01]
- ft_anchors: [FT-011, FT-016]
- bt_anchors: [BT-009]
- estimate: 1h
- test_file: tests/unit/test_ports.py
- dependencies: [T-02, T-03]
- hints: @runtime_checkable Protocol; single method per port; return type is result only — no vendor types in signatures

## T-05: Implement WordTimingProvider coordinator (ADR-015 fallback)

- design_element: DE-03
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-014]
- bt_anchors: [BT-012]
- estimate: 1.5h
- test_file: tests/unit/test_word_timing_provider.py
- dependencies: [T-03, T-04]
- hints: 3-predicate check (non-empty, count==tokens, monotonic); TIRVI_TTS_MARK_RELIABILITY=low opt-out; emit timing_source metric on fallback

## T-06: Fake registry for OCR, NLP, Diacritizer, G2P ports

- design_element: DE-04
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-015]
- bt_anchors: [BT-010, BT-011]
- estimate: 1.5h
- test_file: tests/unit/test_fakes.py
- dependencies: [T-02, T-04]
- hints: JSON/dict fixture file per port under tests/fixtures/; happy-path + 1 failure-mode fixture per port; deterministic across N calls

## T-07: Fake registry for TTS and WordTimingProvider ports

- design_element: DE-04
- acceptance_criteria: [US-01/AC-01, US-02/AC-01]
- ft_anchors: [FT-012, FT-013, FT-014]
- bt_anchors: [BT-010]
- estimate: 1h
- test_file: tests/unit/test_fakes.py
- dependencies: [T-03, T-04, T-05]
- hints: TTSBackendFake with marks-present and marks-absent fixtures; WordTimingProviderFake routes per source field

## T-08: Implement assert_adapter_contract + run against all fakes

- design_element: DE-05
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-016]
- bt_anchors: [BT-009, BT-011]
- estimate: 1.5h
- test_file: tests/unit/test_contracts.py
- dependencies: [T-04, T-06, T-07]
- hints: rejects bytes with "must return <ResultType>"; asserts required fields present; run against all 6 fakes as parametrized test

## T-09: Vendor-import boundary lint (ruff + import test)

- design_element: DE-06
- acceptance_criteria: [US-01/AC-01]
- bt_anchors: [BT-012]
- estimate: 1h
- test_file: tests/unit/test_import_boundary.py
- dependencies: [T-01]
- hints: ruff.toml per-file rule; block google.cloud.*, transformers, torch, huggingface_hub from tirvi/; import-boundary test does subprocess ruff check

## Dependency DAG

```
T-01 → T-02, T-03, T-09
T-02 → T-04
T-03 → T-04
T-04 → T-05, T-06
T-05 → T-07
T-06 → T-08
T-07 → T-08
```

Critical path: T-01 → T-02 → T-04 → T-06 → T-08 (6h)
