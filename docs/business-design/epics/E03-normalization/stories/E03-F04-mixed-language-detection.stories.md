# E03-F04 — Mixed Hebrew / English / Math Span Detection

## Source Basis
- PRD: §6.3 (mark language for TTS)
- HLD: §5.2 (SSML inline `<lang xml:lang="en-US">`)
- Research: src-003 §2.3 ("Google `<lang>` not supported for he"; Azure path), §2.4
- Assumptions: ASM03 (TTS routing depends on this)

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | hears English word read in English | mispronunciation | per-span lang tag |
| P02 Coordinator | English Bagrut prep | accurate switching | inline `<lang>` |
| P08 Backend Dev | wires detector | RTL/LTR span boundaries | clean spans |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: TTS routing (E07-F03 Azure path).
3. System actors: Span detector, normalization output, reading-plan generator.
4. Approvals: detector heuristic changes hit bench.
5. Handoff: spans → SSML; lang attributes per voice path.
6. Failure recovery: Google Hebrew voice on English span: split-and-stitch fallback.

## Behavioural Model
- Hesitation: dev unsure where to split (mid-sentence vs mid-paragraph).
- Rework: false-positive English on Hebrew transliteration.
- Partial info: Hebrew text with English brand name; tag brand only.
- Retry: rule update lands via bench.

---

## User Stories

### Story 1: English spans tagged for TTS routing

**As a** student
**I want** English words pronounced as English
**So that** "DNA" or "p-value" come out right.

#### Main Flow
1. Span detector scans normalized text; emits `lang_spans[]` with `lang ∈ {he, en, math}`.
2. Reading-plan generator wraps English spans in `<lang xml:lang="en-US">…</lang>` for Azure path.

#### Edge Cases
- Single English letter inside Hebrew word; treated as Hebrew.
- Acronym in Latin (`PCR`) inside Hebrew sentence; tagged as English.

#### Acceptance Criteria
```gherkin
Given "ערך p-value הוא 0.05"
When span detection runs
Then `p-value` carries `lang="en"` and `0.05` carries `lang="num"`
```

#### Data and Business Objects
- `LanguageSpan` (start, end, lang, confidence).

#### Dependencies
- DEP-INT to E06 SSML, E07-F03 Azure adapter.

#### Non-Functional Considerations
- Quality: span precision ≥ 95% on bench.
- Reliability: deterministic.

#### Open Questions
- Math span overlap with `lang_spans` — separate channel or unified?

---

### Story 2: Google Hebrew path splits when `<lang>` not supported

**As a** dev
**I want** the Google Hebrew TTS path to split-and-stitch on English spans
**So that** mixed language doesn't yield silence.

#### Preconditions
- src-003 §2.3 documented gotcha: `<lang>` returns silence for Hebrew/Arabic/Persian.

#### Main Flow
1. Reading plan splits block into Hebrew + English chunks.
2. Adapter calls Google Hebrew TTS for Hebrew chunk; Google English TTS for English chunk.
3. Audio stitched; word marks aligned.

#### Edge Cases
- Stitch seam audible: cross-fade < 30 ms.
- Multiple language switches per sentence: stitch overhead measured.

#### Acceptance Criteria
```gherkin
Given a Hebrew sentence with two English fragments
When Google Hebrew adapter is selected
Then the audio is split into 3 chunks and stitched
And the perceived pause at seams is ≤ 30 ms
```

#### Dependencies
- DEP-INT to E07-F01 (Google Wavenet adapter).

#### Non-Functional Considerations
- Quality: stitched audio passes MOS for naturalness.
- Performance: extra overhead ≤ 100 ms per seam.

#### Open Questions
- Pre-emit a "lang tag warning" for QA.
