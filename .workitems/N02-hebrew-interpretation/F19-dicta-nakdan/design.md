---
feature_id: N02/F19
feature_type: domain
status: drafting
hld_refs:
  - HLD-§4/AdapterInterfaces
  - HLD-§5.2/Processing
prd_refs:
  - "PRD §6.4 — Reading plan"
  - "PRD §10 — Success metrics"
adr_refs: [ADR-003, ADR-014, ADR-021, ADR-025, ADR-029]
biz_corpus: true
biz_corpus_e_id: E05-F01
---

# Feature: Dicta-Nakdan Diacritization Adapter (REST API path)

## Overview

Concrete `DiacritizerBackend` adapter wrapping the **Dicta public REST
API** (`https://nakdan-2-0.loadbalancer.dicta.org.il/api`) to add
ניקוד to undecorated Hebrew tokens. ADR-021 originally specced an
in-process HuggingFace loader; that path was abandoned per **ADR-025**
when `dicta-il/dicta-nakdan` proved to be a private/gated repo (HTTP
401). The REST endpoint serves the same Nakdan engine without auth.
Note: Hebrew exam text transits the Dicta public REST endpoint; privacy
posture (data local-first per HLD §9) deferred to MVP per ADR-025.
F18 disambiguation (when reactivated post-F17 reroute per ADR-026)
will supply NLP context which this adapter uses to **score Dicta's
response options** rather than always taking the top pick. Per-word
diacritization picks are also gated by Nakdan's `fconfident` flag and
overridable via the F21 homograph-override lexicon — both learnings
from the v3 demo (issue #20 user feedback on `כל` qamatz-qatan
mispronunciation). ADR-003 anchors the Nakdan + Phonikud stack choice.

## Dependencies

- Upstream: N00/F03 (`DiacritizerBackend` port + `DiacritizationResult`
  value type — locked), N02/F17 (`NLPResult` consumed for context tilt
  via DE-02; absence tolerated — graceful degradation), N02/F14
  (`NormalizedText` input).
- Adapter ports consumed: `tirvi.ports.DiacritizerBackend` (this feature
  implements it).
- External services: **Dicta REST endpoint** (network-required at
  pipeline run time per ADR-025).
- Sibling: **F21 homograph-overrides** — supplies the
  `HOMOGRAPH_OVERRIDES` dict consumed by DE-03; F19 owns the hook,
  F21 owns the entries.
- Downstream: F20 (Phonikud G2P consumes diacritized tokens), F22
  (reading plan stamps pronunciation hint), F23 (SSML emits the
  vocalized form).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.adapters.nakdan` | `DictaNakdanAdapter` | class | implements `DiacritizerBackend.diacritize(text) -> DiacritizationResult` |
| `tirvi.adapters.nakdan` | `DictaNakdanAdapter.diacritize_in_context(text, nlp_context: NLPResult)` | method | NLP-aware overload — scores Dicta response options against POS+morph |
| `tirvi.adapters.nakdan.client` | `diacritize_via_api(text, *, timeout)` | function | POSTs to Dicta REST; stdlib `urllib.request` (per ADR-029) |
| `tirvi.adapters.nakdan.inference` | `_pick(entry)` | function | selection priority: sep > override > options-empty > confidence-gated top option > undecorated fallback |
| `tirvi.adapters.nakdan.overrides` | `HOMOGRAPH_OVERRIDES` | dict | POC seed (1 entry: `כל → כֹּל`); F21 owns the production lexicon |
| `tirvi.adapters.nakdan.normalize` | `to_nfd(text)` | function | NFC→NFD nikud ordering (T-05) |

`DiacritizationResult.provider == "dicta-nakdan-rest"`.
`diacritized_text` is the concatenated per-token vocalized form;
prefix-segmentation marker `|` is stripped (Dicta internal).
`confidence` is `None` for POC (Dicta's `fconfident` is a boolean,
not a numeric margin — finer signal deferred MVP).

## Approach

1. **DE-01**: REST client — POST `{"task":"nakdan","data":<text>,"genre":"modern"}`
   to the Dicta endpoint; 30 s timeout; parse JSON list. Vendor boundary
   (ADR-029) keeps HTTP I/O inside the `client` submodule.
2. **DE-02**: NLP-context conditioning — when `diacritize_in_context`
   receives an `NLPResult` whose tokens align with Dicta's response,
   prefer Dicta options that match the F17 morph signal (POS, gender,
   construct-state). Scoring heuristic: if F17 reports POS=VERB, prefer
   the Dicta option whose vocalized form contains a verb-typical vowel
   pattern (שׁוּרוּק or חִירִיק for binyan markers); if F17 reports
   construct-state=Yes, prefer the Dicta option ending with ַ (patah).
   When no clear signal match, fall through to DE-03 top-pick. This is
   a best-effort heuristic; correctness is gated by the N05 bench.
   Mechanism shifted from "pass context to the model" (in-process)
   to "score response options client-side" (REST) per ADR-025.
3. **DE-03**: Word-level diacritization with override + confidence gate —
   `_pick(entry)` priority chain (matches as-built code in
   `tirvi/adapters/nakdan/inference.py`): (a) `entry.sep == True` →
   emit `entry.word` verbatim (whitespace, punctuation); (b)
   `entry.word in HOMOGRAPH_OVERRIDES` → return the override; (c)
   `not options` → fall back to `entry.word`; (d) `fconfident == False`
   → emit `entry.word` undecorated (Wavenet defaults beat unsure
   nikud, per v3 user feedback); (e) emit `options[0]` with `|`
   markers stripped. **Order rationale**: `sep` first because Dicta
   never returns options for separators; override second because
   separator surfaces (whitespace, punctuation) never appear as
   homograph keys, so reachability of the override branch is preserved.
   The single-character risk surfaced in Round-1 review H2 is
   acceptable since `HOMOGRAPH_OVERRIDES` entries are whole Hebrew
   words. **Refactor contract (required before T-02):** decompose
   `_pick` into three helper predicates — `_passthrough(entry) -> str | None`,
   `_override_hit(word) -> str | None`, `_confidence_gated(entry) -> str | None`
   — so that `_pick` reduces to a chained `or` expression (CC ≤ 3)
   with headroom for T-02's NLP-context branch. This is a named design
   contract, not just a hint.
4. **DE-04**: Token-skip filter — entries whose `word` is pure ASCII /
   pure digits / pure punctuation pass through with no diacritization.
   Implemented inside `_pick` via `entry.sep` flag (Dicta marks these).
5. **DE-05**: NFC→NFD nikud ordering — applied to the concatenated
   diacritized string via `to_nfd()`; downstream G2P (F20) requires NFD.
6. **DE-06**: Adapter contract conformance — `isinstance` against the
   `runtime_checkable` `DiacritizerBackend` Protocol; provider stamp on
   every result; integration smoke uses mocked `urlopen` (the pattern in
   `test_nakdan_client.py`).

## Design Elements

- DE-01: dictaRestClient (ref: HLD-§4/AdapterInterfaces)
- DE-02: nlpContextConditioning (ref: HLD-§5.2/Processing)
- DE-03: wordLevelDiacritizationWithOverride (ref: HLD-§5.2/Processing)
- DE-04: tokenSkipFilter (ref: HLD-§5.2/Processing)
- DE-05: nikudNfcThenNfd (ref: HLD-§4/AdapterInterfaces)
- DE-06: adapterContractConformance (ref: HLD-§4/AdapterInterfaces)

## Decisions

- D-01: Diacritization stack = Nakdan + Phonikud → **ADR-003** (existing).
- D-02: Loader topology = REST API for POC (was in-process per ADR-021) → **ADR-025** (supersedes ADR-021 for POC).
- D-03: Vendor boundary applies to Dicta URL → **ADR-029** (new ADR codifies the previously-implicit rule).
- D-04: Confidence-gated fallback to undecorated when `fconfident=false` → captured in DE-03; no separate ADR (mechanism, not architecture).
- D-05: Homograph override lexicon hook in DE-03; entries owned by F21 → captured in DE-03; no separate ADR.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| In-process loader | REST API for POC | ADR-025 — HF model is private/gated |
| Per-token confidence | Boolean `fconfident` (not softmax margin) | Dicta REST exposes a boolean only; numeric margin requires the in-process model — deferred MVP |
| `diacritize_in_context` mechanism | Score response options client-side, not pass context to model | REST API has no context input; client-side scoring achieves the same intent |
| Lexicon override (E05-F03) | F21 hook present (POC seed in F19); full lexicon owned by F21 | Allows v3 user feedback (`כל → כֹּל`) to land before F21 design completes |
| Word-level accuracy bench | Deferred to N05 | POC has no quality bench |

## HLD Open Questions

- API vs local Nakdan → resolved by ADR-025 (REST for POC).
- Override-vs-fine-tune burden → F21 design (Wave 3) decides lexicon
  schema; current dict is a stop-gap.
- Privacy posture (Hebrew exam text → Dicta servers) → deferred to MVP
  per ADR-025.

## Risks

| Risk | Mitigation |
|------|-----------|
| Dicta endpoint downtime / rate limit | DE-01 timeout + content-hash drafts cache; one call per drafts SHA |
| Dicta JSON shape changes | DE-01 client returns raw response; DE-03 `_pick` is the only consumer with shape assumptions |
| `fconfident=false` over-triggers (too many words fall through to undecorated) | Override lexicon (F21) catches the high-frequency cases; bench in N05 measures rate |
| Override map grows unwieldy | F21 design owns schema + size limit; F19 only consumes |

## Diagrams

- `docs/diagrams/N02/F19/nakdan-rest-adapter.mmd` — text → REST client → `_pick` priority chain (override > sep > confidence-gated top > fallback) → NFC→NFD → DiacritizationResult

## Out of Scope

- In-process model loading (deferred per ADR-025). **Parking strategy:**
  `tirvi/adapters/nakdan/loader.py` and `tests/unit/test_nakdan_loader.py`
  are intentionally **retained on disk** (not deleted) per ADR-025
  §Migration — they are the restoration target if the HF model becomes
  publicly accessible. POC does not exercise the loader path; the
  loader test still passes against its `sys.modules.setdefault` stub
  but is non-load-bearing for runtime correctness. Removing the files
  would require a new ADR.
- Numeric confidence (margin) — deferred to MVP.
- Multi-pass refinement (deferred MVP).
- Word-level accuracy bench (deferred N05).
- Lexicon schema for F21 (separate feature).
- Privacy posture for production (deferred MVP per ADR-025).
