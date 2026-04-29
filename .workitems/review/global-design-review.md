# Global Design Review — tirvi Business & Functional Design Phase

Synthesis of the 10-reviewer panel across all 12 epics × 58 features.
Per-feature review tables live in
`docs/business-design/epics/<epic>/reviews/<feature>.design-review.md`.

## Review Participants

| Reviewer | Role | Focus Area |
|----------|------|-----------|
| Product Strategy | PRD / market evidence / persona accuracy | tracks PRD §1–§11 + research §1, §6 |
| DDD | bounded context fit, aggregate design, event naming | aligns to taxonomy YAML |
| Functional Testing | test coverage, traceability, missing scenarios | per-feature FT/BT plans |
| Behavioural UX | realistic user patterns, emotional states, edge flows | per-feature BT plans |
| Architecture | system boundary assumptions, integration risks | HLD §3–§8 |
| Data and Ontology | YAML consistency, object relationships | the three ontology YAMLs |
| Security and Compliance | auth, audit, data privacy, regulatory gaps | E11 + cross-cutting |
| Delivery Risk | scope creep, dependency risks, timeline signals | research §10 phasing |
| Adversarial | challenges all other reviewers | every "must-fix" claim |
| Team Lead Synthesizer | consolidates consensus, ranks findings | this document |

## Review Scope

- 12 epics (E00–E11) covering the 6-phase canonical PLAN.md (N00–N05).
- 58 feature-level designs (skill labelling).
- 315 functional test scenarios + 208 behavioural test scenarios indexed.
- 47 business objects and 3 ontology YAMLs.

## Opening Positions

### Product Strategy Reviewer

Concept and scope match PRD + research recommendations. Practice-mode framing
is consistently applied. Two PRD claims (≥ 90% pronunciation, ≥ 95% acronym)
remain aspirational pending E10-F01/F03 internal study. Player UX (E09)
correctly inherits the differentiator from the reading-plan layer (E03–E06).

### DDD Reviewer

12 bounded contexts mapped cleanly to subdomains. `reading_plan`,
`hebrew_text`, `hebrew_nlp`, `pronunciation` are core; rest supporting or
generic. `Document`, `Manifest`, `ReadingPlan`, `AudioObject`, `MOSStudy`,
`ConsentRecord`, `Lexicon` named as aggregate roots — appropriate. Caveat:
`Manifest` is a read model of `Document` rather than a separate aggregate;
business-taxonomy.yaml documents this nuance.

### Functional Testing Reviewer

315 functional scenarios organised by stage. Critical-path tests called out
in the ontology YAML cover every PRD SLO. Coverage gaps: bench (E10-F01)
must include adversarial OCR pages (busy backgrounds, math-heavy, civics
homographs); without them, gates risk false confidence.

### Behavioural UX Reviewer

208 behavioural scenarios cover hesitation, abandonment, retry, escalation,
collaboration breakdown. Critical scenarios — privacy hesitation (BT-021),
homograph reporting (BT-097), screen-reader end-to-end (BT-175), parent
consent latency (BT-197) — appropriately weighted. Concern: the MVP MOS
study (n=10) is statistically thin; treat as directional, not definitive.

### Architecture Reviewer

Adapter-port discipline is cleanly preserved. Critical decisions still
deferred to ADR slots (ADR-001 voice routing, ADR-002 NLP backbone, ADR-003
diacritization+G2P, ADR-004 OCR primary, ADR-005 TTL, ADR-009 alignment
fallback, ADR-010 NLP compute primitive). The skill records each as an
open question; ADR authoring is downstream of this phase.

### Data and Ontology Reviewer

3 YAMLs synchronized. business-taxonomy carries 47 business objects, 12
collaboration objects, 10 assumptions, 5 open questions. dependency-map has
45 edges including 5 to inferable future implementation objects.
functional-test-ontology indexes all 523 tests + spotlights 17 critical-path
tests with full schema entries. Cross-walk to PLAN.md is captured.

### Security and Compliance Reviewer

E11 (privacy & legal) covers PPL Amendment 13 minors' consent, 24h TTL,
upload attestation, no-PII logging, feedback capture. Audio cache
exemption (ASM09 — shareable cross-user cache) is the single load-bearing
privacy trade-off and must be reviewed by external counsel before MVP
launch. Server-side enforcement of attestation gating is mandatory (modal
alone insufficient).

### Delivery Risk Reviewer

16-week phasing per research §10 is feasible for Option B. Top delivery
risks: (1) DictaBERT model footprint vs single-Docker compose floor
(addressed by `--profile models`), (2) MOS study recruitment drag could
delay MVP launch, (3) bench fixture provenance work could extend beyond
T-2 weeks pre-launch.

### Adversarial Reviewer

See `global-adversarial-review.md` for full challenge log.

## Discussion Summary

Three load-bearing debates converged on these conclusions:

1. **Hebrew SSML `<mark>` reliability (Architecture vs Adversarial).**
   Adversarial argued the Wavenet path is one provider regression away
   from collapse. Architecture defended the dual-path design (E08-F01
   forced-alignment fallback). Outcome: agreed that the failover path must
   be CI-tested every release, not just exercised in a smoke test.

2. **Audio-cache cross-user sharing (Security vs Architecture).**
   Security flagged the audio cache exemption to 24h TTL as a privacy
   trade-off requiring external sign-off. Architecture noted that without
   it the $0.02/page SLO collapses. Outcome: ADR-005 must explicitly
   document the exemption with privacy reviewer sign-off as gating MVP.

3. **MOS study sample size (Behavioural UX vs Product).**
   UX flagged n=10 as thin for a statistical claim. Product noted MVP
   needs directional evidence, not paper-quality. Outcome: MOS gate
   passes at MOS ≥ 3.5 and is directional only; "≥ 90% pronunciation"
   PRD claim must be softened to "evidence-backed for practice use" until
   v1.

## Agreements

- Practice-mode framing is correct for MVP (R1).
- 24-hour default TTL with audio-cache exemption is the right shape pending
  legal sign-off (R3).
- DictaBERT primary + AlephBERT/YAP fallback is the right NLP stance.
- Dicta-Nakdan + Phonikud + curated lexicon override is the moat.
- Voice routing (Wavenet word-sync, Chirp continuous, Azure alt) reflects
  src-003 §2.3 evidence.
- WordTimingProvider port with TTS-marks + WhisperX fallback is mandatory.
- Bench-driven CI gates are the only defensible quality story.
- WCAG 2.2 AA is non-negotiable for an accommodation product.

## Disagreements

| ID | Claim | Reviewers | Evidence Gap | Resolution Path |
|----|-------|-----------|--------------|-----------------|
| D-01 | "Word-sync ≤ 80 ms is achievable on Hebrew at 1×" | Adversarial vs Arch | unverified end-to-end on Wavenet | tirvi-bench v0 timing pages + ADR-009 |
| D-02 | "Audio cache cross-user sharing is privacy-acceptable" | Security vs Product | external counsel not engaged | block ADR-005 closure on legal sign-off |
| D-03 | "MOS panel n=10 is enough" | UX vs Delivery | statistical power untested | downgrade PRD claim to "directional"; expand panel for v1 |
| D-04 | "Hebrew acoustic model for WhisperX is production-ready" | Arch vs Adversarial | quality unmeasured on bagrut content | gate ADR-009 on bench result |
| D-05 | "47 features in 16 weeks is feasible" | Delivery vs Adversarial | dependent on partnership timing | break PLAN.md F44 (DPIA) into pre-launch + post-launch |

## Required Revisions

| ID | Severity | Reviewer | File | Required Change |
|----|---------|---------|------|----------------|
| R-01 | Critical | Security | E11-F01 stories | Add explicit audio-cache exemption review gate |
| R-02 | Critical | Adversarial | E07-F01 functional-test-plan | Add CI-mandatory failover smoke test |
| R-03 | Critical | Adversarial | E10-F01 stories | Add adversarial bench pages (busy bg, math, civics) |
| R-04 | Critical | Security | E11-F03 stories | Make server-side attestation enforcement explicit |
| R-05 | High | Functional Test | E04-F03 functional-test-plan | Add schema-bump migration test coverage |
| R-06 | High | Behavioural UX | E10-F03 stories | Document MOS-as-directional-only framing |
| R-07 | High | Arch | E08-F03 stories | Document hash bump procedure (cache invalidation) |
| R-08 | High | Delivery | PLAN.md cross-walk | Map every E## feature to F## scope explicitly |
| R-09 | Medium | DDD | business-taxonomy.yaml | Annotate Manifest as read model of Document |
| R-10 | Medium | Onto | dependency-map.yaml | Add 5 edges to FUT-* future implementation objects |
| R-11 | Medium | Product | E10-F03 stories | Soften PRD ≥ 90% pronunciation claim language |
| R-12 | Medium | Adversarial | E03-F04 stories | Quantify Latin-transliteration false-positive rate |

## Evidence Gaps

- Hebrew Wavenet `<mark>` timepoint reliability across full 1000-word block.
- MOS scores for Hebrew Wavenet vs Chirp 3 HD vs Azure HilaNeural on
  bagrut content with dyslexic teen panel.
- Hebrew acoustic-model quality for WhisperX forced alignment.
- Israeli legal opinion on cross-user audio cache exemption.
- Tesseract `heb` block-segmentation recall on adversarial pages.
- DictaBERT-large-joint resource footprint inside single Docker compose.

## Consensus Status

- Overall: **Partial** — consensus reached on direction; 4 Critical revisions
  must close before this design phase is complete.
- Blockers remaining: R-01, R-02, R-03, R-04 (queued for autoresearch loop).
