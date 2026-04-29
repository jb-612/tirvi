---
feature_id: N02/F20
status: ready
total_estimate_hours: 6.0
---

# Tasks: N02/F20 — Phonikud G2P adapter

## T-01: Phonikud loader with lazy import

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- estimate: 1h
- test_file: tests/unit/test_phonikud_loader.py
- dependencies: []
- hints: lazy `import phonikud` inside load function; lru_cache; raise PhonikudNotInstalled with installation hint when missing in non-test code path

## T-02: Per-token IPA + stress emission

- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-152, FT-154, FT-157]
- bt_anchors: [BT-101]
- estimate: 1.5h
- test_file: tests/unit/test_phonikud_inference.py
- dependencies: [T-01]
- hints: per-token call into phonikud; PronunciationHint(ipa: str, stress: int | None, shva: list[bool] | None); pass diacritized text from F19

## T-03: Vocal-shva passthrough (no synthesis)

- design_element: DE-03
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-153]
- estimate: 1h
- test_file: tests/unit/test_vocal_shva.py
- dependencies: [T-02]
- hints: copy phonikud.vocal_shva when emitted; emit None when phonikud is silent; never invent based on heuristics

## T-04: Token-skip filter for NUM / EN / punct

- design_element: DE-04
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-156]
- bt_anchors: [BT-102]
- estimate: 1h
- test_file: tests/unit/test_g2p_skip_filter.py
- dependencies: [T-02]
- hints: same predicate as F19 token-skip; emit Token with pronunciation_hint=None and confidence=None

## T-05: PronunciationHint shape + JSON-safe escape

- design_element: DE-05
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-152]
- bt_anchors: [BT-103]
- estimate: 0.5h
- test_file: tests/unit/test_pronunciation_hint.py
- dependencies: [T-02]
- hints: frozen @dataclass; ensure ipa survives json.dumps/loads round-trip; document 1-based stress index

## T-06: Adapter contract conformance

- design_element: DE-06
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-155]
- bt_anchors: [BT-104]
- estimate: 1h
- test_file: tests/unit/test_phonikud_adapter.py
- dependencies: [T-02, T-03, T-04, T-05]
- hints: pass PhonikudG2PAdapter through assert_adapter_contract; provider="phonikud"; tests use F03 G2PBackendFake when phonikud missing

## Dependency DAG

```
T-01 → T-02 → T-03
              T-04
              T-05
T-02, T-03, T-04, T-05 → T-06
```

Critical path: T-01 → T-02 → T-03 → T-06 (4.5h)
