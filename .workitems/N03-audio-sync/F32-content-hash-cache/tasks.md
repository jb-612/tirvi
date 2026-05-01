---
feature_id: N03/F32
status: ready
total_estimate_hours: 0.5
deferred: true
---

# Tasks: N03/F32 — TTS Content-Hash Audio Cache (Deferred MVP)

This feature is confirmed deferred per PLAN-POC.md. A single stub task covers
the always-None cache miss. Full cache backend wiring is MVP scope.

## T-01: Implement get_cached_audio always-miss POC stub

- [x] **T-01 done**

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.5h
- test_file: tests/unit/test_tts_cache_stub.py
- dependencies: []
- hints: >
    `tirvi/cache/tts.py` — `def get_cached_audio(reading_plan_sha: str) -> None: return None`.
    When TIRVI_TTS_CACHE is set, raise NotImplementedError (cache backend not wired).
    Test: assert returns None when gate unset; assert raises NotImplementedError when set.

## Dependency DAG

```
T-01 (standalone stub)
```
