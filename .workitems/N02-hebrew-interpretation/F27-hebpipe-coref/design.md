---
feature_id: N02/F27
feature_type: domain
status: designed
hld_refs:
  - HLD-§3.3/Worker
prd_refs:
  - "PRD §6.3 — Hebrew NLP"
adr_refs: []
biz_corpus: true
biz_corpus_e_id: E04-F04
---

# Feature: HebPipe CoNLL-U Coreference (Deferred MVP)

## Overview

Optional NLP enrichment pass that runs HebPipe (Bar-Ilan ONLP Lab) in
CoNLL-U mode to extract coreference chains — linking pronouns to their
antecedents. **POC scope: deferred** per PLAN-POC.md and biz corpus
("post-MVP gate"; biz OQ: "MVP or v1.1?"). POC ships a feature-flag stub
that always returns empty chains. When enabled (MVP), HebPipe runs after
the primary NLP stage; its output supplements the NLPResult with coref_chains
(a separate data structure, not part of the locked F03 NLPToken schema).

## Dependencies

- Upstream: N00/F03 (NLPResult base — this feature adds an optional supplement),
  N02/F17 or F26 (primary NLP output).
- Downstream: N02/F22 (reading plan could use coref for gender/number agreement).
- External services: HebPipe CLI or library (optional; not shipped in POC Docker image).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| tirvi.coref | enrich_with_coref(nlp_result: NLPResult) -> CorefResult | function | POC: returns CorefResult(chains=[]) always; MVP: runs HebPipe |
| tirvi.coref | CorefResult(chains) | dataclass | chains: list[CorefChain]; empty list = no coref available |
| tirvi.coref | COREF_ENABLED | bool constant | POC: False; env TIRVI_COREF |

## Approach

1. DE-01: Coref gate — COREF_ENABLED env flag; POC: False; returns CorefResult(chains=[]).
2. DE-02 (MVP): HebPipe runner — invoke HebPipe on the normalized text in CoNLL-U mode;
   parse chains; map antecedent token indices to NLPToken IDs.
3. DE-03 (MVP): Size gate — skip HebPipe for pages < 500 words (FT-142 threshold) for
   latency budget.

## Design Elements

- DE-01: corefGate (ref: HLD-§3.3/Worker)
- DE-02: hebpipeRunner (ref: HLD-§3.3/Worker) [MVP only]
- DE-03: pageSizeGate (ref: HLD-§3.3/Worker) [MVP only]

## Decisions

No ADR — stub; full design deferred to MVP. HebPipe binary dependency is opt-in.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Coreference enrichment | Not implemented in POC | Post-MVP per PLAN-POC.md; biz OQ unresolved |

## HLD Open Questions

- HebPipe latency budget (FT-141: 500 words in 5 s) -> MVP profiling.
- Quantifiable benefit over lemma-only baseline -> N05 bench.

## Risks

| Risk | Mitigation |
|------|-----------|
| HebPipe upgrade breaks CoNLL-U chain format | Pinned dependency; regression test; DE-01 gate means no POC impact |

## Diagrams

None required for stub.

## Out of Scope (POC)

- HebPipe CoNLL-U integration.
- CorefChain → reading plan gender agreement wiring.
- FT-141, FT-142, FT-143, FT-145 — all deferred MVP.
- FT-144 (disabled flag test) — anchored to T-01.
