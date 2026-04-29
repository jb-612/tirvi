# E00-F03 — Adapter Ports & Fakes: Functional Test Plan

## Scope
Verifies adapter ports return rich result objects, the in-memory fake registry
returns deterministic outputs, and the WordTimingProvider falls back correctly.

## Source User Stories
| Story ID | Title | Priority |
|----------|-------|---------|
| E00-F03-S01 | Rich result objects | Critical |
| E00-F03-S02 | WordTimingProvider with fallback | Critical |

## Functional Objects Under Test
| Object | Type | Related Story | Expected Behaviour |
|--------|------|--------------|-------------------|
| `OCRResult` | value object | S01 | bboxes + conf + lang per page |
| `TTSResult` | value object | S01 | audio + marks + voice meta |
| `WordTimingProvider` | port | S02 | fallback path triggers on missing marks |
| Fake registry | platform | S01 | canned results for happy + 1 failure path |

---

## Test Scenarios

### FT-011: OCRResult schema check
**Input:** Tesseract fake → `OCRResult`
**Expected:** schema includes `pages[].words[].bbox`, `pages[].words[].conf`, `pages[].lang_hints[]`
**Priority:** Critical

### FT-012: TTSResult includes marks where supported
**Input:** Wavenet fake with marks
**Expected:** `TTSResult.word_marks` non-empty; `voice_meta.codec="mp3"`
**Priority:** Critical

### FT-013: TTSResult marks-absent path
**Input:** Chirp 3 HD fake (no SSML support)
**Expected:** `TTSResult.word_marks=None`; downstream path uses forced alignment
**Priority:** Critical

### FT-014: WordTimingProvider switches on schema mismatch
**Input:** Wavenet fake returns truncated marks (only first sentence)
**Expected:** provider returns alignment from forced-alignment adapter; `source` field = `forced-alignment`
**Priority:** Critical

### FT-015: Fake registry returns deterministic OCR
**Input:** Fake `OCRBackend.ocr_pdf(canonical-page-001)`
**Expected:** identical result on N invocations
**Priority:** High

### FT-016: Adapter contract test catches schema drift
**Input:** rename `bbox` field on a real adapter
**Expected:** contract test fails with schema-diff message
**Priority:** High

## Negative Tests
- Adapter returns plain bytes → contract test rejects with "must wrap in result type".
- Provider raises typed error; result wrapper preserves error category.

## Boundary Tests
- Empty PDF (zero pages); `OCRResult.pages == []`.
- Single-token block; TTS result still includes one mark.

## Permission and Role Tests
- N/A (adapter layer is internal; no auth surface).

## Integration Tests
- E00-F03 fake → E03 normalization (verifies result objects flow through).
- E07 TTS adapter → E08 WordTimingProvider on real-mark and no-mark paths.

## Audit and Traceability Tests
- Each result type has a `provider` field (`google-wavenet`, `tesseract`, `whisperx`).
- Logs include adapter name + provider version per call.

## Regression Risks
- Adding a field to `OCRResult` without bumping schema version.
- TTS provider deprecates `<mark>`; fallback path must be exercised in CI.

## Open Questions
- Do we version result types with a numeric schema or rely on contract tests
  alone?
