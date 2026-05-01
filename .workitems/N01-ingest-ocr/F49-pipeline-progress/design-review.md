# F49 — Design Review: CLI Pipeline Progress Reporting

**Reviewers:** Product Strategy, DDD, Architecture, Testing, Adversarial
**Artifacts reviewed:** user_stories.md, user_stories.part-2.md,
  functional-test-plan.md, behavioural-test-plan.md

---

## Reviewer 1 — Product Strategy

**Verdict:** PASS with one Medium note.

**F49-PR-01** [Medium] The feature targets P04 (Developer/Operator) only. The
feature description says "developers and operators running the CLI demo locally
or in a cloud session." This is explicitly a dev-tooling feature and is not in
the path of P01 (Student) or P02 (Coordinator). PRD §7.2 is the only PRD
section directly applicable (TTFA ≤ 30s p50). Progress reporting itself does
not change TTFA — it only makes the existing latency visible. Recommendation:
add a one-sentence scope guard to user_stories.md clarifying this is a
dev-tooling overlay with no UX contract toward P01. **Resolution:** Accepted
as informational; scope guard added in US-F49-01 Source Basis note.

**F49-PR-02** [Low] The "Correction Cascade" stage label differs from HLD §3.3
stage names (normalize → nlp → plan → synthesize). The five stages in F49
(Rasterize, OCR, Nakdan, Correction Cascade, TTS) map to the POC demo pipeline
in `tirvi/pipeline.py`, not the full HLD pipeline. This is correct given
F49's scope is `scripts/run_demo.py`. No action required; label alignment to
future full-pipeline stages is deferred to when run_demo.py covers all stages.

---

## Reviewer 2 — DDD

**Verdict:** PASS with one High clarification resolved.

**F49-DDD-01** [High — resolved in review] Initial draft named two bounded
contexts `bc:pipeline_orchestration` and `bc:observability`. Review challenged
whether a new BC is warranted for a tooling overlay vs. adding to `bc:platform`.
**Resolution:** `bc:observability` is accepted as a lightweight supporting
subdomain of `D01-SD06 Platform & Quality`. It does NOT introduce a new
aggregate or repository — `StageTiming` and `PipelineReport` are pure value
objects consumed by the dev CLI only. No domain event broker; the
`ProgressEvent` subtypes (StageStarted, StageCompleted, TokenProcessed,
PipelineCompleted) are emitted in-process via the existing `EventListener`
pattern already established in F48 (ADR-033). This is consistent with the
codebase pattern.

**F49-DDD-02** [Low] The `TokenProcessed` event is specific to the Correction
Cascade stage and may not generalize to other stages. Keeping it narrow is
correct — it is a stage-specific event, not a pipeline-level contract.
Naming it `CascadeTokenProcessed` would be more precise; deferred to
sw-designpipeline phase.

---

## Reviewer 3 — Architecture

**Verdict:** PASS with one High concern resolved.

**F49-ARCH-01** [High — resolved in review] **Callback hook location:** The
feature description calls for a "per-token progress hook" in
`tirvi/correction/service.py`. Review evaluated two options:

Option A — Hook inside `CorrectionCascadeService.run_page`:
  - Pro: minimal interface; already has an `EventListener` protocol (F48).
  - Con: adds UI concern to domain service; violates single-responsibility.

Option B — Hook via the existing `EventListener` protocol:
  - Pro: `CorrectionCascadeService` already dispatches events to listeners.
    A `ProgressReporter` registered as a listener receives `CorrectionApplied`
    and `CorrectionRejected` events and can count tokens without touching
    the domain service.
  - Con: requires token-count to be inferrable from event stream. It is —
    each token produces exactly one verdict event.

**Decision:** Option B is cleaner. The `ProgressReporter` attaches as an
`EventListener` to `CorrectionCascadeService`. Token count = sum of
`CorrectionApplied` + `CorrectionRejected` events. LLM call count = count of
events where `stage == "llm_reviewer"`. No change to service.py needed.
This is the architecture recommendation for sw-designpipeline.

**F49-ARCH-02** [Medium] `rich` library must be an optional dev dependency.
The import should be guarded (`try: from rich...; except ImportError: ...`)
so the pipeline itself does not crash if `rich` is absent in a minimal
production image. Plain-log fallback (US-F49-05) already covers the no-rich
path by design.

**F49-ARCH-03** [Low] The `ProgressReporter` must not hold a reference to
`rich.Live` when stdout is not a TTY. Constructing `rich.Live` on a non-TTY
stdout may cause an error or garbage output depending on the `rich` version.
TTY detection must happen at construction time before any `rich` object is
created.

---

## Reviewer 4 — Testing

**Verdict:** PASS with two Low gap notes.

**F49-TEST-01** [Low] Functional tests FT-316..FT-328 test the `ProgressReporter`
value object API directly. No test currently covers the wiring between
`run_pipeline` in `tirvi/pipeline.py` and the `ProgressReporter`. An
integration test (Track C) should verify that `run_pipeline` actually calls
`stage_start` / `stage_done` for each stage. This is in scope for Track C
(`@integration-test`) and is deferred to that phase.

**F49-TEST-02** [Low] Behavioural test BT-215 (performance non-regression)
requires two sequential runs and a ≤ 500 ms delta claim. In a cloud session
with variable CPU, this delta may be flaky. Recommendation: increase the
threshold to ≤ 2000 ms or mark the test as advisory (not a gate). Deferred
to TDD phase for threshold tuning.

**F49-TEST-03** [Low — gap] No test covers the `rich` ImportError guard
(F49-ARCH-02). A unit test that imports `ProgressReporter` without `rich`
installed and confirms plain-log fallback is activated would close this gap.
Noted for TDD task list.

---

## Reviewer 5 — Adversarial

**Verdict:** PASS with three concerns, one Medium resolved.

**F49-ADV-01** [Medium — resolved] **TTY detection edge case:** `sys.stdout.isatty()`
returns `False` in many cloud SSH sessions even when the operator is watching
a real terminal. This could silently downgrade to plain-log in cloud IDE
sessions. **Resolution:** F49 targets `uv run scripts/run_demo.py` in a
developer context. If the operator wants rich output in a cloud session,
they can ensure a PTY is allocated (`ssh -t`). The plain-log fallback is
always correct and never broken. The risk is aesthetic only. Accepted as-is;
documented in ASM-F49-04.

**F49-ADV-02** [Medium] **Cascade hook thread-safety:** If `run_page` is ever
parallelized in a future refactor, a shared `ProgressReporter` receiving
events from multiple threads without locking could produce incorrect counters.
Current code is sequential (ASM-F49-03); this is a future risk. **Resolution:**
The `ProgressReporter` should document its non-thread-safe assumption. Deferred
to sw-designpipeline design notes; no story change needed.

**F49-ADV-03** [Low] **Rich performance overhead:** `rich.Live` refreshes on
a timer (default 4 Hz). Updating a `Live` display 4 times/second for 60
seconds adds ~240 render calls. Each render call is O(rows) where rows = 5.
This is negligible (<< 1 ms per render). No performance risk.

**F49-ADV-04** [Low] **Summary table after ctrl-C:** If the operator kills
the pipeline with Ctrl-C, the summary table currently may not be printed
(KeyboardInterrupt bypasses normal exit). `run_demo.py` already catches
`KeyboardInterrupt` in the HTTP server loop but not during pipeline execution.
The `ProgressReporter` should register a `finally` / `atexit` to flush the
summary on abnormal exit. Deferred to TDD task list.

---

## Summary: Findings by Severity

| ID | Severity | Status | Owner |
|----|----------|--------|-------|
| F49-PR-01 | Medium | Resolved — scope guard in stories | — |
| F49-DDD-01 | High | Resolved — Option B EventListener pattern | sw-design |
| F49-ARCH-01 | High | Resolved — EventListener hook, no service change | sw-design |
| F49-ARCH-02 | Medium | Open — deferred to TDD (import guard) | TDD |
| F49-ADV-01 | Medium | Resolved — plain-log fallback is always correct | — |
| F49-ADV-02 | Medium | Open — deferred (thread-safety doc note) | sw-design |
| F49-DDD-02 | Low | Deferred — naming to sw-designpipeline | sw-design |
| F49-ARCH-03 | Low | Open — TTY detection at construction | TDD |
| F49-TEST-01 | Low | Deferred — integration test Track C | @integration-test |
| F49-TEST-02 | Low | Deferred — threshold tuning in TDD | TDD |
| F49-TEST-03 | Low | Deferred — ImportError guard test | TDD |
| F49-ADV-03 | Low | Resolved — negligible overhead | — |
| F49-ADV-04 | Low | Deferred — atexit flush | TDD |
| F49-PR-02 | Low | Resolved — label alignment deferred | sw-design |

**No unresolved Critical findings.**
**No unresolved High findings.**
**Design approved for sw-designpipeline.**
