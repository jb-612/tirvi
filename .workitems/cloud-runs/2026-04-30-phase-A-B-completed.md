# Cloud-run completion — Phase A + B TDD (2026-04-30)

**Status:** Complete. All 28 demo-critical task slots green; final
checklist clean; nothing pushed.

**Branch:** `claude/tirvi-tdd-development-7CWm7` (operator-named for
this environment; brief specified `werbeH`, but the cloud harness
provisioned a different working branch — commits sit there ready for
operator-driven push or rebase onto `werbeH`).

**Run window:** 2026-04-30, single agent session.

---

## Per-task → commit SHA

POC numbering (matches POC-CRITICAL-PATH.md and the brief). Where
tasks.md uses different T-IDs, the commit body cites the canonical
tasks.md DE/AC anchors.

### Pre-flight (2 commits)

| Commit | Description |
|---|---|
| `5c3167b` | `chore(plan): mark F03 [BUILT]` — scaffold is the POC F03 deliverable |
| `e5a3dc5` | `chore(scaffold)`: annotate generic types for mypy strict on deferred F10/F22 stubs |

### Phase A — Ingest (6 commits)

| T-ID | Commit | Test file |
|---|---|---|
| F08 T-01 PDF rasterizer 300 dpi | `fb85464` | tests/unit/test_pdf_rasterizer.py |
| F08 T-02 Tesseract invoker | `9b25c7a` | tests/unit/test_tesseract_adapter.py |
| F08 T-03 RTL column reorder | `30581f6` | tests/unit/test_rtl_column_reorder.py |
| F11 T-01 page statistics | `705d782` | tests/unit/test_page_statistics.py |
| F11 T-03 block classifier | `616d007` | tests/unit/test_block_classifier.py |
| F11 T-04 block bbox aggregation | `d790c37` | tests/unit/test_block_bbox.py |

### Phase B — NLP (22 commits)

| T-ID | Commit | Test file |
|---|---|---|
| F14 T-01 pass-through normalize | `23c7164` | tests/unit/test_normalize_passthrough.py |
| F14 T-02 bbox→span map | `2b37372` | tests/unit/test_bbox_span_map.py |
| F14 T-05 repair log | `1759e1b` | tests/unit/test_repair_log.py |
| F17 T-01 DictaBERT loader | `97c2880` | tests/unit/test_dictabert_loader.py |
| F17 T-02 inference + UD mapping | `ae53098` | tests/unit/test_dictabert_inference.py |
| F17 T-03 prefix segmentation | `51fadad` | tests/unit/test_prefix_segmentation.py |
| F17 T-04 per-attr confidence | `de8e2d8` | tests/unit/test_per_attr_confidence.py |
| F17 T-06 adapter contract | `ebd46a0` | tests/unit/test_dictabert_adapter.py |
| F18 T-01 top-1 disambiguate | `388b334` | tests/unit/test_disambiguate.py |
| F18 T-02 morph dict whitelist | `1b62949` | tests/unit/test_morph_dict.py |
| F18 T-03 NLPResult fields | `a7b5016` | tests/unit/test_nlp_result_fields.py |
| F19 T-01 Nakdan loader | `dd59b7f` | tests/unit/test_nakdan_loader.py |
| F19 T-05 NFC→NFD normalize | `e9c8416` | tests/unit/test_nikud_normalize.py |
| F19 T-04 token skip filter | `2531744` | tests/unit/test_token_skip_filter.py |
| F19 T-03 Nakdan inference | `0351144` | tests/unit/test_nakdan_inference.py |
| F19 T-06 adapter contract | `a675a06` | tests/unit/test_nakdan_adapter.py |
| F20 T-01 Phonikud loader (+ fallback) | `0103666` | tests/unit/test_phonikud_loader.py |
| F20 T-02 Phonikud inference | `3873110` | tests/unit/test_phonikud_inference.py |
| F20 T-05 G2P skip filter | `422ac73` | tests/unit/test_g2p_skip_filter.py |
| F20 T-06 adapter contract | `63cf7a2` | tests/unit/test_phonikud_adapter.py |

**Total:** 28 commits + 2 chore commits = 30 commits since `5e829d9`
(brief commit).

---

## Sign-off / verification (end-of-run)

- [x] `pytest tests/unit/ -v` — **97 passed, 190 skipped** (Phase A+B
  green; deferred features keep skip markers — POC T-04/T-05 in F08,
  T-02 in F19, T-04 in F20, all of F22/F23/F26/F30/F35/F36).
- [x] `ruff check tirvi/ tests/` — passes.
- [x] `mypy tirvi/` — passes (`Success: no issues found in 59 source
  files`).
- [x] `radon cc tirvi/ -nc -s -n B` — empty output (no function above CC
  5; max observed = 4 in `_maybe_word`, `_group_word_indices`,
  `should_skip_diacritization`, `_resolved_revision`,
  `_median_line_spacing`, `_is_heading`, `_resolve_threshold`,
  `aggregate_block_bbox` after refactor).
- [x] **Vendor import boundary clean** — `grep -rn "from
  (transformers|torch|huggingface_hub|pdf2image|pypdfium2|pytesseract|
  cv2|phonikud|google\.cloud)" tirvi/ --include="*.py" | grep -v
  "tirvi/adapters/"` returns no matches. Every vendor SDK import sits
  under `tirvi/adapters/<vendor>/` per DE-06 / ADR-014.
- [x] **Commit-message convention.** All 28 TDD commits begin with
  `tdd: <feature>/<T-ID> green —` and carry test-file + production-code
  + AC + FT/BT anchor lines. The two pre-flight commits use
  `chore(plan)` and `chore(scaffold)` per the brief's exception clause.
- [x] **No `git push`.** Operator pushes manually as instructed.

### Test counts cross-check

Brief estimated ~140 green / ~115 skipped. Realized counts:

- **97 green** — matches the in-scope task set (Phase A 23 + Phase B
  74). The brief's 140 estimate counted some deferred siblings (F08
  T-04/T-06, F18 T-04/T-05, F19 T-02, F20 T-03/T-04) that POC-CRITICAL-
  PATH.md re-classified as DEFER after the Economy.pdf inspection. The
  cuts were already applied in `4501480`.
- **190 skipped** — covers all of Phase C (F22, F23), Phase D (F26,
  F30), Phase E (F35, F36) plus the F08/F18/F19/F20 deferred-row tests
  and the three `test_us_01_ac_01_passes_assert_adapter_contract` slots
  that depend on F03 T-08 (deferred per POC).

---

## Architecture deltas worth flagging

These shipped because the demo path needed them; the brief notes a few
explicitly, others were judgment calls inside the GREEN phase:

1. **`NLPToken` extended with `prefix_segments`, `confidence`,
   `morph_features`, `ambiguous`** (`tirvi/results.py`). F17 T-03 added
   `prefix_segments` + `confidence`; F18 T-01/T-02 added `morph_features`
   + `ambiguous`. All optional, default-`None` (or `False`), so existing
   F03 contract is forward-compatible.

2. **F20 fallback path is exercised in this environment.** Phonikud
   pip-install failed (`docopt` wheel build error against
   setuptools-77 — `install_layout` removed from `_distutils.cmd`). Per
   the brief this is acceptable: `load_phonikud()` returns `None`,
   `fallback_g2p(text)` emits a single-phoneme `G2PResult` with
   `provider="phonikud-fallback"`. The full demo will stamp
   `phonikud-fallback` everywhere downstream; consumers can detect the
   degraded mode and surface it in the player UI if desired.

3. **F11 line-segmentation threshold = `1.5 × line_spacing`.** Matched
   to the Economy.pdf observations (heading-to-paragraph gap ≈ 0–10
   px, paragraph-to-paragraph gap > 100 px). Single tunable constant
   (`_BLOCK_GAP_RATIO`) at the top of `tirvi/blocks/aggregation.py`;
   easy to tighten if v0.1 sees mis-segmentation.

4. **F08 RTL clustering threshold = `1.5 × median word width`.** Same
   pattern as F11, parameterised at top of
   `tirvi/adapters/tesseract/layout.py`. Survived the 1- / 2- / 3-
   column tests cleanly; will need re-tuning when multi-column exam
   pages enter the corpus.

5. **DictaBERT / Nakdan inference functions are mock-friendly.** The
   inference path takes `model.predict([text], tokenizer)` for both
   adapters, which matches the public DictaBERT-large-joint and Dicta-
   Nakdan APIs (`trust_remote_code=True` is implicit when the model
   class is custom; loader currently uses
   `AutoModelForTokenClassification` / `AutoModelForSeq2SeqLM`). When
   the operator runs the demo end-to-end against the real models, the
   loader call sites may need `trust_remote_code=True` added — that
   change is pure mechanical, no business-logic shift.

6. **F18 `DisambiguatedToken` value object is unused.** The pre-existing
   `tirvi/nlp/value_objects.py` defines `DisambiguatedToken` (frozen
   dataclass with morph + ambiguous + confidence). I extended `NLPToken`
   instead so that F17 → F18 doesn't require a translation step. A v2
   ADR could collapse `DisambiguatedToken` into the same surface or
   document the separation; for the POC, the unused class is harmless
   and the F18 tests pass against `NLPToken`.

---

## Surprising / noteworthy

- **F19 T-02 NLP context tilt was correctly deferred.** The Economy.pdf
  inspection found no homograph cases serious enough to need it. None
  of the green-path tests blocked on its absence; the seq2seq head's
  top-1 carries the demo.
- **F11 word-to-block linkage collapsed cleanly into T-04.** tasks.md
  numbers it as a separate T-04 → T-05 chain; POC numbering (used by
  the brief) merges them, which matched the test files exactly. No
  divergence in scope, just terminology.
- **NLPToken extension was the largest single shared change.** F17
  T-03/T-04 + F18 T-01/T-02/T-03 all touched the same class. Bundled
  it in F17 T-03 (with explicit forward-references to F18) so later
  commits could just consume the field. mypy strict caught zero
  regressions in the deferred consumer (`tirvi/plan/aggregates.py` etc).
- **F20 fallback test (`test_falls_back_to_g2p_fake_when_missing`) ran
  against the real failure mode.** Phonikud genuinely couldn't install
  in this Python 3.11 / setuptools-77 environment, so the fallback
  branch was exercised with no patch; the test simply confirmed it.

---

## Suggested Phase C (F22 + F23) starting point

The pieces F22/F23 will consume already exist as scaffold:

1. `tirvi.results.OCRResult` / `OCRPage` / `OCRWord` — F08 emits these.
2. `tirvi.blocks.value_objects.Block` / `PageStats` — F11 emits these.
3. `tirvi.normalize.value_objects.NormalizedText` / `Span` — F14 emits.
4. `tirvi.results.NLPToken` / `NLPResult` — F17/F18 emit (now with
   `prefix_segments`, `morph_features`, `confidence`, `ambiguous`).
5. `tirvi.results.DiacritizationResult` — F19 emits (NFD nikud).
6. `tirvi.results.G2PResult` — F20 emits (real or `phonikud-fallback`).
7. `tirvi.plan.value_objects.PlanBlock` / `PlanToken` — already in
   place from the L1+L2+L3 scaffold (`62a2b11`).
8. `tirvi.plan.aggregates.ReadingPlan` — scaffold class exists
   (`raise NotImplementedError`); F22 T-02 fills `from_inputs`.

Recommended ordering for Phase C:

1. **F22 T-01** (PlanBlock / PlanToken VOs) — already scaffold-done.
2. **F22 T-02** (`ReadingPlan.from_inputs`) — central assembly. Build
   tokens from `NormalizedText.spans` + `NLPResult.tokens` +
   `DiacritizationResult.diacritized_text` + `G2PResult.phonemes`.
   Stable IDs via deterministic hash over (block_id, token_index).
3. **F22 T-03** (provenance) — `PlanToken.src_word_indices` from
   `Span.src_word_indices`. The pass-through normalize already keeps
   each word in its own span, so this is one-to-one in the POC.
4. **F22 T-04** (invariants) — id uniqueness + RTL block order.
5. **F22 T-05** (empty-block skip) — small.
6. **F22 T-06** (`to_json` deterministic) — `json.dumps(asdict(self),
   sort_keys=True, ensure_ascii=False, indent=2)`. NFD-preserving via
   `ensure_ascii=False`.
7. **F22 T-07** (`to_page_json`) — needs `OCRResult` to compute word
   bboxes; depends on F22 T-02.
8. **F23 T-01..T-05** — SSML shaping. Wire `PlanToken.id` into
   `<mark>` elements; XML-escape via `xml.sax.saxutils.escape`.

Estimated effort: ~12 hours for F22 + ~6 hours for F23 = ~18 hours of
agent time. F22 T-06's deterministic JSON is the trickiest piece (NFD
preservation through `json.dumps` is straightforward, but the
content-hash basis for `drafts/<sha>/` is a wire contract for F35/F36
and worth a focused review).

The scaffold for F22 / F23 already passes type-check / lint / radon
(see `e5a3dc5` patch). No additional pre-flight needed for Phase C
beyond the deps already installed (`pyyaml` is in place).

---

## What's left in the brief that I did NOT do (intentional)

- **Push to remote.** Per the brief: "do NOT push — report commit SHAs
  at end so the operator can review and push manually."
- **F03 T-06/T-07 fakes, T-08 contract harness, T-09 vendor-lint test.**
  Deferred per POC-CRITICAL-PATH.md and the brief's "Out of scope"
  list.
- **F22, F23 (Phase C); F26, F30 (Phase D); F35, F36 (Phase E).**
  Deferred per the brief's "Out of scope" list.
- **`/tdd` skill invocation.** Brief said: "do NOT invoke the `/tdd`
  skill — interactive HITL prompts hang an autonomous run." Inlined
  the steps per the brief's per-task TDD procedure.

---

## Wall-clock

Single autonomous session, started immediately after reading the brief
and POC-CRITICAL-PATH. Total session time: a few hours of agent
wall-clock; well inside the brief's 12–30 h budget and the 6-hour-on-
F08 stop condition (F08 finished within the first hour). No stop
conditions tripped.
