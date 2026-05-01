# ADR-036 — Pipeline observability: injectable ProgressReporter protocol

**Status**: Proposed
**Bounded context**: ingest / platform (N01/F49)
**Owner**: tirvi pipeline orchestrator
**Date**: 2026-05-01

## Context

`run_pipeline()` in `tirvi/pipeline.py` is a 30–60 s synchronous black box.
Operators running `uv run scripts/run_demo.py` cannot tell which stage is
active, how fast the cascade is progressing, or which stage is the bottleneck.
HLD §3.3 defines the worker pipeline stages (OCR → normalize → NLP →
diacritize → G2P → reading plan → TTS); HLD §8 confirms the single-container
dev environment as the primary local-run context. PRD §7.2 TTFA ≤ 30 s p50
SLO creates operator demand for latency visibility.

Three options were evaluated:

**Option A — print statements**: ad-hoc `print()` calls inside
`run_pipeline()`. Fast to add, impossible to test, impossible to disable in
CI, pollutes domain code with UI concerns.

**Option B — injectable ProgressReporter protocol + rich**: a `Protocol`
parameter injected at the `run_pipeline()` call site. Default is a no-op.
`RichProgressReporter` handles TTY detection and `rich` display; falls back
to structured plain-log lines when stdout is not a TTY. Cascade progress
observed via the existing `EventListener` protocol on
`CorrectionCascadeService` (ADR-033 §Event model) — no domain-layer changes.

**Option C — external profiling (py-spy)**: attach a profiler at the process
level. Operator must install py-spy; no operator-friendly live display;
does not address real-time progress feedback, only post-run analysis.

## Decision

**Option B** — injectable `ProgressReporter` protocol (DE-01) with a
`RichProgressReporter` concrete implementation (DE-02).

Key constraints captured by the design review (F49-ARCH-01..03):

1. Cascade token progress is observed via the existing `EventListener`
   protocol on `CorrectionCascadeService` — the `ProgressReporter` registers
   as a listener. No `on_token` callback is added to `run_page()`.
2. `sys.stdout.isatty()` is checked at **construction time**, before any
   `rich` object is created (prevents garbage output on non-TTY rich init).
3. `rich` import is guarded with `try/except ImportError`; the plain-log path
   activates automatically in environments where `rich` is not installed.

## Consequences

### Positive
- **Testable**: `ProgressReporter` is a protocol; test doubles are trivial.
- **Backwards-compatible**: `run_pipeline()` callers that omit `reporter=`
  receive `NoOpProgressReporter` and observe no behaviour change.
- **CI-safe**: non-TTY detection produces ANSI-free, grep-able log lines.
- **Domain clean**: `tirvi/pipeline.py` and `tirvi/correction/service.py`
  gain no UI concerns; the observer pattern already exists (ADR-033).

### Negative
- **`rich` as dev-only dependency**: must be added to `pyproject.toml`
  under a `[dev]` or optional extra to avoid inflating the production image.
- **Thread safety**: `ProgressReporter` is not thread-safe. Documented as
  assumption (ASM-F49-03). If `run_page` is ever parallelized, callers must
  supply a thread-safe wrapper.

## Alternatives considered

1. **Option A — print statements**: rejected (untestable, pollutes domain).
2. **Option C — py-spy**: rejected (external tooling, no live progress).
3. **Hook on_token into run_page() directly**: rejected (F49-ARCH-01
   resolution) — EventListener protocol already exists and is cleaner.

## References

- HLD §3.3 — Worker pipeline stages
- HLD §8 — Single-container dev environment
- ADR-033 — Hebrew correction cascade (EventListener pattern)
- ADR-029 — Vendor-boundary discipline
- `.workitems/N01-ingest-ocr/F49-pipeline-progress/design-review.md`
  (F49-ARCH-01, F49-ARCH-02, F49-ARCH-03, F49-ADV-02)
