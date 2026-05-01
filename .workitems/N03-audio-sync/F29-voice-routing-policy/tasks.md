---
feature_id: N03/F29
status: ready
total_estimate_hours: 0.5
deferred: true
---

# Tasks: N03/F29 — Voice Routing Policy (Deferred MVP — Single-Voice POC)

This feature is confirmed deferred (multi-voice routing) per PLAN-POC.md. A single
stub task covers the constant-`"wavenet"` return. Full policy table is MVP scope.

## T-01: Implement route_voice constant-wavenet POC stub

- [ ] **T-01 done**

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.5h
- test_file: tests/unit/test_voice_router_stub.py
- dependencies: []
- hints: >
    `tirvi/voice_router.py` — `def route_voice(block, config) -> str: return "wavenet"`.
    When TIRVI_VOICE_ROUTING is set, raise NotImplementedError (multi-voice policy
    not yet implemented). Test: assert return == "wavenet" when gate unset.

## Dependency DAG

```
T-01 (standalone stub)
```
