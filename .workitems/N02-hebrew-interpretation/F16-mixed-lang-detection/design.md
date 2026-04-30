---
feature_id: N02/F16
feature_type: domain
status: drafting
hld_refs:
  - HLD-§5.1/Input
  - HLD-§5.2/Processing
prd_refs:
  - "PRD §6.3 — Reading aloud / language switching"
adr_refs: [ADR-019, ADR-029, ADR-031]
biz_corpus: true
biz_corpus_e_id: E03-F04
---

# Feature: Mixed-Language Run Detection (Hebrew / English / Numeric)

## Overview

Pure-Python module that scans normalized Hebrew text and emits
`LanguageSpan[]` (start, end, lang, confidence) so downstream stages can
route per-span TTS pronunciation. POC scope is **deterministic**:
Unicode-script classification + curated heuristics (single-letter Latin
→ transliteration, multi-Latin runs → English, digit/operator runs →
`num`). The detector owns no voice routing — F24 (Wave 3) consumes the
spans and decides Azure inline `<lang>` vs Google split-and-stitch. F16
also resolves the biz Open Question on math/lang overlap by collapsing
math symbols into `num` (ADR-031); per-character math segmentation
defers to F25. Pure-Hebrew demo input emits one `he` span — fast no-op.

## Dependencies

- Upstream: N02/F14 `NormalizedText` (text + bbox spans, pass-through).
- Adapter ports consumed: none. F16 introduces no new port.
- External services: none.
- Sibling: F15 (acronym lexicon) — runs **before** F16 so `ד״ר →
  דוקטור` arrives as Hebrew, not Latin.
- Downstream: F22 (copies `lang_spans` into per-block plan JSON);
  F24 lang-switch-policy Wave 3 (consumes `LanguageSpansResult`, owns
  voice routing per biz US-02 — **do not edit F24's workitem from
  this feature**); F25 content-templates Wave 3 (owns full math
  expression rendering; F16 emits coarse `num` only).
- Biz `bo:LanguageSpan` (start, end, lang, confidence) reused unchanged.

## Interfaces

| Module | Symbol | Kind |
|--------|--------|------|
| `tirvi.lang_spans` | `detect_language_spans(text) -> LanguageSpansResult` | function (pure) |
| `tirvi.lang_spans.classify` | `classify_char(c) -> Script` | function |
| `tirvi.lang_spans.aggregate` | `aggregate_runs(tags, text) -> list[LanguageSpan]` | function |
| `tirvi.lang_spans.heuristics` | `apply_transliteration_rule / apply_hyphen_bridge_rule / apply_num_unification` | functions |
| `tirvi.lang_spans.results` | `LanguageSpansResult` | frozen dataclass |

`LanguageSpan.lang ∈ {he, en, num}` — biz `math` literal folded into
`num` (ADR-031). `LanguageSpansResult.provider = "tirvi-rules-v1"`.
Span tuple sorted by `start`; deterministic.

## Approach

1. **DE-01 unicodeScriptClassifier.** Per-codepoint map: Hebrew block
   (U+0590–U+05FF, U+FB1D–U+FB4F) → `HE`; Latin Basic / Latin-1 letter
   → `LATIN`; ASCII or Arabic-Indic digit → `DIGIT`; math operators
   `+−×÷=%` and decimal punctuation `.,` → `SYMBOL`; whitespace →
   `WS`; other → `OTHER` (treated as `WS` boundary).
2. **DE-02 runLengthAggregation.** Walk tag stream, collapse same-tag
   chars into raw `(start, end, tag)` runs. `WS` runs absorbed into
   the previous lang span so `"ערך p-value"` is not split by spaces.
3. **DE-03 transliterationHeuristic.** Single-char `LATIN` run flanked
   by `HE` (same word boundary) reclassifies to `he`. Biz US-01 edge.
4. **DE-04 hyphenBridgeRule.** `LATIN`-`SYMBOL`(hyphen)-`LATIN` with
   no internal whitespace merges into one `en` span (e.g. `p-value`).
5. **DE-05 numMathChannelUnification.** Adjacent `DIGIT` and `SYMBOL`
   runs merge into one `num` span. Resolves biz Open Question per
   ADR-031.
6. **DE-06 languageSpansResultEmission.** Frozen dataclass tagged
   `provider="tirvi-rules-v1"`. Span `confidence` = 1.0 for pure
   single-block hits; 0.85 when DE-03/DE-04 reclassified; aggregate =
   min over spans.
7. **DE-07 pipelinePlacementAndDownstream.** Runs after F14 and
   **before** F17 so NLP sees lang-tagged text and skips Latin spans
   during morph. F22 copies `lang_spans` additively to plan JSON.

## Design Elements

- DE-01: unicodeScriptClassifier (ref: HLD-§5.1/Input)
- DE-02: runLengthAggregation (ref: HLD-§5.1/Input)
- DE-03: transliterationHeuristic (ref: HLD-§5.2/Processing)
- DE-04: hyphenBridgeRule (ref: HLD-§5.2/Processing)
- DE-05: numMathChannelUnification (ref: HLD-§5.2/Processing)
- DE-06: languageSpansResultEmission (ref: HLD-§5.1/Input)
- DE-07: pipelinePlacementAndDownstream (ref: HLD-§5.2/Processing)

## Decisions

- D-01: Rule-based Unicode + heuristics; ML deferred MVP → **ADR-031**.
- D-02: math/lang unified into `num`; F25 owns math read-aloud →
  **ADR-031**.
- D-03: No vendor; stdlib-only surface → **ADR-029** (existing).
- D-04: Mirrors F14 deterministic rule-registry precedent →
  **ADR-019** (existing).
- D-05: No new port; future ML detector can hide behind a future
  `LanguageDetectorBackend` at MVP — captured in DE-07.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| HLD §5.1 lists language spans inside norm.json metadata | Emit as separate `LanguageSpansResult` | Keeps F14 single-purpose; F22 merges in plan JSON |
| Biz BO16 + HLD §5.1 list `math` as a separate channel (`{he, en, math, num}`) | POC unifies math → `num` (3-channel `{he, en, num}`) | ADR-031: per-character math segmentation belongs to F25; F16 emits coarse `num` for digits + math symbols. F16 is the **first** code realisation of `LanguageSpan`, so this is initial typing, not a schema narrowing — ADR-014 contract-test machinery does not apply (no port, no adapter). |
| Biz US-02 split-and-stitch | Out of F16 scope | F24 owns voice routing |

## HLD Open Questions

- math/lang overlap → resolved unified by ADR-031.
- "lang tag warning" for QA → deferred to F24.

## Risks

| Risk | Mitigation |
|------|-----------|
| Single-Latin over-reclassified to `he` | DE-03 conservative (HE both sides AND len 1); F39 bench |
| Acronym (`PCR`) misclassified | DE-02 default already correct (multi-Latin → `en`) |
| Math read as flat number string | F25 templates own rendering; F16 emits `num` |
| Brand-name false positives | Override hook deferred MVP (mirrors F21) |
| `p-value` mis-split | DE-04 explicit; FT-112 fixture |

## Diagrams

- `docs/diagrams/N02/F16/lang-spans-detector.mmd`

## Out of Scope

- Voice routing (Azure inline vs Google split-stitch) — F24.
- Math expression read-aloud — F25.
- ML language identifier — MVP per ADR-031; future
  `LanguageDetectorBackend` port.
- Override lexicon (brand names) — deferred MVP.
- Word-level accuracy bench — N05 / F39.
