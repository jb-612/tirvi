# E05-F04 — Confidence Scoring on Disambiguation

## Source Basis
- HLD: §5.2 disambiguation
- Research: src-003 §2.2 (confidence informs SSML markup)
- Assumptions: ASM01; ≥ 85% homograph correct rate MVP gate

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | trust the audio | wrong pronunciation feels random | confidence-aware behaviour |
| P08 Backend Dev | telemetry-aware | unknown ambiguity rate | per-token conf |
| P10 Test Author | bench gates | unmeasured ambiguity | conf threshold tests |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: SRE (alerts), product (UX surfaces).
3. System actors: NLP + Nakdan + Phonikud + lexicon — all contribute confidence.
4. Approvals: confidence threshold tuning is bench-led.
5. Handoff: confidence to SSML / UI layer.
6. Failure recovery: low-confidence token → mark for player UX (e.g., subtle visual cue).

## Behavioural Model
- Hesitation: dev unsure where to set threshold.
- Rework: lowering threshold causes too many warnings; tighten.
- Partial info: confidence values from different stages aggregated naively.
- Retry: feedback (E11-F05) updates lexicon.

---

## User Stories

### Story 1: Per-token confidence aggregated across stages

**As a** dev
**I want** per-token confidence aggregated from NLP, Nakdan, Phonikud, and lexicon decisions
**So that** UX and SRE have a single signal for "is this token reliable?".

#### Main Flow
1. Aggregator combines stage confidences with weighted average.
2. Output `Token.confidence` (0..1) and `Token.confidence_source` enum.

#### Edge Cases
- Lexicon override = 1.0 confidence by definition.
- Missing stage confidence → null fields excluded.

#### Acceptance Criteria
```gherkin
Given a token has NLP=0.92, Nakdan=0.85, Phonikud=0.88
When aggregation runs (default weights)
Then `Token.confidence` ≈ 0.88
And `Token.confidence_source = "aggregated"`
```

#### Data and Business Objects
- `Token.confidence`, `Token.confidence_source`.

#### Dependencies
- DEP-INT to E04, E05-F01, E05-F02, E05-F03.

#### Non-Functional Considerations
- Reliability: deterministic given fixed inputs.
- Auditability: weights versioned.

#### Open Questions
- Do we surface confidence to the player or only internally?

---

### Story 2: SRE alerts on low-confidence rate

**As an** SRE
**I want** an alert when low-confidence rate spikes for a document or globally
**So that** I can investigate before bench catches it.

#### Main Flow
1. Telemetry emits per-page low-confidence rate.
2. Alert at sustained threshold (e.g., > 10% for 30 min).

#### Edge Cases
- One pathological doc; alert deduplicated.

#### Acceptance Criteria
```gherkin
Given low-confidence rate exceeds 10% for 30 minutes
When the alert fires
Then SRE on-call is paged with a link to recent docs
```

#### Dependencies
- DEP-INT to E10-F05 (telemetry).

#### Non-Functional Considerations
- Reliability: alert noise budget.

#### Open Questions
- Surface confidence in player UI?
