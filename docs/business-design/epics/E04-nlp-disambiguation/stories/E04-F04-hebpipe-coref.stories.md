# E04-F04 — HebPipe CoNLL-U Fallback for Coreference

## Source Basis
- Research: src-003 §2.2 (HebPipe fallback / coreference utility); §10 deferred (coref is post-MVP gate)
- HLD: §3.3 NLP stage
- Assumptions: ASM04 (DictaBERT primary; HebPipe specialty)

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P08 Backend Dev | wires HebPipe path | cross-sentence pronouns mispronounced | coref-aware reading |
| P01 Student | follows long passage | ambiguous "he/she" referent | post-MVP gate | (post-MVP) |
| P11 SDK Maintainer | port stability | optional adapter | clean opt-in |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: SDK maintainer; test author.
3. System actors: HebPipe CLI / library (CoNLL-U).
4. Approvals: feature-flagged; off by default in MVP.
5. Handoff: optional `coref_chains` → reading-plan stage.
6. Failure recovery: coref absent → fallback to lemma-based heuristics.

## Behavioural Model
- Hesitation: dev unsure whether to enable in MVP (latency cost).
- Rework: coref output irregular on noisy text.
- Partial info: missing chain; reading plan ignores.
- Retry: gate run only on long-form pages.

---

## User Stories

### Story 1: HebPipe runs on opt-in basis for long passages

**As a** dev
**I want** HebPipe to run on documents above a threshold (e.g., 500 words / page)
**So that** coreference is available for long civics or science passages without slowing exam-shaped material.

#### Preconditions
- Feature flag `nlp.hebpipe.coref=true`.

#### Main Flow
1. NLP stage decides per-page based on word count.
2. HebPipe pipeline runs CoNLL-U; emits coref chains as enrichment.
3. Reading plan consumes chains where present.

#### Edge Cases
- Chain references span pages; ignored in MVP.
- Missing antecedent: chain ignored.

#### Acceptance Criteria
```gherkin
Given a long passage with pronouns
When HebPipe coref runs
Then `coref_chains` annotate the NLP output
And reading plan can use them when applying pronunciation hints
```

#### Data and Business Objects
- `CorefChain` (mention[], antecedent_index).

#### Dependencies
- DEP-INT to E06 (reading plan).

#### Non-Functional Considerations
- Performance: HebPipe latency budget ≤ 5 s per long page.
- Reliability: failures fall back silently.

#### Open Questions
- Should this be MVP at all, or v1.1?

---

### Story 2: Coref improves long-passage pronunciation

**As a** student
**I want** pronoun referents to inform pronunciation
**So that** ambiguous "he/she/they" use the right form.

#### Main Flow
1. Coref chain points to `Token.X` antecedent.
2. Reading plan emits matching gender/number agreement.

#### Edge Cases
- Conflicting chains; prefer recent antecedent.

#### Acceptance Criteria
```gherkin
Given a passage where "הוא" refers to "המורה"
When reading plan applies coref
Then the verb following "הוא" reflects masculine singular agreement
```

#### Dependencies
- DEP-INT to E06.

#### Non-Functional Considerations
- Quality: marginal improvement vs lemma-only baseline.

#### Open Questions
- Quantifiable benefit over lemma-only baseline?
