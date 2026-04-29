# E00-F03 — Adapter Ports & In-Memory Fakes

## Source Basis
- PRD: §7.5 Portability (vendor isolation), §9 Constraints
- HLD: §4 Adapter interfaces (StorageBackend, OCRBackend, TTSBackend), §6 OCR decision
- Research: src-003 §3 architecture change #1 (WordTimingProvider port), change #4 (rich result objects)
- Assumptions: ASM03 (TTS-marks unverified; forced-alignment fallback required)

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P08 Backend Dev | builds pipeline | swap real / fake backends per env | adapter drift | one port + ≥ 2 adapters + 1 in-memory fake |
| P10 Test Author | writes feature tests | deterministic pipeline runs | non-hermetic OCR / TTS | fakes return canned `OCRResult` / `TTSResult` |
| P11 SDK Maintainer | curates port shape | keep ports rich, not bytes | "lowest common denominator" anti-pattern | result objects carry timepoints, bboxes, conf, lang |

## Collaboration Model
1. Primary: backend dev defining a new adapter.
2. Supporting: test author wiring fakes into FUNC tests.
3. System actors: `StorageBackend`, `OCRBackend`, `NLPBackend`, `DiacritizerBackend`, `G2PBackend`, `TTSBackend`, `WordTimingProvider`, `QueueBackend`.
4. Approvals: port shape changes require ADR-NNN entry (out of phase scope here).
5. Handoff: fake registry → TDD test-mock-registry skill in TDD phase.
6. Failure recovery: adapter contract test catches schema drift.

## Behavioural Model
- Hesitation: dev unsure whether to add a method or extend a result object.
- Rework: dev returns `bytes` from OCR; reviewer rejects; dev wraps in `OCRResult`.
- Partial info: TTS provider doesn't emit timepoints; adapter falls back to `WordTimingProvider`.
- Abandoned flow: dev half-builds an adapter; contract test red surfaces missing methods.

---

## User Stories

### Story 1: Define rich result objects for every adapter

**As a** backend developer
**I want** every adapter port to return a rich result type (not bytes)
**So that** downstream stages receive bboxes, confidence, lang hints, and timepoints unchanged.

#### Preconditions
- Hexagonal pattern is the architectural baseline (HLD §4, src-003 §3.4).

#### Main Flow
1. Define `OCRResult`, `NLPResult`, `DiacritizationResult`, `G2PResult`, `TTSResult`, `WordTimingResult` as immutable value objects.
2. Each result includes per-token / per-block metadata required by ≥ 2 downstream consumers.
3. Adapter test suite asserts result shape against schema fixtures.

#### Edge Cases
- Provider doesn't supply confidence; adapter sets `confidence=null` not `0.0`.
- Provider returns multi-page result; adapter maps to per-page list.

#### Acceptance Criteria
```gherkin
Given a new TTS provider needs to be added
When the adapter is implemented against `TTSBackend`
Then `synthesize()` returns a `TTSResult` with audio bytes + word marks + voice meta
And no caller imports the provider SDK directly
```

#### Dependencies
- DEP-INT to E02–E08 (every pipeline stage consumes a result type)
- DEP-INT to E07-F04 (voice selection policy reads `TTSResult.voice_meta`)

#### Non-Functional Considerations
- Portability: domain code never imports vendor SDKs.
- Testability: in-memory fake covers happy path + 1 failure mode.

#### Open Questions
- Do we version result schemas with explicit `version` field or rely on adapter contract tests?

---

### Story 2: WordTimingProvider with TTS-marks + forced-alignment paths

**As a** backend developer
**I want** word timing to come from TTS marks when present and from forced alignment when not
**So that** the player highlight works whether the TTS provider supports `<mark>` or not.

#### Preconditions
- Per ASM03, Hebrew `<mark>` support is unverified end-to-end.

#### Main Flow
1. Define `WordTimingProvider` with two adapters: `TTSEmittedTimingAdapter`, `ForcedAlignmentAdapter` (WhisperX Hebrew).
2. Pipeline picks adapter at synthesize time; adapter choice stored in `audio/{block_hash}.timings.json`.
3. Forced-alignment adapter accepts audio + transcript and returns per-word start/end times.

#### Edge Cases
- TTS marks present but truncated (Google Neural2 regression); fall back automatically.
- Forced alignment fails on RTL text; provider raises typed error; player degrades to block-level highlight.

#### Acceptance Criteria
```gherkin
Given a Wavenet voice does not return marks for a 200-word block
When the synthesize stage requests timings
Then `WordTimingProvider` falls back to the forced-alignment adapter
And the resulting `WordTimingResult.source` field records `forced-alignment`
```

#### Dependencies
- DEP-INT to E07-F01..F03 (TTS adapters), E08-F02 (WhisperX Hebrew)

#### Non-Functional Considerations
- Reliability: failover budget ≤ 200 ms.
- Quality gate: alignment error ≤ 80 ms (ASM10).

#### Open Questions
- What is the fallback decision policy — automatic on schema mismatch, or explicit voice-config flag?
