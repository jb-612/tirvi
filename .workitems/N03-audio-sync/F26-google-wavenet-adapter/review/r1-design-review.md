# R1 Design Review — N03/F26 Google Wavenet he-IL-Wavenet-D Adapter

- **Feature:** N03/F26 (Google Cloud TTS adapter — primary voice for POC)
- **Reviewer:** R1 multi-role (6 specialist roles synthesized)
- **Date:** 2026-05-01
- **Inputs reviewed:** design.md, tasks.md, traceability.yaml, ontology-delta.yaml,
  user_stories.md, functional-test-plan.md, behavioural-test-plan.md,
  docs/diagrams/N03/F26/wavenet-adapter.mmd, ADR-001,
  HLD §4/AdapterInterfaces, PRD §6.5 TTS, PRD §9 Constraints

---

## Role 1 — Contract Alignment

### Finding 1: T-04 (mark truncation detect) not done — downstream F30 dependency
- **Area:** contract
- **Issue:** T-04 sets `voice_meta["tts_marks_truncated"] = True` when Wavenet
  returns fewer timepoints than marks in the SSML. F30 DE-05 reads this flag to
  apply graceful alignment. T-04 is `[ ] not done` while T-03 and T-05 are done.
  F30's truncation handling will not be triggered correctly if T-04 is missing.
- **Severity:** High
- **Recommendation:** Prioritize T-04 before F30 T-05 (mark-count alignment) is
  tested. The two tasks have a cross-feature dependency that is not documented in
  either feature's tasks.md.

### Finding 2: ADC credential handling at runtime vs test time
- **Area:** contract / security
- **Issue:** T-01 hints say "raise WavenetCredentialError if ADC missing in non-test
  path." design.md does not document how ADC (Application Default Credentials) is
  expected to be provided in the POC Docker container vs. in tests.
- **Severity:** Low
- **Recommendation:** Add to design.md §Dependencies: "Requires Google Cloud ADC at
  runtime (gcloud auth application-default login or service account key via
  GOOGLE_APPLICATION_CREDENTIALS env var). Tests mock the client; no real ADC needed."

---

## Role 2 — Architecture & Pattern

### Finding 3: Retry policy (3x, 1s/2s/4s) hardcoded — not configurable
- **Area:** architecture
- **Issue:** T-06 specifies 3 retries with 1s/2s/4s backoff, hardcoded. In demo
  environments with flaky connectivity, 4s max backoff may be too fast; in CI,
  3 retries add 7s to every failure. No env var override.
- **Severity:** Low
- **Recommendation:** Add TIRVI_WAVENET_MAX_RETRIES env var (default 3). Consistent
  with TIRVI_NAKDAN_TIMEOUT pattern.

### Finding 4: drafts/<sha>/ no-overwrite policy — may block re-runs
- **Area:** architecture
- **Issue:** T-05 "raises if files exist (no overwrite)." In development/demo
  re-runs, the same reading plan SHA will be presented again. The no-overwrite
  behavior will block re-synthesis after the first run.
- **Severity:** Medium
- **Recommendation:** Add a TIRVI_DRAFTS_OVERWRITE env var (default False) to allow
  overwriting for development/demo iteration. Document in design.md §Approach DE-05.

---

## Role 3 — Test Coverage

### Finding 5: FT-198 (timepoints round-trip) anchored to both T-02 and T-03 — double-anchor
- **Area:** test coverage
- **Issue:** FT-198 anchors both T-02 and T-03. Same double-anchor issue as F20's FT-152.
- **Severity:** Low
- **Recommendation:** Keep in T-02 (synthesis test); remove from T-03 (assembly test
  should reference FT-193 specifically, not the synthesis-level FT).

---

## Role 4 — HLD Compliance

### Finding 6: HLD §4 specifies WordTimingResult.source as Literal — F26 respects this
- **Area:** HLD compliance
- **Issue:** TTSResult.word_marks feeds into F30 which sets source="tts-marks". F26
  correctly emits WordMark objects (not WordTimingResult) — the Literal typing is
  downstream. Design is correct.
- **Severity:** Low (confirmation)

---

## Role 5 — Security

### Finding 7: Audio bytes stored in drafts/ — no encryption at rest
- **Area:** security / privacy
- **Issue:** TTS audio of Hebrew exam text is stored in `drafts/<sha>/audio.mp3` on
  the local filesystem (or Cloud Storage if Docker). No encryption at rest is specified.
  For POC this is acceptable; for production (student exam content), encryption is needed.
- **Severity:** Low (POC)
- **Recommendation:** Add to design.md §Out of Scope: "Audio at-rest encryption deferred
  MVP per PRD §9 privacy constraints."

---

## Role 6 — Complexity

### Finding 8: Retry logic CC — 3 retries with backoff is CC ≤ 4 if using tenacity/loop
- **Area:** complexity
- **Issue:** Retry with 1s/2s/4s backoff could be implemented as a for-loop with sleep,
  which is CC 3-4. Or via `tenacity` library which abstracts it to CC 1. Either is fine.
  The design does not specify which approach.
- **Severity:** Low
- **Recommendation:** Specify in T-06 hints: "Prefer tenacity @retry decorator over
  manual loop to keep CC ≤ 2."

---

## Summary

| Finding | Severity | Area | Action |
|---------|----------|------|--------|
| F1: T-04 pending → F30 dependency | **High** | Contract | Prioritize T-04 before F30/T-05 |
| F2: ADC credential docs | Low | Contract | Add to Dependencies |
| F3: retry not configurable | Low | Architecture | Add env var |
| F4: no-overwrite blocks re-runs | Medium | Architecture | Add TIRVI_DRAFTS_OVERWRITE |
| F5: FT-198 double-anchor | Low | Test | Remove from T-03 |
| F6: Literal typing correct | Low | HLD | None |
| F7: audio at-rest encryption | Low | Security | Add to Out of Scope |
| F8: retry CC via tenacity | Low | Complexity | Add tenacity hint to T-06 |

**High (1):** F1 — T-04 must complete before F30/T-05 is testable.
