# N02/F48 — Feedback Loop User Stories

## Scope
Student/teacher marks "wrong" in F50 inspector → sqlite at `drafts/feedback.db` → after ≥ 3 occurrences, system suggests promoting to a permanent rule. RL-light per UAT-2026-05-01-why-models-miss §"feedback loop".

## Sibling Links
- Parent: `user_stories.md`
- Adjacent: `user_stories.correction-log.md`

## Ontology Refs
- BC: `hebrew_text` (rule promotion) + `player` (UI capture).
- BO56 `FeedbackEntry`, BO46 `FeedbackEntry` (existing — extend), Lexicon (existing BO15).

## Dependency Refs
- Required from: F50 inspector (capture surface), F47 feedback-capture (existing minimal MVP).
- Promotes to: F21 homograph-overrides, future F49 lexicon governance.

---

### Story F48-S05: Threshold-gated rule promotion from feedback

**As a** pipeline engineer (and indirectly: any future student running the same exam type)
**I want** the same OCR confusion reported by ≥ 3 distinct sessions to *suggest* promotion to a permanent rule
**So that** my engineering effort scales — instead of growing `_KNOWN_OCR_FIXES` by hand, I review a queue of evidence-backed suggestions.

#### Context
UAT §"feedback loop" + ADR-033 §Consequences "self-improving via feedback loop". Hard rule: ≥ 3 occurrences before suggestion. Engineer tunes thresholds, prompts, model versions; evidence comes from the same sqlite.

#### Preconditions
- F50 inspector has a "Mark as wrong" affordance per word.
- A local sqlite at `drafts/feedback.db` initialized (schema versioned).
- Cascade has been running and accumulating `corrections.json`.

#### Main Flow
1. Teacher / student clicks "this is wrong" on a corrected token in F50.
2. F50 writes a `FeedbackEntry(sha, mark_id, ocr_word, system_chose, expected, ts, persona_role)` to sqlite.
3. Cascade reads sqlite at start of next run; revert any token whose `(ocr_word, sentence_context_hash, system_chose)` is in the *user-rejected* set; preference cached for that draft.
4. Background aggregator script (cron / on-demand) groups by `(ocr_word, expected)` across all rows; emits suggestions when count ≥ 3 from ≥ 2 distinct shas.
5. Suggestion file `drafts/rule_suggestions.json` lists `{pattern, support_count, distinct_shas, sample_contexts}`.
6. Engineer reviews; if accepted, appends to `tirvi/normalize/confusion_pairs.yaml` (Stage 2 input) or to homograph lexicon (F21).

#### Alternative Flows
- Same correction reverted by one teacher but accepted by another → both votes recorded; suggestion only fires when *net* count ≥ 3.
- Feedback for a deprecated rule (`_KNOWN_OCR_FIXES`) → record but mark "deprecated_path"; engineer cleanup task.

#### Edge Cases
- sqlite missing / locked → skip read silently; pipeline continues without preference cache.
- Two distinct teachers disagree on the *expected* form → both forms recorded; suggestion is per-pair, support count includes only matching expected form.
- Adversarial spam (one user marking everything wrong) → cap per-sha contribution to count; suggestion requires ≥ 2 distinct shas.

#### Acceptance Criteria
```gherkin
Given a teacher marks "גורס" (system kept original) as wrong, with expected="גורם", in 3 distinct drafts
When the aggregator runs
Then drafts/rule_suggestions.json contains a suggestion for pattern (ocr="גורס", correct="גורם")
And support_count = 3
And distinct_shas = 3
And the suggestion is NOT auto-applied
```

```gherkin
Given the same teacher marks the same correction wrong 5 times in one draft
When the aggregator runs
Then support_count = 1 (per-sha cap)
And no suggestion is emitted yet
```

```gherkin
Given an engineer accepts a suggestion and appends it to confusion_pairs.yaml
When the cascade runs again
Then the new pair contributes candidates in stage 2
And subsequent runs catch the same OCR error automatically
```

```gherkin
Given a student marks a correction wrong on draft <sha>
When the cascade runs the same draft <sha> again
Then the rejected correction is reverted (preference cached)
And future drafts are unaffected until the rule is promoted
```

#### Data and Business Objects
- `FeedbackEntry` — extend BO46 with optional `system_chose` and `persona_role`.
- `RuleSuggestion(pattern, support_count, distinct_shas, sample_contexts)` — BO56 (new).

#### Dependencies
- F47 feedback capture (minimal MVP record).
- F50 inspector "Mark as wrong" UI.
- F21 homograph overrides (one promotion target).

#### Non-Functional Considerations
- Privacy: sqlite stays on-device. No PII; only OCR token + expected token + ts.
- Performance: aggregator is background; not in pipeline hot path.
- Auditability: every promotion suggestion cites the source FeedbackEntry rows.
- Compliance: retention follows F43 TTL on the parent draft; aggregated suggestions outlive the draft (token-only).

#### Open Questions
- Cross-document privacy boundary — can a suggestion include sample contexts from a deleted draft? Default: no; sample_contexts only retained as long as parent draft exists. Captured in design.md.
- Auto-promote after very high support (e.g., 50+)? Defer; spec says ≥ 3 *suggests*; auto-apply requires explicit engineer toggle (`D-AUTO-PROMOTE-POLICY`).
