# N02/F48 — Stage 2 DictaBERT-MLM Scorer User Stories

## Scope
For tokens that NakdanGate marked "suspect", DictaBERTMLMScorer generates char-substitution candidates from a confusion table and ranks by masked-LM probability. Source: ADR-033 §Decision step 2; UAT root cause for F-2 ם/ס class.

## Sibling Links
- Parent: `user_stories.md`
- Upstream: `user_stories.nakdan-gate.md`
- Downstream: `user_stories.llm-reviewer.md`

## Ontology Refs
- BC: `hebrew_text`
- BO50 `MLMSubstitutionCandidate`, BO51 `ConfusionPair`, BO52 `StageDecision`
- CO14 `DictaBERTMLMScorer`

## Dependency Refs
- Required from: F17 DictaBERT adapter (provides MLM head; or extension thereof).
- Required by: stage 3 LLMReviewer when MLM result is ambiguous (delta below threshold or multiple high-scoring candidates).

---

### Story F48-S02: Confusion-table candidate scoring with MLM probability

**As a** pipeline engineer
**I want** the cascade to generate single-character substitution candidates from a confusion table and rank them by masked-LM probability in context
**So that** new OCR confusion pairs (e.g., ב↔כ in handwritten scans) are caught with **zero code change** — the table covers them and MLM ranks them.

#### Context
UAT-2026-05-01-why-models-miss §1: DictaBERT-MLM scoring of `mask` candidates generalizes the hardcoded ם/ס fix list to ANY Tesseract confusion pair. Empirical: delta=1.0 caught 3/3 known errors but 4 false positives; delta=3.0 caught 1/3 with 0 false positives. F48 needs threshold + LLM tiebreaker to balance.

#### Preconditions
- NakdanGate verdict was `suspect` for this token.
- DictaBERT MLM head loaded (≤ 16 GB resident; ASM03).
- Confusion table loaded from `tirvi/normalize/confusion_pairs.yaml` (default: `ם↔ס, ן↔ו, ר↔ד, ה↔ח, ב↔כ, פ↔ף`).

#### Main Flow
1. Build candidate set: `{original} ∪ {original.replace(a,b) for (a,b) in confusion_pairs}`.
2. For each candidate, compute `mlm_score(c, sentence_context)`.
3. Sort descending; top = `c0`, runner-up = `c1`.
4. Compute `delta = score(c0) - score(c_original)`.
5. **Decision tree**:
   - `delta < threshold_low` (default 1.0) → `verdict="keep_original"`.
   - `threshold_low ≤ delta < threshold_high` (default 3.0) → `verdict="ambiguous"` → escalate to LLM.
   - `delta ≥ threshold_high` AND `c0 ∈ NakdanWordList` AND `score(c0) - score(c1) ≥ margin (default 0.5)` → `verdict="auto_apply"`.
   - Otherwise → `verdict="ambiguous"` → escalate.
6. Record `MLMSubstitutionCandidate` rows in `corrections.json`.

#### Alternative Flows
- Candidate set is empty (no confusion pairs match) → `verdict="keep_original"`.
- All candidates score below original → `verdict="keep_original"`.

#### Edge Cases
- Long word with multiple confusion sites — Cartesian explosion bounded by combinatorial cap (≤ 16 candidates); above cap, top-K masking strategy or only single-site swaps. Default: single-site only (per ADR-033 example).
- Same context, two different OCR runs → identical scores (cache by `(word, context_hash)`).
- Sentence context unavailable (heading-only block) → score with token-only context; widen threshold.

#### Acceptance Criteria
```gherkin
Given an OCR word "תגרוס" in context "האיוס תגרוס נזק כלכלי"
And the confusion table includes ם↔ס
When DictaBERTMLMScorer runs
Then the candidate set includes "תגרום"
And mlm_score("תגרום", context) > mlm_score("תגרוס", context) by ≥ 3.0
And the verdict is "auto_apply" with corrected="תגרום"
```

```gherkin
Given a valid uncommon Hebrew word "קעורה" misclassified as suspect
When DictaBERTMLMScorer scores it
Then no candidate beats the original by ≥ 1.0
And verdict="keep_original" (no false positive)
```

```gherkin
Given thresholds threshold_low=1.0, threshold_high=3.0, margin=0.5
And a token where delta=2.0 (between thresholds)
When MLM scorer runs
Then verdict="ambiguous"
And the token is forwarded to LLMReviewer with the top-3 candidates
```

#### Data and Business Objects
- `MLMSubstitutionCandidate(text, score, in_word_list)` — BO50.
- `ConfusionPair(a, b, source_writer="hebrew_print"|"hebrew_handwrite")` — BO51.

#### Dependencies
- F17 DictaBERT adapter (extended with MLM head).
- F19 Nakdan word list (validates `c0 ∈ NakdanWordList`).

#### Non-Functional Considerations
- Privacy: in-process; no network. Hard rule.
- Performance: ≤ 50 ms per token p50; ≤ 200 ms p95. Page-level: ≤ 5 candidates × 50 ms = 250 ms typical.
- Recall: contributes to ≥ 90% recall target with stage 3.
- Precision: ≤ 1% false-positive rate after stage 3 review.
- Determinism: deterministic given (token, context, model_version, confusion_table_version, thresholds).
- Auditability: every MLM score recorded.

#### Open Questions
- Should multi-site swaps be enabled for handwritten scans? Defer to feature-flag; default off (research §3).
- Threshold defaults verified on Wave-1 corpus only; tune per-cohort. Captured as engineer story §F48-S05 reuse.
