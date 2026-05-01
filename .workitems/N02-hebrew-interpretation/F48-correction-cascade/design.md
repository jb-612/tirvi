---
feature_id: N02/F48
feature_type: domain
status: designed
hld_refs: [HLD-§4, HLD-§5.2, HLD-§10]
prd_refs:
  - "PRD §6.4 — Reading plan"
  - "PRD §7.1 — Accommodation quality"
  - "PRD §9 — Privacy"
adr_refs: [ADR-019, ADR-026, ADR-029, ADR-033, ADR-034, ADR-035]
biz_corpus: true
biz_corpus_e_id: F48-correction-cascade
wave: 3
---

# Feature: N02/F48 — Hebrew correction cascade

## Overview

Three-stage cascade — NakdanGate → DictaBERT-MLM scorer → local Gemma reviewer —
that silently corrects OCR errors before F19 diacritization. The hardcoded
`tirvi/normalize/ocr_corrections.py::_KNOWN_OCR_FIXES` is formally **deprecated**
and retained only for the `no_mlm` / `emergency_fixes` degraded modes (FT-327).
All processing is on-device (privacy hard rule, ADR-033). The cascade emits a
per-token reasoning trail consumed by F50 inspector, plus a feedback loop
(sqlite-backed) that **suggests — never auto-applies** confusion-pair promotions
once a correction recurs across ≥ 3 distinct shas.

Package: `tirvi/correction/`. Invoked between F14 normalization (DEP-057) and
F19 Dicta-Nakdan (DEP-052). Model identifiers used here are the ones in the
user's local Ollama: `gemma4:31b-nvfp4` (primary, 20 GB) and `llama3.1:8b`
(optional fast tier). Biz mentioned `gemma3:27b`; corrected here.

## Design Elements

### DE-01: `ICascadeStage` port + `CorrectionVerdict` value object (HLD-§4)
Single-method port `evaluate(token, context) -> CorrectionVerdict`. `CorrectionVerdict`
is a frozen dataclass `(stage, verdict, original, corrected_or_none, score?,
candidates?, mode, cache_hit, reason?, model_versions?)`. Verdict enum
`{pass, suspect, keep_original, ambiguous, auto_apply, apply, skip_empty,
skip_short, skip_non_hebrew}`. No vendor types (ADR-029).

### DE-02: `NakdanGate` — first-stage word-list filter (HLD-§5.2)
`tirvi.correction.NakdanGate` realizes `ICascadeStage` over an injected
`NakdanWordListPort.is_known_word(token)` (CO13). In-memory; ≤ 5 ms p95
(FT-317). `pass` short-circuits; `suspect` forwards to DE-03. Skips:
empty/`len<2`/digit/Latin → `skip_*`. Cache `(token, word_list_version)`.

### DE-03: `DictaBertMLMScorer` — confusion-table + masked-LM ranker (HLD-§5.2, ADR-026)
Loads data-driven `tirvi/correction/confusion_pairs.yaml` (BO51; defaults
`ם↔ס, ן↔ו, ר↔ד, ה↔ח, ב↔כ, פ↔ף`). For each suspect: build single-site
candidates, score under DictaBERT-MLM (`dicta-il/dictabert`),
`delta = score(c0) - score(original)`. Decision tree (defaults
`low=1.0, high=3.0, margin=0.5`): `<low → keep_original`;
`[low,high) → ambiguous`; `≥high ∧ c0∈WordList ∧ score(c0)-score(c1)≥margin
→ auto_apply`; else `ambiguous`. Single-site only (POC). Cache
`(token, sentence_context_hash, mlm_model_id, table_version)`.

### DE-04: `OllamaLLMReviewer` — local Gemma reviewer with anti-hallucination guard (HLD-§5.2, ADR-033)
POSTs to `http://127.0.0.1:11434/api/generate`; AUD-03 asserts no
non-localhost outbound. Default model `gemma4:31b-nvfp4`; fast tier
`llama3.1:8b`. `temperature=0`, `seed=0`. Prompt at
`tirvi/correction/prompts/he_reviewer/v1.txt` (BO54). Parses
`{verdict: "OK"|"REPLACE", chosen, reason}`; rejects `chosen ∉ candidates`
or `chosen ∉ NakdanWordList` (anti-hallucination). One re-prompt on
parse failure; second failure → `keep_original`. Per-page LLM-call cap
(default 10; BT-F-05). HTTP behind `LLMClientPort`. **D-01 + ADR-034
cache key**: `sha256(model_id || prompt_template_version || sentence_hash
|| sorted(candidates))`.

### DE-05: `CorrectionCascadeService` — orchestrator + per-page aggregate (HLD-§5.2)
`run_page(tokens, sentences) -> PageCorrections`. Holds the transient
`CorrectionCascade` aggregate (BO49). Conditionally walks DE-02 → 03 → 04.
Emits `CorrectionApplied` (BO57), `CorrectionRejected` (BO58),
`CascadeModeDegraded` (BO59). Token-in/token-out invariant — never splits
or merges (DEP-052/053; INT-03).

### DE-06: `CorrectionLog` — auditable reasoning trail writer (HLD-§5.2)
Writes `drafts/<sha>/corrections.json` with `corrections_schema_version: 1`.
Rows are `CorrectionLogEntry` (BO55) with stages, model_versions,
prompt_template_version, ts_iso, cache_hit_chain, page_index,
sentence_hash. Pass-through NOT logged unless `--log-passthrough`.
Disk-full → `drafts/<sha>/audit_gaps.json` + page marked
audit-incomplete (FT-324). **D-02 + ADR-035**: single JSON array per
page; chunked `corrections.<page>.json` when document > 50 pages.

### DE-07: `HealthProbe` + degraded-mode policy (HLD-§10)
Init-time probe: Ollama `GET /api/tags` (≤ 1 s) + DictaBERT load.
Mode fixed per-page (BT-213 alt). Modes: `full | no_llm | no_mlm |
emergency_fixes | bypass`. `no_llm`: `threshold_low=2.0`, ambiguous →
`keep_original` (FT-326). `no_mlm`: NakdanGate + deprecated
`_KNOWN_OCR_FIXES` (FT-327). Mode written to every `StageDecision` and
page header; emits `cascade_mode_degraded` event for F50 banner.

### DE-08: `FeedbackAggregator` — threshold-gated rule promotion suggestions (HLD-§5.4)
Reads `drafts/feedback.db` (sqlite — schema-compat extension of F47's
BO46 `FeedbackEntry`: adds `system_chose`, `expected`, `persona_role`,
`sentence_context_hash`). Cascade also reads at init to revert
user-rejected corrections (BT-211). Aggregator groups by
`(ocr_word, expected)`; emits `RuleSuggestion` (BO56) with
`support_count`, `distinct_shas`. **Per-sha cap = 1** (anti-spam,
FT-325 second variant, BT-220). Threshold ≥ 3 distinct shas. Output
`drafts/rule_suggestions.json`. Engineer-gated; never auto-applies.

## Decisions

- **D-01 → ADR-034**: LLM reviewer prompt template + cache-key strategy.
- **D-02 → ADR-035**: `corrections.json` schema (versioned) + chunking policy.
- **D-FAST-TIER-AB** *(deferred)*: A/B `llama3.1:8b` vs `gemma4:31b-nvfp4`.
- **D-AUTO-PROMOTE-POLICY** *(deferred)*: auto-promote threshold for very high support.
- **D-LOG-INTEGRITY** *(deferred)*: signature on `corrections.json` to detect tampering.

## DDD-7L Recommendation

Recommend `@ddd-7l-scaffold` after User Gate. F48 has clean DDD shape:
`hebrew_text` BC re-entry, transient aggregate `CorrectionCascade`, value
objects (BO50–BO56), domain events (BO57–BO59), explicit policies
(thresholds, anti-hallucination, per-sha cap), 3 ports (`ICascadeStage`,
`NakdanWordListPort`, `LLMClientPort`).
