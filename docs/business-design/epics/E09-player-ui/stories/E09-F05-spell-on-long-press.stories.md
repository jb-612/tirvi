# E09-F05 — Long-Press To Spell A Word

## Source Basis
- PRD: §5 use case 5 (spell letter by letter)
- HLD: §3.1 player
- Research: src-003 §1 (acronym fallback uses spell-out)
- Assumptions: ASM01

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | hears letters of unfamiliar word | catches once | long-press affordance |
| P09 Frontend Dev | implements gesture | mobile vs desktop | unified handler |
| P02 Coordinator | demos | discoverability | tooltip + tutorial |

## Collaboration Model
1. Primary: frontend dev.
2. Supporting: accessibility consultant (gesture + keyboard).
3. System actors: gesture handler, TTS adapter (letter-by-letter SSML), audio cache.
4. Approvals: a11y review.
5. Handoff: word → letter SSML → TTS.
6. Failure recovery: letters missing pronunciation → fallback Hebrew letter table.

## Behavioural Model
- Hesitation: student doesn't know about feature.
- Rework: gesture conflicts with mobile selection menu.
- Partial info: word is symbol-only (math); offer short symbol description.
- Retry: tap-tap fast; rate-limit.

---

## User Stories

### Story 1: Long-press a word to spell it

**As a** student
**I want** long-pressing a word to play letter-by-letter audio
**So that** I can catch unfamiliar Hebrew or English words.

#### Preconditions
- Word is rendered text (not image).

#### Main Flow
1. Long-press triggers spell mode for the targeted word.
2. SSML emits per-letter break.
3. Audio cached per word_hash.

#### Edge Cases
- Acronym already expanded; spelling repeats source acronym letters.
- English word; spelled in English.
- Math symbol; uses E03-F05 fallback name.

#### Acceptance Criteria
```gherkin
Given a Hebrew word "מאתיים"
When long-press triggers
Then audio reads "מ א ת י י ם" with brief pauses
```

#### Data and Business Objects
- `WordSpellAudio` keyed by word_hash.

#### Dependencies
- DEP-INT to E07, E08-F03 (cache).

#### Non-Functional Considerations
- Accessibility: keyboard equivalent (Shift+S on focused word).

#### Open Questions
- Mobile gesture conflict with text selection.

---

### Story 2: Letter-table fallback for unknown letters

**As a** student
**I want** even non-Hebrew letters spelled correctly using a simple table
**So that** the feature does not silently fail.

#### Main Flow
1. Letter-table maps Latin / Greek / common symbols → Hebrew names.
2. SSML built from table.

#### Edge Cases
- Letters not in table; "סימן מיוחד".

#### Acceptance Criteria
```gherkin
Given a word "α" in math context
When long-press triggers
Then audio reads "אלפא"
```

#### Dependencies
- DEP-INT to E03-F05.

#### Non-Functional Considerations
- Quality: bench coverage.

#### Open Questions
- Language attribute for letter-by-letter Hebrew vs English.
