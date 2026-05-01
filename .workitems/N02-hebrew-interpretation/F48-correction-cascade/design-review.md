# N02/F48 Hebrew Correction Cascade — Per-Feature Design Review (biz)

This stub captures the per-feature view of the multi-agent design review run during `@biz-functional-design` Stage 8. The full meeting-room transcript and adversarial loop live in `.workitems/review/global-design-review.md` and `.workitems/review/global-adversarial-review.md`. The autoresearch iteration log lives in `.workitems/review/review-iteration-log.md`.

## Review Participants
| Reviewer | Role | Focus |
|----------|------|-------|
| Product Strategy | PRD §6.4 / §7.1 + ADR-033 | Reads ADR-033 as contract; checks story coverage of every claimed benefit |
| DDD | bounded contexts, aggregates | Checks BO49 CorrectionCascade + BO52 StageDecision modelling |
| Functional Testing | FT-316..FT-330 | Coverage of every quality requirement |
| Behavioural UX | BT-209..BT-220 | Realistic patterns + degradation visibility |
| Architecture | HLD §10 alignment, on-device privacy | NLP chain re-entry; no cloud calls |
| Data and Ontology | YAML deltas | New BOs/COs/edges added safely (append-only) |
| Security and Compliance | privacy hard rule + retention | 127.0.0.1 enforcement, F43 TTL alignment |
| Delivery Risk | sequencing | F50 inspector dependency; MVP vs v1.1 cuts |
| Adversarial | challenges every load-bearing claim | "Recall ≥ 90% target unproven", "Cache key drift", "Spam-resistant?" |
| Team Lead Synthesizer | reaches consensus | This document is the per-feature consolidation |

## Review Scope
- 6 user-stories files (index + 5 sub-feature splits).
- Functional plan with 15 FTs (FT-316..FT-330) + 5 NTs + 5 BTs (boundary).
- Behavioural plan with 12 BTs (BT-209..BT-220).
- Ontology deltas (BO49..BO56, CO13..CO16, P15, DEP-052..DEP-058).

## Findings (per-feature roll-up)
Severity / area / id / status — full text in global review.

| ID | Severity | Area | Finding | Status | Files affected |
|----|---------|------|---------|--------|----------------|
| F48-R1-1 | Critical | Architecture | Privacy invariant must be **tested**, not just documented | Fixed via FT-AUD-03 (network monitor assertion) | functional-test-plan.md |
| F48-R1-2 | Critical | Functional Testing | "Recall ≥ 90%" is unmeasurable without a labelled bench | Fixed by deferring SLO measurement to F40 quality gates / F39 bench; F48 owns the pipeline + recall test scaffold | functional-test-plan.md, deferred-findings.md (D-RECALL-BENCH) |
| F48-R1-3 | High | DDD | `CorrectionCascade` aggregate boundary vs page aggregate (ReadingPlan BO25) | Fixed: cascade is a *transient* aggregate per page; lives within hebrew_text BC; not persisted as a long-lived aggregate root | user_stories.md, business-domains.yaml |
| F48-R1-4 | High | Behavioural UX | Degraded-mode banner copy must be accessible (Hebrew + English) | Fixed via BT-218 acceptance | behavioural-test-plan.md |
| F48-R1-5 | High | Security | "127.0.0.1 only" allowlist needs CI enforcement | Fixed: AUD-03 in functional-test-plan; CI gate listed | functional-test-plan.md |
| F48-R1-6 | Medium | Functional Testing | Latency budget assumes a small ambiguous-tokens fraction; unbounded LLM calls per page | Fixed: FT-330 cap at 10 LLM calls/page; BT-F-05 boundary | functional-test-plan.md |
| F48-R1-7 | Medium | DDD | LLMReviewer is a "domain service" or an "agentic actor"? | Fixed: modelled as a *collaboration_object* (CO15) the cascade calls; aligns with existing CO-style LLM consumers | business-domains.yaml |
| F48-R1-8 | Medium | Delivery Risk | F50 inspector is "under design" — circular dependency? | Fixed: F48 produces a stable JSON schema; F50 reads it; F48 does not block on F50 UI | user_stories.correction-log.md, dependencies.yaml |
| F48-R1-9 | Medium | Adversarial | Spam attack on feedback DB | Fixed: per-sha cap (FT-325 second variant) | user_stories.feedback-loop.md, functional-test-plan.md |
| F48-R1-10 | Low | Ontology | Naming inconsistency: "ConfusionPair" vs "OCRConfusionPair" | Fixed: standardize on `ConfusionPair` per BO51 | business-domains.yaml, user_stories.mlm-scorer.md |
| F48-R1-11 | Low | Product | Should we cite `_KNOWN_OCR_FIXES` in deprecation notice? | Fixed: degradation story lists deprecation explicitly | user_stories.degradation.md |

## Cross-Feature Concerns
- DEP-052: F48 → F19 Nakdan adapter — corrected token must round-trip diacritization without changing token count (regression of F-3 marker drift).
- DEP-053: F48 ↔ F22/F23 — token-in / token-out invariant; never split or merge.
- DEP-054: F48 → F47 feedback capture — schema-compatible extension.
- DEP-055: F48 → F50 inspector — JSON schema contract; F48 is producer.
- DEP-056: F48 → F40 quality-gates-ci — recall/precision metric source.
- DEP-057: F48 ← F14 normalization — must run before cascade.
- DEP-058: F48 → F21 homograph-overrides — promotion target for accepted suggestions.

## Required Revisions Already Applied
All R1 findings folded into the user_stories / test plans before close. R2 not required (0 unresolved Critical, 0 unresolved High).

## Consensus Status
- Overall: **Reached** (after R1 + adversarial loop iteration 1; iteration 2 confirmed stability).
- 0 Critical / 0 High open.
- Mediums: all addressed.
- Lows: all addressed.
- Deferred (with Git issue stubs): see `.workitems/review/deferred-findings.md`.

## Hand-off to @sw-designpipeline
- All inputs ready: user_stories(.*).md, functional-test-plan.md, behavioural-test-plan.md, design-review.md, ontology updates.
- Next phase produces: `design.md`, `tasks.md`, `traceability.yaml`, ADR confirmations, diagrams.
- DDD scaffold (Step 2.5) recommended: F48 has bounded contexts (`hebrew_text` re-entry), aggregates (CorrectionCascade), policies (threshold rules), domain events (CorrectionApplied / CorrectionRejected / CascadeModeDegraded). `@ddd-7l-scaffold` is a fit.
