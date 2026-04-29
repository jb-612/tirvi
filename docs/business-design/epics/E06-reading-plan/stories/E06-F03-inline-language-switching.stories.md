# E06-F03 — Inline `<lang xml:lang="en-US">` Switching

## Source Basis
- HLD: §5.2 SSML shaping (language switching)
- Research: src-003 §2.3 ("Google `<lang>` does not support Semitic switches"; Azure path supports)
- Assumptions: ASM03

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | English mid-sentence read in English | mispronunciation | per-span lang switch |
| P08 Backend Dev | builds switching | provider differs | voice-aware policy |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: TTS adapter (E07).
3. System actors: span detector (E03-F04), reading-plan generator.
4. Approvals: voice-policy changes via review.
5. Handoff: SSML to TTS provider.
6. Failure recovery: Google Hebrew + English mix → split-and-stitch.

## Behavioural Model
- Hesitation: dev unsure whether to fragment SSML.
- Rework: stitch seam audible; tighten cross-fade.
- Partial info: detector misses a span; manual review.
- Retry: smoke test on every provider change.

---

## User Stories

### Story 1: Azure path emits inline `<lang>` switch

**As a** dev
**I want** Azure Hebrew voice to receive SSML with inline `<lang>` for English spans
**So that** mixed sentences are read with proper pronunciation.

#### Preconditions
- E03-F04 detected English spans.

#### Main Flow
1. Profile inserts `<lang xml:lang="en-US">…</lang>` around each English span.
2. Azure adapter consumes; native pronunciation produced.

#### Edge Cases
- Nested spans (rare); collapse to outermost.

#### Acceptance Criteria
```gherkin
Given a Hebrew sentence with two English fragments
When SSML is built for Azure
Then both English fragments are wrapped in `<lang xml:lang="en-US">`
```

#### Dependencies
- DEP-INT to E07-F03 (Azure adapter), E03-F04 (span detector).

#### Non-Functional Considerations
- Quality: span boundary precision ≥ 95%.

---

### Story 2: Google path uses split-and-stitch fallback

**As a** dev
**I want** the Google Hebrew path to split at lang boundaries and stitch separate audio chunks
**So that** users on Google voice still hear correct pronunciation.

#### Main Flow
1. Profile detects voice family.
2. For Google: emit per-language SSML + glue audio post-synthesis.

#### Edge Cases
- Multiple seams; total stitch overhead ≤ 100 ms (per E03-F04 NFR).

#### Acceptance Criteria
```gherkin
Given a Hebrew block with 1 English phrase routed to Google Wavenet
When the synthesize stage runs
Then 2 audio chunks are produced and stitched
And the seam is < 30 ms perceived
```

#### Dependencies
- DEP-INT to E07-F01 (Google adapter), E08-F01 (timing alignment).

#### Non-Functional Considerations
- Performance: stitch overhead bounded.
- Quality: perceived seam acceptable.

#### Open Questions
- Cross-fade vs gap-zero policy.
