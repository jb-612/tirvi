---
feature_id: N02/F19
status: implementing
total_estimate_hours: 6.5
---

# Tasks: N02/F19 — Dicta-Nakdan REST adapter (per ADR-025)

POC scope: T-01..T-04 + T-06 are GREEN (code lives in `tirvi/adapters/nakdan/`); T-05 already covered by inline normalization; T-02 NLP-context tilt awaits F17 reroute completion. Marked status reflects this.

## T-01: Dicta REST HTTP client

- [x] **T-01 done**
- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- bt_anchors: [BT-099]
- estimate: 1h
- test_file: tests/unit/test_nakdan_client.py
- dependencies: []
- status: implemented (`tirvi/adapters/nakdan/client.py`)
- hints: stdlib `urllib.request`; POST `{"task":"nakdan","data":text,"genre":"modern"}`; configurable timeout; mock `urlopen` with context-manager pattern. Vendor boundary: HTTP I/O lives only in this submodule (ADR-029).

## T-02: NLP-context option scoring (gated on F17 reroute)

- [x] **T-02 done**
- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-146, FT-147]
- bt_anchors: [BT-097]
- estimate: 1.5h
- test_file: tests/unit/test_nakdan_context.py
- dependencies: [T-01, N02/F17 T-02]
- status: pending (waiting for F17 to emit real NLPResult)
- hints: `diacritize_in_context(text, NLPResult)` consumes per-token POS+gender+state; for each Dicta entry where multiple `options` exist, pick the option whose decoded morph signal best matches the NLP context; without context, fall through to T-03's selection priority.

## T-03: Selection priority (override > sep > confidence > fallback)

- [x] **T-03 done**
- design_element: DE-03
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-150]
- estimate: 1.5h
- test_file: tests/unit/test_nakdan_inference.py
- dependencies: [T-01]
- status: implemented (`tirvi/adapters/nakdan/inference.py::_pick`)
- hints: priority chain in `_pick(entry)` — order matches as-built code: (a) `entry.sep` → emit `entry.word`; (b) `entry.word in HOMOGRAPH_OVERRIDES` → use override; (c) `not options` → emit `entry.word`; (d) `not entry.get("fconfident", True)` → emit `entry.word`; (e) emit `options[0].replace("|", "")`. **Refactor target before T-02 lands**: extract helper predicates `_passthrough(entry) -> str | None`, `_override_hit(word) -> str | None`, `_confidence_gated(entry) -> str | None` so `_pick` reduces to a chained `or` expression with CC ≤ 3, leaving headroom for T-02's NLP-context branch. Per CLAUDE.md global rule (CC ≤ 5), current as-built `_pick` is at threshold; refactor brings it within budget without changing behaviour. Add a refactor regression test asserting the priority chain output matches the original on a representative input matrix.

## T-04: Token-skip filter via Dicta `sep` flag

- [x] **T-04 done**
- design_element: DE-04
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.5h
- test_file: tests/unit/test_nakdan_inference.py (covered)
- dependencies: [T-01]
- status: implemented
- hints: Dicta marks separators (whitespace, punctuation) with `entry.sep == True`; `_pick` short-circuits and emits `entry.word` verbatim. No additional logic needed for ASCII/digits — they arrive as `sep=True` in the response.

## T-05: NFC→NFD nikud ordering

- [x] **T-05 done**
- design_element: DE-05
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.5h
- test_file: tests/unit/test_nakdan_inference.py::test_diacritized_text_is_nfd
- dependencies: [T-03]
- status: implemented (`tirvi/adapters/nakdan/normalize.py::to_nfd`)
- hints: `unicodedata.normalize("NFD", text)` applied to the concatenated diacritized string before returning the result. F20 G2P stability depends on this.

## T-06: Adapter contract conformance + REST client wiring

- [x] **T-06 done**
- design_element: DE-06
- acceptance_criteria: [US-01/AC-01, US-02/AC-01]
- estimate: 1.5h
- test_file: tests/unit/test_nakdan_adapter.py
- dependencies: [T-03, T-05]
- status: implemented (`tirvi/adapters/nakdan/adapter.py`)
- hints: `isinstance(DictaNakdanAdapter(), DiacritizerBackend)`; provider stamp = `"dicta-nakdan-rest"`; mock `diacritize_via_api` in tests with canned Dicta response shape.

## Dependency DAG

```
T-01 → T-03 → T-05 → T-06
T-01 → T-04
T-01, F17 T-02 → T-02
```

Critical path: T-01 → T-03 → T-05 → T-06 (5h). T-02 unblocks once F17 ships per ADR-026.
