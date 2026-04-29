# E07-F04 — Voice Selection Policy (Per-Block Routing)

## Source Basis
- Research: src-003 §2.3 split-routing recommendation; ADR-001
- HLD: §5.2 voice routing
- Assumptions: ASM03

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | best voice per use case | one-size-fits-all wrong | per-block routing |
| P08 Backend Dev | implements policy | rule complexity | data-driven policy |
| P04 SRE | observability | unknown voice mix | per-block voice metric |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: SRE (metrics), product (UX choices).
3. System actors: voice routing service, MOS results (E10-F03).
4. Approvals: routing change → ADR-001 refresh.
5. Handoff: voice spec injected into reading plan.
6. Failure recovery: provider outage → policy reroutes.

## Behavioural Model
- Hesitation: dev unsure of default voice.
- Rework: cost spike from over-using Chirp.
- Partial info: MOS panel limited; refine over time.
- Retry: policy re-evaluated per block.

---

## User Stories

### Story 1: Per-block voice routing by use case

**As a** dev
**I want** voice routing to map use case → voice
**So that** word-sync mode uses Wavenet/Azure and continuous mode uses Chirp.

#### Main Flow
1. Routing service consumes block_type, user toggle, document context.
2. Selects voice spec; passes to TTS adapter.
3. Routing decision logged per block.

#### Edge Cases
- User toggles "premium" mid-doc; subsequent blocks use Chirp; old cached audio stays.
- Provider outage; routing reroutes.

#### Acceptance Criteria
```gherkin
Given the user has selected continuous-play mode
When the worker synthesizes a block
Then voice spec = Chirp 3 HD
```

#### Data and Business Objects
- `VoiceRoutingDecision` (block_id, voice_spec, reason).

#### Dependencies
- DEP-INT to E07-F01..F03, E10-F03 (MOS), E10-F05 (cost).

#### Non-Functional Considerations
- Cost: cap on Chirp usage.
- Quality: MOS-driven default.

#### Open Questions
- Should student see voice indicator?

---

### Story 2: Failover during outage

**As an** SRE
**I want** routing to failover when a provider's failure rate spikes
**So that** the player keeps working.

#### Main Flow
1. Failure-rate detector emits signal.
2. Routing policy switches primary for next blocks.

#### Edge Cases
- Both providers down; manifest flag; SRE alert.

#### Acceptance Criteria
```gherkin
Given Azure fails > 10% over 5 min
When routing reevaluates
Then next-block primary becomes Wavenet
```

#### Dependencies
- DEP-INT to E07-F03 (Azure), E07-F01 (Wavenet).

#### Non-Functional Considerations
- Reliability: failover bounded.

#### Open Questions
- Cooldown before re-promoting recovered provider.
