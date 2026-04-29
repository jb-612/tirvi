# E07-F03 — Azure he-IL HilaNeural / AvriNeural Adapter

## Source Basis
- Research: src-003 §2.3 (Azure cleanest production word-timing API for he-IL; `<bookmark>` + `WordBoundary`; supports inline `<lang>`); ADR-001
- HLD: §4 TTSBackend
- Assumptions: ASM03 (Azure may become primary if Wavenet marks unreliable)

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | clean word-sync | Wavenet marks may truncate | reliable Azure path |
| P08 Backend Dev | wires Azure | `<bookmark>` + `WordBoundary` events | event-stream consumer |
| P10 Test Author | benchmarks parity | Azure vs Wavenet | bench |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: SDK maintainer (TTSResult shape parity).
3. System actors: Azure Speech SDK / REST.
4. Approvals: ADR-001.
5. Handoff: `TTSResult` shape identical to Wavenet.
6. Failure recovery: Azure outage → Wavenet primary.

## Behavioural Model
- Hesitation: dev unsure if Azure is primary or alt.
- Rework: voice rotation; SDK changes.
- Partial info: WordBoundary event missing; backfill from bookmark.
- Retry: SDK auto-retry.

---

## User Stories

### Story 1: Azure synthesizes Hebrew + emits WordBoundary events

**As a** dev
**I want** the Azure adapter to consume SSML with `<bookmark>` and `<lang>` and emit per-word timing
**So that** mixed-language Hebrew/English playback is reliable.

#### Preconditions
- Azure key in Secret Manager; voice `he-IL-HilaNeural` configured.

#### Main Flow
1. Adapter sends SSML; subscribes to `WordBoundary` + `BookmarkReached` events.
2. Maps to `TTSResult.word_marks`.
3. Provider field = `azure-hila`.

#### Edge Cases
- Voice deprecates; ADR-001 update.
- Hebrew + inline English: native support.

#### Acceptance Criteria
```gherkin
Given Hebrew + 2 English fragments routed to Azure
When the adapter synthesizes
Then `TTSResult.word_marks` covers all words across both languages
```

#### Dependencies
- DEP-INT to E06 SSML, E03-F04, E08-F01.

#### Non-Functional Considerations
- Cost: $16/1M chars Neural.
- Reliability: SDK retries.

#### Open Questions
- Default voice: Hila (female) or Avri (male) per ADR-001 evidence.

---

### Story 2: Azure swap-in path under Wavenet outage

**As a** SRE
**I want** the system to swap Wavenet to Azure under sustained outage
**So that** the player keeps working.

#### Preconditions
- Both adapters healthy; voice routing flag.

#### Main Flow
1. Wavenet failure rate > threshold (e.g., 10% in 5 min).
2. Voice routing (E07-F04) shifts to Azure for new blocks.
3. Cache picks up new voice's `block_hash`.

#### Edge Cases
- Both providers degraded; manifest flag for QA.

#### Acceptance Criteria
```gherkin
Given Wavenet failure rate exceeds 10% over 5 minutes
When voice routing reevaluates
Then new blocks route to Azure
And old cached audio remains valid
```

#### Dependencies
- DEP-INT to E07-F04 (routing policy).

#### Non-Functional Considerations
- Reliability: failover bounded.
- Quality: voice change mid-doc disclosed in manifest.

#### Open Questions
- Mid-doc voice swap UX impact?
