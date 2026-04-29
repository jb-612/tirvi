---
feature_id: N02/F23
feature_type: domain
status: drafting
hld_refs:
  - HLD-§5.3/Output
prd_refs:
  - "PRD §6.4 — Reading plan"
adr_refs: []
biz_corpus: true
biz_corpus_e_id: E06-F02
---

# Feature: SSML Shaping (POC minimum)

## Overview

Fills the `ssml` field of every `PlanBlock` produced by F22. POC scope
is intentionally minimal: `<break>` between blocks and per-word
`<mark name="w_N"/>` for word-timing alignment with the player.
Question-stem emphasis (biz S01) and answer-option pacing (biz S02)
are deferred — POC's demo PDF needs only the synchronized word
highlight, not pacing prosody. Wavenet (F26) is the only POC voice
and supports full SSML, so no plain-text fallback path is required.

## Dependencies

- Upstream: N02/F22 (`ReadingPlan` value type — F22 reserves the
  `ssml` field; F23 fills it).
- Adapter ports consumed: none — F23 mutates the immutable plan via
  reconstructing each `PlanBlock` with `ssml` populated.
- External services: none.
- Downstream: F26 (Wavenet adapter consumes the SSML), F30 (word-timing
  port keys timing back to the `<mark>` IDs F23 emits), F35 (player
  reads back the marks for highlight box stepping).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.ssml` | `shape(plan: ReadingPlan) -> ReadingPlan` | function | returns a new plan with `ssml` populated per block |
| `tirvi.ssml.builders` | `block_to_ssml(block: PlanBlock) -> str` | helper | one block → one `<speak>` document |
| `tirvi.ssml.escape` | `xml_escape(text: str)` | helper | XML special-char escape; preserves IPA codepoints |
| `tirvi.ssml.invariants` | `assert_ssml_v1(ssml: str)` | helper | XML parse check; speak root; mark IDs unique |

`<mark>` ID convention: `mark_id == PlanToken.id` (e.g.,
`mark_id="b3-0"` for the first token of block 3). Stable across runs
because PlanToken IDs are derived from `(block_id, position)` per F22.

## Approach

1. **DE-01**: SSML block builder — wrap content in `<speak xml:lang="he-IL">`;
   F22's POC block types map to a small, fixed SSML shape (no prosody
   variations in POC).
2. **DE-02**: Per-word `<mark>` insertion — emit `<mark name="<token.id>"/>`
   immediately before each token's text so Wavenet's mark-timing
   feature returns `(token.id, t_seconds)` pairs.
3. **DE-03**: Inter-block `<break>` insertion — between `PlanBlock`s in
   the same plan, prepend `<break time="500ms"/>` so the audio is
   reasonably segmented.
4. **DE-04**: XML-safe escape — `<`, `>`, `&`, `"`, `'` and any IPA
   codepoint that must be escaped for the target SSML profile;
   Hebrew NFD nikud characters pass through unchanged.
5. **DE-05**: SSML invariant check — parse the per-block SSML with
   `xml.etree.ElementTree`; assert single `<speak>` root and unique
   `<mark>` IDs; raise `SSMLValidationError` on failure.
6. **DE-06**: Plan re-emit — produce a new `ReadingPlan` with each
   `PlanBlock` reconstructed (frozen dataclasses → `dataclasses.replace`).

## Design Elements

- DE-01: ssmlBlockBuilder (ref: HLD-§5.3/Output)
- DE-02: perWordMarkInsertion (ref: HLD-§5.3/Output)
- DE-03: interBlockBreak (ref: HLD-§5.3/Output)
- DE-04: xmlSafeEscape (ref: HLD-§5.3/Output)
- DE-05: ssmlInvariantCheck (ref: HLD-§5.3/Output)
- DE-06: planReEmit (ref: HLD-§5.3/Output)

## Decisions

- D-01: No new ADR. POC SSML shape is the minimum stipulated by
  PLAN-POC.md F23 scope; richer profiles (question-stem prosody,
  answer pacing) lift into MVP and will be ADR'd at that time.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Question-stem emphasis | Out of scope (POC drops US-01 prosody) | PLAN-POC.md F23 scope: minimum SSML |
| Answer-option pacing | Out of scope (POC drops US-02) | Demo PDF has no answer-option blocks (F11 POC taxonomy) |
| Plain-text fallback | Out of scope | Wavenet supports full SSML; no fallback path needed in POC |
| Per-voice SSML profiles | Single-profile only | One voice in POC (Wavenet) |

## HLD Open Questions

- Rate variation evidence-backed → deferred MVP (no rate variation in POC).
- Per-student pause customization → deferred MVP.

## Risks

| Risk | Mitigation |
|------|-----------|
| `<mark>` ID collision across blocks if two blocks share index | DE-02 uses PlanToken.id (`{block_id}-{position}`), unique by F22 invariant |
| Hebrew NFD characters mis-escaped as XML entities | DE-04 escape list explicitly excludes Hebrew block; round-trip test enforces |
| SSML grows past Wavenet's 5000-char request limit | POC single-page demo well under cap; long-page chunking deferred to MVP |

## Diagrams

- `docs/diagrams/N02/F23/ssml-shaping.mmd` — ReadingPlan → block builder + mark + break → SSML-populated plan

## Out of Scope

- Question-stem `<prosody>` and `<emphasis>` (deferred MVP).
- Answer-option `<break>` between options (deferred MVP).
- Per-voice SSML profile registry (deferred MVP).
- Plain-text fallback (deferred MVP).
- SSML chunking for very long pages (deferred MVP).
