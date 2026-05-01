---
feature_id: N02/F26
status: ready
total_estimate_hours: 8.0
---

# Tasks: N02/F26 — AlephBERT + YAP fallback NLP path (per ADR-027)

## T-01: YAP HTTP client (POST + parse)

- [ ] **T-01 done**
- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-131]
- bt_anchors: [BT-087]
- estimate: 1h
- test_file: tests/unit/test_yap_client.py
- dependencies: []
- hints: stdlib `urllib.request`; payload `json.dumps({"text": text}, ensure_ascii=False).encode("utf-8")`; `Content-Type: application/json` header; POST to `${YAP_BASE_URL}/api/v0/joint`; 30s timeout; mock `urlopen` with context-manager pattern (mirror `test_nakdan_client.py:33-44`); env override via `TIRVI_YAP_URL`. Test must assert the request body decodes back to the input Hebrew text.

## T-02: YAP response parser (lattice → token list)

- [ ] **T-02 done**
- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-133]
- estimate: 1h
- test_file: tests/unit/test_yap_response_parser.py
- dependencies: [T-01]
- hints: walk `response["lattice_md"]`; per-edge extract `surface`, `lemma`, `CPOSTag`, `FPOSTag`, `feats` ("Definite=Def|Gender=Masc|..."); split feats on `|` and `=` into a dict; collapse multi-edge tokens by surface form.

## T-03: UD-Hebrew schema mapper

- [ ] **T-03 done**
- design_element: DE-03
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-133, FT-134]
- estimate: 1h
- test_file: tests/unit/test_yap_ud_mapper.py
- dependencies: [T-02]
- hints: dict mapping `VB → VERB`, `NN → NOUN`, `JJ → ADJ`, `RB → ADV`, `IN → ADP`, `DT → DET`, `CC → CCONJ`, `PRP → PRON`, etc.; UD-Hebrew morph keys filled where YAP feats provide them, missing keys absent from `morph_features` dict (per biz S02 AC: "missing fields filled with None or sensible defaults" — locked schema uses `None` for the whole `morph_features` field when YAP gave no feats; otherwise emit only the keys YAP provided). Preserve original CPOSTag inside `morph_features` under key `raw_pos` for debugging. Schema target: locked F03 `NLPToken` — no new fields.

## T-04: AlephBertYapFallbackAdapter (NLPBackend implementor)

- [ ] **T-04 done**
- design_element: DE-04
- acceptance_criteria: [US-01/AC-01, US-02/AC-01]
- ft_anchors: [FT-131]
- estimate: 1h
- test_file: tests/unit/test_alephbert_yap_adapter.py
- dependencies: [T-01, T-02, T-03]
- hints: class implements `NLPBackend.analyze(self, text: str, lang: str) -> NLPResult` (port signature from `tirvi/ports.py`; `lang` accepted but ignored — YAP is Hebrew-only). provider="alephbert+yap"; empty input short-circuit (mirror F17 pattern returning `NLPResult(provider="alephbert+yap", tokens=[], confidence=None)`); module-level vendor boundary (no transformers/AlephBERT imports for POC per ADR-027 + ADR-029).

## T-05: Connection-failed degraded path

- [ ] **T-05 done**
- design_element: DE-05
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-135]
- bt_anchors: [BT-090]
- estimate: 1h
- test_file: tests/unit/test_yap_degraded_path.py
- dependencies: [T-01, T-04]
- hints: catch `(URLError, socket.timeout, ConnectionRefusedError, json.JSONDecodeError, KeyError)` plus non-200 HTTP status; return `NLPResult(provider="degraded", tokens=[], confidence=None)`. Empty input is NOT degraded — `analyze("")` short-circuits to `provider="alephbert+yap", tokens=[]` (asserted in T-04). Test each branch independently.

## T-06: Integration test — F17 → F26 failover chain

- [ ] **T-06 done**
- design_element: DE-06 (verifies F17 T-06 wiring)
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-131, FT-132]
- estimate: 1h
- test_file: tests/integration/test_f17_to_f26_failover.py
- dependencies: [T-04, T-05]
- hints: integration test (NOT unit) — F17 owns the wiring per F17 T-06. This task verifies the chain works: instantiate `DictaBERTAdapter`, monkey-patch `tirvi.adapters.dictabert.loader.load_model` to raise `ImportError`, call `adapter.analyze("שלום", "he")`, assert `result.provider == "alephbert+yap"`. Second case: also patch out F26's import, assert `result.provider == "degraded"`. F26 source itself is not edited by this task — only `AlephBertYapFallbackAdapter` must be importable from `tirvi.adapters.alephbert`.

## T-07: Adapter contract conformance

- [ ] **T-07 done**
- design_element: DE-06
- acceptance_criteria: [US-01/AC-01, US-02/AC-01]
- estimate: 0.5h
- test_file: tests/unit/test_alephbert_yap_adapter.py (extend)
- dependencies: [T-04]
- hints: `isinstance(AlephBertYapFallbackAdapter(), NLPBackend)` (runtime_checkable Protocol from F03 with two-arg `analyze(self, text: str, lang: str)` signature); provider stamp set on every result; assert that `analyze("שלום", "he")` returns NLPResult; `assert_adapter_contract` deferred per POC-CRITICAL-PATH (track in F03 backlog).

## T-08: YAP availability health probe (DE-07)

- [ ] **T-08 done**
- design_element: DE-07
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.5h
- test_file: tests/unit/test_yap_health_probe.py
- dependencies: [T-04]
- hints: in `AlephBertYapFallbackAdapter.__init__`, issue one-shot `urlopen("${YAP_BASE_URL}/", timeout=2.0)`; on connection failure, log a single WARN line via stdlib `logging` (one log per adapter instance — guard with an `_probed: bool` flag). Test: mock urlopen to raise ConnectionRefusedError, capture logs via `caplog`, assert WARN line present and contains the actionable text "start with `yap api`".

## T-09: YAP API JSON fixture capture (one-time, manual)

- [ ] **T-09 done**
- design_element: DE-02 (precondition)
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.5h
- test_file: tests/fixtures/yap_lattice_sample.json (data file, no test)
- dependencies: []
- status: pending (manual one-time setup before T-02 RED phase)
- hints: with YAP server running locally, `curl -s -X POST -H 'Content-Type: application/json' -d '{"text":"שלום עולם"}' http://127.0.0.1:8000/api/v0/joint > tests/fixtures/yap_lattice_sample.json`. Capture a 5-10 token Hebrew sentence covering common UD POS classes. T-02 unit test imports this fixture instead of a hand-authored mock — guards against the same API-drift class that broke F20 Phonikud's original `transliterate()` design.

## T-10: F22 reading-plan tolerance assertion (cross-feature integration)

- [ ] **T-10 done**
- design_element: DE-05 (verifies degraded contract)
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.5h
- test_file: tests/integration/test_f22_tolerates_degraded_nlp.py
- dependencies: [T-05]
- hints: integration test — call `ReadingPlan.from_inputs(...)` with `nlp_result=NLPResult(provider="degraded", tokens=[], confidence=None)`; assert no exception raised AND `plan.blocks[0].tokens` is non-empty (uses fallback metadata) AND each `PlanToken` has `pos=None, lemma=None, morph_features=None` but valid `text` and `bbox`. Pins ADR-027's "no worse than current `_StubNLP` baseline" claim with a concrete assertion.

## Dependency DAG

```
T-01 → T-02 → T-03 → T-04 → T-07
              T-04 → T-05 → T-10
              T-04 → T-08
              T-04, T-05 → T-06
T-09 (one-time) → T-02
```

Critical path: T-01 → T-02 → T-03 → T-04 → T-05 → T-06 (6h).
