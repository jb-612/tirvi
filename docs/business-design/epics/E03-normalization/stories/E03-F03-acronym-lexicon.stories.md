# E03-F03 — Acronym Lexicon & Expansion

## Source Basis
- PRD: §6.3 (acronym expansion)
- HLD: §5.2 SSML shaping; §5.4 feedback loop
- Research: src-003 §1 (acronym density), §2.4 Dicta acronym tools, Otzar Roshei Tevot
- Assumptions: ASM01 (practice mode); MVP target ≥ 95% acronym precision (PRD §10)

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | hears `ד״ר` → "דוקטור" | acronym spelled letter-by-letter | curated lexicon |
| P11 Lexicon Maintainer | curates entries | drift over time | versioned lexicon |
| P02 Coordinator | unusual acronyms in subject | uncovered domain | gentle fallback |

## Collaboration Model
1. Primary: lexicon maintainer (offline curator).
2. Supporting: backend dev (loader); test author (bench).
3. System actors: lexicon loader, acronym tagger, feedback corrections (E11-F05).
4. Approvals: lexicon updates land via PR with bench validation.
5. Handoff: tagged acronyms → SSML in E06.
6. Failure recovery: unknown acronym → letter-by-letter spell + "review" flag.

## Behavioural Model
- Hesitation: maintainer unsure if entry conflicts with regular word.
- Rework: maintainer fixes ambiguous expansion via context rule.
- Partial info: acronym with two valid expansions (e.g., `ת״א` = "תל-אביב" or "תיבת אזהרה"); pick by context.
- Retry: feedback-driven corrections land monthly.

---

## User Stories

### Story 1: Common acronyms expand to full Hebrew form

**As a** student
**I want** common acronyms expanded automatically
**So that** the audio reads naturally.

#### Main Flow
1. Loader reads `data/acronym-lexicon.yaml` versioned.
2. Tagger matches whole-token acronyms against lexicon.
3. Emits expansion as part of normalized text with `original_form` ref.

#### Edge Cases
- Acronym at sentence end with punctuation; tagger strips and re-attaches.
- Embedded acronym (`לדר״ר`) — handled by sub-token match where appropriate.

#### Acceptance Criteria
```gherkin
Given the page contains "ד״ר כהן"
When normalization runs
Then the spoken form is "דוקטור כהן"
```

#### Data and Business Objects
- `AcronymEntry` (form, expansion, context, source).
- `Lexicon` (entries[], version).

#### Dependencies
- DEP-INT to E11-F05 (feedback corrections).

#### Non-Functional Considerations
- Quality: ≥ 95% precision on PRD §10 metric.
- Reliability: lexicon load is deterministic; cache mtime.

#### Open Questions
- Disambiguation by domain (`חז״ל` vs `ת״ז`) — pull from POS/NER context?

---

### Story 2: Unknown acronym spelled letter-by-letter as fallback

**As a** student
**I want** unknown acronyms spelled letter-by-letter (not silently wrong)
**So that** I can recognize them and provide feedback.

#### Main Flow
1. Tagger flags unknown acronyms via heuristics (geresh `׳` / gershayim `״`, all-uppercase Latin).
2. SSML emits letter-by-letter via per-letter break.
3. Feedback path captures user correction (E11-F05).

#### Edge Cases
- Hebrew word coincidentally containing geresh; tagger uses lexicon allow-list.

#### Acceptance Criteria
```gherkin
Given an acronym `ב״הנלד״ץ` not in lexicon
When the player synthesizes
Then audio spells the letters with brief pauses
And a "report wrong" affordance is offered
```

#### Dependencies
- DEP-INT to E07 (TTS), E11-F05.

#### Non-Functional Considerations
- Quality: spell-out cleanly without stuttering.

#### Open Questions
- Should fallback acronym be silently logged for offline review?
