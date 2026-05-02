# N02 — Hebrew Interpretation — THE MOAT

**Window:** weeks 4–8 · **Features:** 12 · **Type:** domain (defensible layer)

This is the layer that makes tirvi defensible. Hebrew morphology, contextual
disambiguation, diacritization, G2P, and exam-shaped reading plans. The
academic framing is *"context-aware Hebrew reading through morphological
disambiguation, pronunciation prediction, and exam-domain adaptation"* —
matches the engineering one and the Bar-Ilan ONLP / Dicta / HUJI line of
research.

## Features

- **F14-normalization-pass** — repair OCR artifacts, `num2words` Hebrew, dates / percentages / ranges
- **F15-acronym-lexicon** — curated lexicon (Otzar Roshei Tevot + Dicta), expansion at norm time
- **F16-mixed-lang-detection** — Hebrew / English / math span detection, per-span lang tags
- **F17-dictabert-adapter** — `dicta-il/dictabert-large-joint` (segmentation, morph, lemma, dependency, NER)
- **F18-disambiguation** — context-driven homograph resolution + confidence
- **F19-dicta-nakdan** — diacritization adapter
- **F20-phonikud-g2p** — IPA + stress + vocal-shva G2P
- **F21-homograph-overrides** — curated override lexicon for top 500 exam homographs
- **F22-reading-plan-output** — block-typed `plan.json`
- **F23-ssml-shaping** — breaks between answers, emphasis on question numbers, per-word marks
- **F24-lang-switch-policy** — Azure inline `<lang xml:lang="en-US">` for English spans
- **F25-content-templates** — math reading template + table reading template
- **F51-homograph-context-rules** — sentence-context rule layer between Nakdan and the LLM reviewer (sibling of F21; ships possessive-mappiq rule + Gemma harness prompt; per ADR-038)
- **F52-block-kind-taxonomy** *(Phase 0 reading-accommodation)* — extend F11 segmenter with `instruction / question_stem / datum / answer_blank / multi_choice_options` block kinds; per ADR-041
- **F53-clause-split-ssml-chunker** *(Phase 0 reading-accommodation)* — F23-resident chunker that inserts `<break time="500ms"/>` SSML breaks at safe boundaries when a sentence > 22 words; per ADR-041

## Exit criteria

- Diacritization word-level accuracy ≥ 85% on tirvi-bench v0
- Homograph correct-pronunciation rate ≥ 85%
- Acronym expansion coverage ≥ 95% on the curated 200-item list
- `plan.json` validates against schema for every block type

## ADRs gated here

- ADR-002 NLP backbone (DictaBERT-large-joint primary, AlephBERT fallback)
- ADR-003 Diacritization + G2P (Dicta-Nakdan + Phonikud)

## Deferred follow-ups (opened, not yet scheduled)

- [Issue #27](https://github.com/jb-612/tirvi/issues/27) — fix dormant
  DictaBERT→Nakdan integration (`_pick_in_context` morph-options gating
  is unreachable under current Dicta REST option shape; per
  ADR-038 §Finding 1). Independent of F51. Needs an ADR-039 to choose
  between (A) request morph-bearing Dicta response shape and
  (B) string-level POS scoring on candidate options.
- [Issue #28](https://github.com/jb-612/tirvi/issues/28) — ambiguity
  flagging in `corrections.json` for genuinely two-valued sentences
  like UAT-2026-05-02 §S1. Refines ADR-035 schema with
  `verdict: "ambiguous"`. Reviewed UI (F50) is the downstream consumer.
