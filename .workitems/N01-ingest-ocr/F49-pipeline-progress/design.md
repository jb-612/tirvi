---
feature_type: integration
hld_refs: [HLD-§3.3-worker-pipeline-stages, HLD-§5.2-processing, HLD-§8-dev-environment]
adr_refs: [ADR-037]
biz_corpus: true
---

# F49 — Design: CLI Pipeline Progress Reporting

## Design Elements

### DE-01: ProgressReporter protocol

A `typing.Protocol` injected into `run_pipeline()` as an optional keyword
argument (`reporter: ProgressReporter = _NOOP_REPORTER`). Defines:

- `stage_started(name: str, total_tokens: int | None = None) -> None`
- `stage_completed(name: str, elapsed_s: float, metric_label: str) -> None`
- `stage_error(name: str, error_label: str) -> None`
- `token_tick() -> None` — called once per token from EventListener hook
- `summarize() -> None` — prints/emits the summary table

Injecting the protocol preserves backwards-compat: callers that omit
`reporter=` get `NoOpProgressReporter` silently.

### DE-02: RichProgressReporter (TTY path)

Implements `ProgressReporter`. Detected at construction time via
`sys.stdout.isatty()`. TTY path: `rich.live.Live` + `rich.progress.Progress`
with spinners, elapsed timers, and a progress bar for the cascade stage.
Non-TTY path: plain `logging.INFO` lines with ISO 8601 timestamps (no ANSI).

**Design notes from review:**
- ADR-037 decision: constructor checks `sys.stdout.isatty()` BEFORE creating
  any `rich` objects (F49-ARCH-03).
- `rich` import is guarded with `try/except ImportError`; falls back to
  plain-log path automatically (F49-ARCH-02).
- `ProgressReporter` documents non-thread-safe assumption (F49-ADV-02).

### DE-03: Pipeline stage instrumentation

`run_pipeline()` wraps each top-level stage call:

```python
reporter.stage_started("OCR")
# ... ocr call ...
reporter.stage_completed("OCR", elapsed_s, f"{word_count} words")
```

Cascade stage additionally wires `ProgressReporter` as an `EventListener`
on `CorrectionCascadeService`. The reporter's `on_correction_applied` /
`on_correction_rejected` handler calls `token_tick()` and increments the
LLM call counter when `event.stage == "llm_reviewer"`.

**Architecture decision (F49-ARCH-01):** Cascade token progress is observed
via the existing `EventListener` protocol — NOT via an `on_token` callback
parameter on `run_page()`. No change to `service.py` required.

### DE-04: Summary table

After all stages complete, `summarize()` renders a table sorted descending
by `elapsed_s`. TTY path: `rich.table.Table`. Non-TTY path: tab-separated
plain text lines (stage, duration_s, metric) with a "Total" footer line.
Printed once after the `Live` display closes.

### DE-05: PipelineReport value object

`@dataclass(frozen=True) class PipelineReport` with
`stages: tuple[StageTiming, ...]` where `StageTiming` has
`name: str`, `elapsed_s: float | None`, `metric_label: str`, `errored: bool`.
`run_pipeline()` returns `dict[str, Any]` extended with `"report": PipelineReport`.

## Decisions

- **D-01**: `ProgressReporter` as injected protocol (not global state, not
  subclassing) — see ADR-037.

## Deferred / Out of Scope

- E2E: `[ANCHOR]` placeholder for full-stack pipeline instrumentation tests.
- BT-215 threshold tuning deferred to TDD phase.
- `atexit` flush on Ctrl-C deferred to TDD phase (F49-ADV-04).
