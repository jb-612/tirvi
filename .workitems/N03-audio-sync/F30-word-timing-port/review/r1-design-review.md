# R1 Design Review — N03/F30 Word-Timing Port (TTS-marks Adapter)

- **Feature:** N03/F30 (WordTimingProvider — TTS-marks adapter for POC)
- **Reviewer:** R1 multi-role (6 specialist roles synthesized)
- **Date:** 2026-05-01
- **Inputs reviewed:** design.md, tasks.md, traceability.yaml, ontology-delta.yaml,
  user_stories.md, functional-test-plan.md, behavioural-test-plan.md,
  docs/diagrams/N03/F30/word-timing-port.mmd, ADR-015,
  HLD §4/AdapterInterfaces

---

## Role 1 — Contract Alignment

### Finding 1: T-01 not done — adapter class shell missing
- **Area:** contract
- **Issue:** T-01 (TTSEmittedTimingAdapter class) is `[ ] not done` while T-02, T-03,
  T-04 are done. T-02/T-03/T-04 are helpers/invariants; T-01 is the public adapter
  class. Unclear how helpers were implemented without the containing class.
- **Severity:** Medium
- **Recommendation:** Verify `tirvi/adapters/tts_marks/__init__.py` exists with the
  TTSEmittedTimingAdapter class. If it does, mark T-01 done. If helpers are standalone
  functions not yet wired to the adapter class, T-01 is genuinely pending.

### Finding 2: F30 DE-05 (truncation alignment) depends on F26 T-04 (truncation detect)
- **Area:** contract
- **Issue:** design.md DE-05 reads `tts_result.voice_meta.get("tts_marks_truncated")`.
  F26 T-04 sets this flag. If F26 T-04 is not yet done (as noted in F26 review F1),
  F30 DE-05 will always see False and never trigger the alignment logic.
- **Severity:** High (cross-feature dependency, same as F26 review F1)
- **Recommendation:** Block F30 T-05 TDD on F26 T-04 completion. Document in F30 tasks.md.

---

## Role 2 — Architecture & Pattern

### Finding 3: end_s derivation for last WordTiming — fragile when audio_duration absent
- **Area:** architecture
- **Issue:** DE-02 specifies "last token's end_s from tts_result.audio_duration_s or
  last_mark.start_s + 0.2." The 0.2s fallback is a magic constant with no documented
  rationale. For short last words (monosyllabic Hebrew endings like "ה"), 0.2s may
  over-estimate. For long words, it may under-estimate.
- **Severity:** Low
- **Recommendation:** Document in design.md DE-02: "0.2s fallback for last word
  duration is a POC approximation; calibrated from average Hebrew monosyllable TTS
  duration (N05 bench will refine)."

---

## Role 3 — Test Coverage

### Finding 4: T-05 (truncation alignment) not in task list
- **Area:** test coverage
- **Issue:** design.md DE-05 describes truncation-aware alignment (post-review C2) but
  tasks.md does not have a T-05 task for it. T-04 is the monotonicity invariant.
  DE-05 has no corresponding task.
- **Severity:** High
- **Recommendation:** Add T-05 to tasks.md: "Mark-count vs transcript-token alignment
  (DE-05) — when tts_marks_truncated flag is set, align up to min(marks, tokens),
  log warning." This task depends on F26 T-04.

---

## Role 4 — HLD Compliance

### Finding 5: ADR-015 dual-adapter pattern correctly referenced; WhisperX correctly deferred
- **Area:** HLD compliance
- **Issue:** design.md correctly states "ADR-015 references the fallback policy but it
  does not activate here." WhisperX is deferred per PLAN-POC.md. This is correct.
- **Severity:** Low (confirmation)

---

## Roles 5-6: No additional findings

---

## Summary

| Finding | Severity | Area | Action |
|---------|----------|------|--------|
| F1: T-01 not done — verify adapter shell | Medium | Contract | Verify class exists |
| F2: DE-05 depends on F26 T-04 | **High** | Contract | Block F30/T-05 on F26/T-04 |
| F3: 0.2s magic constant | Low | Architecture | Document rationale in DE-02 |
| **F4: T-05 missing from tasks.md** | **High** | Test | Add T-05 for DE-05 truncation alignment |
| F5: ADR-015 correct | Low | HLD | None |

**High (2):** F2 (cross-feature block), F4 (missing task). Both block F30 completion.
