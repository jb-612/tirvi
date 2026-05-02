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

## Exit criteria

- Diacritization word-level accuracy ≥ 85% on tirvi-bench v0
- Homograph correct-pronunciation rate ≥ 85%
- Acronym expansion coverage ≥ 95% on the curated 200-item list
- `plan.json` validates against schema for every block type

## ADRs gated here

- ADR-002 NLP backbone (DictaBERT-large-joint primary, AlephBERT fallback)
- ADR-003 Diacritization + G2P (Dicta-Nakdan + Phonikud)
