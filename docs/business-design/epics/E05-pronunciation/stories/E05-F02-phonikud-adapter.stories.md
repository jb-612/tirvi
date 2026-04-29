# E05-F02 — Phonikud G2P Adapter

## Source Basis
- Research: src-003 §2.2 (Phonikud G2P with stress + vocal shva, IPA, real-time)
- HLD: §5.2 SSML hints
- Assumptions: ASM01

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | natural prosody | flat / wrong-stress reading | Phonikud stress + IPA |
| P08 Backend Dev | integrates G2P | TTS-pronunciation hint passing | IPA hint into SSML |
| P10 Test Author | benchmarks G2P | drift | bench |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: lexicon maintainer (override).
3. System actors: Phonikud (open-source), reading-plan generator.
4. Approvals: ADR-003 covers choice.
5. Handoff: per-token IPA / stress / shva → SSML.
6. Failure recovery: Phonikud unavailable → rule-based G2P fallback.

## Behavioural Model
- Hesitation: dev unsure how aggressively to inject IPA into SSML.
- Rework: TTS drops IPA hint silently; bench catches.
- Partial info: low-confidence stress; emit default.
- Retry: model server restart on memory pressure.

---

## User Stories

### Story 1: Per-token IPA + stress hint

**As a** dev
**I want** Phonikud to emit per-token IPA, stress, and vocal-shva indicators
**So that** the reading plan can pass them to the TTS layer for natural prosody.

#### Preconditions
- Diacritized tokens from E05-F01.

#### Main Flow
1. `G2PBackend.process(diacritized_tokens)` → IPA + stress per token.
2. Hints stored on `Token.pronunciation_hint`.

#### Edge Cases
- Vocal-shva ambiguity; default to silent shva unless context flag.
- Stress ambiguous; emit default with warning.

#### Acceptance Criteria
```gherkin
Given the diacritized token "סִפֵּר"
When Phonikud runs
Then IPA = "siˈper" with stress on second syllable
```

#### Data and Business Objects
- `G2PResult`, `Token.pronunciation_hint` (ipa, stress, shva).

#### Dependencies
- DEP-INT to E06 (SSML), E05-F01 (input).

#### Non-Functional Considerations
- Quality: stress accuracy ≥ 85% on bench.
- Performance: ≤ 0.5 s per page.

#### Open Questions
- Inject IPA via SSML `<phoneme>` or via voice-specific hint protocols?

---

### Story 2: Rule-based fallback when Phonikud unavailable

**As a** dev
**I want** a rule-based G2P fallback when Phonikud fails
**So that** pipeline does not stall on G2P outage.

#### Main Flow
1. Adapter detects failure; switches to rule fallback.
2. Fallback uses POS + diacritization + simple G2P rules.

#### Edge Cases
- Both fail → undecorated SSML; manifest flag `g2p_degraded=true`.

#### Acceptance Criteria
```gherkin
Given Phonikud fails three times for a page
When the worker retries
Then the rule-based fallback emits hints
```

#### Dependencies
- DEP-INT to E10-F05 (telemetry on fallback rate).

#### Non-Functional Considerations
- Quality: degraded but coherent prosody.
- Reliability: failover budget ≤ 200 ms.

#### Open Questions
- Should fallback rate trigger SRE alert at threshold?
