# E08-F04 — Sentence-Level Cache Key (Cross-Document Reuse)

## Source Basis
- PRD: §6.5 (cache aggressively); §7.4
- HLD: §3.4 audio prefix
- Research: src-003 §5 Cost (sentence-level cross-doc reuse)
- Assumptions: ASM09

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P02 Coordinator | bulk-uploads exam variants | repeats free | sentence-level hits |
| P08 Backend Dev | implements cache key | block vs sentence boundary | adaptive key |
| P04 SRE | cost guard | better hit rate | observed amortization ≤ $0.02 |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: SRE; product (coordinator workflow).
3. System actors: hash computer, TTS adapters.
4. Approvals: hashing change via ADR.
5. Handoff: cross-doc cache reuse.
6. Failure recovery: hash collision → cache miss.

## Behavioural Model
- Hesitation: dev unsure if sentence-level beats block-level.
- Rework: hit rate analysis quarterly.
- Partial info: punctuation differences cause misses; normalize.
- Retry: per request.

---

## User Stories

### Story 1: Sentence-level cache key catches identical sentences across docs

**As a** dev
**I want** an additional cache key per sentence (within a block) so identical sentences hit across different documents
**So that** cross-document reuse compounds savings.

#### Preconditions
- Reading plan emits per-sentence subdivisions (could be a v1.1 scope; in MVP we do block-level).

#### Main Flow
1. Sentence hash = `hash(sentence_ssml + voice_spec + provider + version)`.
2. On block synthesize, the worker first checks sentence-level cache; assembles block from sentences.
3. Stitching at sentence boundaries within block.

#### Edge Cases
- Sentence ends with comma in one doc, period in another; normalize.
- Stitch seam acceptable (≤ 30 ms).

#### Acceptance Criteria
```gherkin
Given two documents share an identical sentence
When the second is synthesized
Then the sentence audio is reused from the cache
```

#### Dependencies
- DEP-INT to E08-F03.

#### Non-Functional Considerations
- Cost: improves amortized hit rate.
- Quality: stitch seam audible if not handled.

#### Open Questions
- Is sentence-level subdivision MVP or v1.1?

---

### Story 2: Coordinator-uploaded variant set benefits

**As a** coordinator
**I want** uploading a near-duplicate exam variant to mostly hit cache
**So that** prep is cheap.

#### Main Flow
1. Coordinator uploads two near-identical exams.
2. Sentence-level cache yields high hit rate.
3. Cost telemetry confirms.

#### Edge Cases
- Variants with re-ordered answers; cache reuse still applies per-sentence.

#### Acceptance Criteria
```gherkin
Given a coordinator uploads exam A then exam A' with 3 sentences modified
When synthesize completes
Then ≥ 90% of sentences hit cache
```

#### Dependencies
- DEP-INT to E08-F03, E10-F05.

#### Non-Functional Considerations
- Cost: tracked per coordinator workflow.

#### Open Questions
- MVP vs v1.1.
