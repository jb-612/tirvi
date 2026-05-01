# R2 Adversary Challenge — N03/F30 Word-Timing Port

- **Feature:** N03/F30 (TTS-marks adapter)
- **Stance:** Adversary
- **Date:** 2026-05-01

---

### Finding 4 (High): T-05 missing — OVERTURN (partially)

**R1 stance:** High — T-05 missing from tasks.md; DE-05 has no task.

**Verification:** tasks.md ALREADY HAS T-05 marked `[x] done`. R1 read the
list incorrectly — T-05 exists and covers DE-05/DE-06. However, the as-built
T-05 raises `MarkCountMismatch` on count mismatch, while design.md DE-05 specifies
graceful alignment (min of marks and tokens) when the F26 truncation flag is set.

This is a design-implementation GAP:
- T-05 (as built): strict count check → raises on mismatch
- DE-05 (design): graceful alignment when `tts_marks_truncated=True`

**Verdict:** OVERTURN finding as "T-05 missing" (T-05 exists). However, the gap
between T-05's strict behavior and DE-05's graceful alignment IS a real defect.
Add T-06 (or amend T-05) to implement the truncation-aware path after F26/T-04
sets the flag. This is Medium, not High.

---

### Finding 2: F26/T-04 dependency — SUSTAIN HIGH

The design gap (Finding 4 reclassified) is the same underlying issue: F26/T-04
(truncation detect) must complete before the graceful-alignment path in F30 can
be added. **Verdict:** SUSTAIN HIGH (cross-feature dependency).

### Finding 1: T-01 verify — AGREE (MEDIUM)

T-02/T-03/T-04 are done. If T-01 (adapter class) is pending while helpers are
implemented as standalone functions, they must be wired to the class before T-05
can be correctly wired to the adapter. **Verdict:** SUSTAIN MEDIUM.

### Finding 3: 0.2s magic constant — AGREE (LOW)

Document rationale. **Verdict:** SUSTAIN LOW.

---

## R2 Synthesis

### Confirmed High
1. **F2:** Block truncation-alignment task on F26/T-04.

### Confirmed Medium
2. **F1:** Verify T-01 adapter class exists and wire helpers.
3. **F4 reclassified:** Add T-06 to tasks.md for truncation-aware graceful alignment
   (complement to T-05's strict count check — T-06 adds the flag-check path).

### Overturned
- **F4 original (High):** T-05 exists and is done. Gap is narrower (strict vs graceful).

### Required tasks.md edit (add T-06)
```markdown
## T-06: Truncation-aware graceful alignment (DE-05 graceful path)

- [ ] **T-06 done**
- design_element: DE-05
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.75h
- test_file: tests/unit/test_tts_marks_adapter.py
- dependencies: [T-05, N03/F26 T-04]
- hints: when voice_meta.get("tts_marks_truncated") is True, align marks to
  transcript_tokens up to min(len(marks), len(tokens)); log a warning with both
  counts. T-05's strict MarkCountMismatch applies only when flag is absent/False.
```

### Gate
T-02, T-03, T-04, T-05 green. T-01 needs verification. T-06 is the new task
after F26/T-04 completes.
