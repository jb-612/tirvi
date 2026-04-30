# tirvi — POC Critical-Path Checklist

**Purpose:** Filter the 256 scaffolded test stubs (across F03 + 14 POC
features) to the **must-pass-for-demo** subset. Anything not on this
list is deferred to v0.1 — not deleted, not invalid, just not on the
critical path for the `Economy.pdf p.1` end-to-end demo.

**Parent:** `.workitems/PLAN-POC.md`. **Created:** 2026-04-30.
**Status:** Pre-`/tdd` scope freeze.

## Filter rules

A test is **demo-critical** if its production code is exercised by the
end-to-end run on `docs/example/Economy.pdf` p.1, OR its absence breaks
a wire-contract chain (PlanToken.id, audio.json, page.json).

A test is **deferred** if it covers:
- A code path the demo PDF doesn't exercise (e.g., corrupt-PDF handling
  on a clean fixed input)
- A regression net for evolution (e.g., adapter-contract harness across
  all fakes)
- Optional graceful degradation (e.g., forced-alignment fallback —
  already deferred per ADR-015)
- A toolchain check that's already enforced elsewhere (e.g., ruff
  banned-api lint vs. the unit test that verifies the rule fires)

## Critical-path summary

**~50 demo-critical task slots → ~180 demo-critical tests. ~30 deferred
task slots → ~76 deferred tests.**

| Phase | Features | Demo-critical / Total tasks |
|---|---|---|
| Foundation | F03 | 1 / 9 (after scope cut — see below) |
| A. Ingest | F08 + F10 + F11 | 9 / 14 |
| B. NLP | F14 + F17 + F18 + F19 + F20 | 24 / 29 |
| C. Plan/SSML | F22 + F23 | 11 / 12 |
| D. Audio | F26 + F30 | 9 / 11 |
| E. Player | F35 + F36 | 4 / 12 (F36 deferred to v0.1 except T-01) |

## Per-feature checklist

### F03 — adapter ports & in-memory fakes

The L1+L2+L3 scaffold output **already covers most of F03's tasks**
(types, ports, errors are in place). The TDD load is much smaller than
the design's 9.5h estimate suggests.

| T-ID | Demo? | Why |
|---|---|---|
| T-01 scaffold package | ✅ DONE (scaffold) | `tirvi/__init__.py` + module shells exist; tests collect |
| T-02 result dataclasses | ✅ DONE (scaffold) | All 6 result types are frozen + provider + confidence |
| T-03 WordTimingResult Literal | ✅ DONE (scaffold) | `source: Literal[...]` in place |
| T-04 port Protocols | ✅ DONE (scaffold) | All 6 `@runtime_checkable` Protocols defined |
| T-05 WordTimingCoordinator | ❌ DEFER | POC has only TTS-marks adapter; coordinator fallback logic doesn't fire (F30's `TTSEmittedTimingAdapter` is called directly). Land logic in MVP when forced-alignment lands |
| T-06 fakes OCR/NLP/Dia/G2P | ❌ DEFER | Demo uses real adapters; fakes only matter for integration tests (deferred) and contract harness (deferred) |
| T-07 fakes TTS/WordTiming | ❌ DEFER | Same |
| T-08 `assert_adapter_contract` | ❌ DEFER | Regression net for adapter evolution; not a demo blocker |
| T-09 vendor-import lint test | ❌ DEFER | Rule already enforced via `ruff.toml` banned-api; the unit test is verification of the verifier |

**F03 effective TDD load: ~0h** — scaffold output is the demo
deliverable. (Re-confirm before kicking off Phase 2.)

### F08 — Tesseract adapter

| T-ID | Demo? | Why |
|---|---|---|
| T-01 PDF rasterizer 300dpi | ✅ | Entry point; one PIL Image per page |
| T-02 Tesseract invoker | ✅ | Core OCR call; psm 6, lang heb, conf normalize |
| T-03 RTL column reorder | ✅ | Hebrew RTL is the project's defining constraint |
| T-04 inline lang_hint | ⚠️ MAYBE | Only matters if Economy.pdf has English mixed in; **inspect PDF first**, defer if pure Hebrew |
| T-05 corrupt-PDF handling | ❌ DEFER | Economy.pdf is fixed; corrupt input doesn't happen in demo |
| T-06 deskew preprocessor | ❌ DEFER | If Economy.pdf is OCR-clean. Default `deskew=False` per ADR-016 |

### F10 — OCRResult contract

| T-ID | Demo? | Why |
|---|---|---|
| T-01 builder.from_yaml | ⚠️ MAYBE | Useful for unit tests; not required for demo runtime path |
| T-02 schema validate | ❌ DEFER | Validator for evolution; not demo-critical |
| T-03 v1 invariants | ❌ DEFER | Same |

**F10 effective load: 0–1 task.** This feature is mostly deferred in
practice — the F03 result types already exist; F10 was design
clarifying semantics that ADR-014 says we test via contract tests
(also deferred).

### F11 — block segmentation

| T-ID | Demo? | Why |
|---|---|---|
| T-01 page statistics | ✅ | Required by classifier |
| T-02 block taxonomy | ✅ DONE (scaffold) | Literal + BLOCK_TYPES tuple in place |
| T-03 block classifier | ✅ | Demo PDF has heading + paragraph + question_stem |
| T-04 block bbox aggregation | ✅ | Word→block round-trip invariant |

### F14 — normalization

| T-ID | Demo? | Why |
|---|---|---|
| T-01 pass-through | ✅ | Default behavior |
| T-02 bbox→span map | ✅ | Downstream stages need span provenance |
| T-03 line-break rejoin | ⚠️ MAYBE | If demo PDF has hyphenated line breaks within paragraphs |
| T-04 stray punct repair | ⚠️ MAYBE | If OCR introduces spurious punctuation |
| T-05 repair log | ✅ | Audit trail; small, ship it |
| T-06 NormalizedText VO | ✅ DONE (scaffold) | Frozen dataclass in place |

### F17 — DictaBERT adapter

| T-ID | Demo? | Why |
|---|---|---|
| T-01 module-LRU loader | ✅ | First-call init; reused thereafter |
| T-02 inference + UD mapping | ✅ | Core call |
| T-03 prefix segmentation | ✅ | Hebrew-specific; downstream needs it |
| T-04 per-attr confidence | ✅ | Biz S01 — confidence shape |
| T-05 long-sentence chunking | ⚠️ MAYBE | Inspect Economy.pdf — if all sentences < model context, defer |
| T-06 adapter contract | ✅ | Smoke test — runtime_checkable + return type |

### F18 — disambiguation

| T-ID | Demo? | Why |
|---|---|---|
| T-01 top-1 disambiguate | ✅ | Picks the sense |
| T-02 morph dict whitelist | ✅ | Schema enforcement |
| T-03 NLPResult fields | ✅ | Provider + tokens + confidence |
| T-04 fixture builder | ❌ DEFER | Test infra, not demo path |
| T-05 v1 invariants | ❌ DEFER | Regression net |

### F19 — Dicta-Nakdan adapter

| T-ID | Demo? | Why |
|---|---|---|
| T-01 loader | ✅ | First-call init |
| T-02 NLP context tilt | ⚠️ MAYBE | Heuristic prior; base seq2seq works without it. Test if Economy.pdf has homographs |
| T-03 inference | ✅ | Core call |
| T-04 token skip filter | ✅ | Skip non-Hebrew / numeric / punct |
| T-05 NFC→NFD normalize | ✅ | F20 G2P stability depends on it |
| T-06 adapter contract | ✅ | Smoke test |

### F20 — Phonikud G2P adapter

| T-ID | Demo? | Why |
|---|---|---|
| T-01 loader (lazy + fallback) | ✅ | Phonikud may not install cleanly |
| T-02 inference | ✅ | Core call |
| T-03 PronunciationHint VO | ✅ DONE (scaffold) | Frozen dataclass in place |
| T-04 vocal shva | ❌ DEFER | Phonikud handles internally; verify post-demo |
| T-05 g2p skip filter | ✅ | Same as F19 token skip |
| T-06 adapter contract | ✅ | Smoke test |

### F22 — reading plan

| T-ID | Demo? | Why |
|---|---|---|
| T-01 plan value types | ✅ DONE (scaffold) | PlanBlock + PlanToken in place |
| T-02 ReadingPlan.from_inputs | ✅ | Central assembly |
| T-03 plan provenance | ✅ | Token → src_word_indices |
| T-04 plan invariants | ✅ | Id uniqueness + RTL ordering |
| T-05 empty block skip | ✅ | Edge case; small |
| T-06 deterministic JSON | ✅ | Content-hash basis for `drafts/<sha>/` |
| T-07 page.json projection | ✅ | F35 wire contract; post-review C4 |

### F23 — SSML shaping

| T-ID | Demo? | Why |
|---|---|---|
| T-01 SSML block builder | ✅ | `<speak>` document |
| T-02 per-word `<mark>` | ✅ | Wire-contract pin to PlanToken.id |
| T-03 inter-block `<break>` | ✅ | Pacing |
| T-04 XML escape | ✅ | Hebrew NFD preservation |
| T-05 populate_plan_ssml | ✅ | End-to-end shape |

### F26 — Google Wavenet adapter

| T-ID | Demo? | Why |
|---|---|---|
| T-01 v1beta1 client | ✅ | timepoints require v1beta1 |
| T-02 synthesize | ✅ | Core call |
| T-03 TTSResult assembly | ✅ | word_marks + audio_duration_s |
| T-04 mark truncation detect | ✅ | Hebrew specifically risky; F30 needs the flag |
| T-05 drafts dir write | ✅ | Player loads from `drafts/<sha>/` |
| T-06 adapter contract | ✅ | Smoke test |

### F30 — TTS marks → timings

| T-ID | Demo? | Why |
|---|---|---|
| T-01 mark→timing project | ✅ | Core projection |
| T-02 marks monotonic | ✅ | Adapter regression catch |
| T-03 per-block scope | ✅ | Demo runs block-by-block |
| T-04 graceful truncation | ✅ | Hebrew truncation common; tail-token end_s=null |

### F35 — word-sync highlight (vanilla HTML+JS)

| T-ID | Demo? | Why |
|---|---|---|
| T-01 player.js boot | ✅ | Loads `audio.json` + `page.json` |
| T-02 timing.js parser | ✅ | Sorts timings; binary-search ready |
| T-03 highlight.js rAF loop | ✅ | The visible product |

### F36 — accessibility controls (DEFERRED to v0.1)

| T-ID | Demo? | Why |
|---|---|---|
| T-01 single play button | ✅ | One button gets the demo running |
| T-02 4-button state machine | ❌ DEFER | Pause + restart + replay are polish |
| T-03 button mount/ARIA | ❌ DEFER | A11y is v0.1 |
| T-04 keyboard shortcuts | ❌ DEFER | Polish |
| T-05 button enable states | ❌ DEFER | Polish |
| T-06 focus management | ❌ DEFER | Polish |

**F36 effective load: ~1h** for a one-button play control wired into
F35's `<audio>` element. The remaining 5h of F36 ships in v0.1.

## Phase-level totals (after scope cut)

| Phase | Original task count | Demo-critical | Hours (rough) |
|---|---|---|---|
| Foundation (F03) | 9 | 0 (scaffold covers it) | 0 |
| A. Ingest (F08+F10+F11) | 14 | 8–9 | 12 |
| B. NLP (F14+F17+F18+F19+F20) | 29 | 22–24 | 28 |
| C. Plan/SSML (F22+F23) | 12 | 11 | 12 |
| D. Audio (F26+F30) | 11 | 9 | 11 |
| E. Player (F35+F36) | 12 | 4 | 6 |
| **Total** | **87** | **~55** | **~70h** |

That's a 35% reduction from the original ~110h estimate. Wall-clock
with bundled TDD + AI authorship + parallel cloud sessions: 20–30
hours of agent time, distributed.

## Verification before kicking off — RESOLVED 2026-04-30

Inspected `docs/example/Economy.pdf` p.1 (Hebrew accountant-board exam
intro). All four MAYBE rows defer:

| Task | Decision | Why |
|---|---|---|
| F08-T-04 lang_hint | ❌ DEFER | Page is pure Hebrew; no inline English |
| F14-T-03 line-break rejoin | ❌ DEFER | Paragraphs flow normally; no hyphenated line breaks |
| F14-T-04 stray punct repair | ❌ DEFER (provisional) | PDF is OCR-clean; budget 30 min if Tesseract introduces stray quote marks during real run |
| F17-T-05 long-sentence chunking | ❌ DEFER | Longest sentence ~30 words, well within DictaBERT 512-token context |

**Phase totals after PDF inspection: ~50 demo-critical tasks, ~64h.**

### PDF observations relevant to Phase A TDD

- **Block types observed**: heading (red, bold, underlined),
  paragraph, **numbered list (1–6)**. F11's POC taxonomy is
  `["heading", "paragraph", "question_stem"]`. Numbered list items
  don't match any of the 3 — F11 classifier should treat them as
  `paragraph` (acceptable: the audio reads them; no special handling
  needed). Verify in F11-T-03 (block classifier) test fixture.
- **Red text** is used for visual emphasis ("הנכונה ביותר", "מצב
  הבחינה", etc.). OCR drops color; for the demo the text content alone
  suffices.
- **Footer** (copyright, page number, version) sits at the page
  bottom — Tesseract will pick it up. F11 will treat it as another
  block; F22 will include it in the reading plan; the audio will read
  it aloud. Acceptable for POC; visually marker box stops there.
- **No tables, figures, math, answer-options** on this page —
  matches F11's POC scope cleanly. `BlockTypeOutOfScope` shouldn't
  fire on this PDF.

### Other confirmations

- Single-page demo — yes per `.workitems/PLAN-POC.md`
- No per-block voice routing — yes per PLAN-POC.md

## Handoff to `/tdd`

For each demo-critical task, `/tdd` will:
1. Read the existing skip-marked tests in the linked test file
2. Pick one acceptance criterion (or run **bundled mode** for the whole
   task — recommended for adapter / mechanical tasks)
3. Convert skip-marked stub → failing test (RED)
4. Write minimum code in the relevant `tirvi/<feature>/` module (GREEN)
5. Refactor where needed (REFACTOR)

Skip-marked tests for **deferred** rows stay skip-marked. They're
documented intent; v0.1 unblocks them when their code paths land.
