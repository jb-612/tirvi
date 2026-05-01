# ADR-033 — Hebrew OCR/diacritization correction cascade (Nakdan + DictaBERT-MLM + Gemma reviewer)

**Status**: Proposed
**Bounded context**: hebrew-interpretation (N02), audio-delivery (N03)
**Owner**: tirvi pipeline orchestrator
**Date**: 2026-05-01

## Context

The POC pipeline reads exam PDFs aloud in Hebrew. Source: HLD §10 (NLP
chain), §12-OQ2 (TTS quality). UAT (`docs/UAT/UAT-2026-05-01-tts-quality.md`)
identified 9 distinct mispronunciation classes and `docs/UAT/UAT-2026-05-01-why-models-miss.md`
showed that hardcoding fix lists does not scale. Empirical run with
DictaBERT-MLM alone caught 3 known errors but introduced 4 false positives
(`לנבחן→לנבחו`, `שמימין→שמימיו`, `קעורה→קעודה`).

Three layers of capability are available:

| Layer | Strength | Limitation |
|---|---|---|
| Nakdan word-list (`fnotfromwl`) | Instant validity check | Many OCR errors land on real Hebrew words |
| DictaBERT-MLM | Catches lexical errors fast (~50ms/word) | Over-corrects valid uncommon words |
| LLM reasoning (Gemma 3 27B local via Ollama) | Reads MEANING, catches semantic drift | Slow (~1-2s/sentence), can hallucinate |

None alone is sufficient. The hardcoded ם/ס fix list (F-2 in UAT) would grow
unbounded as new exam corpora are added.

## Decision

Adopt a **three-stage cascade** for OCR/diacritization correction:

1. **Nakdan word-list filter** — drop "obviously valid" words (~98% pass).
2. **DictaBERT-MLM substitution** — for the 2% rejected by stage 1, generate
   single-character substitution candidates from a confusion table
   (`ם↔ס`, `ן↔ו`, `ר↔ד`, `ה↔ח`, etc.) and rank them by masked-LM probability
   in context.
3. **Gemma 3 reviewer** (Ollama, `gemma3:27b` or `:4b`) — for words still
   ambiguous after stage 2 (delta below threshold or multiple high-scoring
   candidates), prompt the LLM with the full sentence and the candidate set:
   "Is this Hebrew sentence semantically and grammatically valid? If not,
   which word should be replaced and why?" Use Gemma's verdict as the final
   gate.

Each stage caches its decision (`(word, context_hash) → result`) so steady-state
runs hit only changed text.

The hardcoded `_KNOWN_OCR_FIXES` table (`tirvi/normalize/ocr_corrections.py`)
becomes a deprecated fallback retained only for offline mode (no LLM available).

## Consequences

### Positive

- **Generalizes**: new OCR confusion pairs (e.g., ב↔כ in handwritten scans)
  require zero code change — DictaBERT's substitution table covers them and
  Gemma vets the result.
- **Auditable**: every correction has a Gemma reasoning trail saved to
  `corrections.log`. User can review and amend.
- **Self-improving via feedback loop** (per `docs/UAT/...why-models-miss.md`):
  reviewer notes feed back into a corrections sqlite which can fine-tune
  Phonikud (LoRA on M4 Max).
- **Cascade economics**: 98% of words skip the LLM. ~50 sentences/page
  × 1.5s/sentence ≈ 60s pipeline overhead — acceptable for one-off
  PDF processing.

### Negative

- **Latency**: full pipeline grows from ~30s to ~90s per page in worst case.
  Mitigated by aggressive caching and stage-1 filtering.
- **Local-LLM dependency**: requires Ollama + `gemma3:27b` (or `:4b`) pulled.
  Offline mode falls back to hardcoded list (degraded but functional).
- **Determinism**: LLM output isn't strictly deterministic. Cache key
  includes prompt + model + temperature=0; further variance acceptable.
- **Hallucination risk**: Gemma could "improve" already-correct text.
  Mitigated by a strict prompt that asks for `"OK"` when no change needed
  and rejects suggestions where the candidate isn't in Nakdan's word list.

## Alternatives considered

1. **Keep hardcoded list, grow it manually** — rejected. Doesn't scale,
   relies on human enumeration.
2. **DictaBERT-MLM alone with high threshold** — tried (delta=3.0 + Nakdan
   gate). Caught 1/3 known errors, 0 false positives. Too conservative.
3. **DictaBERT-MLM alone with low threshold** — tried (delta=1.0). Caught
   3/3 known errors but 4 false positives. Too aggressive.
4. **Train a custom Hebrew OCR-correction model on synthetic data** — viable
   long-term (LoRA fine-tune on M4 Max) but defers signal we already have
   from off-the-shelf DictaBERT + Gemma.
5. **Cloud LLM (gpt-4o-mini)** — works but introduces cost ($0.001/page),
   network dependency, privacy concern (exam content). Local Gemma keeps
   everything on-device.

## References

- `docs/UAT/UAT-2026-05-01-tts-quality.md` — symptom catalogue
- `docs/UAT/UAT-2026-05-01-why-models-miss.md` — root cause analysis
- ADR-026 (DictaBERT-morph reroute), ADR-027 (AlephBERT+YAP fallback),
  ADR-028 (Phonikud G2P), ADR-029 (vendor boundary)
