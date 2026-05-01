# N02/F48 — Degradation / Offline Mode User Stories

## Scope
Graceful degradation when Ollama is down or DictaBERT-MLM is unloaded. Final fallback to deprecated `_KNOWN_OCR_FIXES`. Source: ADR-033 §Consequences "Local-LLM dependency", §Alternatives.

## Sibling Links
- Parent: `user_stories.md`
- Adjacent: `user_stories.llm-reviewer.md`

## Ontology Refs
- BC: `hebrew_text`
- BO52 `StageDecision` (mode field), `_KNOWN_OCR_FIXES` (existing deprecated rule set, `tirvi/normalize/ocr_corrections.py`).

## Dependency Refs
- Required from: detection of Ollama health (HTTP probe), DictaBERT health.
- Required by: pipeline orchestrator (F22 reading-plan output).

---

### Story F48-S06: Degraded modes with stricter thresholds and audited fallback

**As a** dyslexic Hebrew student
**I want** the pipeline to still produce audio when Ollama is down or DictaBERT can't load
**So that** I can keep practicing during my study session — even if quality is reduced — and so the system does not silently swallow errors.

#### Context
ADR-033 §Consequences acknowledges Local-LLM dependency. Spec hard requirement: graceful degradation with NakdanGate + DictaBERT-MLM at stricter threshold; final fallback to deprecated `_KNOWN_OCR_FIXES`. UAT-2026-05-01-tts-quality recommendation #1: deprecated list still works for known F-2 cases.

#### Preconditions
- Pipeline starts a page run.
- Health probes run during cascade init: Ollama HTTP `/api/tags` (≤ 1 s timeout), DictaBERT model load.

#### Main Flow
1. **Mode detection** (init phase):
   - `mode="full"`: NakdanGate + MLM + LLM all healthy.
   - `mode="no_llm"`: Ollama unreachable → use NakdanGate + MLM with `threshold_low=2.0` (stricter than full's 1.0); skip LLM stage; ambiguous verdicts default to `keep_original`.
   - `mode="no_mlm"`: DictaBERT failed to load → NakdanGate only + deprecated `_KNOWN_OCR_FIXES` lookup; LLM unused (no candidates to review).
   - `mode="emergency_fixes"`: NakdanGate also unloaded → only deprecated `_KNOWN_OCR_FIXES`. Pipeline continues but logs `audit_quality="degraded:emergency_fixes"`.
2. Mode is recorded on every `StageDecision.mode` and in `corrections.json` page header.
3. UI banner: when mode != "full", inspector shows a warning ("Cascade running in degraded mode: <mode>; corrections may be reduced").
4. Pipeline log emits a structured event `cascade_mode_degraded` per page.

#### Alternative Flows
- Ollama recovers mid-run → mode change is *not* applied mid-page; per-page mode is fixed at init. Next page re-evaluates.
- All cascade stages fail → fall back to identity (no corrections applied); record `mode="bypass"`; inspector shows banner.

#### Edge Cases
- Ollama up but model not pulled → treated as `no_llm` mode; structured warning includes missing-model hint.
- DictaBERT model file corrupted → treated as `no_mlm`; warning includes file path.
- Health probe times out exactly at the timeout boundary → treat as failure (fail-closed).

#### Acceptance Criteria
```gherkin
Given Ollama is unreachable at init
When the cascade runs a page
Then mode="no_llm"
And ambiguous tokens (delta in [1.0, 3.0]) default to verdict="keep_original"
And every corrections.json page header records mode="no_llm"
And the inspector renders a degraded-mode banner
```

```gherkin
Given DictaBERT failed to load
When the cascade runs a page
Then mode="no_mlm"
And only NakdanGate filters tokens
And known F-2 OCR confusions still map via deprecated _KNOWN_OCR_FIXES
And the page completes (no abort)
```

```gherkin
Given everything is healthy
When the cascade runs
Then mode="full" recorded for every page
And no degradation banner appears
```

```gherkin
Given the cascade is in mode="no_llm"
When a token has MLM delta=4.0 (above stricter threshold_low=2.0) and unique top candidate
Then verdict="auto_apply" still fires
And the correction is logged with reasoning_trail.stages = [nakdan_gate, mlm_scorer]
```

#### Data and Business Objects
- `CascadeMode` enum value object (new sub-VO of BO52 StageDecision).
- Reuses `_KNOWN_OCR_FIXES` from `tirvi/normalize/ocr_corrections.py` (now formally deprecated; annotation added).

#### Dependencies
- Health-probe utility (sw-pipeline decides if it's a port or inline).
- F50 inspector banner element.

#### Non-Functional Considerations
- Privacy: degraded mode does not change the on-device-only invariant. Hard rule.
- Reliability: every mode is a tested path (FT-326..FT-330 cover modes).
- Observability: structured event `cascade_mode_degraded` per page; engineer can grep logs.
- Auditability: mode written to `corrections.json` AND the run-level summary.

#### Open Questions
- Should pipeline auto-retry on Ollama recovery between pages? Defer; conservative default off.
- Threshold tuning per cohort feeds back into F48-S05 engineer story.
