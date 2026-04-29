# E08-F03 — Content-Hash Audio Cache In GCS

## Source Basis
- PRD: §6.5 (cache by content hash); §7.4 Cost
- HLD: §3.4 audio prefix; §10 cost
- Research: src-003 §5 Cost (cache is dominant lever); §7 principle 4
- Assumptions: ASM09

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | re-read free | repeat costs | cache hit |
| P08 Backend Dev | implements cache | hash schema | versioned hash |
| P04 SRE | cost guard | budget overruns | hit-rate metric |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: SRE; test author.
3. System actors: GCS bucket, hash computer, TTS adapters, lifecycle (none on audio).
4. Approvals: hash scheme change → ADR.
5. Handoff: cache to player + retention.
6. Failure recovery: hash collision (rare) → cache miss path.

## Behavioural Model
- Hesitation: dev unsure how to version hash for voice spec changes.
- Rework: cache-miss spike on voice rotation.
- Partial info: audio bytes invalid (rare); evict.
- Retry: PUT retry on transient errors.

---

## User Stories

### Story 1: Cache by `block_hash = hash(ssml + voice_spec + provider + version)`

**As a** dev
**I want** the audio cache key to include voice spec, provider, and content
**So that** cross-user reuse stays correct under voice rotation.

#### Main Flow
1. Hash function deterministic; documented.
2. PUT/GET against `audio/{block_hash}.mp3` and `.timings.json`.

#### Edge Cases
- Provider version bump; new keys; old objects orphan until cost review.

#### Acceptance Criteria
```gherkin
Given identical SSML + voice_spec + provider
When two students request the same block
Then both receive the same cached audio
```

#### Data and Business Objects
- `AudioObject`, `block_hash` value object.

#### Dependencies
- DEP-INT to E07-F01..F03, E11-F01 (TTL).

#### Non-Functional Considerations
- Cost: dominant lever.
- Privacy: cache shareable per ASM09; no PII.

#### Open Questions
- Orphan eviction policy.

---

### Story 2: Hit rate metric

**As an** SRE
**I want** cache-hit-rate dashboard
**So that** I can verify cost SLO.

#### Main Flow
1. Adapter emits hit/miss; aggregated by hour.

#### Acceptance Criteria
```gherkin
Given 100 synthesize requests
When the metric is queried
Then hits + misses sum to 100
And hit rate exceeds 25% within first 7 days
```

#### Dependencies
- DEP-INT to E10-F05.

#### Non-Functional Considerations
- Reliability: metric independent of TTS provider.

#### Open Questions
- Pre-warm strategies on day-of-launch.
