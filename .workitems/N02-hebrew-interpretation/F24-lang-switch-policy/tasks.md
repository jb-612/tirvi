---
feature_id: N02/F24
status: ready
total_estimate_hours: 0.5
---

# Tasks: N02/F24 — Inline Language Switching Policy (deferred MVP stub)

## T-01: Lang-switch no-op stub

- [x] **T-01 done**
- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-183]
- estimate: 0.5h
- test_file: tests/unit/test_lang_switch.py
- dependencies: []
- hints: Create tirvi/ssml/lang_switch.py with LANG_SWITCH_ENABLED=False and
  apply_lang_policy(ssml, lang_spans, voice_profile) -> str that returns ssml unchanged
  when LANG_SWITCH_ENABLED is False. Test: apply_lang_policy(s, [], "wavenet") == s.
  FT-183 (nested spans) is deferred MVP; anchor T-01 only for the gate test (FT-144 equiv).

## Dependency DAG

T-01 (standalone)
