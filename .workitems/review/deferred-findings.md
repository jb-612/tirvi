# Deferred Findings — tirvi Business & Functional Design Phase

Findings that cannot be resolved in this skill's scope. Each entry has an
explicit re-evaluation trigger.

> **`gh issue create` skipped — gh was not authenticated for issue creation
> at the time of this run.** Each row below is structured to be 1:1 portable
> into a GitHub issue using
> `.claude/skills/biz-functional-design/templates/deferred-finding-issue.md`.
> Re-run issue creation after `gh auth login` when ready.

| # | ID | Severity | Area | Reason for Deferral | Affected Files | Business Risk | Technical Risk | Re-Evaluation Trigger | Recommended Owner | Due Condition | Related Epic / Feature | Issue URL |
|---|-----|---------|------|--------------------|----------------|---------------|----------------|----------------------|-------------------|---------------|------------------------|-----------|
| 1 | D-AUDIO-CACHE-LEGAL | Critical | Security / Compliance | Requires Israeli privacy counsel sign-off; outside skill scope | `epics/E08-word-timing-cache/stories/E08-F03-content-hash-audio-cache.stories.md`; `epics/E11-privacy-legal/stories/E11-F01-24h-ttl-automation.stories.md`; `ontology/business-taxonomy.yaml` ASM09 | PPL Amendment 13 violation; product-killing legal exposure | Cost SLO collapses if cross-user cache disallowed; per-session cache fallback path needed | When privacy counsel completes review of ADR-005 (audio-cache exemption) | Legal lead + SRE | Before MVP launch | E08, E11 | [#2](https://github.com/jb-612/tirvi/issues/2) |
| 2 | D-PRD-MOS-LANGUAGE-REWRITE | Critical | Product | Requires `docs/PRD.md` edit; outside skill scope | `docs/PRD.md` §10 | PRD claim collapses on adversarial scrutiny; accommodation-grant programmes reject | Misalignment between PRD and shipped product | When PRD revision PR opens softening §10 ≥ 90% claim to "directional, evidence-backed for practice use" | Product lead | Before MVP launch | E10-F03 | [#3](https://github.com/jb-612/tirvi/issues/3) |
| 3 | D-OCR-BENCH-RUN | High | Functional Test | Requires real bench fixtures + provenance-cleared pages; v1.0 prep work | `epics/E10-quality-validation/stories/E10-F01-tirvi-bench-v0.stories.md`; `epics/E02-ocr-pipeline/stories/E02-F06-ocr-benchmark-harness.stories.md` | Quality gates remain aspirational; ADR-004 cannot close | Tesseract recall claim unverified | When tirvi-bench v0 is populated with 20 provenance-cleared pages | Test author | Before MVP cut | E02, E10 | [#4](https://github.com/jb-612/tirvi/issues/4) |
| 4 | D-MOS-PANEL-EXPAND-V1 | High | Product / Behavioural UX | Requires recruitment ramp for n ≥ 30 dyslexic teen panel | `epics/E10-quality-validation/stories/E10-F03-blind-mos-study.stories.md` | Bagrut-grade claim deferred | MOS gate remains directional only | When v1 panel recruitment pipeline produces ≥ 30 participants | Research lead + ethics | Before v1 launch (post-MVP) | E10-F03 | [#5](https://github.com/jb-612/tirvi/issues/5) |
| 5 | D-SCHEMA-V-OCR | Medium | Architecture | Procedure documented; first migration test deferred to first real version bump | `epics/E02-ocr-pipeline/tests/E02-F03-ocr-result-contract.functional-test-plan.md` | Adapter drift undetected on bump | Consumer code breaks silently | When OCRResult schema v2 lands | SDK maintainer | At first version bump | E02-F03 | [#7](https://github.com/jb-612/tirvi/issues/7) |
| 6 | D-SCHEMA-V-NLP | Medium | Architecture | Procedure documented; first migration test deferred to first real version bump | `epics/E04-nlp-disambiguation/tests/E04-F03-per-token-pos-morph.functional-test-plan.md` | Same as D-SCHEMA-V-OCR for NLPResult | Same | When NLPResult schema v2 lands | SDK maintainer | At first version bump | E04-F03 | [#8](https://github.com/jb-612/tirvi/issues/8) |
| 7 | D-TRANSLIT-BENCH | Medium | Functional Test | Bench fixture expansion; depends on D-OCR-BENCH-RUN | `epics/E03-normalization/stories/E03-F04-mixed-language-detection.stories.md` | Mid-sentence English route applied to Hebrew transliteration; mispronunciation | Span detector precision unmeasured | When tirvi-bench v0 includes ≥ 3 transliteration-density pages | Test author | Before MVP cut | E03-F04 | [#9](https://github.com/jb-612/tirvi/issues/9) |
| 8 | D-VOICE-ROTATION-PLAYBOOK | Medium | DevOps | Playbook documented; ops rehearsal deferred | `epics/E08-word-timing-cache/reviews/E08-F03-content-hash-audio-cache.design-review.md` | Cache-miss flood + cost spike on first rotation | Hit-rate dashboard temporarily misleading | Before first scheduled voice rotation event | SRE | Before first rotation | E08-F03 | [#10](https://github.com/jb-612/tirvi/issues/10) |
| 9 | D-BLOCK-TAXONOMY-V1 | Medium | DDD | Footnote / sidenote / rubric block types deferred to v1.1 | `epics/E02-ocr-pipeline/stories/E02-F04-block-segmentation.stories.md`; `ontology/business-taxonomy.yaml` BO10 | Recall floor depends on default-paragraph fallback | Adversarial bagrut content under-tagged | After tirvi-bench v0 results show recall floor breach risk | Backend dev + lexicon maintainer | v1.1 release window | E02-F04 | [#11](https://github.com/jb-612/tirvi/issues/11) |
| 10 | D-COREF-MVP-SCOPE | Medium | Delivery | E04-F04 HebPipe coref MVP-vs-v1.1 decision pending quality measurement | `epics/E04-nlp-disambiguation/stories/E04-F04-hebpipe-coref.stories.md` | Long-passage pronunciation marginal vs lemma-only baseline | Latency cost without measured benefit | Once HebPipe lift is benchmarked on tirvi-bench v0 | Backend dev | Before v1 launch | E04-F04 | [#12](https://github.com/jb-612/tirvi/issues/12) |
| 11 | D-COORD-BULK-V1 | Medium | Behavioural UX | Coordinator class roster + sharing scoped to v1 | `epics/E01-document-ingest/reviews/E01-F03-per-page-status.design-review.md`; `epics/E01-document-ingest/reviews/E01-F04-delete-with-cascade.design-review.md` | Schools cannot adopt without bulk flows; GTM weakened | Coordinator persona behaviourally underdeveloped in MVP | After MVP launch + first school pilot feedback | Product + UX | v1 release | E01 | [#13](https://github.com/jb-612/tirvi/issues/13) |
| 12 | D-LIFECYCLE-AUDIO-LEGAL-FOLLOWUP | High | Compliance | Linked to D-AUDIO-CACHE-LEGAL; lifecycle automation for `audio/` blocked on legal sign-off | `epics/E11-privacy-legal/stories/E11-F01-24h-ttl-automation.stories.md` | Same as D-AUDIO-CACHE-LEGAL | Lifecycle config cannot finalize until exemption confirmed | When D-AUDIO-CACHE-LEGAL closes | SRE | Before MVP launch | E11-F01 | [#6](https://github.com/jb-612/tirvi/issues/6) |

## Issue Creation Status

All 12 deferred-finding rows above were created as GitHub issues using
`gh issue create` with labels `design-deferred` and `severity:critical|high|medium`:

| ID | Issue |
|----|------|
| D-AUDIO-CACHE-LEGAL | [#2](https://github.com/jb-612/tirvi/issues/2) |
| D-PRD-MOS-LANGUAGE-REWRITE | [#3](https://github.com/jb-612/tirvi/issues/3) |
| D-OCR-BENCH-RUN | [#4](https://github.com/jb-612/tirvi/issues/4) |
| D-MOS-PANEL-EXPAND-V1 | [#5](https://github.com/jb-612/tirvi/issues/5) |
| D-LIFECYCLE-AUDIO-LEGAL-FOLLOWUP | [#6](https://github.com/jb-612/tirvi/issues/6) |
| D-SCHEMA-V-OCR | [#7](https://github.com/jb-612/tirvi/issues/7) |
| D-SCHEMA-V-NLP | [#8](https://github.com/jb-612/tirvi/issues/8) |
| D-TRANSLIT-BENCH | [#9](https://github.com/jb-612/tirvi/issues/9) |
| D-VOICE-ROTATION-PLAYBOOK | [#10](https://github.com/jb-612/tirvi/issues/10) |
| D-BLOCK-TAXONOMY-V1 | [#11](https://github.com/jb-612/tirvi/issues/11) |
| D-COREF-MVP-SCOPE | [#12](https://github.com/jb-612/tirvi/issues/12) |
| D-COORD-BULK-V1 | [#13](https://github.com/jb-612/tirvi/issues/13) |

When any item closes (re-evaluation trigger met), update the row's status
in this file and close the corresponding GitHub issue. The issue body uses
the deferred-finding-issue.md template fields (Severity / Area / Reason /
Affected Files / Business Risk / Technical Risk / Re-Evaluation Trigger /
Recommended Owner / Due Condition / Related Review Finding / Related Epic
and Feature).

---

## Append: N02/F48 Hebrew correction cascade — deferred findings

> **Issue stubs only — `gh issue create` was NOT called for this batch** per the
> @biz-functional-design Stage 14 instruction in this run's spec. Each row is
> portable into a GitHub issue via the deferred-finding-issue template once
> approved by the user.

| # | ID | Severity | Area | Reason for Deferral | Affected Files | Business Risk | Technical Risk | Re-Evaluation Trigger | Recommended Owner | Due Condition | Related Feature | Issue URL |
|---|-----|---------|------|--------------------|----------------|---------------|----------------|----------------------|-------------------|---------------|-----------------|-----------|
| F48-1 | D-RECALL-BENCH | Critical | Functional Test | F40 quality-gates wiring + F39 bench page count needed; F48 ships scaffold only | `.workitems/N02-hebrew-interpretation/F48-correction-cascade/functional-test-plan.md`, `user_stories.md`, `ontology-delta.yaml` ASM12 | "≥ 90% recall" PRD claim cannot be validated against a real corpus until F39 lands | F48 quality target unmeasured; regressions silent | When F39 tirvi-bench-v0 has ≥ 20 provenance-cleared pages with OCR-error labels AND F40 quality-gates wires F48 metrics | Test author + product lead | Before MVP launch | N02/F48 + N05/F39 + N05/F40 | (stub) |
| F48-2 | D-FAST-TIER-AB | Medium | Product / Architecture | Llama 3.1 8B vs Gemma 3 4B fast-tier A/B requires runtime; defer until F48 ships | `user_stories.llm-reviewer.md` open questions, ADR-033 §Decision | Quality / latency trade-off unknown for fast tier | Wrong default may degrade UX | When F48 lands and 1 month of runtime data is available | Pipeline engineer | Post-MVP tuning window | N02/F48 | (stub) |
| F48-3 | D-AUTO-PROMOTE-POLICY | Medium | Adversarial / Security | Anti-Sybil + auto-promote policy beyond MVP; per-sha cap is partial | `user_stories.feedback-loop.md` open questions | Spam-driven false rule promotion possible if uploader can fabricate distinct shas | Lexicon poisoning vector | When auth lands (post-MVP, see ASM07) | Engineer + security review | Post-MVP | N02/F48 + post-MVP auth | (stub) |
| F48-4 | D-LOG-INTEGRITY | Low | Compliance | Signature on `corrections.json` not in MVP scope; on-device only mitigates | `behavioural-test-plan.md` Misuse Behaviour | Forged audit trail in adversarial setting | Trust regression for QA flow | When MVP+1 introduces multi-user trust boundary | SRE + product | v1.1 | N02/F48 | (stub) |

**F48 deferred tally**: 1 Critical · 0 High · 2 Medium · 1 Low — all carry explicit re-evaluation triggers.

---

## Append: N01/F49 CLI pipeline progress reporting — deferred findings

> **Issue stubs only — `gh issue create` not called for this batch** (same
> pattern as F48: portable to GitHub issues via the deferred-finding-issue
> template once approved by the user).

| # | ID | Severity | Area | Reason for Deferral | Affected Files | Business Risk | Technical Risk | Re-Evaluation Trigger | Recommended Owner | Due Condition | Related Feature | Issue URL |
|---|-----|---------|------|--------------------|----------------|---------------|----------------|----------------------|-------------------|---------------|-----------------|-----------|
| F49-1 | D-F49-ONTOLOGY-WRITE | Medium | Ontology | `ontology/*.yaml` is a protected path (orchestrator.md); HITL required to write business_domains/dependencies/testing YAML additions for F49 | `ontology/business-domains.yaml`, `ontology/dependencies.yaml`, `ontology/testing.yaml` | Ontology cross-walk incomplete until F49 biz objects registered; traceability queries miss F49 | No implementation risk; design artefacts are complete in workitem folder | When user explicitly authorizes ontology YAML update via HITL gate | Repository owner | Before sw-designpipeline run for F49 | N01/F49 | (stub) |
| F49-2 | D-F49-ARCH-02 | Medium | Architecture | `rich` ImportError guard — production image may not have `rich`; guard needed in ProgressReporter constructor | `tirvi/pipeline.py` (future), `scripts/run_demo.py` (future) | Pipeline crashes if `rich` absent; plain-log fallback not activated | Minor; guard is a 3-line try/except | Implement during TDD Green phase for ProgressReporter | TDD code-writer | TDD T-xx green | N01/F49 | (stub) |
| F49-3 | D-F49-ADV-02 | Medium | Architecture | Thread-safety: if `run_page` is ever parallelized, shared ProgressReporter counter would be racy; must document non-thread-safe assumption | `tirvi/correction/service.py` design notes | Future parallelization silently corrupts progress counters | Low risk today (sequential); risk increases with future refactors | When sw-designpipeline adds design notes for ProgressReporter; note non-thread-safe contract explicitly | sw-designpipeline | Before sw-design closes | N01/F49 | (stub) |
| F49-4 | D-F49-ADV-04 | Low | Robustness | atexit/finally flush — if Ctrl-C is pressed during pipeline execution, summary table not printed | `scripts/run_demo.py` main() | Minor UX annoyance; operator loses timing data on abort | Trivial fix (try/finally around run_pipeline call) | TDD task for ProgressReporter cleanup path | TDD code-writer | TDD implementation | N01/F49 | (stub) |

**F49 deferred tally**: 0 Critical · 0 High · 3 Medium · 1 Low — all carry explicit re-evaluation triggers.
Low items (F49-ARCH-03, F49-TEST-01, F49-TEST-02, F49-TEST-03) are tracked in
design-review.md and will be picked up by TDD; not elevated to this file.
