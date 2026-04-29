<!-- DERIVED FROM docs/business-design/epics/E04-nlp-disambiguation/stories/E04-F03-per-token-pos-morph.stories.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T20:49:21Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E04-F03 — Per-Token POS / Morph / Lemma in `nlp.json`

## Source Basis
- PRD: §6.4 Reading plan
- HLD: §3.3, §5.2, §5.3
- Research: src-003 §2.2 (DictaBERT joint output)
- Assumptions: ASM04

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P08 Backend Dev | consumes NLP output | fields scattered | one canonical token shape |
| P10 Test Author | seeds test data | inconsistent fixtures | builder reuse |
| P11 SDK Maintainer | guards schema | drift | versioned schema |

## Collaboration Model
1. Primary: SDK maintainer + backend dev.
2. Supporting: test author.
3. System actors: NLPBackend port, downstream stages (E05/E06).
4. Approvals: schema bump → ADR.
5. Handoff: `nlp.json` to plan stage.
6. Failure recovery: missing field → typed null; flagged for stage review.

## Behavioural Model
- Hesitation: dev unsure whether to add `def` (definiteness).
- Rework: schema bump on E04 lands; downstream consumers update.
- Partial info: AlephBERT fallback lacks fields; null filled.
- Retry: schema validation in CI.

---

## User Stories

### Story 1: Canonical NLPResult schema with versioning

**As a** SDK maintainer
**I want** `NLPResult` to carry text, POS (UD-style), lemma, morphological features (per UD-Hebrew), and confidence per attribute
**So that** all downstream consumers integrate against a stable contract.

#### Main Flow
1. Schema v1 published.
2. Adapter (DictaBERT or AlephBERT/YAP) emits this shape.
3. Schema validator runs in CI.

#### Edge Cases
- Confidence missing (older fallback); emit `null`.
- Lemma collapses to surface form for unknown token.

#### Acceptance Criteria
```gherkin
Given a Hebrew sentence
When NLP runs
Then `nlp.json` includes per-token POS, lemma, morph features
And schema validation passes against v1
```

#### Data and Business Objects
- `NLPResult.tokens[]`, `Token.morph_features` (gender, number, person, tense, def, ...).

#### Dependencies
- DEP-INT to E05, E06.

#### Non-Functional Considerations
- Reliability: schema bump procedure.
- Testability: fixture builder.

#### Open Questions
- Include dependency-parse heads as edge metadata or not?

---

### Story 2: Builder produces deterministic NLPResult fixtures

**As a** test author
**I want** an `NLPResult.builder()` that takes a YAML template and produces canonical results
**So that** E05/E06 functional tests are deterministic.

#### Main Flow
1. Builder accepts YAML with tokens; emits valid result.
2. Used by E05/E06 functional tests.

#### Edge Cases
- Builder with deprecated field → warning.

#### Acceptance Criteria
```gherkin
Given a 3-token YAML template
When the builder runs
Then the resulting NLPResult passes schema v1 validation
```

#### Dependencies
- DEP-INT to E00-F03 (fakes).

#### Non-Functional Considerations
- DX: YAML or DSL — pick one.
