<!-- DERIVED FROM docs/business-design/epics/E06-reading-plan/stories/E06-F01-block-typed-reading-plan.stories.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T20:58:03Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E06-F01 — Block-Typed Reading Plan (`plan.json`)

## Source Basis
- PRD: §6.4 Reading plan
- HLD: §5.3 Output `plan.json`; §3.3 plan stage
- Research: src-003 §7 ("reading plan is the product")
- Assumptions: ASM01

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | hears block-shaped audio | flat reading | per-block plan |
| P08 Backend Dev | builds plan generator | block + token + hint integration | structured plan.json |
| P10 Test Author | benches plan | invariants | schema validation |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: lexicon maintainer; SDK maintainer.
3. System actors: Block detector (E02-F04), NLP (E04), diacritization (E05), TTS (E07).
4. Approvals: schema bumps via ADR.
5. Handoff: `plan.json` to TTS stage and player.
6. Failure recovery: plan generation degrades — flat block emitted with flag.

## Behavioural Model
- Hesitation: dev unsure whether to mix tokens + SSML in same JSON.
- Rework: SSML escape errors found in QA.
- Partial info: partial NLP missing fields; plan emits best-effort.
- Retry: plan stage idempotent.

---

## User Stories

### Story 1: Plan emits per-block SSML and token list

**As a** dev
**I want** `plan.json` per page with per-block SSML, voice spec, and token list with hints
**So that** TTS and player consume a single source of truth.

#### Main Flow
1. Plan generator iterates blocks.
2. For each block: assemble tokens + IPA hints + acronym expansions + SSML shaping (pauses, language switches, emphasis).
3. Emit `block_id`, `block_type`, `voice_spec`, `ssml`, `tokens[]`.

#### Edge Cases
- Block with only one token; SSML still emits.
- Block without tokens (figure_caption empty); skip TTS.

#### Acceptance Criteria
```gherkin
Given a question block with 2 sentences
When the plan generator runs
Then `plan.json` includes the block's SSML and tokens with IPA + lemma + POS hints
```

#### Data and Business Objects
- `ReadingPlan`, `PlanBlock`, `PlanToken`.

#### Dependencies
- DEP-INT to E02-F04, E04, E05, E07, E09.

#### Non-Functional Considerations
- Reliability: schema validation in CI.
- Auditability: provenance per token (which adapter produced which field).

#### Open Questions
- Plan size cap? (Long pages → chunked plan?)

---

### Story 2: Plan invariants enforced

**As an** SDK maintainer
**I want** `plan.json` invariants (every token belongs to a block, IDs unique, SSML well-formed)
**So that** downstream stages cannot consume malformed plans.

#### Main Flow
1. Plan validator runs per page on emit.
2. Failures are typed and stage-fatal (manifest flagged).

#### Edge Cases
- SSML XML invalid → reject; manifest captures error.

#### Acceptance Criteria
```gherkin
Given an emitted `plan.json`
When the validator runs
Then unique IDs, SSML well-formedness, and token-block linkage are verified
```

#### Dependencies
- DEP-INT to E07 (TTS consumer).

#### Non-Functional Considerations
- Reliability: zero malformed plan reaches TTS.

#### Open Questions
- Strictness on SSML attribute namespaces?
