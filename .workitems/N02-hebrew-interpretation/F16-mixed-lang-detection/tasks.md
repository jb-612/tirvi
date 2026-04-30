---
feature_id: N02/F16
status: designed
total_estimate_hours: 8.5
---

# Tasks: N02/F16 — Mixed-Language Run Detection (per ADR-031)

POC scope: full task set is MVP-targeted (F16 is **not** demo-critical
per `.workitems/POC-CRITICAL-PATH.md` — Economy.pdf p.1 is pure
Hebrew). Tasks run when Wave 3 begins, **before** F24 / F25 — F24/F25
consume the `LanguageSpansResult` contract that F16 emits.

**TDD mode**: bundled (per task: write all tests first, then code, then
refactor). Three rule tasks (T-04/T-05/T-06) share
`tests/unit/test_lang_spans_heuristics.py` so bundled mode keeps the
red-green-refactor cycle coherent across the rule chain.

## T-01: Package scaffold + LanguageSpansResult value type

- design_element: DE-06
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-112]
- estimate: 1h
- test_file: tests/unit/test_lang_spans_results.py
- dependencies: []
- hints: `tirvi/lang_spans/` package init; `tirvi/lang_spans/results.py`
  with `@dataclass(frozen=True) class LanguageSpansResult` carrying
  `spans: tuple[LanguageSpan, ...]`, `provider: str = "tirvi-rules-v1"`,
  `confidence: float | None`. `confidence` is `None` when `spans` is
  empty (avoids `min(())` ValueError on the empty-input contract from
  T-03); when non-empty, aggregate is `min(span.confidence for span in
  spans)`. `LanguageSpan` is the shared biz value object; F16 is the
  first realisation in code, so `tirvi.lang_spans.LanguageSpan`
  becomes the canonical re-export — F22/F24/F25 will import it from
  here. Frozen + tuple → hashable + immutable for content-hash drafts
  cache parity with other result types.

## T-02: Unicode-script per-character classifier

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-112, FT-113]
- estimate: 1.5h
- test_file: tests/unit/test_lang_spans_classify.py
- dependencies: [T-01]
- hints: `classify_char(c: str) -> Script` enum; cover Hebrew base
  block U+0590–U+05FF and presentation forms U+FB1D–U+FB4F; Latin
  Basic + Latin-1; ASCII digits + Arabic-Indic digits U+0660–U+0669;
  math operators `+−×÷=%`; decimal `.,`; whitespace; OTHER.
  **Implementation: explicit per-codepoint range table dispatch** (an
  ordered list of `(start, end, Script)` tuples + small linear scan or
  bisect); **do NOT** use `unicodedata.category` / `unicodedata.script`
  — the explicit ranges match DE-01's prose verbatim and are easier to
  audit. CC ≤ 5; no vendor imports.

## T-03: Run-length aggregation with whitespace absorption

- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-112, FT-114]
- estimate: 1.5h
- test_file: tests/unit/test_lang_spans_aggregate.py
- dependencies: [T-02]
- hints: `aggregate_runs(tags, text) -> list[LanguageSpan]`; collapse
  consecutive same-tag chars; absorb `WS` runs into the previous lang
  span (boundary + ordering). **Acceptance: after WS absorption, two
  adjacent same-lang spans separated only by absorbed whitespace MUST
  merge into one span.** This makes `"Microsoft Word"` deterministically
  emit a single `en` span (FT-114), `"hello world"` → one `en` span,
  and prevents degenerate adjacent-same-lang spans from leaking into
  F22/F24's plan + SSML output. Output is `start`-sorted. Edge cases:
  empty input returns empty tuple; all-`WS` input returns empty tuple.

## T-04: Transliteration heuristic (single Latin inside Hebrew word)

- design_element: DE-03
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-113]
- estimate: 1h
- test_file: tests/unit/test_lang_spans_heuristics.py
- dependencies: [T-03]
- hints: `apply_transliteration_rule(spans, text)`; predicate
  `len(text[span]) == 1 and prev.lang == "he" and next.lang == "he"`
  → reclassify span to `he` and merge into a single he span with
  neighbours. Lowers `confidence` to 0.85 on the merged span. Order
  matters: this rule fires **before** DE-04 hyphen-bridge so
  surrounded singletons are absorbed first.

## T-05: Hyphen-bridge rule (`p-value` → single `en` span)

- design_element: DE-04
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-112]
- estimate: 1h
- test_file: tests/unit/test_lang_spans_heuristics.py
- dependencies: [T-04]
- hints: `apply_hyphen_bridge_rule(spans, text)`; pattern
  LATIN-hyphen-LATIN with no internal whitespace → merge to `en`,
  `confidence = 0.85`. Standalone hyphen (no Latin neighbour) stays
  in its source span (typically `WS` boundary). Idempotent: running
  twice yields same result.

## T-06: Number / math unification

- design_element: DE-05
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-112]
- estimate: 1h
- test_file: tests/unit/test_lang_spans_heuristics.py
- dependencies: [T-04]
- hints: `apply_num_unification(spans, text)`; adjacent `DIGIT` and
  `SYMBOL` runs collapse into one span tagged `lang="num"`,
  `confidence=1.0`. Resolves biz Open Question (math/lang overlap)
  per ADR-031. Math expression rendering is F25's concern; F16 only
  emits `num`.

## T-07: detect_language_spans pipeline + smoke

- design_element: DE-06, DE-07
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-112, FT-113, FT-114]
- bt_anchors: [BT-075, BT-076]
- estimate: 1.5h
- test_file: tests/unit/test_lang_spans_detect.py
- dependencies: [T-03, T-04, T-05, T-06]
- hints: `detect_language_spans(text)` chains classifier → aggregate
  → transliteration → hyphen-bridge → num-unification → emits
  `LanguageSpansResult`. Smoke fixtures: pure Hebrew (single `he`
  span; demo path); biz example `"ערך p-value הוא 0.05"` → `[he,
  en, he, num]` matching FT-112; pure English page → single `en`.
  Verify aggregate `confidence` is `min` of span confidences and that
  result is deterministic (same input → identical bytes).

## Dependency DAG

```
T-01 → T-02 → T-03 → T-04 → T-05 → T-07
                       |       \
                       └─ T-06 ─┘
```

Critical path: T-01 → T-02 → T-03 → T-04 → T-05 → T-07 (~7.5h).
T-06 forks off T-04 and rejoins at T-07.

## Test coverage map

- FT-112 (`"ערך p-value..."`) — T-07 main fixture; spans T-03 + T-05 +
  T-06 paths.
- FT-113 (single English letter inside Hebrew word) — T-04 rule;
  smoke at T-07.
- FT-114 (brand name `Microsoft Word` → en) — T-03 default behaviour;
  smoke at T-07.
- FT-115 / FT-116 (split-stitch / Azure inline) — anchored to F24;
  F16 emits the spans only, no test code here.
- BT-075 / BT-076 — covered as smoke at T-07.
- BT-077 (dev tunes rule) / BT-078 (audio seam) — anchored to F24 /
  F39 bench respectively; not F16 tests.
