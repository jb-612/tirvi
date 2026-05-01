# Dispute Items — Wave 2 Scaffold + TDD

Log of design uncertainties encountered during autonomous scaffold/TDD runs.
Each item: feature, layer/task, the uncertainty, the decision taken, and whether it needs human review.

Format:
```
## [FXXX / Layer] Short title
- **Uncertainty**: what was ambiguous
- **Decision taken**: what the agent did
- **Review needed**: yes/no — why
```

---

## [F35+F36 / test runner] tasks.md `test_file:` points at Python paths
- **Uncertainty**: every remaining task in F35/F36 lists `test_file: tests/unit/test_*.py`, but `player/` is a Vitest/jsdom sub-project; existing T-01..T-03 tests for F35 and T-01 for F36 live at `player/test/*.spec.js`, not `tests/unit/`. Hint H4 in F35 T-02 says "jsdom-based test" — confirms intent was JS.
- **Decision taken**: implement remaining tests as Vitest specs in `player/test/*.spec.js`. Don't create dead `tests/unit/test_*.py` stubs. Flip tasks.md done markers once JS tests pass. Note in scaffold-notes.md that test_file fields in tasks.md drift from reality.
- **Review needed**: yes — after wave2 ends, sync tasks.md test_file fields to JS paths in a follow-up PR.

## [F36 / scope] T-01 currently mounts ONE button (POC-CRITICAL-PATH deferral) vs. team-lead asking for full state machine
- **Uncertainty**: `controls.js` comment + existing `controls.spec.js` say "POC ships ONE button. T-02..T-06 deferred to v0.1" per `POC-CRITICAL-PATH.md`. Team-lead brief says T-01 is done (4 buttons) and asks for T-02..T-06.
- **Decision taken**: follow team-lead. Extend `controls.js` to mount the four buttons (Play | Pause | Continue | Reset) wired via new state machine + Controls.bind from T-03. Keep `mountPlayButton` exported for back-compat with `main.js`. New API supersedes it.
- **Review needed**: yes — POC-CRITICAL-PATH.md says deferred; either that doc is stale or this is scope creep. Reviewer to reconcile.

## [F36 / aria] aria-keyshortcuts choice for Space and R
- **Uncertainty**: T-06 hints aria-labels in he+en but does not specify aria-keyshortcuts attribute values. T-05 maps Space → toggle play/pause/resume, R → reset.
- **Decision taken**: Play and Continue both get `aria-keyshortcuts="Space"`; Reset gets `aria-keyshortcuts="R"`; Pause also gets `aria-keyshortcuts="Space"` since Space pauses when playing.
- **Review needed**: low — convention check at code-review.

## [F40/F41/F42/F43 / test paths] tasks.md test_file fields drift from team-lead globs
- **Uncertainty**: each tasks.md specifies a test_file (e.g. `tests/bench/test_quality_gates.py` for F40, `tests/unit/test_mos_aggregation.py` for F41, `tests/unit/test_latency_cost_profiler.py` for F42, `tests/unit/test_ttl_cleanup.py` for F43) that diverges from the team-lead's glob territory (`test_quality_gates*.py`, `test_mos*.py`, `test_profiling*.py`, `test_ttl*.py`).
- **Decision taken**: used the team-lead globs as authoritative since these are gate-stub tests living in `tests/unit/`. Files: `test_quality_gates.py`, `test_mos_study.py`, `test_profiling.py`, `test_ttl_automation.py`. Real bench-CI test under `tests/bench/` will be authored when F40 is un-deferred.
- **Review needed**: low — when biz-functional-design re-runs N05, sync tasks.md `test_file:` fields to the actual paths.
