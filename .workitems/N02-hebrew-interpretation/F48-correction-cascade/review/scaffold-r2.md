# Scaffold Review — Gate 2 (L3 Domain Model) ★ MOST IMPORTANT

**Verdict**: PASS

## Scope
- Layer: L3 (domain).
- Files: `tirvi/correction/domain/{cascade,events,policies}.py`,
  `tirvi/correction/errors.py` (4).

## Aggregate boundary check

`CorrectionCascade` is the only aggregate root for the bounded context
`hebrew_correction`. Boundary verified:

- **Transient per-page** (biz F48-R1-3) — instance lifetime ⊆ a single
  page run; no caching across pages. State held: `_mode`,
  `_stage_decisions`, `_applied`/`_rejected`/`_mode_events`/`_cap_events`,
  `_llm_calls_made`, `_llm_cap`. All accumulators, all reset by GC at
  end of `run_page`.
- **Identity = (page_index, sha)** — sufficient since cascades never
  outlive a page.
- **Mutator surface kept tight** — `lock_mode`, `record_decision`,
  `configure_llm_cap`, `note_llm_call`, `drain_events`. No getter
  surface beyond what F50 inspector + log writer need.
- **No external repository required** — aggregate is transient and
  emits events plus drains via `drain_events()`. Persistence is in
  `CorrectionLog` (DE-06), not in the aggregate. Correctly avoided
  the "repository for transient aggregate" anti-pattern.

## Invariant placement check

| INV | Location | Notes |
|-----|----------|-------|
| INV-CCS-001 (token-in/out) | `TokenInTokenOutPolicy` invoked by `record_decision` | DE-05 owns it; service calls policy before append. |
| INV-CCS-002 (anti-hallucination) | `AntiHallucinationPolicy` (uses `NakdanWordListPort`) | DE-04 owns it; LLM reviewer calls policy. Single source of word-list truth. |
| INV-CCS-003 (every applied → log entry) | enforced at service boundary in DE-06 (`log.py`) | Aggregate emits events; log writer asserts cardinality match. Documented in `CorrectionCascade` docstring. |
| INV-CCS-004 (privacy / localhost-only) | enforced at adapter + integration test (T-10) | Not a domain invariant — networking concern. Correctly placed outside domain. |
| INV-CCS-005 (mode fixed per page) | `PerPageModeFixedPolicy` + `lock_mode` aggregate method | T-07 fills. |
| INV-CCS-006 (per-sha cap = 1) | `PerShaContributionCapPolicy` (DE-08) | T-08 fills; covers BT-220. |

All six invariants from `traceability.yaml` are placed; none orphaned.

## Domain events check

5 events scaffolded, mapped 1:1 to ontology BO IDs + AC trail:

| Event | BO | AC | Emitted by |
|-------|----|----|------------|
| `CorrectionApplied` | BO57 | F48-S02/AC-03, F48-S03/AC-01 | `CorrectionCascade.record_decision` (verdict ∈ {auto_apply, apply}) |
| `CorrectionRejected` | BO58 | F48-S03/AC-03, F48-S04/AC-02 | `CorrectionCascade.record_decision` (NT-02/NT-03/BT-211) |
| `CascadeModeDegraded` | BO59 | F48-S06/AC-01..04 | `CorrectionCascade.lock_mode` (mode ≠ "full") |
| `LLMCallCapReached` | (BT-F-05) | F48-S03/AC-02 | `CorrectionCascade.note_llm_call` |
| `RulePromoted` | (BO56 surface) | F48-S05/AC-03 | `FeedbackAggregator.run` (DE-08, separate from cascade) |

Events are frozen dataclasses. `RulePromoted` lives outside the
aggregate's emitter set (DE-08 is its own bounded sub-context); kept
in the same module for DDD locality. Acceptable for a small feature.

## Anti-pattern checks (clean)

- ✅ No infrastructure imports under `tirvi/correction/domain/`.
- ✅ No vendor types in port signatures (ADR-029).
- ✅ Value objects are frozen dataclasses; primitive obsession avoided
  (`CorrectionVerdictName` Literal, `CascadeMode` VO).
- ✅ Every method body is `raise NotImplementedError(...)` with AC + T-NN
  in the message — TDD agent gets the right hint.
- ✅ Events carry `occurred_at` for audit ordering.
- ✅ Policies are stateless (frozen dataclasses with refs only) —
  testable in isolation.

## Findings
None blocking. The L3 model accurately reflects the design. Proceeding
to L4/L5.
