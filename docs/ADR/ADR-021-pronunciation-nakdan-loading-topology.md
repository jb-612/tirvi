# ADR-021: Dicta-Nakdan loaded in-process for POC; API path deferred

**Status:** Proposed

## Context

Biz corpus E05-F01 / S01 surfaces an open question: cloud-hosted
Dicta-Nakdan API vs locally-loaded model. POC ships a single-process
synchronous demo (PLAN-POC.md). API integration brings auth, retry,
network privacy minimization, and rate limits — none of which the demo
needs. ADR-003 already selects Nakdan + Phonikud as the diacritization
stack; ADR-020 set the precedent for in-process model loading. This
ADR makes the same call for Nakdan.

## Decision

POC loads Nakdan **in-process** at module level on first call, cached
through the same `functools.lru_cache` pattern as DictaBERT (ADR-020).
Hosted API path is deferred to MVP and lives behind the same
`DiacritizerBackend` port — adopting it later swaps the loader, not
the call sites.

## Consequences

Positive:
- Zero auth / network setup; the demo runs offline once weights are
  warm.
- Determinism for unit tests (no flaky network).
- Consistent with F17 model-loader pattern.

Negative:
- Adds Nakdan model RAM on top of DictaBERT in the same process —
  laptops with < 8 GB free RAM will struggle.
- No network-side privacy considerations to validate the BT-099
  minimization pattern; deferred to MVP.

## Alternatives

- **Hosted Dicta-Nakdan API.** Rejected for POC: privacy minimization,
  retry policy, and rate-limit handling are MVP work, not demo work.
- **Subprocess Nakdan worker.** Rejected: extra moving part with no
  measurable POC benefit.

## References

- HLD §5.2 — NLP-driven processing (lexicon + heuristics + Nakdan)
- ADR-003 — Diacritization + G2P stack (Nakdan + Phonikud)
- ADR-020 — DictaBERT loaded in-process for POC
- Biz corpus E05-F01 / S01 / Open Question
- Related: N02/F19 design.md DE-01
