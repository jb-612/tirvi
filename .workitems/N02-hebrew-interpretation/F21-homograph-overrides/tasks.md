---
feature_id: N02/F21
status: ready
total_estimate_hours: 3.0
---

# Tasks: N02/F21 — Hebrew Homograph Override Lexicon

## T-01: HomographEntry dataclass + YAML schema definition

- [ ] **T-01 done**
- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-158]
- estimate: 0.5h
- test_file: tests/unit/test_homograph_entry.py
- dependencies: []
- hints: Frozen dataclass `surface_form: str`, `vocalized_form: str`,
  `pos_filter: str | None = None`. Test: assert FrozenInstanceError on set attempt.

## T-02: YAML loader + validation

- [ ] **T-02 done**
- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-158, FT-159, FT-162]
- estimate: 1h
- test_file: tests/unit/test_homograph_loader.py
- dependencies: [T-01]
- hints: `load_overrides(path) -> dict[str, str]` — `yaml.safe_load()`;
  skip entries with pos_filter set (POC flat-dict only); malformed YAML
  raises ValueError. Assert load of 2-entry YAML < 200 ms (FT-162).
  Use tmp_path fixture. Test: empty → {}; 2-entry → {כל: כֹּל}; malformed → ValueError.

## T-03: HOMOGRAPH_OVERRIDES singleton + F19 integration

- [ ] **T-03 done**
- design_element: DE-03
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-158]
- bt_anchors: [BT-107]
- estimate: 0.5h
- test_file: tests/unit/test_homograph_overrides.py
- dependencies: [T-02]
- hints: Module-level `HOMOGRAPH_OVERRIDES = load_overrides(default_path)` in
  `tirvi/lexicon/homograph.py`. Update `tirvi/adapters/nakdan/overrides.py` to
  import from `tirvi.lexicon.homograph`. Send coordination mailbox msg to TDD
  session before editing nakdan/overrides.py (shared file).

## T-04: POC seed data in data/homograph-lexicon.yaml

- [ ] **T-04 done**
- design_element: DE-04
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-158, FT-159]
- estimate: 0.5h
- test_file: tests/unit/test_homograph_loader.py (covered)
- dependencies: [T-01]
- hints: Two entries — (1) {surface_form: כל, vocalized_form: כֹּל, pos_filter: null};
  (2) {surface_form: ספר, vocalized_form: סָפַר, pos_filter: VERB} (POS-filtered
  exemplar; skipped by POC loader). Add YAML schema comment header.

## T-05: Diagram docs/diagrams/N02/F21/homograph-lexicon.mmd

- [ ] **T-05 done**
- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.5h
- test_file: —
- dependencies: []
- hints: flowchart LR — Maintainer → yaml → load_overrides() → HOMOGRAPH_OVERRIDES → F19_pick.
  No subgraph, no classDef.

## Dependency DAG

```
T-01 → T-02 → T-03
T-01 → T-04
T-05 (independent)
```

Critical path: T-01 → T-02 → T-03 (2h)
