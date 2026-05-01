---
feature_id: N03/F31
status: ready
total_estimate_hours: 0.5
deferred: true
---

# Tasks: N03/F31 — WhisperX Forced-Alignment Fallback WordTimingProvider (Deferred MVP)

This feature is confirmed deferred per ADR-015 and PLAN-POC.md. A single stub task
covers the unconditional NotImplementedError. Full WhisperX integration is MVP scope.

## T-01: Implement align_with_whisperx deferred stub (always NotImplementedError)

- [x] **T-01 done**

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.5h
- test_file: tests/unit/test_whisperx_stub.py
- dependencies: []
- hints: >
    `tirvi/adapters/whisperx/__init__.py` — `def align_with_whisperx(audio_bytes, ssml)`:
    raise NotImplementedError("WhisperX fallback deferred to MVP per ADR-015").
    Unconditional — gate does not enable; it signals future intent only.
    Test: assert raises NotImplementedError always.

## Dependency DAG

```
T-01 (standalone stub)
```
