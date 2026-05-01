# Design Review R2 — Adversary Challenge — N04/F38 WCAG Conformance

**Feature:** N04/F38 — WCAG 2.1 AA conformance audit (deferred MVP)
**Round:** R2 adversary challenge + synthesis
**Date:** 2026-05-01
**Status:** R2 complete — approved

---

## Adversary Position

The adversary accepts the deferred stub classification. One adversary probe:

**Probe:** F38 is classified as a `ui` feature, but it is more accurately
a quality-gate process: it produces no shipping code, only a violation
report and remediation tasks. Classifying it as `ui` may cause the ACM
graph to mislead consumers (e.g., the graph shows F38 as a UI module when
it is really a testing/audit workflow). A more accurate `feature_type` might
be `integration` or a new type `quality-gate`.

**Synthesis:** The adversary's concern is valid at a modeling level. However
changing `feature_type` would require an ontology schema change — a
protected-path operation. For the deferred MVP stub, `ui` is acceptable as
a placeholder (the remediation tasks will touch UI files). The MVP designer
should consider proposing a `quality-gate` feature type via ADR when
scheduling F38. Flagged as a Low informational note; no revision needed
to the stub.

---

## R2 Synthesis Verdict

**Approved.** F38 stub design is well-formed. The `feature_type: ui`
placeholder is acceptable for the deferred stub; the MVP designer should
revisit the type classification when scheduling. Activate via
`@design-pipeline` after all upstream player features are complete.
