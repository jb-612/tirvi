---
feature_id: N03/F27
status: ready
total_estimate_hours: 0.5
deferred: true
---

# Tasks: N03/F27 — Google Chirp3 HD Voice TTS Adapter (Deferred MVP)

This feature is confirmed deferred per PLAN-POC.md. A single stub task covers
the no-op identity function. Full Chirp3 synthesis tasks are MVP scope.

## T-01: Implement synthesize_chirp3 feature-gated stub

- [ ] **T-01 done**

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.5h
- test_file: tests/unit/test_chirp3_stub.py
- dependencies: []
- hints: >
    `tirvi/adapters/chirp3/__init__.py` — if os.getenv("TIRVI_CHIRP3") is falsy,
    raise NotImplementedError("Chirp3 adapter is deferred MVP"). No real API calls.
    Test: assert raises NotImplementedError when env var absent.

## Dependency DAG

```
T-01 (standalone stub)
```
