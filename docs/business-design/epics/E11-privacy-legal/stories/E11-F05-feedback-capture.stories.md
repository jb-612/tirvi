# E11-F05 — Feedback Capture ("Word Was Read Wrong")

## Source Basis
- PRD: §6.4 + §10
- HLD: §5.4 feedback loop (no live retraining)
- Research: src-003 §1 (user feedback for quality moat); §7 principle 6
- Assumptions: ASM01

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | reports wrong word | irritation | one tap |
| P11 Lexicon Maintainer | offline review | volume | dashboard |
| P04 SRE | privacy guard | PII leakage | minimal payload |

## Collaboration Model
1. Primary: backend dev + frontend dev.
2. Supporting: maintainer.
3. System actors: feedback capture endpoint, reviewer dashboard, lexicon update process.
4. Approvals: lexicon updates monthly via PR.
5. Handoff: feedback → review queue.
6. Failure recovery: feedback endpoint outage → in-browser queue.

## Behavioural Model
- Hesitation: student unsure if wrong reading is feedback-worthy.
- Rework: false reports; reviewer dismisses.
- Partial info: feedback without context; reviewer asks.
- Retry: queued offline.

---

## User Stories

### Story 1: One-tap "wrong word" report

**As a** student
**I want** a one-tap "wrong word" affordance per word
**So that** I can report easily.

#### Main Flow
1. Word receives a small flag affordance on hover/long-press.
2. Tap → POST `/documents/{id}/feedback` with word_id, suggested correction (optional).
3. Confirmation toast.

#### Edge Cases
- Offline: queued in-browser; retry on reconnect.
- Multiple reports: dedup per word per session.

#### Acceptance Criteria
```gherkin
Given a student taps the flag
When the network is healthy
Then a feedback record is stored
```

#### Data and Business Objects
- `FeedbackEntry` (doc_id, word_id, optional correction, timestamp, session_id).

#### Dependencies
- DEP-INT to E01 (manifest), E03-F03/E05 (lexicon).

#### Non-Functional Considerations
- Privacy: feedback stored under `feedback/{doc_id}/{ts}.json`; subject to TTL.
- Reliability: offline queue.

#### Open Questions
- Should we let the student suggest the correct pronunciation in audio?

---

### Story 2: Reviewer dashboard + monthly lexicon update

**As a** lexicon maintainer
**I want** a dashboard of feedback entries and the ability to land lexicon updates monthly
**So that** quality improves over time.

#### Main Flow
1. Dashboard reads `feedback/` (TTL-limited).
2. Maintainer picks recurring patterns; opens lexicon PR.
3. Bench validates lift.

#### Acceptance Criteria
```gherkin
Given 100 feedback entries in 30 days
When the maintainer reviews
Then patterns inform lexicon update PR
```

#### Dependencies
- DEP-INT to E03-F03 acronym lexicon, E05-F03 homograph lexicon.

#### Non-Functional Considerations
- Privacy: dashboard limited; no PII.

#### Open Questions
- Auto-flag recurring corrections?
