# E00-F02 — Per-Feature Design Review

| Reviewer | Severity | Area | Finding | Files | Must-fix |
|----------|---------|------|---------|-------|----------|
| Product Strategy | Low | Product | TF setup not user-facing; consistent with phase 0. | — | No |
| DDD | Medium | Domain | "Environment" treated as a value object but stories imply lifecycle (apply/destroy) — could be Aggregate root for infra context. | stories, business-taxonomy.yaml | Yes — promote to Aggregate. |
| Functional Testing | Low | Test | FT-008 fan-out test depends on real Cloud Tasks; needs an emulator strategy. | functional-test-plan | No |
| Behavioural UX | Low | Behaviour | BT-007 pair-review uses Slack; alternative chat needed for incidents. | behavioural-test-plan | No |
| Architecture | Medium | Arch | `min-instances=1` only specified for prod; staging policy unspecified. | stories | Yes — define staging stance. |
| Data and Ontology | Low | Onto | `QueueDefinition`, `RetentionPolicy` need taxonomy entries. | business-taxonomy.yaml | No (appended this batch). |
| Security and Compliance | High | Security | TF service account uses Owner — violates least-privilege. | stories S1 | Yes — switch to least-priv role bundle. |
| Delivery Risk | Medium | Delivery | Dev stack-up time (15 min) excludes weight downloads; combined onboarding > 30 min. | stories | Yes — add timing breakdown to docs. |
| Adversarial | Medium | Risk | Workspace switch could trigger destroy/create on shared bucket; need destroy-protect. | stories | Yes — add destroy-protect on `audio/`. |
| Team Lead Synthesizer | High | All | Security finding + workspace destroy-protect are top priorities. | — | Yes |

## Aggregate Severity
- Critical: 0  High: 2  Medium: 4  Low: 4
- Status: 6 revisions queued for iteration 1.
