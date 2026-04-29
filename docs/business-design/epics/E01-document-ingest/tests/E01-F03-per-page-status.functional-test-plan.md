# E01-F03 — Per-Page Status: Functional Test Plan

## Scope
Verifies progressive availability, per-page error surfaces, and SRE-side
manifest CLI.

## Source User Stories
| Story ID | Title | Priority |
|----------|-------|---------|
| E01-F03-S01 | Progressive page availability | Critical |
| E01-F03-S02 | Failed page does not block siblings | Critical |
| E01-F03-S03 | SRE inspects manifest history | Medium |

## Functional Objects Under Test
| Object | Type | Related Story | Expected Behaviour |
|--------|------|--------------|-------------------|
| Page status state machine | aggregate | S01 | uploaded → ocr → norm → nlp → plan → audio-ready |
| Page failure annotation | value object | S02 | error code + retry count |
| `tirvi-cli manifest` | dev tool | S03 | human-readable timeline |

---

## Test Scenarios

### FT-039: Page 1 audio-ready while page 2 still in NLP
**Input:** worker fast-paths page 1
**Expected:** browser sees `audio-ready` for page 1 within 2 polls; page 2 shows progress
**Priority:** Critical

### FT-040: Page 3 fails; pages 4-5 continue
**Input:** OCR returns confidence < threshold for page 3
**Expected:** page 3 marked failed; pages 4-5 continue OCR / NLP / plan / TTS
**Priority:** Critical

### FT-041: Document-level summary computes from page statuses
**Input:** 3/5 pages audio-ready, 1 failed, 1 in TTS
**Expected:** doc summary = "partial" with counts
**Priority:** High

### FT-042: Retry surfaces a clean state transition
**Input:** user clicks "retry page 3"
**Expected:** page 3 returns to OCR pending; old failure preserved in history
**Priority:** High

### FT-043: tirvi-cli prints manifest timeline
**Input:** SRE invokes CLI on stuck doc
**Expected:** stage timestamps + error codes; no document content
**Priority:** Medium

## Negative Tests
- Page state regressed (e.g., audio-ready → ocr): rejected by manifest writer
  precondition; logged.
- Stage status omits required fields; manifest validator rejects.

## Boundary Tests
- All 5 pages succeed simultaneously: doc summary "complete" emitted exactly once.
- All 5 pages fail: doc summary "failed"; UI offers full document retry.

## Permission and Role Tests
- CLI run without auth requires SRE-only context; API enforces.

## Integration Tests
- Manifest projection ↔ player UI (E09-F01) consume same event shape.

## Audit and Traceability Tests
- Per-page state transitions logged with stage + duration.

## Regression Risks
- New stage added but document summary aggregator not updated.

## Open Questions
- Does retry trigger a different OCR adapter automatically?
