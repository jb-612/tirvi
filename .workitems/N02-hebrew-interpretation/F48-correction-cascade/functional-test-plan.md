# N02/F48 Hebrew Correction Cascade — Functional Test Plan

## Scope
Functional behaviour of the 3-stage cascade (NakdanGate → DictaBERTMLMScorer → LLMReviewer), plus correction logging, feedback ingestion, and degradation modes.

**Out of scope**: TTS audio quality (covered by F26/F29 + F40 quality gates), UI rendering of inspector (F50), OCR engine accuracy (F08/F09).

## Source User Stories
| Story ID | Title | Priority |
|----------|-------|---------|
| F48-S01 | NakdanGate first-stage filter | Critical |
| F48-S02 | DictaBERT-MLM confusion-table candidate scoring | Critical |
| F48-S03 | Local Gemma reviewer for ambiguous verdicts | Critical |
| F48-S04 | Auditable correction trail | High |
| F48-S05 | Threshold-gated rule promotion from feedback | High |
| F48-S06 | Degraded modes with stricter thresholds | High |

## Functional Objects Under Test
| Object | Type | Related Story | Expected Behaviour |
|--------|------|--------------|-------------------|
| BO49 CorrectionCascade | aggregate_root | all | orchestrates 3 stages, accumulates StageDecisions |
| BO50 MLMSubstitutionCandidate | value_object | F48-S02 | (text, score, in_word_list) with deterministic scores |
| BO51 ConfusionPair | value_object | F48-S02 | YAML-driven; loaded once per run |
| BO52 StageDecision | value_object | all | records (stage, verdict, mode, scores?) |
| BO53 LLMReviewVerdict | value_object | F48-S03 | parsed JSON output + cache-key |
| BO54 LLMPromptTemplate | value_object | F48-S03 | versioned; locale=he |
| BO55 CorrectionLogEntry | value_object | F48-S04 | row in corrections.json |
| BO56 RuleSuggestion | value_object | F48-S05 | aggregator output |

---

## Test Scenarios

### FT-316: NakdanGate passes ≥ 95% of valid words on a representative page
- Related stories: F48-S01
- Related business objects: BO49, BO52
- Preconditions: Wave-1 fixture page (214 words, 5 known errors).
- Input: page tokens.
- Expected output: ≥ 95% verdict="pass"; the 5 known-error tokens forwarded as "suspect".
- Validation method: pytest fixture; assert pass-rate; assert exact suspect set.
- Failure mode: false-positive suspects (gate over-rejecting) inflate latency past budget.
- Priority: Critical

### FT-317: NakdanGate single-token p95 latency ≤ 5 ms
- Related stories: F48-S01
- Preconditions: warm in-process word list.
- Input: 1000 random Hebrew tokens.
- Expected output: per-token latency p95 ≤ 5 ms.
- Validation method: timed loop with assertion.
- Failure mode: word-list lookup is not in-memory; falls into network/disk path.
- Priority: High

### FT-318: DictaBERT-MLM auto-applies ם/ס when delta ≥ 3.0
- Related stories: F48-S02
- Preconditions: confusion table includes ם↔ס; sentence context "האיוס תגרוס נזק".
- Input: token "תגרוס".
- Expected output: corrected="תגרום", verdict="auto_apply", delta ≥ 3.0.
- Validation method: golden test against ADR-033 example.
- Failure mode: regression on the empirical Wave-1 result.
- Priority: Critical

### FT-319: DictaBERT-MLM keeps original when delta < threshold_low
- Related stories: F48-S02
- Preconditions: rare-but-valid Hebrew token "קעורה" in plausible context.
- Input: token + context.
- Expected output: verdict="keep_original" (no false positive).
- Validation method: golden test seeded from UAT empirical run (4 false positives).
- Failure mode: precision target ≤ 1% FP violated.
- Priority: Critical

### FT-320: LLMReviewer applies REPLACE when chosen ∈ candidates ∧ chosen ∈ NakdanWordList
- Related stories: F48-S03
- Preconditions: Ollama reachable; Gemma 3 27B (or 4B) pulled; test mode uses recorded fixture LLM response.
- Input: ambiguous token + top-3 candidates + sentence.
- Expected output: verdict="apply" with correction applied; LLMReviewVerdict logged.
- Validation method: pytest with `LLMClient` fake returning canned JSON.
- Failure mode: parsing regression; cache-key drift.
- Priority: Critical

### FT-321: LLMReviewer rejects hallucination (chosen ∉ candidate set)
- Related stories: F48-S03
- Preconditions: fake LLM response proposes token NOT in candidates.
- Input: as above.
- Expected output: verdict="keep_original" + structured "anti_hallucination_reject" event logged.
- Validation method: log assertion + state assertion.
- Failure mode: precision target violated by hallucinations.
- Priority: Critical

### FT-322: LLMReviewer cache hit on second pass eliminates LLM calls
- Related stories: F48-S03
- Preconditions: prior run populated cache with verdict for `cache_key`.
- Input: same page, same model_id, same prompt_template_version.
- Expected output: 0 LLM calls; verdict reused.
- Validation method: instrument `LLMClient` call count.
- Failure mode: determinism / cost regression.
- Priority: High

### FT-323: corrections.json contains a row per corrected token with full reasoning trail
- Related stories: F48-S04
- Preconditions: page with 5 known errors.
- Input: full pipeline run.
- Expected output: 5 CorrectionLogEntry rows; each has stages, model_versions, prompt_template_version, ts_iso.
- Validation method: JSON schema validation + content assertion.
- Failure mode: audit gap; 100% reasoning-trail target violated.
- Priority: High

### FT-324: Pipeline tolerates corrections.json write failure
- Related stories: F48-S04
- Preconditions: tmp_path with 0 free bytes (mocked OSError on write).
- Input: full run.
- Expected output: pipeline completes; audit_gaps.json records the failure.
- Validation method: pytest with monkey-patched open().
- Failure mode: hard failure on disk-full breaks practice session.
- Priority: Medium

### FT-325: Aggregator emits suggestion only at ≥ 3 distinct shas with ≥ 1 sha each
- Related stories: F48-S05
- Preconditions: feedback.db seeded with N rows.
- Input: 3 distinct shas, each with 1 vote → expected: 1 suggestion, support=3.
- Input variant: 1 sha with 5 votes → expected: 0 suggestions (per-sha cap).
- Expected output: rule_suggestions.json content matches.
- Validation method: pytest table.
- Failure mode: spam-driven false promotion.
- Priority: High

### FT-326: Mode="no_llm" applies stricter threshold and skips LLM
- Related stories: F48-S06
- Preconditions: Ollama probe returns unreachable.
- Input: page run.
- Expected output: cascade_mode_degraded event; threshold_low=2.0 used; ambiguous verdicts default to keep_original; mode="no_llm" in every StageDecision.
- Validation method: log assertion + state assertion.
- Failure mode: silent fallback or pipeline abort.
- Priority: Critical

### FT-327: Mode="no_mlm" preserves deprecated _KNOWN_OCR_FIXES path
- Related stories: F48-S06
- Preconditions: DictaBERT load fails.
- Input: page with one F-2 confusion (e.g., "תגרוס").
- Expected output: correction applied via deprecated path; mode="no_mlm" recorded.
- Validation method: pytest with monkey-patched MLM init.
- Failure mode: degraded mode loses known fix coverage.
- Priority: High

### FT-328: Cascade is deterministic across two runs of the same input + model versions
- Related stories: F48-S02, F48-S03 (determinism non-functional)
- Preconditions: temperature=0, seed=0, full cache disabled.
- Input: fixture page, two runs.
- Expected output: identical corrections.json (modulo timestamp).
- Validation method: deep diff with timestamp masked.
- Failure mode: variance breaks reproducibility.
- Priority: Critical

### FT-329: Page-level latency budget — full mode median ≤ 1 s/sentence; p95 ≤ 5 s; full page ≤ 90 s
- Related stories: F48 quality requirements
- Preconditions: warm caches; Ollama up; small ambiguous-tokens fraction.
- Input: 50-sentence page.
- Expected output: median sentence cascade ≤ 1 s; p95 ≤ 5 s; full page ≤ 90 s.
- Validation method: `pytest-benchmark` (or similar) gate.
- Failure mode: SLO breach makes feature unusable for one-off PDFs.
- Priority: Critical

### FT-330: 100% of corrections have reasoning trail (auditability target)
- Related stories: F48-S04
- Preconditions: any non-degraded run.
- Input: any corrected-token output.
- Expected output: ratio = 1.0; CI hard gate.
- Validation method: ratio assertion in CI.
- Failure mode: silent skip of logging breaks UAT-derived hard rule.
- Priority: Critical

---

## Negative Tests
- **NT-01** Confusion-table YAML missing → cascade init raises typed `ConfusionTableMissing` error; pipeline aborts with explicit message (not a silent fallback).
- **NT-02** Ollama responds with non-JSON garbage → re-prompt once; on second failure, verdict="keep_original"; structured `llm_parse_failure` event.
- **NT-03** LLM proposes correction not in NakdanWordList → reject; `llm_word_list_violation` event.
- **NT-04** Empty token after normalization → cascade skips; emits `verdict="skip_empty"`.
- **NT-05** Sentence context > LLM context window → chunk to ±5 words; assert chunked prompt fits.

## Boundary Tests
- **BT-F-01** Page with 0 OCR errors → corrections.json is `[]`, exists.
- **BT-F-02** Page with 100% OCR errors → all tokens flow through full cascade; latency budget tested.
- **BT-F-03** Single-character token (Hebrew letter) → NakdanGate verdict="skip_short" or "pass" (design decision: `len < 2` skipped).
- **BT-F-04** Threshold exactly at boundary (delta=1.0 with `low=1.0`): inclusive on `low`, exclusive on `high`.
- **BT-F-05** Ollama call cap reached at the 11th ambiguous token in a page → 11+ tokens default to `keep_original`; structured `llm_call_cap_reached` event.

## Permission and Role Tests
- **PR-01** Pipeline engineer can override thresholds via config; no other persona can.
- **PR-02** Teacher-QA can mark wrong via F50; cannot edit confusion_pairs.yaml directly (separation of concerns).
- **PR-03** Student persona has no write path into feedback.db (read-only audio consumption).

## Integration Tests
- **INT-01** F14 → F48 — normalized text reaches cascade with wrap chars stripped.
- **INT-02** F48 → F19 (Nakdan) — corrected text is what gets diacritized, not original.
- **INT-03** F48 → F22 reading-plan / F23 SSML — corrected token IDs match `<mark>` IDs (no drift like UAT F-3).
- **INT-04** F48 ↔ F50 inspector — `corrections.json` schema matches inspector reader.
- **INT-05** F48 ↔ F47 feedback capture — feedback.db schema compatible.

## Audit and Traceability Tests
- **AUD-01** Every CorrectionLogEntry includes `model_versions` (NakdanGate version, MLM model id, LLM model id) and `prompt_template_version`.
- **AUD-02** `audit_gaps.json` is created when any logging fails; pipeline summary marks page accordingly.
- **AUD-03** Privacy assertion: outbound network calls during cascade resolve only to `127.0.0.1` (assert via socket monkey-patch).

## Regression Risks
- F-3 (marker drift): if F48 inserts/removes tokens, `<mark>` mapping breaks. **Mitigation**: cascade is 1:1 token-in / token-out; NEVER splits or merges tokens. INT-03 covers.
- F-2 (ם/ס deprecated path): if `_KNOWN_OCR_FIXES` removal happens before `mode="no_mlm"` ships, degraded mode loses coverage. **Mitigation**: deprecation only after FT-327 green for two release cycles.
- F-9 (wrap chars): F14 must run before F48; INT-01 enforces.

## Open Questions
- Cache eviction policy for LLM responses (LRU? size-bounded?). Defer to sw-pipeline.
- Whether to expose threshold knobs via CLI flags or YAML only — engineer story F48-S05 prefers YAML for reproducibility.
