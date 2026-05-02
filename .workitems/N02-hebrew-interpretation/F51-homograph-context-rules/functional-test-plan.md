<!-- Authored 2026-05-02 as Phase-0 design backfill; F51 was already merged in PR #29. -->

# N02/F51 — Homograph Context-Rules: Functional Test Plan

## Scope

Verifies the rule-based context layer between Dicta-Nakdan output
and the F48 correction cascade. Covers the possessive-mappiq rule
(deterministic) and the Gemma homograph-judge prompt template
(LLM, deferred consumer). Per ADR-038.

## Source User Stories

- **F51-S01** Reading-disabled student hears the right possessive
  form — Critical
- **F51-S02** Reviewer sees clearer reasoning in corrections.json — High
- **F51-S03** Pipeline maintainer knows the cascade is regression-free — High
- **F51-S04** `שלו` reads as "calm" when context demands (conditional T-05) — Medium

## Test Scenarios

- **FT-300** `apply_rule(sentence, focus, options)` returns the
  1-based index of the first mappiq option when the sentence
  contains a possessor trigger (e.g., `כל אם`). Critical
  (F51-S01/AC-01).
- **FT-301** `apply_rule` returns None when no possessor trigger
  matches. Critical (F51-S01/AC-02).
- **FT-302** `apply_rule` returns None when no mappiq variant
  exists in the candidate list (even if trigger fires). High.
- **FT-303** Trigger lexicon: `כל + {אם / אב / הורה / אישה /
  איש / בן / בת / אדם}` — all 8 lemmas trigger the rule. High.
- **FT-304** Negative case: `המשחק מתאים לכל ילד או ילדה` —
  trigger word `ילד` is NOT in the lexicon; rule must NOT fire.
  Critical.
- **FT-305** Mappiq detection: word ending in `ה` followed by
  U+05BC (DAGESH/MAPIQ) is recognised; word ending in `ה`
  without U+05BC is not. Critical.
- **FT-306** Pipe-prefix handling: `לְ|יַלְדָּהּ` → stem
  `יַלְדָּהּ` correctly identified as mappiq-bearing.
- **FT-307** Empty options list returns None. High.
- **FT-308** Returns FIRST mappiq index when multiple exist
  (for stable, deterministic output).
- **FT-309** F19 Nakdan inference layer (`_apply_context_rules`)
  calls `apply_rule` and overrides Nakdan's top-1 when the rule
  fires. Critical.
- **FT-310** When the rule does not fire, Nakdan's top-1 (or NLP-
  contextualised pick) is preserved unchanged. Critical.
- **FT-311** Provenance: when the rule fires, an entry of shape
  `{stage: "context_rule", rule: "possessive-mappiq", picked_index:
  <int>, fired: true}` is recorded in corrections.json. High.

## Negative Tests

- **FT-312** Rule does NOT fire on a sentence with `כל` but no
  trigger noun (e.g., `כל יום`).
- **FT-313** Rule does NOT fire on isolated `אם` without `כל`
  prefix (e.g., `אם רוצה`).

## Boundary Tests

- **FT-314** Sentence with a single trigger word and a single
  mappiq option: rule returns 1. Smallest non-trivial case.
- **FT-315** Sentence with multiple trigger matches: rule still
  returns the first mappiq index in the candidate list (matches
  are not multiplied).

## Permission and Role Tests

- Read-only at runtime. The rule is a pure function over
  `(sentence, focus, options)` — no I/O, no mutation.

## Integration Tests

- **FT-316** F19 → F51 → F48 chain: the override flows through
  Nakdan inference, into the correction cascade, into
  corrections.json with a proper stage entry.
- **FT-317** Homograph judge prompt template
  `tirvi/correction/prompts/he_homograph_judge/v1.txt` exists,
  contains `{sentence}`, `{focus}`, `{options_block}` placeholders,
  and references the four homograph categories (mappiq, prefix,
  possessive-vs-adjective, interrogative-vs-noun).
- **FT-318** Cache-key isolation per ADR-034: prompt template
  version `v1-homograph-ambiguous` is distinct from the OCR
  reviewer's `v1-scaffold`.

## Audit and Traceability Tests

- **FT-319** Every rule fire is auditable from corrections.json
  back to ADR-038 and the F51 workitem.
- **FT-320** F51 fixture at `tests/fixtures/homographs.yaml` covers
  all 8 BlockType-equivalents for homograph cases (mother /
  whether / calm / his / her-child / etc.) and aggregate strict
  score ≥ 28/30.

## Regression Risks

- **R-01** Trigger lexicon expansion (e.g., adding `כל אדם`) over-
  fires on metaphoric usage. Mitigation: regex anchored on word
  boundaries; explicit negative tests in the F51 unit suite.
- **R-02** F19 Nakdan inference reorganisation could break the
  `_apply_context_rules` integration. Mitigation: integration
  tests at `tests/unit/test_nakdan_inference_context_rules.py`
  assert the contract.
- **R-03** Gemma 4 31B does ~2-5k tokens of internal reasoning
  before emitting JSON. Production callers MUST NOT cap
  `num_predict` below ~6000. Mitigation: documented in
  `_meta.yaml`; F48 reviewer regression test asserts.

## Open Questions

- **Q-01** Should the rule lexicon be YAML-loaded (like F21) or
  Python-frozen (current)? Current is simpler; YAML lets non-
  developers contribute. Defer until lexicon size grows.
- **Q-02** Should T-05 (`she-conjoined-adjective` rule) ship as a
  Python rule or stay deferred? Currently T-05 is conditional on
  the harness prompt covering 100% of `שלו` cases; if it doesn't,
  ship the rule. Awaiting OllamaHomographJudge measurement.
- **Q-03** Should the F51 fixture exercise the full LLM judge
  cascade? Currently rule-only; LLM judge is a heavyweight
  integration. Defer to T-06 follow-up.
