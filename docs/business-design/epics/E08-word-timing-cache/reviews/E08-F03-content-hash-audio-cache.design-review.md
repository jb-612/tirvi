# E08-F03 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | High | Product | Cost SLO depends on cache. | — | No |
| DDD | Med | Domain | AudioObject aggregate. | business-taxonomy.yaml | Yes |
| FT | High | Test | Hit-rate measurement required. | functional-test-plan | Yes |
| BX | Med | Behaviour | Coordinator workflow benefits. | — | No |
| Arch | Critical | Arch | Hash schema must be future-proof — bump procedure documented. | stories | Yes |
| Onto | Low | Onto | block_hash value object. | business-taxonomy.yaml | Yes |
| Sec | Med | Sec | Cross-user sharing implications validated by privacy review. | stories | Yes — link to E11-F05. |
| Delivery | Med | Delivery | Voice rotation playbook. | stories | Yes |
| Adv | High | Risk | Cache poisoning if hash includes too little. | stories | Yes |
| Lead | Critical | All | One Critical. | — | Yes |

Critical 1 / High 3 / Medium 4 / Low 2.
