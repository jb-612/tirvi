# ADR-020: DictaBERT loaded in-process for POC; sidecar deferred to MVP

**Status:** Proposed

## Context

HLD §8 outlines a `models` sidecar that loads AlephBERT/YAP once and
exposes `/morph` and `/disambiguate`. POC has a single Python app and
synchronous pipeline (PLAN-POC.md). Biz corpus E04-F01 / S01 surfaces
the open question explicitly: load the model in-process or via sidecar.
A sidecar implies Compose / supervisord topology, port wiring, lifecycle,
and warm-up time the POC does not need to demonstrate.

## Decision

For POC, load `dicta-il/dictabert-large-joint` **in-process** at module
level on first call and cache. The adapter exposes the same
`NLPBackend` port surface either way; switching to a sidecar in MVP
swaps `tirvi.adapters.dictabert.loader.load_model` for a thin HTTP
client that talks to the sidecar — no upstream call sites change.

## Consequences

Positive:
- Single `python -m tirvi` runs the entire POC pipeline; no compose,
  no port wiring, no supervisord.
- Adapter contract test in F03 exercises the real model from a single
  process — easier to debug.
- Migration path is clear: only the loader implementation swaps.

Negative:
- Cold-start RAM cost (~1.5–2 GB for `large-joint`) is paid by the
  same process that runs OCR, normalization, TTS — laptop RAM matters.
- No process isolation: a bug in DictaBERT inference can crash the
  whole pipeline.

## Alternatives

- **Sidecar from day one (HLD §8 model server).** Rejected for POC:
  setup cost vs single-PDF demo value.
- **Lazy-load + unload between calls.** Rejected: load latency would
  dominate per-page cost; the demo should feel snappy.

## References

- HLD §5.2 — NLP-driven processing
- HLD §8 — Single-container dev environment (models sidecar pattern)
- ADR-002 — DictaBERT primary
- ADR-010 — Cloud Run CPU
- Biz corpus E04-F01 / S01 / Open Question
- Related: N02/F17 design.md DE-01
