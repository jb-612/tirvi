# E08-F02 — WhisperX Hebrew Adapter (Forced Alignment)

## Source Basis
- Research: src-003 §2.3 (WhisperX + Hebrew wav2vec2), §10 Phase 3 F8.2; ADR-009
- HLD: §5 reading plan (timings)
- Assumptions: ASM03, ASM10

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P08 Backend Dev | aligns audio + transcript | unreliable Hebrew acoustic models | bench |
| P04 SRE | resource budget | GPU vs CPU | profile gate |
| P10 Test Author | benches alignment | drift | bench |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: SRE (resource), test author.
3. System actors: WhisperX (Hebrew acoustic model), audio + transcript inputs.
4. Approvals: ADR-009 captures alignment fallback choice.
5. Handoff: alignment results → WordTimingProvider.
6. Failure recovery: alignment fails → block-level timing only.

## Behavioural Model
- Hesitation: dev unsure GPU vs CPU mode.
- Rework: model quality lower than expected; replace with MFA.
- Partial info: audio cuts mid-word; alignment best-effort.
- Retry: per block.

---

## User Stories

### Story 1: Forced alignment per block

**As a** dev
**I want** WhisperX to align audio to transcript and emit per-word timing
**So that** voices without marks still produce highlights.

#### Preconditions
- Transcript from `plan.json`.

#### Main Flow
1. Adapter receives audio bytes + transcript.
2. Returns `WordTimingResult` with start/end per word.

#### Edge Cases
- Speaker rate variance; alignment recalibrates per block.
- Music / noise in audio (rare); flagged.

#### Acceptance Criteria
```gherkin
Given a Hebrew audio block + transcript
When WhisperX adapter runs
Then per-word start/end times produced
And alignment error ≤ 80 ms on bench
```

#### Dependencies
- DEP-INT to E07 (audio bytes), E08-F01 (provider).

#### Non-Functional Considerations
- Quality: gate ≥ ASM10.
- Performance: ≤ 1 s per block on dev hardware.
- Resource: CPU-only mode acceptable in dev.

#### Open Questions
- WhisperX vs MFA — pick by ADR-009.

---

### Story 2: Telemetry on alignment quality

**As an** SRE
**I want** alignment-error metric emitted per block
**So that** drift is visible.

#### Main Flow
1. Bench produces per-block error histogram.
2. Production emits sampled estimates.

#### Acceptance Criteria
```gherkin
Given the bench is run
When metrics are computed
Then alignment-error p50/p95 are stored
```

#### Dependencies
- DEP-INT to E10-F02.

#### Non-Functional Considerations
- Reliability: deterministic on bench.
