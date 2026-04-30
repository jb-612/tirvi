<!-- DERIVED FROM docs/business-design/epics/E05-pronunciation/stories/E05-F03-homograph-lexicon.stories.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-30T17:52:50Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E05-F03 — Curated Hebrew Homograph Lexicon (Top 500)

## Source Basis
- HLD: §5.2 (lexicon for high-frequency homographs)
- Research: src-003 §2.2 (homograph correctness gates), §7 principles
- Assumptions: ASM01; ≥ 85% homograph accuracy MVP gate (§8.2)

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P11 Lexicon Maintainer | curates entries | drift, maintenance | versioned lexicon |
| P08 Backend Dev | integrates lexicon | conflict with Nakdan | override layer |
| P01 Student | hears correct sense | mispronounced homographs | guarded top-500 |

## Collaboration Model
1. Primary: maintainer.
2. Supporting: dev (loader); test author (bench).
3. System actors: Lexicon loader, override layer (E05-F01).
4. Approvals: lexicon updates via PR with bench gate.
5. Handoff: overrides applied during E05-F01.
6. Failure recovery: missing entry → Nakdan default.

## Behavioural Model
- Hesitation: maintainer unsure if override is truly correct in all contexts.
- Rework: override over-fits one POS; refine context guard.
- Partial info: lexicon outage → bench shows regression.
- Retry: feedback corrections land monthly.

---

## User Stories

### Story 1: Top-500 homographs override Nakdan output

**As a** maintainer
**I want** to curate 500 high-frequency homographs and have them override Nakdan
**So that** known-bad cases stay solved deterministically.

#### Main Flow
1. Lexicon `data/homograph-lexicon.yaml` versioned.
2. Each entry: surface_form, pos_filter (optional), pronunciation_hint.
3. Override layer applies after Nakdan.

#### Edge Cases
- Entry without POS filter; applies broadly; review during PR.
- Conflict with NLP-derived sense; warn.

#### Acceptance Criteria
```gherkin
Given the lexicon contains an override for "ספר" with POS=VERB
When NLP picks POS=VERB and Nakdan returns noun-vocalization
Then the lexicon override wins
```

#### Data and Business Objects
- `HomographEntry`, `Lexicon`.

#### Dependencies
- DEP-INT to E05-F01, E11-F05 (feedback corrections).

#### Non-Functional Considerations
- Quality: top-500 coverage spans frequent ambiguous tokens.
- Reliability: lexicon load deterministic.

#### Open Questions
- How big can lexicon get before fine-tune is cheaper?

---

### Story 2: Lexicon coverage tracked over time

**As a** test author
**I want** bench to report homograph coverage and accuracy
**So that** lexicon work is evidence-driven.

#### Main Flow
1. Bench runs with and without overrides.
2. Diff report shows which overrides moved the needle.

#### Edge Cases
- Override regressed (worse than Nakdan); flagged for revert.

#### Acceptance Criteria
```gherkin
Given the bench has 50 homograph cases
When the bench runs
Then per-entry contribution to accuracy is reported
```

#### Dependencies
- DEP-INT to E10-F02 (quality dashboard).

#### Non-Functional Considerations
- Reliability: bench deterministic.

#### Open Questions
- Per-domain lexicon split (Tanakh, civics, science)?
