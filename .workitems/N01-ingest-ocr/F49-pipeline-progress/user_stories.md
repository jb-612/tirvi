# F49 — CLI Pipeline Progress Reporting: User Stories (Part 1)

**Feature:** N01/F49-pipeline-progress
**Bounded Contexts:** bc:pipeline_orchestration, bc:observability
**Primary Persona:** P04 — Developer / Operator running `uv run scripts/run_demo.py`
**Source Basis:** PRD §7.2 Performance (TTFA ≤ 30s); PRD §7.3 Reliability;
HLD §3.3 Worker pipeline stages; assumptions ASM-F49-01..ASM-F49-04 (Part 2).

**Part 2 file:** `user_stories.part-2.md` (US-F49-04..US-F49-06 + assumptions)

---

## US-F49-01 — See all pipeline stages and their current status

**As** a developer running the CLI demo,
**I want** to see a live list of every pipeline stage (Rasterize, OCR, Nakdan,
Correction Cascade, TTS) with a spinner while running and a checkmark when done,
**so that** I know which stage is currently active and can tell at a glance
whether the run is proceeding normally.

**Source:** PRD §7.2 (TTFA ≤ 30s p50); ASM-F49-01. Scope: dev-tooling only;
no UX contract toward P01 (Student) or P02 (Coordinator).

### AC-01 — Stages appear in correct order before first stage starts
```gherkin
Given the pipeline has not yet started
When `uv run scripts/run_demo.py --stubs` is invoked
Then the terminal displays five stage rows in order:
  Rasterize, OCR, Nakdan, Correction Cascade, TTS
And each row shows a spinner icon in the "pending" state
```

### AC-02 — Active stage shows animated spinner and elapsed time
```gherkin
Given Rasterize stage is running
When the display refreshes
Then the Rasterize row shows a running spinner
And the elapsed time in seconds updates at least once per second
And all other rows remain in "pending" state
```

### AC-03 — Completed stage shows checkmark and final elapsed time
```gherkin
Given the OCR stage has finished successfully
When the display refreshes
Then the OCR row shows a green checkmark
And the final elapsed duration is frozen and displayed
And the next stage row shows the running spinner
```

### AC-04 — Error stage shows error icon and message
```gherkin
Given the TTS stage raises an unhandled exception
When the display refreshes
Then the TTS row shows a red error icon
And the row includes a brief error label (first 60 chars of exception message)
And the summary table is still printed after the error
```

---

## US-F49-02 — See per-stage key metrics

**As** a developer running the CLI demo,
**I want** each stage row to display a key metric alongside elapsed time,
**so that** I can confirm the pipeline is producing expected output volumes.

**Source:** Feature description; ASM-F49-02

### AC-01 — OCR stage shows word count
```gherkin
Given the OCR stage has completed
When I observe the OCR row
Then it shows the number of words extracted (e.g. "42 words")
```

### AC-02 — Cascade stage shows token count and LLM call count
```gherkin
Given the Correction Cascade stage has completed
When I observe the Cascade row
Then it shows the total token count processed (e.g. "42 tokens")
And it shows the number of LLM calls made (e.g. "3 LLM calls")
```

### AC-03 — TTS stage shows output audio size in KB
```gherkin
Given the TTS stage has completed
When I observe the TTS row
Then it shows the size of audio output (e.g. "128 KB")
```

### AC-04 — Stages with no applicable metric show a dash
```gherkin
Given the Rasterize stage has completed
When I observe the Rasterize row
Then the metric column shows "—" (no applicable per-stage metric)
```

---

## US-F49-03 — See real-time token progress for the Correction Cascade

**As** a developer running the CLI demo,
**I want** the Correction Cascade stage row to update its percentage completion
as each token is processed,
**so that** I can see the cascade is making progress and estimate how long it
will take to finish.

**Source:** Feature description; ASM-F49-03

### AC-01 — Progress percentage updates with each token
```gherkin
Given the Correction Cascade stage is running on 50 tokens
When 25 tokens have been processed
Then the Cascade row shows approximately "50%" progress
```

### AC-02 — Progress reaches 100% when all tokens are processed
```gherkin
Given the Correction Cascade stage was running on N tokens
When the last token is processed
Then the Cascade row shows "100%" and transitions to the "done" checkmark state
```

### AC-03 — LLM call count increments live during cascade
```gherkin
Given the Correction Cascade stage is running
When an LLM call is made for an ambiguous token
Then the LLM call counter on the Cascade row increments immediately
```
