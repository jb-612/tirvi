# F48 design review — Round 2 (sw-pipeline)

Mode: **inline / lite** — confirms R1 fixes landed and no regression.

## R1 fixes verified

| R1 ID | Fix landed in | Status |
|-------|---------------|--------|
| F48-SW-1 | (validation only — HLD §5.4 exists) | Verified |
| F48-SW-2 | design.md DE-05 ("transient per page") | Verified |
| F48-SW-3 | ADR-034 `sorted(candidates)` + `\|` separator | Verified |
| F48-SW-4 | ADR-034 cache lives under `drafts/<sha>/llm_cache.sqlite` | Verified |
| F48-SW-5 | ADR-035 `model_versions` required; LLM keys conditional | Verified |
| F48-SW-6 | tasks.md T-08 — `ConfusionTableMissing` typed error | Verified |
| F48-SW-7 | design.md DE-04 splits `LLMClientPort` from `OllamaLLMReviewer` | Verified |
| F48-SW-8 | design.md DE-07 — F48 emits event; F50 owns banner copy | Acknowledged (cross-feature) |
| F48-SW-9 | design.md DE-04 LLM-call cap is config field | Verified |
| F48-SW-10 | design.md DE-04 — `LLMClientPort` is the test seam | Verified |
| F48-SW-11 | design.md DE-08 — aggregator is script; cascade reads via `FeedbackReadPort` | Verified |
| F48-SW-12 | design.md uses `gemma4:31b-nvfp4` + `llama3.1:8b` | Verified |

## Coverage cross-check

| Source set | Count | All mapped to ≥ 1 DE/Task? |
|------------|-------|----------------------------|
| Stories F48-S01..S06 | 6 | yes (S01→DE-02, S02→DE-03, S03→DE-04, S04→DE-06, S05→DE-08, S06→DE-07) |
| FT-316..FT-330 | 15 | yes (see `traceability.yaml` `tests[]`) |
| BT-209..BT-220 | 12 | yes (every BT has at least one task pointing at the DE the BT exercises) |
| NT-01..NT-05 | 5 | yes (NT-01→T-08; NT-02→T-04; NT-03→T-04; NT-04→T-02; NT-05→T-04) |
| BT-F-01..BT-F-05 | 5 | yes (boundary tests covered by T-02/T-03/T-04/T-05) |
| AUD-01..AUD-03 | 3 | yes (T-06, T-07) |
| INT-01..INT-05 | 5 | yes (Track C — `@integration-test` after Track A green) |

## Outcome

- 0 Critical / 0 High / 0 Medium / 0 Low open
- HLD ref validation: PASS
- Biz coverage gaps: 0
- Cross-feature contracts captured: F50 (DEP-055), F47 (DEP-054)

R2 closed. Ready for User Gate.
