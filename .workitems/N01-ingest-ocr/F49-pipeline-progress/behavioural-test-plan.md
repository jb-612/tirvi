# F49 — Behavioural Test Plan: CLI Pipeline Progress Reporting

**Feature:** N01/F49-pipeline-progress
**Bounded Contexts:** bc:pipeline_orchestration, bc:observability
**Test ID Range:** BT-209..BT-218
**Source stories:** US-F49-01..US-F49-06
**Test Layer:** Behavioural (operator-goal, observable outcome, no mock internals)

---

## BT-209 — Operator spots a hung stage and knows which one

**Goal:** The operator's mental model maps directly to what the display shows.
**Story:** US-F49-06/AC-01, US-F49-01/AC-02

```gherkin
Given `uv run scripts/run_demo.py --stubs` is running
And the Nakdan stage has been running for 35 seconds
When the operator looks at the terminal
Then they see exactly one row with a running spinner — the Nakdan row
And the Nakdan elapsed time is ≥ 35 seconds and still increasing
And all previous stage rows show a green checkmark
And no other stage shows a spinner or timer
```

**Why it matters:** Before F49 the terminal showed nothing during the 30-60s
run. A hung Nakdan with no feedback looked identical to normal operation.

---

## BT-210 — Operator runs in CI; output is structured and grep-able

**Goal:** CI can extract per-stage timing from captured stdout.
**Story:** US-F49-05/AC-01..AC-04

```gherkin
Given the demo script is invoked as part of a CI job (stdout is not a TTY)
When the pipeline completes successfully
Then each stage produces a "done" line in the form:
  [<ISO8601-ts>] <STAGE> done elapsed=<float>s <metric_label>
And the summary block starts with a line containing "Summary"
And all lines are safe to pipe through `grep`, `awk`, and `jq`
And no line contains ANSI control sequences
```

**Why it matters:** CI captures stdout for artifact diff. Rich live output would
corrupt logs with escape codes and confuse tee/grep pipelines.

---

## BT-211 — Operator watches LLM call count grow during Correction Cascade

**Goal:** Operator understands that LLM calls are happening and roughly how many.
**Story:** US-F49-03/AC-03, US-F49-02/AC-02

```gherkin
Given the Correction Cascade stage is running on 20 ambiguous tokens
And at least 3 tokens require an LLM call
When the operator watches the Cascade row during execution
Then the LLM call count starts at 0
And the operator can observe it increment in real time during the run
And the final LLM call count displayed matches the actual call count in the summary
```

**Why it matters:** Operators debugging prompt latency need to know whether
LLM calls are happening at all, and whether the anti-hallucination policy is
causing more or fewer calls than expected.

---

## BT-212 — Operator sees the slowest stage at a glance after run completes

**Goal:** The summary table delivers its bottleneck signal without scrolling.
**Story:** US-F49-04/AC-01

```gherkin
Given the pipeline has completed
When the operator looks at the terminal immediately after completion
Then the first data row of the summary table is the slowest stage
And the stage name, duration, and metric are all visible in that row
And the operator can identify the bottleneck without reading all rows
```

---

## BT-213 — Operator running `--stubs` mode sees deterministic fast run

**Goal:** Stub mode completes quickly and the progress display still makes sense.
**Story:** US-F49-01/AC-03, US-F49-04/AC-01

```gherkin
Given `uv run scripts/run_demo.py --stubs` is invoked
When the pipeline completes
Then all five stage rows show a green checkmark
And no row shows elapsed time greater than 5 seconds
And the summary table is printed with durations in sub-second range
And no error rows are displayed
```

---

## BT-214 — Operator running real mode can identify TTS as slowest stage

**Goal:** Real-mode run surfaces TTS cost to the operator.
**Story:** US-F49-04/AC-01, US-F49-02/AC-03

```gherkin
Given `uv run scripts/run_demo.py` (no --stubs) is invoked
And the pipeline completes successfully
When the operator reads the summary table
Then the TTS stage row shows a non-zero KB metric
And the summary table is sorted by duration, not by pipeline order
```

---

## BT-215 — Rich display does not measurably slow down the pipeline

**Goal:** The progress instrumentation overhead is negligible.
**Story:** US-F49-01 (performance non-regression)

```gherkin
Given the pipeline is run in stub mode twice:
  Run A: with progress reporter enabled
  Run B: with progress reporter disabled (LOG_LEVEL=WARNING, no rich)
When both runs complete
Then Run A total elapsed is no more than 500 ms longer than Run B
```

**Why it matters:** ADR-033 established that observability hooks must not
perturb the pipeline timing budget (PRD §7.2 TTFA ≤ 30s p50).

---

## BT-216 — Error in one stage does not suppress the summary table

**Goal:** The operator gets timing data even on a partial failure.
**Story:** US-F49-04/AC-02, US-F49-01/AC-04

```gherkin
Given the TTS stage raises an exception mid-run
When the demo script finishes (with non-zero exit code)
Then the summary table is still printed to stdout
And all stages that completed before the error show their real durations
And the errored stage shows "ERROR" in the Duration column
```

---

## BT-217 — Cascade progress percentage matches actual token position

**Goal:** Operator can reliably judge how far through the cascade they are.
**Story:** US-F49-03/AC-01 + AC-02

```gherkin
Given the Correction Cascade is running on N tokens (N > 10)
When the operator reads the progress percentage at any point
Then the displayed percentage is within ±2% of (tokens_processed / N * 100)
And the percentage never decreases during a single cascade run
And the percentage reaches exactly 100% before the "done" state appears
```

---

## BT-218 — Non-TTY mode is automatically selected — no flag required

**Goal:** Operator does not need to remember a `--no-rich` flag in CI.
**Story:** US-F49-05/AC-04

```gherkin
Given the demo script is invoked in a pipeline where stdout is redirected:
  `uv run scripts/run_demo.py --stubs > /tmp/demo.log`
When /tmp/demo.log is read
Then it contains plain-text stage lines (no ANSI codes)
And the operator did not pass any extra flag to enable plain-log mode
```
