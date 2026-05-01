# N02/F48 — CorrectionLog User Stories

## Scope
Reasoning trail for every correction. Saved to `drafts/<sha>/corrections.json`. Surfaced in F50 inspector OCR tab.

## Sibling Links
- Parent: `user_stories.md`
- Adjacent: `user_stories.feedback-loop.md`

## Ontology Refs
- BC: `hebrew_text` + `privacy_compliance` (no PII; document-scoped).
- BO55 `CorrectionLogEntry`, BO49 `CorrectionCascade`.

## Dependency Refs
- Required from: stages 1–3 (each emit `StageDecision`).
- Required by: F47 feedback capture, F50 inspector, F45 no-PII logging audit.

---

### Story F48-S04: Auditable correction trail per draft

**As a** teacher / QA reviewer
**I want** every correction recorded with the full reasoning trail (which stage caught it, scores, candidates, LLM verbatim, model versions)
**So that** I can verify in the F50 inspector that a `גורס → גורם` change is justified before signing off — and so that disputes against pronunciation choices have an evidence file.

#### Context
ADR-033 §Consequences "Auditable" + spec hard rule "100% of corrections have a reasoning trail". UAT-2026-05-01-tts-quality recommends recommendation #1 ("OCR fix list will grow…") which depends on this trail being machine-readable.

#### Preconditions
- A pipeline run produced a draft at `drafts/<sha>/`.
- Cascade ran for at least one suspect token.

#### Main Flow
1. For each token, accumulate `StageDecision` rows from stages 1–3.
2. After page completes, write `drafts/<sha>/corrections.json` (ndjson or single JSON; final shape captured in design.md by sw-pipeline).
3. Each entry: `CorrectionLogEntry(token_id, original, corrected_or_null, stages: [{stage, verdict, scores?, candidates?, llm_response?}], page_index, sentence_hash, model_versions, prompt_template_version, ts_iso, cache_hit_chain)`.
4. Pass-through tokens (NakdanGate verdict="pass") are NOT logged by default; engineer flag `--log-passthrough` enables for debugging.
5. F50 inspector OCR tab loads this file when the user opens the version.

#### Alternative Flows
- Cascade was skipped (degraded mode + deprecated fixes only) → log entry uses stage `"deprecated_fixes"` with the matched rule id.
- Page contains zero corrections → emit empty `corrections.json` (existence is evidence).

#### Edge Cases
- File write fails (disk full) → log warning, do NOT fail the pipeline; continue with audit gap recorded in `audit_gaps.json`.
- Multi-MB log on 1000-page documents → chunk per page (`drafts/<sha>/corrections.<page>.json`), index file lists chunks.
- Backwards-incompatible schema change → bump `corrections_schema_version`; F50 reader gates on version.

#### Acceptance Criteria
```gherkin
Given a page with 5 OCR errors
When the cascade runs to completion
Then drafts/<sha>/corrections.json contains 5 CorrectionLogEntry records
And every record has stages, model_versions, prompt_template_version, ts_iso
And every record's chosen correction matches the diacritized output token
```

```gherkin
Given a teacher opens F50 inspector OCR tab for the draft
When they hover a corrected word
Then the reasoning trail (NakdanGate verdict, MLM scores, LLM verdict, reason) is rendered
And the original OCR text is shown side by side with the corrected text
```

```gherkin
Given the file write fails because the disk is full
When the cascade tries to persist corrections.json
Then the pipeline does NOT abort
And audit_gaps.json records the page index and sha and timestamp
And the run-level summary marks the page "audit-incomplete"
```

#### Data and Business Objects
- `CorrectionLogEntry` — BO55.
- `CorrectionCascade` — BO49 (the per-page aggregate).

#### Dependencies
- Storage layer (write to `drafts/`).
- F50 inspector reader (consumer).
- F45 no-PII logging — assert no PII fields in `corrections.json`.

#### Non-Functional Considerations
- Privacy: file is on-device; document-scoped; subject to F43 24h TTL when document is deleted.
- Auditability: 100% target — measured on every CI page run.
- Performance: log write ≤ 100 ms per page.
- Reliability: write failures degrade gracefully; do not fail pipeline.
- Compliance: subject to retention policy (BO06 RetentionPolicy).
- Schema: versioned; F50 inspector pins major version.

#### Open Questions
- Should `corrections.json` be encrypted at rest? Defer; on-device only, follows existing draft policy.
- ndjson vs JSON object — sw-pipeline decides (performance trade-off for 1000-page docs).
