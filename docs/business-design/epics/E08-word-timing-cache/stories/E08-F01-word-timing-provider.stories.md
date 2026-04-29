# E08-F01 — WordTimingProvider Port

## Source Basis
- Research: src-003 §3 architecture change #1 (port + dual adapters), §10 Phase 3 F8.1; ADR-009
- HLD: §4 adapter interface (implicit)
- Assumptions: ASM03, ASM10

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | accurate highlight | desync feels broken | timing budget |
| P08 Backend Dev | wires provider | TTS marks unreliable | fallback path |
| P10 Test Author | benches alignment | drift | bench timings |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: SRE (telemetry), test author.
3. System actors: TTSEmittedTimingAdapter, ForcedAlignmentAdapter (E08-F02).
4. Approvals: ADR-009.
5. Handoff: WordTimingResult → player.
6. Failure recovery: TTS-mark fail → forced alignment within budget.

## Behavioural Model
- Hesitation: dev unsure when to switch source.
- Rework: alignment quality drifts; bench catches.
- Partial info: adapters partial; player handles missing words.
- Retry: per-block.

---

## User Stories

### Story 1: Provider returns per-word timing or fallback

**As a** dev
**I want** the WordTimingProvider to return per-word timing from TTS marks when present and from forced alignment when not
**So that** the player highlight works on every voice.

#### Preconditions
- E07 produced TTSResult.

#### Main Flow
1. Provider inspects TTSResult.word_marks.
2. If present + complete → emit timing from marks.
3. If absent or truncated → call forced alignment adapter; emit timing.
4. Result includes `source` field.

#### Edge Cases
- Both adapters fail → degraded result; player falls back to block-level highlight.

#### Acceptance Criteria
```gherkin
Given a Wavenet TTSResult with full marks
When provider runs
Then `WordTimingResult.source = "tts-marks"`
And alignment error budget ≤ 80 ms

Given a Chirp 3 HD TTSResult without marks
When provider runs
Then `source = "forced-alignment"`
```

#### Data and Business Objects
- `WordTimingResult`, `WordTiming`.

#### Dependencies
- DEP-INT to E07 + E08-F02.

#### Non-Functional Considerations
- Quality: alignment error ≤ 80 ms (ASM10).
- Reliability: failover ≤ 200 ms.

#### Open Questions
- Auto vs explicit policy (E00-F03 carry-over).

---

### Story 2: Telemetry on source distribution

**As an** SRE
**I want** per-block timing source emitted as a metric
**So that** I can detect TTS-mark unreliability over time.

#### Main Flow
1. Provider emits `timing_source` counter.
2. Dashboard shows distribution.

#### Edge Cases
- Burst of forced-alignment usage; alert at threshold.

#### Acceptance Criteria
```gherkin
Given 100 blocks synthesized
When the metric is queried
Then per-source counts are reported
```

#### Dependencies
- DEP-INT to E10-F05.

#### Non-Functional Considerations
- Reliability: low-noise alerts.
