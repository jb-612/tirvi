---
feature_id: N03/F28
status: ready
total_estimate_hours: 0.5
deferred: true
---

# Tasks: N03/F28 — Azure Cognitive Services TTS Adapter (Deferred MVP)

This feature is confirmed deferred per PLAN-POC.md. A single stub task covers
the no-op identity function. Full Azure TTS synthesis tasks are MVP scope.

## T-01: Implement synthesize_azure feature-gated stub

- [x] **T-01 done**

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.5h
- test_file: tests/unit/test_azure_tts_stub.py
- dependencies: []
- hints: >
    `tirvi/adapters/azure_tts/__init__.py` — if os.getenv("TIRVI_AZURE_TTS") is falsy,
    raise NotImplementedError("Azure TTS adapter is deferred MVP"). No Azure SDK import.
    Test: assert raises NotImplementedError when env var absent.

## Dependency DAG

```
T-01 (standalone stub)
```
