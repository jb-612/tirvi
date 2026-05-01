---
feature_id: N02/F27
status: ready
total_estimate_hours: 0.5
---

# Tasks: N02/F27 — HebPipe Coref (deferred MVP stub)

## T-01: Coref no-op stub

- [x] **T-01 done**
- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-144]
- estimate: 0.5h
- test_file: tests/unit/test_coref_stub.py
- dependencies: []
- hints: Create tirvi/coref/__init__.py with COREF_ENABLED=False, CorefResult dataclass
  (chains: list = field(default_factory=list)), enrich_with_coref(nlp_result) -> CorefResult
  always returning empty chains when COREF_ENABLED=False. Test FT-144: assert
  enrich_with_coref(any_nlp_result).chains == [] when env flag is not set.

## Dependency DAG

T-01 (standalone)
