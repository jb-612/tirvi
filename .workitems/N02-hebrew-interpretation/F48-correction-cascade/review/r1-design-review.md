# F48 design review — Round 1 (sw-pipeline)

Mode: **inline / lite** — biz already ran the full 10-reviewer + adversary
loop (see `design-review.md`). R1 here covers ONLY the sw-layer artifacts
(`design.md`, ADR-034, ADR-035, diagrams).

## Reviewers (this round)
| Role | Focus |
|------|-------|
| HLD compliance | every DE → HLD ref resolves; no architecture drift |
| Hexagonal / DDD | port surfaces, aggregate boundary, value-object purity |
| Determinism + caching | cache-key shape; replayable; invalidates safely |
| Privacy + audit | localhost-only invariant; `corrections.json` 100% target |
| Coverage adversary | every FT/BT/AC has a target DE/decision |

## Findings

| ID | Severity | Reviewer | Finding | Status |
|----|----------|----------|---------|--------|
| F48-SW-1 | Medium | HLD compliance | Was using `HLD §5.4` for feedback loop — needed to confirm the section exists | **Resolved** — `validate-hld-refs.sh` PASS on §5.4 (HLD §5.4 "Feedback loop") |
| F48-SW-2 | High | DDD | `CorrectionCascade` aggregate could leak across pages if service caches it | **Resolved** in DE-05: aggregate is *transient per page* (matches biz F48-R1-3); never persisted |
| F48-SW-3 | High | Determinism | Original cache key did not include candidate ordering → key drift | **Resolved** in ADR-034: `sorted(candidates)` always; canonical join with `\|` |
| F48-SW-4 | High | Privacy | Cache living under `~/.tirvi` would survive draft delete → privacy invariant violated | **Resolved** in ADR-034: cache under `drafts/<sha>/llm_cache.sqlite`; F43 TTL applies |
| F48-SW-5 | Medium | Privacy | `corrections.json` writes during degraded mode could miss model_versions | **Resolved** in ADR-035: model_versions is required; LLM keys omitted only when mode=no_llm |
| F48-SW-6 | Medium | Coverage | NT-01 (confusion-table missing) not visible in design — implicit only | **Resolved** by tasks T-08 below: add explicit `ConfusionTableMissing` typed error in DE-03 |
| F48-SW-7 | Low | DDD | `LLMReviewer` mixes HTTP and domain logic | **Resolved** by splitting `LLMClientPort` (transport) from `OllamaLLMReviewer` (domain) per DE-04 |
| F48-SW-8 | Medium | Coverage adversary | BT-218 (banner copy) needs F50 collaboration — could block F48 ship | **Acknowledged**: F48 emits the structured event with mode field; F50 owns banner copy. Recorded in DE-07 + DEP-055. |
| F48-SW-9 | Low | Determinism | Per-page LLM cap at 10 is hardcoded in design — should be a config knob | **Resolved**: cap is config field on `CorrectionCascadeService`; default 10. |
| F48-SW-10 | High | Coverage | FT-322 cache-hit verification needs test seam — `LLMClient` must be a port | **Resolved** in DE-04: `LLMClientPort` is the testable seam |
| F48-SW-11 | Medium | DDD | `FeedbackAggregator` reads sqlite — should it be a port too, or a script? | **Resolved**: aggregator is a *script* (cron / on-demand) under `tirvi/correction/feedback_aggregator.py`; cascade init reads sqlite directly via `FeedbackReadPort` to keep boundary clean |
| F48-SW-12 | Low | HLD compliance | Biz design referenced `gemma3:27b` — wrong identifier for the user's environment | **Resolved**: design.md uses `gemma4:31b-nvfp4` (primary) and `llama3.1:8b` (fast tier) per the user's local Ollama |

## Adversarial pokes

- *"What if Ollama is up but the model wasn't pulled?"* — DE-07 treats it
  as `no_llm` mode (BT-213 alt flow); structured warning carries the
  missing-model hint. Covered.
- *"What if a future ADR re-shapes `corrections.json`?"* —
  `corrections_schema_version` integer + F50 reader gates on version.
  Tested via FT-323 schema validation.
- *"What if Tesseract starts producing 3-character confusion runs that
  the single-site swap can't catch?"* — Acknowledged limitation in DE-03;
  multi-site behind a flag, default off. New confusion classes that need
  multi-site become engineer follow-ups via the feedback loop, not
  silent regressions.

## Outcome

- 0 Critical open
- 0 High open (all 4 resolved in design.md / ADR-034 / ADR-035)
- 0 Medium open (all 5 resolved or acknowledged + tracked)
- 1 Low open: configurable LLM-call cap default — already a config field; doc-only.

R1 closed. Proceeding to revision pass + R2.
