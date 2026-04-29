# E03-F02 — Numbers / Dates / Percentages to Spoken Form

## Source Basis
- PRD: §6.3 (numbers, dates, percentages, ranges spoken form)
- HLD: §5.2 reading plan SSML shaping
- Research: src-003 §2.4 (`num2words` Hebrew + ordinal layer)
- Assumptions: none new

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | hears numbers naturally | "two hundred forty-seven" not "two-four-seven" | num2words Hebrew |
| P08 Backend Dev | implements rules | gendered counters, ordinals | rule library |
| P02 Coordinator | math practice content | range "1-5" vs "minus 5" | context heuristics |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: lexicon maintainer.
3. System actors: `num2words` (Hebrew), custom Hebrew ordinal/range layer.
4. Approvals: rule additions reviewed.
5. Handoff: spoken-form text into reading-plan generator.
6. Failure recovery: ambiguous tokens flagged for review (E11-F05 feedback).

## Behavioural Model
- Hesitation: dev unsure if "1-5" is a range or "1 minus 5" in math context.
- Rework: gendered counter mistakes; lexicon adds rules.
- Partial info: percentage with embedded comma (e.g., 99,9%); rule covers locale.
- Retry: feedback-driven correction lands in lexicon.

---

## User Stories

### Story 1: Hebrew numbers read naturally

**As a** student
**I want** numbers like 247 read as "מאתיים ארבעים ושבע"
**So that** numeric content is understandable in audio.

#### Main Flow
1. Detector finds digits / digit groups.
2. Routes through `num2words(lang='he')` with custom gender hint based on noun context.
3. Emits spoken form into `NormalizedText` with span ref.

#### Edge Cases
- Year (2026): year-form rules.
- Ordinal (#3 → "השלישי"): ordinal rule.
- Phone numbers / IDs: read digit-by-digit when context flag set.

#### Acceptance Criteria
```gherkin
Given the page contains "247 תלמידים"
When normalization runs
Then the spoken form is "מאתיים ארבעים ושבעה תלמידים"
And the gender agreement matches noun "תלמידים" (masc plural)
```

#### Dependencies
- DEP-INT to E04 (POS for noun gender).

#### Non-Functional Considerations
- Quality: rule precision ≥ 95% on bench.
- Reliability: deterministic.

#### Open Questions
- Custom Israeli date formats (e.g., 5.4.26 vs 5/4/26).

---

### Story 2: Ranges, fractions, percentages handled

**As a** student
**I want** "1-5", "1/4", "99.9%" read in Hebrew naturally
**So that** math and statistics passages make sense.

#### Main Flow
1. Detector recognizes range / fraction / percentage tokens.
2. Routes through specialized rules (range → "מ-1 עד 5"; fraction → "רבע"; percentage → "תשעים ותשע נקודה תשע אחוז").

#### Edge Cases
- Range with negative ("-5–10") in math context: render with sign.
- Percentage in financial context: "ahuz" (אחוז) singular vs plural agreement.

#### Acceptance Criteria
```gherkin
Given "99.9%" appears
When normalization runs
Then the spoken form is "תשעים ותשע נקודה תשע אחוז"
```

#### Dependencies
- DEP-INT to E03-F05 (math template overlap).

#### Non-Functional Considerations
- Quality: ≥ 95% on numeric bench pages.

#### Open Questions
- Date in DD/MM vs MM/DD ambiguity guard.
