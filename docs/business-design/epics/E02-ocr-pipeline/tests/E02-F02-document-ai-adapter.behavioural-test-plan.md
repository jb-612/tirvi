# E02-F02 — Document AI Adapter: Behavioural Test Plan

## Behavioural Scope
Covers SRE budget anxiety, dev choice between processors, and student
confusion when their doc hits cap.

## Human Behaviour Patterns Covered
| Behaviour | Persona | Risk | Test Method |
|-----------|---------|------|------------|
| SRE budget guard | P04 | runaway cost | per-doc cap |
| Dev processor choice | P08 | wrong tool | ADR pointer |
| Student capped doc | P01 | quality loss | UX hint |

## Behavioural Scenarios

### BT-044: SRE configures budget cap on prod
**Persona:** P04
**Intent:** prevent cost spike
**Human behaviour:** sets cap=20 pages
**System expectation:** TF apply propagates; runtime enforces
**Acceptance criteria:** SRE sees cap honored on synthetic load

### BT-045: Dev chooses Form Parser experimentally
**Persona:** P08
**Intent:** evaluate tables
**Human behaviour:** runs bench with Form Parser
**System expectation:** results saved alongside OCR processor; ADR draft updated
**Acceptance criteria:** dev produces evidence-backed recommendation

### BT-046: Student doc hits cap mid-processing
**Persona:** P01
**Intent:** finish reading
**Human behaviour:** sees mixed-quality experience
**System expectation:** UI surfaces "some pages used a faster engine; quality may vary"
**Acceptance criteria:** student understands without surprise

### BT-047: Coordinator batch hits global daily cap
**Persona:** P02
**Intent:** prep weekly material
**Human behaviour:** uploads 30 PDFs
**System expectation:** later docs queued or capped; coordinator notified
**Acceptance criteria:** coordinator paces uploads

## Edge Behaviour
- Quota reset boundary: doc straddling reset hour treated correctly.
- Network blip mid-call: backoff + retry.

## Misuse Behaviour
- Dev tries to disable cap locally; SRE policy in TF wins.

## Recovery Behaviour
- API outage: doc enters degraded state; retry on outage clear.

## Collaboration Breakdown Tests
- Document AI deprecates a feature; ADR-004 updated; bench rerun.

## Open Questions
- Allow per-user "boost" budget for critical docs?
