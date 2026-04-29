<!-- DERIVED FROM docs/business-design/epics/E05-pronunciation/stories/E05-F01-dicta-nakdan-adapter.stories.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T20:51:43Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E05-F01 — Dicta-Nakdan Diacritization Adapter

## Source Basis
- PRD: §6.4 Reading plan, §10 Success metrics
- HLD: §5.2 (lexicon + heuristics + Nakdan path)
- Research: src-003 §2.2 (Dicta-Nakdan accuracy ~86.86%); §10 Phase 2 F5.1; ADR-003 slot
- Assumptions: ASM01

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | hears correct vowels | unvocalized text → wrong reading | Nakdan diacritization |
| P08 Backend Dev | wires adapter | network call cost | local model preferred |
| P11 SDK Maintainer | port stability | adapter drift | DiacritizationResult schema |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: lexicon maintainer.
3. System actors: Dicta-Nakdan adapter (API or local), NLP context (E04), G2P (E05-F02).
4. Approvals: ADR-003 records the choice.
5. Handoff: diacritized tokens to G2P (E05-F02) and reading-plan generator.
6. Failure recovery: Nakdan unavailable → fallback to lexicon-only or undecorated text + flag.

## Behavioural Model
- Hesitation: dev unsure between cloud API vs local model.
- Rework: ambiguous diacritization candidates; pick top by NLP context.
- Partial info: low-confidence; emit warning.
- Retry: transient failures → backoff.

---

## User Stories

### Story 1: Diacritize tokens with NLP-context conditioning

**As a** dev
**I want** Dicta-Nakdan to take the NLP context (POS / lemma / morph features)
**So that** diacritization picks the contextually-correct vowels.

#### Preconditions
- E04 NLP output present.

#### Main Flow
1. DiacritizerBackend.process(tokens, context) → `DiacritizationResult` per token: vocalized form + confidence.
2. Per-token diacritization stored in `pages[].nlp.json`.

#### Edge Cases
- Numbers / English / math: skipped.
- Compound prefix: diacritize whole compound.

#### Acceptance Criteria
```gherkin
Given the NLP-tagged sentence "ספר התלמיד שיר"
When diacritization runs with verb context
Then "ספר" carries the verb diacritization (סִפֵּר, "tell")
```

#### Data and Business Objects
- `DiacritizationResult`, `DiacritizedToken` (text, hint, conf).

#### Dependencies
- DEP-INT to E04, E05-F02, E05-F03 (lexicon override).

#### Non-Functional Considerations
- Quality: word-level accuracy ≥ 85% (src-003 §8.2).
- Performance: ≤ 1.5 s per page.
- Privacy: minimum payload sent to API; never document content.

#### Open Questions
- API vs local Nakdan trade-off.

---

### Story 2: Lexicon override beats Nakdan output

**As a** lexicon maintainer
**I want** my curated entries to override Nakdan output for top-frequency homographs
**So that** known-bad cases are deterministically corrected.

#### Preconditions
- Lexicon (E05-F03) loaded.

#### Main Flow
1. After Nakdan, override layer applies for tokens in lexicon.
2. Final diacritization stored.

#### Edge Cases
- Lexicon entry incompatible with NLP context; emit warning; pick context-fit Nakdan output.

#### Acceptance Criteria
```gherkin
Given the lexicon overrides "תורה" pronunciation when POS=NOUN
When diacritization runs
Then the override is emitted, not Nakdan default
```

#### Dependencies
- DEP-INT to E05-F03.

#### Non-Functional Considerations
- Quality: override coverage tracked.

#### Open Questions
- How many overrides before maintenance burden warrants ML fine-tune?
