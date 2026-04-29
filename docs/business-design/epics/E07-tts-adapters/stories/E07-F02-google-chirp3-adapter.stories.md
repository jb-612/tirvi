# E07-F02 — Google Chirp 3 HD he-IL Adapter (Continuous-Play Mode)

## Source Basis
- Research: src-003 §2.3 (Chirp 3 HD highest-naturalness; NO SSML, NO `<lang>`, NO pause control); ADR-001
- HLD: §4 TTSBackend
- Assumptions: ASM03

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | premium voice for long passage | low naturalness on Wavenet | Chirp 3 HD |
| P08 Backend Dev | wires alternate adapter | no SSML | plain-text path |
| P11 SDK Maintainer | port stability | adapter divergence | TTSResult shape |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: voice routing policy (E07-F04).
3. System actors: Chirp 3 HD endpoint.
4. Approvals: ADR-001 dictates when to use Chirp.
5. Handoff: `TTSResult` (no marks).
6. Failure recovery: marks unavailable → forced alignment via E08-F02.

## Behavioural Model
- Hesitation: dev unsure when to choose Chirp.
- Rework: cost overrun; route only on premium tier.
- Partial info: Chirp drops pause directives; reading-plan adapts.
- Retry: same as Wavenet.

---

## User Stories

### Story 1: Chirp 3 HD synthesizes plain-text Hebrew

**As a** dev
**I want** Chirp 3 HD adapter to accept plain Hebrew text and return `TTSResult` without word marks
**So that** premium voice is available for continuous-play mode.

#### Preconditions
- E06 reading plan emits a plain-text variant when voice spec = Chirp.

#### Main Flow
1. Adapter sends plain text + voice spec.
2. Returns audio bytes; `word_marks=None` by design.
3. Provider field = `google-chirp-3-hd`.

#### Edge Cases
- Pause directives ignored; manifest flagged as continuous-play mode only.
- Cost overshoot; cap by voice routing.

#### Acceptance Criteria
```gherkin
Given continuous-play mode and Chirp 3 HD selected
When the adapter synthesizes a block
Then `TTSResult.word_marks is None` and audio is returned
```

#### Dependencies
- DEP-INT to E07-F04 (routing), E08-F02 (forced alignment).

#### Non-Functional Considerations
- Cost: $30/1M chars; route selectively.
- Quality: highest naturalness on bench; trade-off no marks.

#### Open Questions
- Should we make Chirp opt-in only by user toggle?

---

### Story 2: Reading plan adapts SSML-incompatible voice

**As a** dev
**I want** the reading plan to emit a plain-text variant when voice doesn't support SSML
**So that** the Chirp adapter never receives invalid input.

#### Main Flow
1. Plan generator detects target voice family.
2. Emits both SSML and plain-text variants in `plan.json`.
3. Chirp adapter consumes plain-text variant.

#### Edge Cases
- Voice rotation mid-cycle; cache invalidation policy.

#### Acceptance Criteria
```gherkin
Given a plan with both variants
When Chirp 3 HD is the target voice
Then the plain-text variant is consumed
```

#### Dependencies
- DEP-INT to E06 reading plan.

#### Non-Functional Considerations
- Maintainability: plan size larger; acceptable if voices change.

#### Open Questions
- Cache key inclusion of variant string.
