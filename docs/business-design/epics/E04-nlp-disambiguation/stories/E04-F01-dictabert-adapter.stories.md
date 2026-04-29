# E04-F01 — DictaBERT-large-joint Adapter (Primary NLP Backbone)

## Source Basis
- PRD: §6.4 Reading plan; §9 Constraints (Hebrew NLP local-first)
- HLD: §3.3 NLP stage; §5.2 NLP-driven disambiguation
- Research: src-003 §2.2 (DictaBERT replaces AlephBERT primary), §10 Phase 2 F4.1; ADR-002 slot
- Assumptions: ASM04

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | hears correct word reading | homograph mistakes | DictaBERT context disambiguation |
| P08 Backend Dev | wires NLP adapter | model footprint vs sidecar | model service profile |
| P10 Test Author | benchmarks disambiguation | drift | bench |

## Collaboration Model
1. Primary: backend dev wiring adapter.
2. Supporting: SRE managing model service; test author maintaining bench.
3. System actors: DictaBERT model server, NLPBackend port.
4. Approvals: ADR-002 captures decision.
5. Handoff: `NLPResult` to E05 diacritization.
6. Failure recovery: model server unavailable → AlephBERT fallback (E04-F02).

## Behavioural Model
- Hesitation: dev unsure whether to load model in worker process or sidecar.
- Rework: prediction confidence lower than expected on math content; bench refines.
- Partial info: model returns multiple candidates; pick top with margin threshold.
- Retry: transient failure → retry with backoff.

---

## User Stories

### Story 1: DictaBERT segments, lemmatizes, POS-tags Hebrew tokens

**As a** dev
**I want** the NLP stage to call DictaBERT-large-joint and emit per-token segmentation, POS, lemma, morphological features
**So that** downstream disambiguation, diacritization, and reading-plan stages have rich data.

#### Preconditions
- Model service running (compose `models` profile or sidecar in prod).
- Repaired text from E03 normalization.

#### Main Flow
1. NLPBackend.process(text) → `NLPResult` per token: text, segmentation, POS, lemma, morph features.
2. Service caches model in memory; latency target ≤ 3 s per page on dev hardware.
3. Confidence per attribute included.

#### Edge Cases
- Empty text: returns empty result.
- Token unrecognized; fallback to AlephBERT.
- Numbers / English spans skipped (already tagged in E03).

#### Acceptance Criteria
```gherkin
Given a Hebrew sentence "התלמיד פותר את השאלה"
When NLP runs
Then each token has POS, lemma, morph features
And the lemma of "פותר" is "פתר"
```

#### Data and Business Objects
- `NLPResult`, `Token` (text, lemma, POS, morph, conf).

#### Dependencies
- DEP-INT to E03 (input), E05 (output), E04-F02 (fallback).

#### Non-Functional Considerations
- Performance: per-page ≤ 3 s on dev hardware.
- Quality: UD-Hebrew accuracy ≥ 92% (ADR-002 baseline).
- Resource: model service ≤ 2 GB resident.

#### Open Questions
- Is segmentation needed pre-NLP (compound words like `כשהתלמיד`)?

---

### Story 2: Disambiguation between homographs

**As a** student
**I want** "ספר" read as "book" or "count" or "tell" depending on context
**So that** I'm not surprised by wrong pronunciations.

#### Preconditions
- DictaBERT contextualizes via sentence input.

#### Main Flow
1. NLP returns POS + sense candidates with margin.
2. Tagger picks top candidate (margin > 0.2).
3. Reading-plan generator (E06) consumes sense for pronunciation hint.

#### Edge Cases
- Tied probabilities; emit with `ambiguous=true` and SRE log.
- Sense not in lexicon for pronunciation; default to lemma.

#### Acceptance Criteria
```gherkin
Given the sentence "ספר התלמיד שיר" (the student told a poem)
When disambiguation runs
Then "ספר" carries POS=VERB, sense="tell"
And the reading-plan emits the verb pronunciation
```

#### Dependencies
- DEP-INT to E05-F03 (homograph lexicon override).

#### Non-Functional Considerations
- Quality: homograph accuracy ≥ 85% (ADR-002).

#### Open Questions
- How to capture and learn from feedback corrections? (post-MVP).
