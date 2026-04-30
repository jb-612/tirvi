# ADR-031: F16 mixed-language detection — rule-based unicode + unified lang/math channel

**Status:** Proposed

## Context

Biz corpus E03-F04 specifies a per-span language tag (`he | en | math
| num`) so that downstream TTS can route to the right voice (Azure
inline `<lang>` or Google split-and-stitch — see biz US-01 / US-02).
Two questions need an architectural answer:

1. **Detector strategy.** Should F16 use a learned language identifier
   (e.g., fastText `lid.176`, CLD3) or a deterministic rule set over
   Unicode script blocks?
2. **Math vs lang channel.** Biz raises an Open Question: "Math span
   overlap with `lang_spans` — separate channel or unified?" — i.e.,
   should `lang="math"` ride alongside `lang ∈ {he, en, num}`, or roll
   into one channel?

POC scope is the single Economy.pdf p.1 (per `.workitems/POC-CRITICAL-
PATH.md`), which is pure Hebrew — no English, no math. F16 is **not**
demo-critical; tasks land at MVP. Constraints: no labelled corpus, no
GPU budget for langid inference, no nightly bench. F25 (content
templates, Wave 3) already owns full math expression read-aloud
rendering. HLD §5.1 lists "language spans" as norm.json metadata but
does not constrain detector implementation.

ADR-019 set the precedent: "Normalization uses deterministic rules for
POC; ML repair deferred." F16 mirrors that pattern. ADR-029 codifies
the vendor-boundary rule; F16 has no vendor (stdlib only) and stays
inside its own module.

## Decision

Adopt a **deterministic Unicode-script + curated heuristics** strategy
for POC, exposed as the pure-Python `tirvi.lang_spans` module. The
detector emits `LanguageSpansResult.spans: tuple[LanguageSpan, ...]`
where `LanguageSpan.lang ∈ {he, en, num}` — **not** `{he, en, math,
num}`. Math symbols (`+−×÷=%`) and decimal punctuation (`.,`) collapse
into the `num` channel together with digits. F25 owns full math
expression rendering and consumes the coarse `num` spans.

ML-based language identification (fastText, CLD3, or similar) is
**deferred to MVP**. When it lands, it will hide behind a future
`LanguageDetectorBackend` port so callers keep the same interface.

Per-character math segmentation (separate channel for math symbols,
per-symbol read-aloud rules) is **deferred to F25** at MVP.

## Consequences

Positive:
- Zero training data, zero inference cost. Pipeline budget stays
  unaffected.
- Pure stdlib; no new vendor under ADR-029 boundary discipline.
- Deterministic — same input → same output, content-hash-friendly for
  the drafts cache.
- Resolves biz Open Question with a single channel; simpler downstream
  schema for F22 / F24.
- F25 keeps its math-template ownership intact.

Negative:
- Limited recall on edge cases: brand names with mixed transliteration,
  multilingual quotes embedded in Hebrew, etc. Mitigation: F39 (N05)
  bench measures the gap; override lexicon (mirrors F21 pattern)
  available at MVP.
- Coarse `num` channel: F25 must inspect span text to distinguish
  "0.05" (read as a decimal) from "0+5" (read as an expression). F25's
  template-matching machinery handles this; F16 stays simple.
- Single Latin transliteration heuristic (DE-03) may over-fire on
  legitimate single-letter English (e.g., a math variable `x` inside
  Hebrew). Mitigation: predicate is conservative (HE flank both sides
  AND `len == 1`); bench validates.

## Alternatives

- **fastText `lid.176` (or CLD3) langid.** Rejected for POC: ~140 MB
  model + cold-start cost + per-call inference latency, with no
  measured win on the demo PDF (which is pure Hebrew). Becomes
  attractive when bench shows residual error worth modelling.
- **Per-character math channel.** Rejected: doubles the schema,
  requires F22 + F24 to handle two overlapping span streams, and F25
  already owns expression rendering. Coarse `num` is the simplest
  signal that lets F25 do its job.
- **Lean on F17 (DictaBERT).** Rejected: NLP runs **after** F16 by
  design (DE-07) so morph analysis can skip Latin runs. Reversing the
  order would force NLP to pay morph cost on English / numeric tokens
  it cannot meaningfully analyse.

## References

- HLD §5.1 — Reading-plan input (norm.json language spans)
- HLD §5.2 — Reading-plan processing (`xml:lang` switch step)
- Biz corpus E03-F04 / S01 / Open Question on math/lang overlap
- Composes with: ADR-019 (rule-strategy precedent), ADR-029
  (vendor-boundary discipline)
- Related: N02/F16 design.md DE-01 / DE-05 / DE-06 / DE-07; downstream
  F22, F24 (Wave 3), F25 (Wave 3)
