# F49 — CLI Pipeline Progress Reporting: User Stories (Part 2)

**Continuation of:** user_stories.md (US-F49-01..03 in Part 1)
**This file:** US-F49-04..US-F49-06 + Assumption Register

---

## US-F49-04 — See a ranked summary table after pipeline completes

**As** a developer running the CLI demo,
**I want** a summary table printed after the pipeline finishes that ranks stages
by duration from slowest to fastest,
**so that** I can immediately identify performance bottlenecks without adding
external profiling tools.

**Source:** Feature description; PRD §7.2 (TTFA SLO); ASM-F49-01

### AC-01 — Summary table appears after pipeline completes (success)
```gherkin
Given the pipeline has finished without errors
When the display settles
Then a summary table is printed below the stage rows
And the table has columns: Stage, Duration (s), Metric
And rows are ordered slowest to fastest (descending by duration)
```

### AC-02 — Summary table appears after pipeline completes (partial error)
```gherkin
Given at least one stage errored but others completed
When the display settles
Then the summary table is still printed
And the errored stage row shows "ERROR" in the Duration column
```

### AC-03 — Total wall-clock time is shown at the bottom of the table
```gherkin
Given the pipeline has finished
When I read the summary table
Then the last row shows "Total" with the overall wall-clock elapsed time
```

---

## US-F49-05 — Run in a non-TTY / CI environment without rich display

**As** a developer or CI pipeline running `uv run scripts/run_demo.py`,
**I want** the progress output to gracefully degrade to plain log lines
when stdout is not a TTY (e.g. piped to a file or captured by CI),
**so that** the demo script is still usable in automated environments and
produces machine-parseable structured output.

**Source:** PRD §7.5 Portability; ASM-F49-04 (CI compatibility assumption)

### AC-01 — Non-TTY stdout produces plain log lines with timestamps
```gherkin
Given stdout is not a TTY (e.g. piped: `... | cat`)
When the pipeline runs
Then each stage emits a plain log line of the form:
  [<timestamp>] <STAGE> <event> <metric?>
And no ANSI escape codes or spinner characters are present in the output
```

### AC-02 — Non-TTY output includes stage-start and stage-done lines
```gherkin
Given stdout is not a TTY
When the OCR stage starts
Then a line "[<ts>] OCR started" is printed
When the OCR stage finishes
Then a line "[<ts>] OCR done elapsed=<s>s words=<n>" is printed
```

### AC-03 — Non-TTY output includes the summary table as plain text
```gherkin
Given stdout is not a TTY
When the pipeline finishes
Then a summary block is printed listing each stage, duration, and metric
And the block is in a consistent, parse-friendly format (e.g. TSV or labelled lines)
```

### AC-04 — TTY detection uses sys.stdout.isatty()
```gherkin
Given the progress reporter is constructed
When sys.stdout.isatty() returns False
Then the reporter selects the plain-log renderer
When sys.stdout.isatty() returns True
Then the reporter selects the rich live renderer
```

---

## US-F49-06 — See a hung stage clearly identified

**As** a developer running the CLI demo when a stage hangs,
**I want** the stage row to display a continuously growing elapsed time,
**so that** I can immediately identify which stage is hung and decide whether
to kill the process.

**Source:** Feature description ("eliminates black box experience"); ASM-F49-01

### AC-01 — Hung stage shows ever-growing elapsed timer
```gherkin
Given the Nakdan stage has been running for more than 30 seconds
When I observe the display
Then the Nakdan row elapsed time continues to increase every second
And no other stage row shows an active spinner
```

### AC-02 — No false "done" state is emitted for a hung stage
```gherkin
Given the Nakdan stage is hung
When I observe the display at any refresh interval
Then the Nakdan row never shows a checkmark or "done" state
Until the stage either completes or raises an exception
```

---

## Assumption Register (F49-specific)

| ID | Assumption | Confidence |
|----|------------|-----------|
| ASM-F49-01 | `rich` library is already available in the dev Docker image or is added as a dev dependency via `pyproject.toml`. No production API or web player dependency is introduced. | high |
| ASM-F49-02 | Per-stage metrics (word count, token count, LLM calls, KB) are inferrable from existing pipeline return values and `EventListener` hooks already on `CorrectionCascadeService` (F48). | high |
| ASM-F49-03 | The cascade `run_page` method processes tokens sequentially, so a per-token callback is a valid progress hook without concurrency risk. | high |
| ASM-F49-04 | CI pipelines capturing `run_demo.py` output expect no ANSI codes; plain-log fallback is required for correctness, not just aesthetics. | medium |
