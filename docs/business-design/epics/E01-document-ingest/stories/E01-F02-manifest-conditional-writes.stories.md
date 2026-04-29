# E01-F02 — Manifest Object With Conditional Writes

## Source Basis
- HLD: §3.4 Storage layout (`manifests/{doc_id}.json`), §9 Data flow
- Research: src-003 §3 architecture change #2 (conditional writes), §10 Phase 1 F1.2
- Assumptions: none new (depends on ASM07 anonymous session)

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P08 Backend Dev | implements pipeline | atomic per-document state | race conditions on parallel pages | conditional write `x-goog-if-generation-match` |
| P04 SRE | observes ops | per-doc status visibility | opaque pipeline state | manifest tail-readable |
| P01 Student | polls progress | sees % complete | spinner forever | live status from manifest |

## Collaboration Model
1. Primary: worker writing per-stage results.
2. Supporting: API serving GET status; Manifest Coordinator.
3. System actors: GCS (atomic single-object overwrite), retry budget.
4. Approvals: schema changes captured in ADR slot.
5. Handoff: manifest → API → browser polling.
6. Failure recovery: precondition-failed retries with backoff.

## Behavioural Model
- Hesitation: dev unsure about read-modify-write race; uses precondition.
- Rework: schema field added; old manifests need migration.
- Partial info: stage failed but manifest not updated; observability flags.
- Abandoned flow: orphan manifest cleaned up by lifecycle.

---

## User Stories

### Story 1: Worker updates manifest atomically across 5 parallel pages

**As a** backend dev
**I want** the worker to update the per-document manifest under a generation precondition
**So that** parallel page completions do not lose updates.

#### Preconditions
- HLD storage layout adopted; one manifest per `doc_id`.

#### Main Flow
1. Worker reads `manifests/{doc}.json` (records `generation`).
2. Updates the stage's slot in memory (e.g., `pages[3].nlp = "done"`).
3. Writes back with `if-generation-match=<generation>`.
4. On conflict (412): re-read, re-merge, re-write.

#### Edge Cases
- Two stages finish simultaneously; first wins, second retries cleanly.
- Stage emits twice (idempotency); manifest update is identity if no change.

#### Acceptance Criteria
```gherkin
Given 5 OCR tasks complete in parallel
When each updates the manifest
Then all 5 updates land within 5 seconds and no update is lost
And no manifest history shows a regressed status
```

#### Data and Business Objects
- `Manifest` (doc_id, version, pages[], blocks[], stages[], updated_at)
- `StageStatus` (pending|running|succeeded|failed|skipped)

#### Dependencies
- DEP-INT to E00-F02 (GCS), every pipeline epic E2–E8.

#### Non-Functional Considerations
- Reliability: PUT latency ≤ 100 ms p95.
- Observability: generation history audit-trail.
- Privacy: manifest contains no document content.

#### Open Questions
- Do we shard manifest by stage to reduce contention on long documents?

---

### Story 2: Browser polls manifest for live status

**As a** student
**I want** the page to update progress in real time
**So that** I know the document is making progress, not stuck.

#### Preconditions
- Polling interval configurable (default 1 s).

#### Main Flow
1. Browser polls `GET /documents/{id}`.
2. API serves a denormalized projection of manifest.
3. Browser renders per-page progress bars.

#### Alternative Flows
- Server-sent events (post-MVP) replace polling.

#### Edge Cases
- Long stages: progress shows "still working" with elapsed time.
- Failed page: red marker; "retry page" affordance.

#### Acceptance Criteria
```gherkin
Given a 5-page upload is processing
When the browser polls every 1 s
Then per-page status is visible within 2 polls of stage completion
```

#### Dependencies
- DEP-INT to E09-F01 (player UI consumes the same projection)

#### Non-Functional Considerations
- Performance: poll handler ≤ 50 ms.
- Privacy: status omits document content.
- Accessibility: progress is announced via aria-live.

#### Open Questions
- Long-poll vs short-poll? SSE post-MVP feasibility?
