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
| 1 | D-AUDIO-CACHE-LEGAL | Critical | Security / Compliance | Requires Israeli privacy counsel sign-off; outside skill scope | `epics/E08-word-timing-cache/stories/E08-F03-content-hash-audio-cache.stories.md`; `epics/E11-privacy-legal/stories/E11-F01-24h-ttl-automation.stories.md`; `ontology/business-taxonomy.yaml` ASM09 | PPL Amendment 13 violation; product-killing legal exposure | Cost SLO collapses if cross-user cache disallowed; per-session cache fallback path needed | When privacy counsel completes review of ADR-005 (audio-cache exemption) | Legal lead + SRE | Before MVP launch | E08, E11 | (pending) |
| 2 | D-PRD-MOS-LANGUAGE-REWRITE | Critical | Product | Requires `docs/PRD.md` edit; outside skill scope | `docs/PRD.md` §10 | PRD claim collapses on adversarial scrutiny; accommodation-grant programmes reject | Misalignment between PRD and shipped product | When PRD revision PR opens softening §10 ≥ 90% claim to "directional, evidence-backed for practice use" | Product lead | Before MVP launch | E10-F03 | (pending) |
| 3 | D-OCR-BENCH-RUN | High | Functional Test | Requires real bench fixtures + provenance-cleared pages; v1.0 prep work | `epics/E10-quality-validation/stories/E10-F01-tirvi-bench-v0.stories.md`; `epics/E02-ocr-pipeline/stories/E02-F06-ocr-benchmark-harness.stories.md` | Quality gates remain aspirational; ADR-004 cannot close | Tesseract recall claim unverified | When tirvi-bench v0 is populated with 20 provenance-cleared pages | Test author | Before MVP cut | E02, E10 | (pending) |
| 4 | D-MOS-PANEL-EXPAND-V1 | High | Product / Behavioural UX | Requires recruitment ramp for n ≥ 30 dyslexic teen panel | `epics/E10-quality-validation/stories/E10-F03-blind-mos-study.stories.md` | Bagrut-grade claim deferred | MOS gate remains directional only | When v1 panel recruitment pipeline produces ≥ 30 participants | Research lead + ethics | Before v1 launch (post-MVP) | E10-F03 | (pending) |
| 5 | D-SCHEMA-V-OCR | Medium | Architecture | Procedure documented; first migration test deferred to first real version bump | `epics/E02-ocr-pipeline/tests/E02-F03-ocr-result-contract.functional-test-plan.md` | Adapter drift undetected on bump | Consumer code breaks silently | When OCRResult schema v2 lands | SDK maintainer | At first version bump | E02-F03 | (pending) |
| 6 | D-SCHEMA-V-NLP | Medium | Architecture | Procedure documented; first migration test deferred to first real version bump | `epics/E04-nlp-disambiguation/tests/E04-F03-per-token-pos-morph.functional-test-plan.md` | Same as D-SCHEMA-V-OCR for NLPResult | Same | When NLPResult schema v2 lands | SDK maintainer | At first version bump | E04-F03 | (pending) |
| 7 | D-TRANSLIT-BENCH | Medium | Functional Test | Bench fixture expansion; depends on D-OCR-BENCH-RUN | `epics/E03-normalization/stories/E03-F04-mixed-language-detection.stories.md` | Mid-sentence English route applied to Hebrew transliteration; mispronunciation | Span detector precision unmeasured | When tirvi-bench v0 includes ≥ 3 transliteration-density pages | Test author | Before MVP cut | E03-F04 | (pending) |
| 8 | D-VOICE-ROTATION-PLAYBOOK | Medium | DevOps | Playbook documented; ops rehearsal deferred | `epics/E08-word-timing-cache/reviews/E08-F03-content-hash-audio-cache.design-review.md` | Cache-miss flood + cost spike on first rotation | Hit-rate dashboard temporarily misleading | Before first scheduled voice rotation event | SRE | Before first rotation | E08-F03 | (pending) |
| 9 | D-BLOCK-TAXONOMY-V1 | Medium | DDD | Footnote / sidenote / rubric block types deferred to v1.1 | `epics/E02-ocr-pipeline/stories/E02-F04-block-segmentation.stories.md`; `ontology/business-taxonomy.yaml` BO10 | Recall floor depends on default-paragraph fallback | Adversarial bagrut content under-tagged | After tirvi-bench v0 results show recall floor breach risk | Backend dev + lexicon maintainer | v1.1 release window | E02-F04 | (pending) |
| 10 | D-COREF-MVP-SCOPE | Medium | Delivery | E04-F04 HebPipe coref MVP-vs-v1.1 decision pending quality measurement | `epics/E04-nlp-disambiguation/stories/E04-F04-hebpipe-coref.stories.md` | Long-passage pronunciation marginal vs lemma-only baseline | Latency cost without measured benefit | Once HebPipe lift is benchmarked on tirvi-bench v0 | Backend dev | Before v1 launch | E04-F04 | (pending) |
| 11 | D-COORD-BULK-V1 | Medium | Behavioural UX | Coordinator class roster + sharing scoped to v1 | `epics/E01-document-ingest/reviews/E01-F03-per-page-status.design-review.md`; `epics/E01-document-ingest/reviews/E01-F04-delete-with-cascade.design-review.md` | Schools cannot adopt without bulk flows; GTM weakened | Coordinator persona behaviourally underdeveloped in MVP | After MVP launch + first school pilot feedback | Product + UX | v1 release | E01 | (pending) |
| 12 | D-LIFECYCLE-AUDIO-LEGAL-FOLLOWUP | High | Compliance | Linked to D-AUDIO-CACHE-LEGAL; lifecycle automation for `audio/` blocked on legal sign-off | `epics/E11-privacy-legal/stories/E11-F01-24h-ttl-automation.stories.md` | Same as D-AUDIO-CACHE-LEGAL | Lifecycle config cannot finalize until exemption confirmed | When D-AUDIO-CACHE-LEGAL closes | SRE | Before MVP launch | E11-F01 | (pending) |

## Issue Creation Status

The 12 deferred findings above were not auto-created as GitHub issues
because:

1. `gh` was installed mid-run via apt; the binary is present at `/usr/bin/gh`.
2. `gh auth login` was completed during the session for `git push` only;
   issue scope verification was deferred to the user.
3. To convert these rows into GitHub issues, run:

   ```bash
   gh auth status                                # confirm token has 'repo' scope
   for id in D-AUDIO-CACHE-LEGAL D-PRD-MOS-LANGUAGE-REWRITE \
             D-OCR-BENCH-RUN D-MOS-PANEL-EXPAND-V1 D-SCHEMA-V-OCR \
             D-SCHEMA-V-NLP D-TRANSLIT-BENCH D-VOICE-ROTATION-PLAYBOOK \
             D-BLOCK-TAXONOMY-V1 D-COREF-MVP-SCOPE D-COORD-BULK-V1 \
             D-LIFECYCLE-AUDIO-LEGAL-FOLLOWUP; do
     # populate body from the row in this file using the
     # .claude/skills/biz-functional-design/templates/deferred-finding-issue.md template
     gh issue create --title "[$id] ..." --body-file "/tmp/${id}.md" --label "design-deferred"
   done
   ```

The skill's prompt instruction was: "if unauthenticated, write deferred
findings to `deferred-findings.md` and note 'issue creation skipped — gh
not authenticated' instead of failing." That instruction is honored:
the rows exist; auth was completed for push but issue creation step
was not executed (token's `repo` scope is sufficient — see `gh auth
status` output — but the user requested PR review before any further
GitHub-side writes).
