# F49 — Functional Test Plan: CLI Pipeline Progress Reporting

**Feature:** N01/F49-pipeline-progress
**Bounded Contexts:** bc:pipeline_orchestration, bc:observability
**Test ID Range:** FT-316..FT-328
**Source stories:** US-F49-01..US-F49-06
**Test Layer:** Functional (public API / behaviour contract) + Smoke + Regression

---

## FT-316 — Stage rows render in correct order before execution starts

**Type:** FUNC
**Story:** US-F49-01/AC-01
**Precondition:** A `ProgressReporter` is constructed with a list of five stage names.

```gherkin
Given a ProgressReporter with stages [Rasterize, OCR, Nakdan, Cascade, TTS]
When get_rows() is called before any stage starts
Then five rows are returned in insertion order
And each row has status "pending"
```

---

## FT-317 — Active stage row shows "running" status

**Type:** FUNC
**Story:** US-F49-01/AC-02

```gherkin
Given a ProgressReporter
When stage_start("OCR") is called
Then get_row("OCR").status == "running"
And elapsed_s > 0 after 1 second
```

---

## FT-318 — Completed stage row transitions to "done" with frozen elapsed

**Type:** FUNC
**Story:** US-F49-01/AC-03

```gherkin
Given OCR stage has been started and elapsed 2 seconds
When stage_done("OCR") is called
Then get_row("OCR").status == "done"
And get_row("OCR").elapsed_s is frozen (does not increase after stage_done)
```

---

## FT-319 — Error stage row transitions to "error" with message

**Type:** FUNC
**Story:** US-F49-01/AC-04

```gherkin
Given TTS stage is running
When stage_error("TTS", "Connection refused to Google TTS") is called
Then get_row("TTS").status == "error"
And get_row("TTS").error_label contains "Connection refused"
```

---

## FT-320 — OCR stage metric reports word count

**Type:** FUNC
**Story:** US-F49-02/AC-01

```gherkin
Given OCR stage is running
When set_metric("OCR", "words", 42) is called
Then get_row("OCR").metric == "42 words"
```

---

## FT-321 — Cascade stage metric shows token count and LLM calls

**Type:** FUNC
**Story:** US-F49-02/AC-02

```gherkin
Given Cascade stage is running with 30 tokens and 2 LLM calls recorded
When get_row("Cascade").metric is read
Then it equals "30 tokens · 2 LLM calls"
```

---

## FT-322 — TTS stage metric reports audio size in KB

**Type:** FUNC
**Story:** US-F49-02/AC-03

```gherkin
Given TTS stage completes and produces 131072 bytes of audio
When set_metric("TTS", "audio_bytes", 131072) is called
Then get_row("TTS").metric == "128 KB"
```

---

## FT-323 — Cascade token progress percentage is accurate

**Type:** FUNC
**Story:** US-F49-03/AC-01 + AC-02

```gherkin
Given Cascade stage started with total_tokens=50
When token_progress(25) is called
Then get_row("Cascade").progress_pct == 50
When token_progress(50) is called
Then get_row("Cascade").progress_pct == 100
```

---

## FT-324 — LLM call counter increments live

**Type:** FUNC
**Story:** US-F49-03/AC-03

```gherkin
Given Cascade stage is running
When llm_call_made() is called three times
Then get_row("Cascade").llm_calls == 3
```

---

## FT-325 — Summary table sorted slowest-to-fastest by duration

**Type:** FUNC
**Story:** US-F49-04/AC-01

```gherkin
Given pipeline completed with durations:
  Rasterize=1.2s, OCR=3.4s, Nakdan=12.1s, Cascade=8.7s, TTS=4.3s
When build_summary_table() is called
Then rows appear in order: Nakdan, Cascade, TTS, OCR, Rasterize
And a Total row shows sum ≈ 29.7s
```

---

## FT-326 — Summary table includes error stage without crashing

**Type:** FUNC / REGRESSION
**Story:** US-F49-04/AC-02

```gherkin
Given TTS stage errored
When build_summary_table() is called
Then the TTS row shows "ERROR" in the Duration column
And all successfully completed stages are listed with correct durations
```

---

## FT-327 — Non-TTY renderer emits plain log lines, no ANSI

**Type:** FUNC
**Story:** US-F49-05/AC-01 + AC-02

```gherkin
Given sys.stdout.isatty() returns False
When a ProgressReporter is constructed and stage_start("OCR") is called
Then the output contains no ANSI escape sequences (no \x1b[ patterns)
And the output contains the text "OCR started"
When stage_done("OCR", elapsed_s=2.1, metric_label="42 words") is called
Then the output contains "OCR done" and "elapsed=2.1s" and "words=42"
```

---

## FT-328 — Non-TTY summary block is parseable plain text

**Type:** FUNC / SMOKE
**Story:** US-F49-05/AC-03

```gherkin
Given sys.stdout.isatty() returns False
And the pipeline has completed
When the summary block is written
Then each line is tab-separated with fields: stage, duration_s, metric
And the last line starts with "Total"
And no ANSI codes are present
```
