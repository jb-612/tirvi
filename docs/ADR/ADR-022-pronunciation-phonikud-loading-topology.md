# ADR-022: Phonikud loaded in-process for POC; matching ADR-020/021 pattern

**Status:** Proposed

## Context

ADR-020 (DictaBERT) and ADR-021 (Nakdan) committed to in-process model
loading for POC. Phonikud is the third adapter in the per-feature
loader chain. Keeping the same pattern means a single Python process
warms three model surfaces at startup; switching any of them to a
sidecar is a one-file change behind the existing port.

## Decision

POC loads Phonikud **in-process** at module level on first call and
caches via `lru_cache`. Lazy import (`import phonikud` deferred to
loader call) so unit tests that exercise the fake adapter do not
require Phonikud to be installed.

## Consequences

Positive:
- One pattern across F17, F19, F20 — easier mental model + uniform
  warm-up sequencing for `make warm` (deferred).
- Tests can swap the loader with the fake from F03's fake registry
  without process boundaries.

Negative:
- Adds Phonikud import + initialization latency on cold start; the
  three loaders now serialize on first invocation.
- No process isolation; same pipe-share-RAM caveat as ADR-020/021.

## Alternatives

- **Skip Phonikud, use a rule-based G2P only.** Rejected: drops the
  primary product moat (natural prosody from Phonikud's stress + IPA);
  rule-based is the deferred fallback per F20 design.
- **Phonikud sidecar service from day one.** Rejected: same reasoning
  as ADR-020 — extra moving part with no demo benefit.

## References

- HLD §5.2 — NLP-driven processing
- ADR-003 — Diacritization + G2P stack
- ADR-020 — DictaBERT loaded in-process for POC
- ADR-021 — Dicta-Nakdan loaded in-process for POC
- Biz corpus E05-F02 / S01
- Related: N02/F20 design.md DE-01
