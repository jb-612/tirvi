# E01-F03 — Per-Document & Per-Page Status

## Source Basis
- PRD: §6.1 (per-document status), §7.3 Reliability ("failed pages surfaced")
- HLD: §3.4 manifests; §9 Data flow
- Research: src-003 §10 Phase 1 F1.3
- Assumptions: none

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | wants to start playing as soon as page 1 ready | "still loading" feels broken | first block streams before doc complete |
| P02 Coordinator | tracks batch progress | "where is page 4?" | per-page status |
| P04 SRE | diagnoses stalls | manifest opaque to humans | human-readable summary endpoint |

## Collaboration Model
1. Primary: student polling page 1.
2. Supporting: coordinator bulk view; SRE ops view.
3. System actors: API status endpoint; manifest projection.
4. Handoff: status JSON → browser progress UI; SRE dashboard.
5. Failure recovery: failed page does not block sibling pages.

## Behavioural Model
- Hesitation: student unsure if 30 s waiting means success.
- Rework: SRE sees stuck page; triggers re-run.
- Partial info: page 3 still pending while pages 1, 2, 4, 5 are done.
- Abandoned flow: student leaves mid-process; status persists at TTL boundary.
- Retry: stage retried up to 3× per HLD §3.3; surfaced clearly.

---

## User Stories

### Story 1: Per-page progressive availability

**As a** student
**I want** to start listening to page 1 as soon as it is ready
**So that** I don't wait for the whole 5-page exam to finish.

#### Main Flow
1. Worker completes synthesize for page 1.
2. Manifest updates `pages[0].state = "audio-ready"`.
3. Browser sees new state on next poll; player allows playback.

#### Edge Cases
- Page 3 fails while page 4 is ready; page 4 still playable; page 3 shows error icon.

#### Acceptance Criteria
```gherkin
Given page 1 audio is ready and page 2 is not
When the browser polls
Then play affordance is enabled for page 1 and shows "preparing" for page 2
```

#### Dependencies
- DEP-INT to E08-F03 (audio cache), E09-F02 (player), E01-F02 (manifest).

#### Non-Functional Considerations
- Performance: first-block latency aligned with PRD §7.2 (≤ 30 s p50).
- Accessibility: "preparing" announced via aria-live.

#### Open Questions
- Should we pre-fetch page 2 audio while page 1 plays?

---

### Story 2: Failed page does not block siblings

**As a** student
**I want** a failed page to be flagged without blocking the others
**So that** one bad scan doesn't kill the whole exam.

#### Main Flow
1. Worker for page 3 OCR fails after retries.
2. Manifest sets `pages[2].state = "failed"`, `pages[2].error = "ocr_low_confidence"`.
3. UI shows page 3 with error chip + "retry" affordance; pages 1, 2, 4, 5 unaffected.

#### Edge Cases
- All 5 pages fail; UI surfaces document-level failure with bulk retry.
- Failure on a downstream stage (TTS) but upstream (OCR/NLP) succeeded — user sees text without audio.

#### Acceptance Criteria
```gherkin
Given page 3 OCR fails after 3 retries
When the browser refreshes status
Then page 3 shows an error state with a retry button
And pages 1, 2, 4, 5 are unaffected
```

#### Dependencies
- DEP-INT to E02-F03 (OCRResult confidence), E10-F02 (quality gates)

#### Non-Functional Considerations
- Reliability: retries bounded; backoff per HLD §3.3.
- Auditability: per-page failure reason logged; never document content.

#### Open Questions
- Does retry trigger a different OCR adapter (Tesseract → Document AI)?

---

### Story 3: SRE inspects manifest history

**As an** SRE
**I want** a human-readable summary of manifest stages and timings
**So that** I can diagnose stuck documents quickly.

#### Main Flow
1. SRE runs `tirvi-cli manifest <doc_id>`.
2. CLI fetches manifest and prints stage timeline.

#### Edge Cases
- Document under TTL boundary; CLI warns "expires in 2h".

#### Acceptance Criteria
```gherkin
Given a stuck document with NLP failure
When SRE runs `tirvi-cli manifest <doc_id>`
Then the output shows OCR succeeded at T+12 s, NLP failed at T+18 s with error code
```

#### Dependencies
- DEP-INT to E10-F04 (latency profiling reads same data)

#### Non-Functional Considerations
- Privacy: CLI omits document content.

#### Open Questions
- Is the CLI shipped to all SRE laptops or invoked via a one-shot Cloud Run job?
