---
feature_id: N02/F48
status: ready
total_estimate_hours: 17.5
wave: 3
---

# Tasks: N02/F48 — Hebrew correction cascade

Tasks build the package `tirvi/correction/`. Track-A (unit) per the
`.claude/rules/sdlc-flow-diagram.md` flow; foundational because `ICascadeStage`,
`NakdanWordListPort`, `LLMClientPort`, and `FeedbackReadPort` are net-new ports.
After T-01 → T-02, run `@test-mock-registry` to generate fakes before
adapter/service tasks (T-03..T-08). After T-08, run `@test-functional` then
`@integration-test`.

## T-01: Define `ICascadeStage` port + `CorrectionVerdict` value object

- [x] **T-01 done**
- design_element: DE-01
- acceptance_criteria: [F48-S01/AC-01, F48-S02/AC-02, F48-S03/AC-01, F48-S04/AC-01]
- ft_anchors: [FT-316, FT-323, FT-330]
- bt_anchors: [BT-210]
- estimate: 1.5h
- test_file: tests/unit/test_correction_ports.py
- dependencies: []
- hints: |
    `tirvi/correction/ports.py` — single-method `ICascadeStage.evaluate(
    token: str, context: SentenceContext) -> CorrectionVerdict`. Frozen
    dataclass `CorrectionVerdict` (see DE-01). Verdict enum is a Literal.
    `NakdanWordListPort.is_known_word(token: str) -> bool`. `LLMClientPort.
    generate(prompt: str, model_id: str, temperature: float, seed: int)
    -> str` (raw response body). `FeedbackReadPort.user_rejections(
    draft_sha: str) -> Iterable[UserRejection]`. No vendor types
    (ADR-029). All ports `@runtime_checkable`.

## T-02: Implement `NakdanGate` (DE-02) + skip rules

- [x] **T-02 done**
- design_element: DE-02
- acceptance_criteria: [F48-S01/AC-01, F48-S01/AC-02]
- ft_anchors: [FT-316, FT-317]
- bt_anchors: [BT-209]
- estimate: 1.5h
- test_file: tests/unit/test_nakdan_gate.py
- dependencies: [T-01]
- hints: |
    `tirvi/correction/nakdan_gate.py`. Inject `NakdanWordListPort`. Verdict
    rules per DE-02 + biz NT-04 (`skip_empty`), BT-F-03 (`skip_short` for
    `len<2`), and `skip_non_hebrew` for digit/Latin tokens. Use a small
    in-process LRU keyed on `(token, word_list_version)`. Performance
    target enforced via test marker `slow` for FT-317 (1000-token loop;
    p95 ≤ 5 ms with a warm-list fixture).

## T-03: Implement `DictaBertMLMScorer` (DE-03) — confusion-table + decision tree

- [x] **T-03 done**
- design_element: DE-03
- acceptance_criteria: [F48-S02/AC-01, F48-S02/AC-02, F48-S02/AC-03]
- ft_anchors: [FT-318, FT-319, FT-328]
- bt_anchors: [BT-214]
- estimate: 2.5h
- test_file: tests/unit/test_mlm_scorer.py
- dependencies: [T-01, T-02]
- hints: |
    `tirvi/correction/mlm_scorer.py`. Load `confusion_pairs.yaml` once
    (lru_cache). Single-site swap for POC. Score under `dicta-il/dictabert`
    MLM head (reuse F17 loader where possible). Decision tree per DE-03
    with `(threshold_low, threshold_high, margin)` injected (defaults
    1.0/3.0/0.5). Cache key
    `(token, sentence_context_hash, mlm_model_id, table_version)`. Tests
    use the existing `tirvi.normalize.mlm_correction` fake hook style —
    pin scores via `monkeypatch` so the test is deterministic without
    loading the real model.

## T-04a: Implement `LLMClientPort` adapter (Ollama HTTP) + sqlite cache

- [x] **T-04a done**
- design_element: DE-04
- acceptance_criteria: [F48-S03/AC-02]
- ft_anchors: [FT-321]
- bt_anchors: [BT-220]
- estimate: 1.5h
- test_file: tests/unit/test_ollama_client.py
- dependencies: [T-01]
- hints: |
    `tirvi/correction/adapters/ollama.py` — concrete `LLMClientPort`.
    POST `http://localhost:11434/api/generate` with `model`,
    `prompt`, `stream=false`, `options={temperature:0}`. Per ADR-029
    vendor boundary, this is the ONLY file allowed to import
    `httpx`/`requests`. Model identifiers: `gemma4:31b-nvfp4`
    (primary), `llama3.1:8b` (fast tier).
    Cache: sqlite at `drafts/<sha>/llm_cache.sqlite`, schema per
    ADR-034 — table `llm_calls(cache_key TEXT PRIMARY KEY, model_id,
    prompt_template_version, sentence_hash, response, ts)`. Cache
    key = sha256(model_id + version + sentence_hash). Per-page cap
    on call count (default 10, config field) — when cap reached,
    emit `llm_call_cap_reached` and short-circuit returns
    `keep_original` (BT-F-05).

## T-04b: `OllamaLLMReviewer` domain wrapper + anti-hallucination guards

- [x] **T-04b done**
- design_element: DE-04
- acceptance_criteria: [F48-S03/AC-01, F48-S03/AC-03]
- ft_anchors: [FT-320, FT-322]
- bt_anchors: [BT-217]
- estimate: 1.5h
- test_file: tests/unit/test_llm_reviewer.py
- dependencies: [T-04a, T-03]
- hints: |
    `tirvi/correction/llm_reviewer.py` — domain wrapper around
    `LLMClientPort`. Build prompt from
    `tirvi/correction/prompts/he_reviewer/v1.txt`; load
    `prompt_template_version` from sibling `_meta.yaml`.
    Anti-hallucination guard:
      - chosen ∈ candidates  (LLM cannot invent words outside MLM proposals)
      - chosen ∈ NakdanWordList (chosen must be a real Hebrew word)
      - else → emit `anti_hallucination_reject`, fall back to keep_original
    One re-prompt on parse failure with stricter prompt (NT-02).
    Returns `CorrectionVerdict(stage="llm_reviewer", original, corrected,
    score=None, reasoning=…, cache_hit, prompt_template_version)`.

## T-05: Implement `CorrectionCascadeService` orchestrator (DE-05) + domain events

- [ ] **T-05 done**
- design_element: DE-05
- acceptance_criteria: [F48-S01/AC-01, F48-S02/AC-03, F48-S03/AC-01]
- ft_anchors: [FT-316, FT-326, FT-328, FT-329]
- bt_anchors: [BT-209, BT-211, BT-219]
- estimate: 2h
- test_file: tests/unit/test_cascade_service.py
- dependencies: [T-02, T-03, T-04b]
- hints: |
    `tirvi/correction/service.py`. Hold transient `CorrectionCascade`
    aggregate per page; do NOT cache across pages (DDD per-page
    transient — biz F48-R1-3). Emit `CorrectionApplied`,
    `CorrectionRejected`, `CascadeModeDegraded` via simple
    `EventListener` Protocol (in-process pub-sub; no infra). Token-in
    / token-out invariant (DEP-052; INT-03 will pin in Track C).
    Read user-rejections from `FeedbackReadPort` at init and override
    the corresponding tokens to `keep_original` (BT-211).

## T-06: Implement `CorrectionLog` writer (DE-06) + audit-gap path

- [ ] **T-06 done**
- design_element: DE-06
- acceptance_criteria: [F48-S04/AC-01, F48-S04/AC-02, F48-S04/AC-03]
- ft_anchors: [FT-323, FT-324, FT-330]
- bt_anchors: [BT-210]
- estimate: 1.5h
- test_file: tests/unit/test_correction_log.py
- dependencies: [T-05]
- hints: |
    `tirvi/correction/log.py`. Single JSON object per page per ADR-035.
    Write atomically (`.tmp` rename). Disk-full path: catch `OSError`
    on `os.replace`, append to `audit_gaps.json`, mark page header
    `audit_quality: "audit-incomplete"`. Schema version constant.
    Index file behaviour: always emit `corrections.json` with `chunks`
    list (≤ 50 page docs may also denormalise entries — keep schema
    uniform via index-only).

## T-07: Implement `HealthProbe` + degraded-mode policy (DE-07)

- [ ] **T-07 done**
- design_element: DE-07
- acceptance_criteria: [F48-S06/AC-01, F48-S06/AC-02, F48-S06/AC-03, F48-S06/AC-04]
- ft_anchors: [FT-326, FT-327]
- bt_anchors: [BT-213, BT-218]
- estimate: 1.5h
- test_file: tests/unit/test_health_probe.py
- dependencies: [T-04b, T-05]
- hints: |
    `tirvi/correction/health.py`. Sync probe (≤ 1 s timeout) — `httpx`
    GET to Ollama `/api/tags`; DictaBERT load via existing F17 helper.
    Mode is a value object selected once at cascade init; passed into
    `run_page`. `no_mlm` mode wires the deprecated
    `tirvi/normalize/ocr_corrections.py::_KNOWN_OCR_FIXES` lookup
    AFTER NakdanGate `suspect` — keep that path behind a clearly
    annotated `_deprecated_known_fixes_lookup()` so removal in a
    later release is mechanical.

## T-08: Implement `FeedbackAggregator` script + `FeedbackReadPort` adapter (DE-08)

- [ ] **T-08 done**
- design_element: DE-08
- acceptance_criteria: [F48-S05/AC-01, F48-S05/AC-02, F48-S05/AC-03, F48-S05/AC-04]
- ft_anchors: [FT-325]
- bt_anchors: [BT-211, BT-215, BT-220]
- estimate: 2h
- test_file: tests/unit/test_feedback_aggregator.py
- dependencies: [T-05]
- hints: |
    `tirvi/correction/feedback_aggregator.py` (CLI script). sqlite
    schema-compat extension of F47's `FeedbackEntry` (BO46) — adds
    `system_chose`, `expected`, `persona_role`, `sentence_context_hash`.
    Aggregator logic: group by `(ocr_word, expected)`; per-sha
    contribution capped at 1; emit suggestion only when distinct_shas
    ≥ 3. Output `drafts/rule_suggestions.json`. `FeedbackReadPort`
    adapter at `tirvi/correction/adapters/feedback_sqlite.py`.
    Also: typed `ConfusionTableMissing` error in cascade init when
    `confusion_pairs.yaml` is missing (NT-01).

## T-09: Wire cascade into `tirvi/pipeline.py` between F14 and F19

- [ ] **T-09 done**
- design_element: DE-05
- acceptance_criteria: [F48-S01/AC-01]
- ft_anchors: [FT-329]
- bt_anchors: [BT-209]
- estimate: 1h
- test_file: tests/unit/test_pipeline.py (extend)
- dependencies: [T-05, T-06, T-07]
- hints: |
    Insert cascade call between normalize and Nakdan stages in
    `tirvi/pipeline.py`. Config knob `enable_correction_cascade: bool`
    (default true) so the existing pipeline stays runnable while
    cascade adapters bake. Page-latency assertion is informational
    in unit tests; FT-329 lives in `@test-functional` Track B.

## T-10: Privacy invariant test — assert no non-localhost outbound during cascade

- [ ] **T-10 done**
- design_element: DE-04
- acceptance_criteria: [F48-S03/AC-01]
- ft_anchors: [FT-AUD-03]
- bt_anchors: [BT-216]
- estimate: 1h
- test_file: tests/unit/test_privacy_invariant.py
- dependencies: [T-04b, T-05]
- hints: |
    Monkey-patch `socket.getaddrinfo` and `socket.create_connection` to
    record every outbound; assert all resolved IPs are `127.0.0.1`
    or `::1` during a full cascade run. Hard CI gate; failure freezes
    feature ship per ADR-033 privacy invariant + biz F48-R1-1.
