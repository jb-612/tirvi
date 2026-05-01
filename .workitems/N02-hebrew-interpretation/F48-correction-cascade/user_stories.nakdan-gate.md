# N02/F48 — Stage 1 NakdanGate User Stories

## Scope
NakdanGate uses Nakdan's `fnotfromwl` flag to drop "obviously valid" words (~98% pass-through). Source: ADR-033 §Decision step 1.

## Sibling Links
- Parent index: `user_stories.md`
- Adjacent: `user_stories.mlm-scorer.md`, `user_stories.llm-reviewer.md`

## Ontology Refs
- BC: `hebrew_text` (existing)
- Aggregate: `CorrectionCascade` (new BO49); Stage record `StageDecision` (new BO52)
- Collaborator: `NakdanWordList` (new CO13)

## Dependency Refs
- Required by: `mlm-scorer` (only words rejected here proceed)
- Required from: F14 (normalization repairs OCR artifacts before this stage)

---

### Story F48-S01: Word-list filter as the first cascade stage

**As a** pipeline engineer
**I want** every OCR word checked against Nakdan's word-list (`fnotfromwl`) as the first cascade stage
**So that** the ~98% of valid Hebrew words skip the expensive MLM/LLM stages and the per-page latency budget stays under 90s.

#### Context
Empirical: a 214-word page contains ≤ 5 OCR errors. Without an instant gate, every word would hit DictaBERT-MLM (~50 ms each) or worse, the LLM (~1–2 s). NakdanGate is the cost cap.

#### Preconditions
- F14 normalization has stripped wrap chars, ordinals, slash suffixes.
- Nakdan adapter (F19) is initialized; `fnotfromwl` index loaded into memory.

#### Main Flow
1. Cascade receives `(token, sentence_context, sentence_hash)`.
2. NakdanGate calls `nakdan.is_known_word(token)`.
3. **Pass** → `StageDecision(stage="nakdan_gate", verdict="pass", original=token)` returned; downstream stages skipped.
4. **Reject** → `StageDecision(stage="nakdan_gate", verdict="suspect", original=token)`; cascade proceeds to MLM stage.

#### Alternative Flows
- Token contains a digit / Latin letter → emit `verdict="skip_non_hebrew"`; cascade skipped.
- Token already has nikud (Wave 1 fixture path) → strip diacritics for word-list lookup, preserve original.

#### Edge Cases
- Real Hebrew word that *is* an OCR error (e.g., `גורס` for `גורם`) — passes NakdanGate. Caught only by MLM/LLM. **Acknowledged limitation; covered downstream.**
- Multi-word compound (`רב-בְּרֵרָה`) — gate applies per-component after split on `-`.
- Empty token after normalization — skip.

#### Acceptance Criteria
```gherkin
Given a page with 214 OCR words and 5 known errors
When NakdanGate runs against Nakdan's word list
Then ≥ 95% of words exit the cascade with verdict="pass"
And every "suspect" verdict is forwarded to the MLM stage
And the per-token gate latency p95 ≤ 5 ms (in-process word list lookup)
```

```gherkin
Given a token "גורס" that is a real Hebrew verb but a known OCR confusion
When NakdanGate runs
Then verdict="pass" (the gate cannot detect this; it is an acknowledged limitation)
And documented in design as "covered by stage 2 MLM"
```

#### Data and Business Objects
- `StageDecision` (BO52). `CorrectionCascade` (BO49) accumulates these.

#### Dependencies
- F19 Nakdan adapter (provides `is_known_word`).
- ADR-033 §Decision row 1.

#### Non-Functional Considerations
- Privacy: in-process; no network call. Hard rule from ADR-033.
- Performance: ≤ 5 ms per token. Page p95 ≤ 1 s for the full gate stage.
- Determinism: pure function of (token, word-list-version).
- Auditability: every decision recorded in `corrections.json`.

#### Open Questions
- Should NakdanGate fail-open (treat unknown as pass) or fail-closed (treat unknown as suspect) when the word list is unloaded? **Design decision: fail-closed; force MLM stage. See F48-S06.**
