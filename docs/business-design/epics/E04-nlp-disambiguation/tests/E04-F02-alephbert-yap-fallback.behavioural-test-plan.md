# E04-F02 — AlephBERT/YAP Fallback: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| SRE on call during outage | P04 | slow MTTR | dashboards |
| Dev attempts to disable fallback | P08 | discipline erosion | policy guard |
| Student sees degraded quality | P01 | mistrust | UI flag |

## Scenarios
- **BT-087** DictaBERT outage; SRE confirms fallback engaged.
- **BT-088** Dev tries to disable fallback flag; CI rejects.
- **BT-089** Student sees "degraded NLP" badge; documentation explains.
- **BT-090** Mid-doc primary recovers; subsequent pages use primary; manifest shows mixed providers.

## Edge / Misuse / Recovery
- Edge: identical token classified differently primary vs fallback.
- Misuse: dev caches stale fallback output; cache TTL.
- Recovery: post-outage retro identifies whether fallback should be rerun on cached pages.

## Collaboration Breakdown
- Two independent failures (primary + fallback); document plan.

## Open Questions
- Dual-run comparison?
