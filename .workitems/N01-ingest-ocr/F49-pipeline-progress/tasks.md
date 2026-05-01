# F49 — Tasks: CLI Pipeline Progress Reporting

## T-01: Define ProgressReporter protocol and StageTiming/PipelineReport value objects

- [x] **T-01 done**

- design_element: DE-01, DE-05
- acceptance_criteria: [US-F49-01/AC-01, US-F49-02/AC-01]
- ft_anchors: [FT-316, FT-317]
- estimate: 1h
- test_file: tests/unit/test_progress_reporter.py
- dependencies: []
- hints: >
    `class ProgressReporter(Protocol)` with `stage_started`, `stage_completed`,
    `stage_error`, `token_tick`, `summarize`. `StageTiming(name, elapsed_s,
    metric_label, errored)` and `PipelineReport(stages)` as frozen dataclasses.
    Live in `tirvi/progress.py`.

---

## T-02: Implement NoOpProgressReporter

- [x] **T-02 done**

- design_element: DE-01
- acceptance_criteria: [US-F49-01/AC-02]
- ft_anchors: [FT-318]
- estimate: 0.5h
- test_file: tests/unit/test_progress_reporter.py
- dependencies: [T-01]
- hints: >
    Default no-op implementation satisfying `ProgressReporter` protocol.
    All methods are silent no-ops. Used as default when `reporter=` is omitted
    from `run_pipeline()`. Must not import `rich`.

---

## T-03: Wire ProgressReporter into run_pipeline() stage calls

- [x] **T-03 done**

- design_element: DE-03
- acceptance_criteria: [US-F49-01/AC-01, US-F49-01/AC-03, US-F49-02/AC-04]
- ft_anchors: [FT-319, FT-320, FT-321]
- bt_anchors: [BT-213, BT-214]
- estimate: 1.5h
- test_file: tests/unit/test_pipeline_progress.py
- dependencies: [T-01, T-02]
- hints: >
    Wrap each stage in `tirvi/pipeline.py` with `reporter.stage_started()` /
    `reporter.stage_completed()`. Metrics: OCR → f"{word_count} words",
    Rasterize → "—", Nakdan → f"{token_count} tokens",
    TTS → f"{audio_kb:.0f} KB". `run_pipeline()` gains optional `reporter`
    kwarg defaulting to `NoOpProgressReporter()`. Return dict gains
    `"report": PipelineReport`.

---

## T-04: Wire ProgressReporter as EventListener for Cascade stage progress

- [x] **T-04 done**

- design_element: DE-03
- acceptance_criteria: [US-F49-03/AC-01, US-F49-03/AC-03]
- ft_anchors: [FT-322, FT-323, FT-324]
- bt_anchors: [BT-217]
- estimate: 1h
- test_file: tests/unit/test_pipeline_progress.py
- dependencies: [T-01, T-03]
- hints: >
    `RichProgressReporter` (or a test spy) implements `EventListener` from
    `tirvi/correction/service.py`. Register reporter as listener on
    `CorrectionCascadeService` in `_run_cascade_for_page()`. `token_tick()`
    is called via `on_correction_applied` + `on_correction_rejected`. LLM
    call counter incremented when `event.stage == "llm_reviewer"`. No changes
    to `CorrectionCascadeService.run_page()` signature.

---

## T-05: Implement RichProgressReporter with TTY detection and summary table

- [x] **T-05 done**

- design_element: DE-02, DE-04
- acceptance_criteria: [US-F49-01/AC-01, US-F49-01/AC-02, US-F49-01/AC-03,
    US-F49-05/AC-01, US-F49-05/AC-04]
- ft_anchors: [FT-325, FT-326, FT-327, FT-328]
- bt_anchors: [BT-209, BT-210, BT-212]
- estimate: 2h
- test_file: tests/unit/test_rich_progress_reporter.py
- dependencies: [T-01, T-02]
- hints: >
    Detect `sys.stdout.isatty()` at construction; import `rich` inside a
    `try/except ImportError` — on ImportError fall back to plain-log path
    automatically (F49-ARCH-02). TTY path: `rich.live.Live` + `rich.progress.
    Progress` with spinners and a progress bar for cascade. Non-TTY path:
    `logging.INFO` lines: `[<ISO8601>] <STAGE> started` and
    `[<ISO8601>] <STAGE> done elapsed=<s>s <metric>`. `summarize()` emits
    `rich.table.Table` sorted by elapsed_s descending (TTY) or
    tab-separated plain text with "Total" footer (non-TTY). Document
    non-thread-safe assumption in docstring (F49-ADV-02).

---

## T-06: Wire RichProgressReporter into run_demo.py CLI

- [x] **T-06 done**

- design_element: DE-02
- acceptance_criteria: [US-F49-06/AC-01, US-F49-04/AC-01, US-F49-04/AC-03]
- ft_anchors: [FT-316]
- bt_anchors: [BT-211, BT-216, BT-218]
- estimate: 0.5h
- test_file: tests/unit/test_pipeline_progress.py
- dependencies: [T-03, T-05]
- hints: >
    In `main()`: `reporter = RichProgressReporter()`, pass to
    `run_pipeline(pdf_bytes, _DRAFTS, deps, reporter=reporter)`.
    After pipeline completes: `reporter.summarize()`. Wrap `run_pipeline`
    call in `try/finally` so `summarize()` fires even on partial error
    (F49-ADV-04 partial mitigation).
