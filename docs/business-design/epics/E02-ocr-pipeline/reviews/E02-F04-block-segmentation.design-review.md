# E02-F04 — Per-Feature Design Review

| Reviewer | Severity | Area | Finding | Files | Must-fix |
|----------|---------|------|---------|-------|----------|
| Product Strategy | High | Product | Block taxonomy is a product surface; deserves a public glossary. | docs | Yes |
| DDD | Medium | Domain | Block as value object; per-block aggregate ID. | business-taxonomy.yaml | Yes |
| Functional Testing | High | Test | Quality gate (95/90% recall) cannot be met without diverse fixtures. | functional-test-plan, E10-F01 | Yes |
| Behavioural UX | High | Behaviour | "Wrong block tag" feedback path missing. | stories | Yes — wire to E11-F05. |
| Architecture | Medium | Arch | Heuristic-only MVP; hint at learned-model upgrade path. | stories | No |
| Data and Ontology | Medium | Onto | Block taxonomy needs canonical enum. | business-taxonomy.yaml | Yes |
| Security and Compliance | Low | Security | No PII new. | — | No |
| Delivery Risk | High | Delivery | If recall gate fails on bench, we lose E2-F04 SLO; risk. | stories | Yes — fallback strategy. |
| Adversarial | Critical | Risk | Adversarial scans (busy backgrounds, noise) are not in bench. | E10-F01 | Yes — add adversarial pages. |
| Team Lead Synthesizer | Critical | All | One Critical; gate. | — | Yes |

## Aggregate Severity
- Critical: 1  High: 4  Medium: 4  Low: 1
- Status: must-fix this iteration.
