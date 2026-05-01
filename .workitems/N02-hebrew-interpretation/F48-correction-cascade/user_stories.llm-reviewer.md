# N02/F48 — Stage 3 LLMReviewer User Stories

## Scope
Final reviewer for ambiguous tokens. Gemma 3 27B (or 4B fast tier) via local Ollama. Optional Llama 3.1 8B fast lane. Source: ADR-033 §Decision step 3; UAT root cause for "models read meaning, not surface".

## Sibling Links
- Parent: `user_stories.md`
- Upstream: `user_stories.mlm-scorer.md`
- Adjacent: `user_stories.degradation.md` (Ollama down)

## Ontology Refs
- BC: `hebrew_text`
- BO53 `LLMReviewVerdict`, BO54 `LLMPromptTemplate`, BO52 `StageDecision`
- CO15 `LLMReviewer (Ollama)`

## Dependency Refs
- Required from: F17 DictaBERT (only via candidate set), local Ollama runtime.
- Required by: F19 Nakdan (post-correction diacritization), F23 SSML (final text).

---

### Story F48-S03: Local Gemma reviewer for ambiguous-stage MLM verdicts

**As a** dyslexic Hebrew student
**I want** the cascade to ask a local LLM "is this Hebrew sentence semantically and grammatically valid? if not, which word should be replaced and why?" for ambiguous OCR words
**So that** the model reads MEANING — catching errors like `גורם → גורס` that have identical surface validity but are semantically wrong in context — without my exam content ever leaving the M4 Max.

#### Context
ADR-033 §Decision row 3: stage 3 fires when stage 2 returns `verdict="ambiguous"` (delta in `[1.0, 3.0]` or multiple high-scoring candidates). Empirical: Gemma 3 27B reads meaning; Llama 3.1 8B is faster but less accurate on Hebrew.

#### Preconditions
- Stage 2 emitted `verdict="ambiguous"` with top-3 candidates.
- Ollama daemon reachable at `http://127.0.0.1:11434` (default).
- Configured model `gemma3:27b` (default) or `gemma3:4b` (fast tier) is pulled.

#### Main Flow
1. Build prompt from `LLMPromptTemplate` (BO54): include sentence, original token, top-3 MLM candidates, instruction.
2. POST to Ollama `/api/generate` with `temperature=0`, `seed=0`, model from config.
3. Parse JSON-formatted response: `{verdict: "OK"|"REPLACE", chosen: <token_or_null>, reason: <string>}`.
4. **Verdicts**:
   - `OK` → `verdict="keep_original"`; record reason.
   - `REPLACE` with `chosen` ∈ candidate set AND `chosen ∈ NakdanWordList` → `verdict="apply"`.
   - `REPLACE` with `chosen` ∉ candidate set OR ∉ NakdanWordList → reject hallucination; `verdict="keep_original"`; log warning.
5. Cache by `cache_key = sha256(model_id + prompt_template_version + sentence + token + sorted(candidates))`.
6. Record `LLMReviewVerdict` (BO53) in `corrections.json`.

#### Alternative Flows
- LLM response not JSON-parseable → re-prompt once with stricter instruction; on second failure, `verdict="keep_original"` + log structured error.
- LLM proposes a candidate the cascade did not generate → reject (anti-hallucination guard).

#### Edge Cases
- Sentence too long for context window → chunk to ±5 words around target token.
- Two equally good candidates per LLM → `verdict="keep_original"` (don't flip a coin).
- Stage 3 contradicts Stage 2 (LLM says OK after MLM said apply) → trust LLM; record both verdicts for engineer review.

#### Acceptance Criteria
```gherkin
Given an ambiguous token "גורס" with candidates ["גורם","גורס","גורף"]
And the sentence context implies "causes" semantically
When LLMReviewer prompts Gemma 3 27B with temperature=0
Then the model returns {verdict:"REPLACE", chosen:"גורם", reason:<hebrew explanation>}
And the cascade applies the correction
And the LLMReviewVerdict is cached
```

```gherkin
Given a sentence the LLM mishandles and proposes a token NOT in the candidate set
When LLMReviewer parses the response
Then the cascade rejects the hallucination
And verdict="keep_original"
And a structured "anti_hallucination_reject" event is logged
```

```gherkin
Given two consecutive runs of the same page on the same model+prompt version
When LLMReviewer runs on the second pass
Then 100% of cached verdicts are reused (zero LLM calls)
And page latency drops to NakdanGate + DictaBERT-MLM only
```

#### Data and Business Objects
- `LLMReviewVerdict(model_id, prompt_template_version, verdict, chosen, reason, latency_ms)` — BO53.
- `LLMPromptTemplate(version, body, language="he")` — BO54.

#### Dependencies
- Local Ollama runtime (operator's machine).
- F17 DictaBERT (provides ambiguous escalation set).
- F19 Nakdan word list (validates LLM choice).

#### Non-Functional Considerations
- Privacy: HARD rule — zero exam content leaves the M4 Max. Enforced by hostname `127.0.0.1` allowlist; integration test asserts no outbound DNS.
- Performance: ≤ 1 s p50 per ambiguous token; ≤ 5 s p95. Cap on calls per page = 10 (configurable); above cap, escalations skip LLM and `verdict="keep_original"`.
- Determinism: temperature=0, seed=0, cache by full key. Acknowledged residual variance documented.
- Recall: target ≥ 90% across cascade.
- Precision: ≤ 1% false-positive rate after this stage.
- Auditability: 100% of corrections have reasoning trail (HARD rule from spec).

#### Open Questions
- Llama 3.1 8B vs Gemma 3 4B for fast tier — A/B; defer until F48 lands. (Deferred finding `D-FAST-TIER-AB`.)
- Per-cohort prompt tuning — engineer story F48-S05 covers reuse.
