# E04-F01 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | High | Product | Backbone of differentiator; SLO ≥ 92% UD-Hebrew. | stories | No |
| DDD | Med | Domain | NLP context owns segmentation, lemma, morph. | business-taxonomy.yaml | Yes |
| FT | High | Test | Bench coverage on math/civics needed. | functional-test-plan, E10-F01 | Yes |
| BX | Med | Behaviour | Margin tuning open. | — | No |
| Arch | High | Arch | Sidecar vs in-process decision blocks E0/E11. | stories | Yes |
| Onto | Med | Onto | NLPResult, Token, MorphFeatures taxonomy. | business-taxonomy.yaml | Yes |
| Sec | Low | Sec | None. | — | No |
| Delivery | High | Delivery | DictaBERT model size ≈ 1.5 GB; profile gating mandatory. | stories | Yes |
| Adv | High | Risk | If DictaBERT unavailable in dev for an extended period; fallback path must be CI-tested. | functional-test-plan | Yes |
| Lead | High | All | Multiple Highs. | — | Yes |

Critical 0 / High 5 / Medium 3 / Low 2. Iteration 1 must-fix.
