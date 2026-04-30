---
feature_id: N02/F15
status: designed
total_estimate_hours: 9.0
---

# Tasks: N02/F15 — Acronym lexicon & expansion (post-POC)

Atomic tasks (≤ 2h each), dependency-ordered. Every task traces to a
design element + at least one biz acceptance criterion + functional /
behavioural test.

## T-01: Value types — Lexicon, AcronymEntry, ExpandedText, ExpansionLogEntry

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01, US-02/AC-01]
- estimate: 1h
- test_file: tests/unit/test_acronym_types.py
- dependencies: []
- hints: frozen `@dataclass`; **reuse F14's `Span` type** — `from tirvi.normalize.value_objects import Span`, do NOT redefine; `Lexicon(version: str, entries: tuple[AcronymEntry, ...])` + `_index: dict[str, AcronymEntry] = field(init=False, repr=False, compare=False)` derived in `__post_init__` via `object.__setattr__`; `AcronymEntry(form, expansion, source, context_tags: tuple[str, ...] = ())`; `ExpandedText(text: str, spans: tuple[Span, ...], repair_log, expansion_log, lexicon_version)` — same `Span` shape as F14, multi-word expansions form ONE logical `Span` per DE-04; `ExpansionLogEntry(original_form, expansion, src_word_indices, spell_out: bool)`. All fields immutable.

## T-02: YAML lexicon loader + mtime cache

- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-111]
- estimate: 1h
- test_file: tests/unit/test_acronym_loader.py
- dependencies: [T-01]
- hints: `Lexicon.from_yaml(path)` parses `data/acronym-lexicon.yaml`. Split into public `from_yaml(path: str | Path) -> Lexicon` + private `_load_cached(path: str, mtime_ns: int) -> Lexicon` decorated with `@functools.lru_cache(maxsize=4)` (mtime keyed inside the cache key, not read implicitly). Iterate entries in YAML source order; build `_index` once. Match the ADR-017 fixture pattern. Entries shape: `[{form, expansion, source, context_tags?}]`. Top-level: `{version: str, entries: [...]}`. Tests use a fixture-scoped cache clear (`_load_cached.cache_clear()`).

## T-03: Whole-token matcher + sentence-final punctuation strip-reattach

- design_element: DE-03
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-106, FT-107, FT-109]
- estimate: 1.5h
- test_file: tests/unit/test_acronym_matcher.py
- dependencies: [T-01]
- hints: walk `NormalizedText.spans`; for each span, take its surface, strip trailing run of `.,?:!` (and Hebrew sof-pasuq), look up bare form in `Lexicon._index`. Sentence-final punctuation reattaches to the **expansion** output verbatim. Geresh `׳` and gershayim `״` are part of the form, never stripped. FT-109: `"ד״ר?"` → expansion `"דוקטור?"`.

## T-04: Expansion emitter (whole-token output + ExpansionLogEntry)

- design_element: DE-04
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-106, FT-107, FT-108]
- bt_anchors: [BT-071]
- estimate: 1h
- test_file: tests/unit/test_acronym_expand.py
- dependencies: [T-02, T-03]
- hints: `tag_and_expand(text: NormalizedText, lexicon: Lexicon) -> ExpandedText`; on lexicon hit emit a new span with the expanded surface and an `ExpansionLogEntry(original_form, expansion, src_word_indices, spell_out=False)`; multi-word expansions (`ת״א → תל אביב`) produce one logical span. FT-108 (`ת״א` ambiguity): pick the top lexicon entry; `context_tags` ignored in v1 (D-04). BT-071 traceability: `original_form` enables the player feedback affordance.

## T-05: URL / embedded-acronym skip filter

- design_element: DE-05
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-negative-2 — "Acronym embedded in URL; left untouched"]
- estimate: 0.5h
- test_file: tests/unit/test_acronym_skip_filter.py
- dependencies: [T-03]
- hints: pre-filter span surfaces matching URL heuristic (contains `://`, leading `www.`, or `^[a-z]+\\.[a-z]`); short-circuit before lookup and before fallback. No log entry; the span passes through unchanged.

## T-06: Unknown-acronym fallback (spell_out flag)

- design_element: DE-06
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-110]
- bt_anchors: [BT-073]
- estimate: 1h
- test_file: tests/unit/test_acronym_fallback.py
- dependencies: [T-02, T-03]
- hints: `is_acronym_candidate(token)` is True when token contains `׳` or `״` OR matches `^[A-Z]{2,6}$`; on candidate + lookup miss, emit `ExpansionLogEntry(original_form=token, expansion=token, src_word_indices, spell_out=True)`. Output text keeps the original form; F23 SSML reads `spell_out` and emits per-letter `<break>`. BT-073 (Yiddish acronym `ב״הנלד״ץ`): not in lexicon → spell-out.

## T-07: bbox→span round-trip property across expansion

- design_element: DE-07
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-106]
- estimate: 1h
- test_file: tests/unit/test_acronym_span_roundtrip.py
- dependencies: [T-04, T-06]
- hints: parametrized pytest table sweeping the input space — lexicon hit / miss, multi-word expansion, sentence-final punctuation, URL skip, empty `NormalizedText`. Assert `set(union of ExpandedText spans.src_word_indices) == set(union of NormalizedText spans.src_word_indices)` for each row. **Do not use `hypothesis`** — it is not in `pyproject.toml`; adding it would require protected-path HITL under POC freeze. The hand-enumerated table covers the round-trip invariant adequately.

## T-08: Lexicon version stamp + lint CLI

- design_element: DE-08
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-111]
- bt_anchors: [BT-072]
- estimate: 1h
- test_file: tests/unit/test_acronym_lint.py
- dependencies: [T-02]
- hints: `ExpandedText.lexicon_version = lexicon.version`; `tirvi/acronym/lint.py` exposes `def main(argv: list[str]) -> int`; `__main__` guard wires `sys.exit(main(sys.argv[1:]))`. `python -m tirvi.acronym.lint <path>` returns exit 0 on valid YAML, non-zero with a one-line error on malformed input (missing `version`, missing `form`/`expansion` on any entry, duplicate `form`). v1 dup-check is on `form` only per D-04; **TODO**: switch to `(form, frozenset(context_tags))` when MVP activates `context_tags`. BT-072 maintainer workflow: PR adds entries, lint runs in CI, bench on a held-out set lifts.

## Dependency DAG

```
T-01 → T-02
T-01 → T-03
T-02, T-03 → T-04
        T-03 → T-05
T-02, T-03 → T-06
T-04, T-06 → T-07
        T-02 → T-08
```

Critical path: T-01 → T-03 → T-04 → T-07 (4.5h).
Total estimate: 9.0h (in line with F14 / F18 sibling features).
