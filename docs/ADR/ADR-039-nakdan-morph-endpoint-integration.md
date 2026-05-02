# ADR-039 — Dicta-Nakdan `task: morph` endpoint + lex-based context scoring

**Status**: Proposed
**Bounded context**: hebrew-interpretation (N02/F19, F17, F51)
**Owner**: tirvi pipeline orchestrator
**Date**: 2026-05-02
**Related research**: probe results in this commit (see `docs/research/`)
**Closes**: GitHub issue #27
**Refines**: ADR-025 (Nakdan REST), ADR-038 (homograph context-rules)

## Context

ADR-038 §Finding 1 documented that `tirvi/adapters/nakdan/inference.py::
_pick_in_context` filters Nakdan options to dict-shaped morph entries
that the current Dicta REST call (`task: "nakdan"`) never returns —
options come back as bare strings. DictaBERT's POS+morph features are
computed and silently discarded for the purposes of Nakdan
disambiguation.

Issue #27 proposed two fix paths:

A. Request the morph-bearing response shape from Dicta, if one exists.
B. Implement string-level POS scoring on bare candidate strings.

A reconnaissance probe (2026-05-02) confirmed that Dicta REST
**accepts `task: "morph"`** and returns options as dicts with the
following per-option fields:

```jsonc
{
  "w": "שֶׁלּוֹ",          // vocalized form (same as `task=nakdan` strings)
  "lex": "שֶׁל",            // Hebrew lemma (vocalized) — the semantic key
  "morph": "628815097...", // numeric bitfield, encoding undocumented
  "morphDifference": "..", // optional, distance from consensus
  "levelChoice": 1,        // 1 = Dicta top pick; 2/3 = fallback rankings
  "prefix_len": 0,         // 0 = no clitic prefix; ≥1 = prefix attached
  "Acc": "Acc0",           // accuracy class; Acc0 ≈ confident, AccUnk ≈ uncertain
  "stdW": "שֶׁלּוֹ",        // standardised form (≈ w in modern genre)
  "fMorphNGram": false,
  "NGramID": -1,
  "fNikMatch": false
}
```

Three sample sentences confirm `lex` distinguishes meaning at the
lemma level:

| Surface | lex (option 1)   | lex (alternative) | meaning split             |
|---------|------------------|--------------------|---------------------------|
| `שלו`   | `שֶׁל`           | `שָׁלֵו`           | his (preposition) vs calm (adjective) |
| `האם`   | `אִם`            | `אֵם`              | whether (conj) vs mother (noun) |
| `לילדה` | `יַלְדָּה`        | `יֶלֶד`            | (la-)yalda (girl) vs (le-)yaldah (her child) |

The `morph` numeric field is undocumented; high bits appear to encode
POS class, low bits encode features (gender/number/person/tense), but
without an official schema, decoding it is reverse-engineering — risky
when Dicta upgrades.

## Decision

We adopt **path A** with the **`task: "morph"`** endpoint, but we do
**not** decode the `morph` numeric field. Instead, the inference layer
uses three robust signals:

1. **`lex`** — Hebrew lemma (vocalized). Compared to DictaBERT-Morph's
   `token.lemma` after nikud-stripping, OR matched against a small
   curated function-word lexicon when DictaBERT's lemma is `None` or
   unreliable.
2. **`prefix_len`** — `0` means no clitic prefix attached, `≥ 1` means
   one or more clitic letters (ב/כ/ל/מ/ה/ו) precede the stem.
3. **Surface-vs-lex comparison** — when the prefix-stripped vocalized
   form `w_strip` equals `lex` (as strings, both vocalized), the
   candidate is a "canonical form" of its lemma; combined with
   `prefix_len == 0`, this is a strong adjective/noun signal.

These three signals + DictaBERT's `token.pos` are enough to disambiguate
the case set in ADR-038's bench (ADJ vs ADP for `שלו`; SCONJ vs DET+NOUN
for `האם`) without touching the bitfield.

### Updated inference logic

`_pick_in_context(entry, token)` runs in this order:

1. **F51 context-rules layer** (per ADR-038) — extracts the str list
   `[opt['w'] for opt in options]` and calls
   `tirvi.homograph.possessive_mappiq.apply_rule`. If it returns an
   index, the corresponding `opt['w']` is the resolved form. (F51's
   contract stays str-only; the dict ↔ str conversion lives in the
   inference layer, not the rule.)
2. **DictaBERT-context scoring** — when DictaBERT returned a `pos`
   for the focus token, score each option by its lex / prefix /
   surface fit and pick the highest. Tie-break by `levelChoice` (lower
   wins) then by Dicta's original ordering.
3. **Top-1 fallback** — when DictaBERT returned `pos=None` or no
   option scores higher than the top-1, return `options[0]['w']`.

### Heuristic scoring rules

```python
def _score_option(option, token):
    score = 0
    pos = token.pos
    lex = option.get("lex", "")
    w = option.get("w", "").replace(_PREFIX_MARKER, "")
    prefix_len = option.get("prefix_len", 0)

    if pos == "ADJ" and prefix_len == 0 and _strip_nikud(w) == _strip_nikud(lex):
        score += 3
    if pos in {"ADP", "SCONJ"} and lex in _FUNCTION_WORD_LEXICON:
        score += 3
    if pos == "VERB" and "_" in lex:   # Dicta verb lemma convention "קרא_פעל"
        score += 2
    if pos == "NOUN" and prefix_len <= 1 and "_" not in lex:
        score += 1
    return score
```

`_FUNCTION_WORD_LEXICON`: `{"אִם", "כִּי", "אֲשֶׁר", "שֶׁל", "אֶת",
"אוֹ", "אַף", "אַךְ", "כְּמוֹ", "אֲבָל"}` — small, conservative,
extensible.

### Backwards compatibility

- F51 rule layer: continues to operate on the str list. Inference
  layer extracts `[o['w'] for o in options]` before calling
  `apply_rule`, then maps the returned index back to the dict.
- Existing `tests/unit/test_nakdan_inference_context_rules.py` uses
  manufactured Dicta entries with `options: [str]` — still valid for
  the F51 rule path because the test fixture is hand-crafted. Tests
  are extended (not replaced) with dict-shape options for the new
  scoring path.
- `tests/integration/test_homograph_cascade.py` fixture options are
  bare strings; the test feeds them through `_project_with_context`
  which reaches the F51 rule layer first. No changes required.

### Cache implications

ADR-034's correction-cascade cache key includes
`(token, sentence_hash, model_id, prompt_template_version,
candidates_tuple)`. The `candidates_tuple` for the F48 reviewer is the
list of corrected-spelling candidates, NOT the Nakdan option list, so
this ADR has no cache-key impact.

## Alternatives considered

### B. String-level POS scoring on bare `task: "nakdan"` options

**Rejected.** Bare-string options have no lemma signal. Heuristics on
the vocalized surface alone cannot reliably tell SCONJ `הַאִם`
"whether" from DET+NOUN `הָאֵם` "the mother" — both have similar
nikud patterns. Path A's `lex` field gives us the semantic key for
free, plus we keep DictaBERT's POS as a tie-breaker rather than the
sole signal.

### C. Decode the Dicta `morph` numeric bitfield

**Rejected.** Undocumented schema. We have indirect evidence (POS class
in high bits, features in low bits) but no official mapping. Any
correctness depends on Dicta keeping the encoding stable; their REST
endpoint version (`nakdan-2-0`) suggests they are willing to break.
Heuristic scoring on `lex` + `prefix_len` covers the same disambiguations
without the brittle dependency.

### D. Switch to `task: "nakdan" + addmorph: true + useTokenization: true`

**Rejected.** This variant returns a deeply nested shape
(`{data: [{nakdan: {word, options: [{...}]}}]}`) instead of the flat
list. Larger refactor in `client.py` for the same per-option
information `task: "morph"` already provides. Stick with the
flat-shape variant.

### E. Cache the Dicta response + run BOTH endpoints and merge

**Rejected.** Doubles network cost and adds a merge contract for no
new information; `task: "morph"` is a strict superset of `task:
"nakdan"`'s information.

## Consequences

### Positive

- DictaBERT's POS signal is finally consumed downstream. The bench's
  S4 (`הוא טיפוס שלו ורגוע` — calm) becomes resolvable by the rule +
  scoring path alone, without requiring the LLM judge for that case.
  Estimated F51 fixture impact: 1-2 cases flip from xfail to pass
  (C04 candidate; C19 also if structurally similar).
- Closes the integration breakage that ADR-038 §Finding 1 documented
  but did not solve. The architectural intent of `_pick_in_context`
  is finally realised.
- The `lex` field carries enough information to support future
  semantic rules without further protocol changes.
- Per-page latency is unchanged (same endpoint, same one round-trip).

### Negative

- The `task: "morph"` endpoint is undocumented. Dicta could change or
  retire it. Mitigation: `client.py` has a vendor-boundary test
  asserting the response shape; CI catches a shape change before
  production. If Dicta retires the endpoint, fall back to path B
  (string-level scoring) — research confirmed it as a viable second.
- Adding scoring heuristics adds maintenance surface. The function-
  word lexicon needs occasional curation as we expand language
  coverage. Mitigation: lexicon lives in a single dict in
  `inference.py` with a doc-comment.
- DictaBERT-Morph occasionally mis-tags POS (e.g., S4 `שלו` was
  tagged ADP "his" — wrong). When it does, scoring follows the wrong
  path. The F51 LLM-judge layer remains the safety net; this ADR
  does not promise to make every case correct, only to stop
  discarding the signal.

### Operational

- Vendor-boundary contract test asserts every option in a Dicta
  response has at least `{w, lex, prefix_len, levelChoice}` keys;
  fails fast on schema drift.
- The `_FUNCTION_WORD_LEXICON` lives in `tirvi/adapters/nakdan/
  function_words.py` so future additions don't bloat `inference.py`.
  Module ships with the 10 entries listed above.

## Implementation order

1. **Tests first** — extend
   `tests/unit/test_nakdan_inference_context_rules.py` with dict-shape
   option fixtures covering: ADJ vs ADP for `שלו`, SCONJ vs DET+NOUN
   for `האם`, NOUN vs the same, verb stem.
2. **`tirvi/adapters/nakdan/function_words.py`** — small new module
   for the function-word lexicon. Single dict, no logic.
3. **`tirvi/adapters/nakdan/client.py`** — change `task: "nakdan"` →
   `task: "morph"`. One-line.
4. **`tirvi/adapters/nakdan/inference.py`** — adapt `_pick`,
   `_pick_in_context`, `_apply_context_rules`, `_score_option`,
   `_is_morph_option`. CC ≤ 5 throughout.
5. **Vendor-boundary contract test** —
   `tests/unit/test_nakdan_client_morph_shape.py` asserts the
   live-API response shape on a fixed input. Marked
   `@pytest.mark.network` so CI can skip it when offline; runs in
   the nightly + on PRs that touch `client.py`.
6. **F51 fixture compatibility** — confirm
   `tests/integration/test_homograph_cascade.py` still passes with
   no fixture edits.
7. **F51 fixture extension (optional)** — flip C04 from
   `expected_failure: true` to a pass if the new scoring path
   resolves it.

## References

- GitHub issue #27 — original problem statement
- ADR-025 — Nakdan REST adoption
- ADR-026 — DictaBERT-Morph as NLP backbone (provider of `token.pos`)
- ADR-038 — F51 homograph context-rules (downstream consumer)
- ADR-029 — Vendor-boundary discipline (`client.py` is the only
  module that may change task name)
- ADR-034 — F48 reviewer cache-key strategy (no impact)
