# ADR-038 — Homograph context-rules layer between Nakdan and the LLM reviewer

**Status**: Proposed
**Bounded context**: hebrew-interpretation (N02 — F19, F21, F48 + new F51)
**Owner**: tirvi pipeline orchestrator
**Date**: 2026-05-02
**Related research**: `docs/UAT/UAT-2026-05-02-homograph-pipeline.md`
**Supersedes**: none. Refines ADR-025 (Nakdan REST), ADR-033 (correction
cascade), ADR-034 (LLM reviewer prompt + cache key).

## Context

A 6-sentence homograph benchmark
(`scripts/homograph_judges_bench.py` and `_v2.py`,
trace at `/tmp/homograph_bench{,_v2}.json`,
analysis in the linked UAT) measured the local pipeline against three
hard Hebrew homograph categories:

1. `האם` — interrogative particle "whether" vs definite-article + noun
   "the mother".
2. `שלו` — possessive pronoun "his" vs adjective "calm".
3. **Mappiq inside final ה** — `לְיַלְדָּה` "to a girl" vs
   `לְיַלְדָּהּ` "to her child"; `אִמָּה` "a mother" vs `אִמָּהּ`
   "her mother". One-dot Unicode difference (U+05BC), enormous semantic
   difference. This is the disambiguation that students with reading
   disabilities cannot recover from context — getting it wrong removes
   the reading barrier *and* corrupts the meaning, the worst possible
   failure mode for our user.

Three concrete findings drive this ADR:

### Finding 1 — DictaBERT's morph signal is being silently dropped on the Nakdan path

`tirvi/adapters/nakdan/inference.py::_pick_in_context` filters Nakdan
options to entries that are dicts with a `'morph'` key. The Dicta REST
endpoint we currently call (per ADR-025) returns options as **bare
strings** (`'הָ|אֵם'`, `'הַאִם'`, …). The `_is_morph_option` predicate
returns False for every option, so `morph_options` is always empty and
`_pick_in_context` falls through to `_pick` (top-1 by Dicta confidence).
**DictaBERT POS+morph features are computed and never read.** Verified:
`opts[0]` is `str`, not `dict`. The bench observed zero Nakdan picks
moved by DictaBERT context across all 6 sentences, including S1 where
DictaBERT explicitly tagged `האם` as SCONJ (whether) but Nakdan returned
mother.

### Finding 2 — Nakdan's frequency-ranked top-1 systematically misses possessive-mappiq

For 3rd-fem-sing possessive forms (`לְיַלְדָּהּ`, `אִמָּהּ`, `סִפְרָהּ`,
`בִּתָּהּ`), Nakdan's confidence ranking puts the non-mappiq form first.
This is the right choice on the marginal text (definite-article forms
are commoner overall), but the wrong choice when the surrounding
sentence has a possessor pattern. Lexical lookup (F21) cannot fix this
because the surface form is identical (`לילדה`) — the disambiguator is
**sentence context**, not surface form.

### Finding 3 — Local LLM judges are competitive when the prompt is engineered

A bare "pick the right option" prompt gave Gemma 4 31B 4/6 strict on the
bench (parse-failed on 3, then recovered). A linguistic-harness prompt
that names the homograph categories, walks 6 reasoning steps, and shows
3 worked few-shot examples gave Gemma 4 31B **5/6 strict** with stable
JSON output and ~3× lower latency variance. The remaining S1 failure is
a sentence that is genuinely two-valued in modern Hebrew; even Sonnet
disagreed with the user-stipulated gold via a different mechanism, and
Opus's "right" pick was a stylistic intuition rather than a syntactic
rule.

The business model (Cloud Run + per-page LLM cap, ADR-033 §Cap)
**requires** the production cascade to use a local LLM by default.
Calling Anthropic per page would multiply per-page cost by ~50× and
move the bottleneck from compute to API budget. So the path forward is
*engineering Gemma*, not *swapping Gemma*.

## Decision

We introduce a **rule-based context layer** between Nakdan's output and
the LLM reviewer. The layer is small, deterministic, fast, and
auditable. Two concrete rules ship with this ADR; the layer is open to
more under the same shape.

### Layer position in the cascade

```
F14 normalization
   → F15 acronym expansion
   → F17 NLP (DictaBERT) ───┐
   → F19 Nakdan REST        │
       options[]            │
   → ★ F51 context rules ◄──┘  (new — this ADR)
       cascade pick override (deterministic, optional)
   → F48 correction cascade
       Nakdan gate → DictaBERT-MLM → Ollama LLM reviewer (he_reviewer prompt)
   → F20 Phonikud G2P
   → F23 SSML shaping
```

The context-rules layer sits **after Nakdan and before F48's reviewer
chain**. It operates on `(sentence, focus_word, candidates[])` triples;
when a rule fires, its pick overrides Nakdan's top-1 and is propagated
into the F48 cascade as the `original` token. When no rule fires, the
flow is unchanged.

### Initial rule set (ships with F51 T-01)

1. **possessive-mappiq** (`tirvi/homograph/possessive_mappiq.py`,
   already implemented at research grade, 8/8 tests).

   Trigger lexicon (initial): `\bכל\s+(אם|אב|הורה|אישה|איש|בן|בת|אדם)\b`.
   Action: when fired AND the candidate list contains a variant whose
   stem ends with `הּ` (ה + U+05BC), pick the first such variant. This
   is the rule that fixes S6 in the bench — `כל אם רוצה ... לילדה` →
   `לְיַלְדָּהּ`.

2. **she-conjoined-adjective** (new, in scope of T-02).

   Trigger: focus token is `שלו` AND surrounded by a coordinating
   adjective via `ו` (e.g. "`שלו ורגוע`", "`שלו ושמח`"). Action: pick
   `שָׁלֵו` (calm) over `שֶׁלּוֹ` (his) when both appear in the candidate
   list. This rule is reinforcement for the harness prompt; if the
   prompt alone proves to handle this case 100% across a larger
   regression set, the rule can be deferred.

The interface — `apply_rule(sentence, focus, options) -> int | None` —
is uniform; rules return a 1-based index into the candidate list, or
`None` to fall through. A rule registry composes them in a fixed order
(deterministic-first, conservative-first); the first rule that returns
non-`None` wins.

### Homograph judge prompt — new template namespace, distinct from the OCR reviewer

The existing `tirvi/correction/prompts/he_reviewer/v1.txt` is the
**OCR-correction reviewer** prompt — it answers OK/REPLACE on a single
suspicious token after the F48 NakdanGate flags it. Its variables are
`{sentence}, {original}, {candidates}` and its verdict is binary.

The new prompt being introduced by F51 is a **homograph judge** —
different task, different inputs, different verdict. It answers
"which of N nikud options fits the focus word in this sentence" with
inputs `{sentence}, {focus}, {options_block}`. Re-using the
he_reviewer namespace would conflate the two concerns and confuse the
F48 cascade.

This ADR ships:

- `tirvi/correction/prompts/he_homograph_judge/v1.txt` — the
  linguistic harness (named the 4 homograph categories, 6 reasoning
  steps, 3 worked few-shot examples NOT in the regression fixture).
- `tirvi/correction/prompts/he_homograph_judge/_meta.yaml` —
  `prompt_template_version: v1-homograph`, plus operational notes
  including the `num_predict ≥ 6000` constraint.

The cache key as defined in ADR-034 (`hash(token, sentence_hash,
model_id, prompt_template_version, candidates_tuple)`) is
**automatically isolated** between `v1-homograph` (this template) and
`v1-scaffold` (the OCR reviewer) and any future versions of either —
no migration, no cache collision.

The consumer (an `OllamaHomographJudge` ICascadeStage that reads this
template and returns a `ContextRulePick` analogous to
`CorrectionVerdict`) is OUT of scope for this ADR — see "Out of
scope" below. T-03 ships only the prompt artifact and its tests; the
production wiring of the homograph judge as an ICascadeStage is a
follow-up workitem (F51 T-06 or its own feature, depending on whether
the round-2 deterministic rule + harness+OCR-reviewer fallback closes
the bench gap without a dedicated judge stage).

Operational footnote: Gemma 4 31B does ~2-5k tokens of internal
reasoning before emitting the JSON. Production calls **must not cap
`num_predict` below ~6000**, or the model is killed mid-thought and
returns an empty string. F48 currently uses Ollama defaults (no cap),
so this works as-is — but a regression test asserting
`num_predict >= 6000 OR unset` belongs in the F48 test suite.

### Out of scope for this ADR

- **Fixing the dormant DictaBERT→Nakdan integration**
  (`_pick_in_context` morph-options gating — Finding 1). Worth its own
  ADR + workitem. Tracked as a separate GitHub issue (and as F19
  follow-up) so it doesn't block F51.
- **Ambiguity flagging in `corrections.json`** (per ADR-035) for
  genuinely two-valued sentences like S1. The field shape is a contract
  with F50, so it gets its own ADR rev.
- **Prompt template translation to AlephBERT+YAP fallback path** (F26).
  The v2 prompt assumes DictaBERT-Morph POS tags are in scope; F26 has
  a different POS schema. AlephBERT+YAP path remains on v1 prompt for
  now. ADR review when F26 promotion is back on the docket.

## Alternatives considered

### A. Promote Sonnet/Opus to the F48 reviewer tier

**Rejected.** Killing the local-stack constraint is a business-model
break. Sonnet at ~$3/M input × 1k tokens × 50 calls/page × 1k pages/
day = ~$150/day at our smallest paying-cohort scenario, before output
costs. Local Gemma at the same load is bounded by hardware. The
research showed engineered Gemma reaches 5/6 — same as Sonnet's meaning
score — without the cost.

### B. Replace Nakdan's _pick with a heavier "context-aware" LLM call per token

**Rejected.** Nakdan's frequency prior is correct on the *vast*
majority of words; only a small fraction of focus tokens are
ambiguous-by-context. Calling an LLM per token would inflate
per-page LLM count by ~50× and blow the page-cap policy
(`PerPageLLMCapPolicy`) repeatedly. Targeted rules + a single
reviewer per genuinely-suspect token preserves the cap.

### C. Extend F21 (homograph overrides) with sentence-context patterns

**Rejected.** F21's data shape is a flat surface→vocalized map keyed by
unvocalized form, plus an optional POS filter. Adding regex-over-
sentence patterns to that schema would force F21's loader and
validation to grow into a rule engine. Cleaner to keep F21 as a static
lexicon and own context rules in a sibling feature (F51).

### D. Move the rule layer downstream of F48 (post-LLM correction)

**Rejected.** The F48 reviewer is gated by NakdanGate's "suspect" verdict
and PerPageLLMCapPolicy. If a rule could rescue a token deterministically,
calling the LLM first and then overriding it after the cap has been spent
is wasteful. Rules upstream of F48 short-circuit the LLM call.

### E. Encode the rules in the v2 prompt as instructions, no Python rule layer

**Considered, partially adopted.** The v2 prompt's 6 reasoning steps
*do* encode the linguistic logic, and on the bench Gemma followed them
correctly when the rule would have fired anyway (S6 — Gemma reasoned
about "כל אם" as a possessor cue and picked the mappiq option). But
prompt-only enforcement is non-deterministic across model versions
and stochastic across temperature, and it costs tokens. Hard rules
where they're unambiguous (possessive-mappiq with explicit trigger
lexicon) + soft rules in the prompt (everything else) gives best of
both: zero-cost / zero-latency for the easy cases, harness-engineered
LLM for the rest.

## Consequences

### Positive

- Local-stack accuracy on the homograph bench rises from 4/6 strict
  (v1 Nakdan + bare Gemma) to 5/6 strict (v2 Nakdan + rule + harness).
  Same as Sonnet's meaning-score, at zero per-page API cost. The S1
  remaining miss is a genuine ambiguity, not a model-capacity gap.
- Mappiq distinction (the highest-stakes failure mode for our
  learning-disabled user cohort) goes from 0% (every system without
  Opus) to 100% deterministic on the trigger pattern.
- Per-page LLM call count drops slightly: the rule short-circuits ~5%
  of tokens that would otherwise hit F48's reviewer. Lower cap-pressure
  → fewer `cap_response` no-ops on long documents.
- Adds an auditable, named layer in `corrections.json` (`stages[]`
  gains an entry `{stage: "context_rule", rule: "possessive-mappiq",
  fired: true, picked_index: 3}`). Per ADR-035 the schema is open to
  new stage entries with version bump if shape changes.

### Negative / risks

- A miscalibrated rule trigger could over-fire and wrongly prefer
  mappiq on sentences that don't deserve it (e.g., "כל אם תרצה לפנות
  לילדה ספציפית..."). Mitigation: rule tests pin the trigger lexicon
  exactly, and the rule is conservative (returns None on any ambiguity)
  — no fuzzy matching.
- DictaBERT's POS tags remain dormant on the Nakdan path even after
  this ADR ships. Independent ADR + issue tracks the fix; F51 does not
  block it but does not solve it either.
- Adds a new module to maintain: `tirvi/homograph/possessive_mappiq.py`
  (already shipped at research grade) plus a future
  `tirvi/homograph/context_rules.py` registry. Both small (<100 LOC
  each, CC ≤ 5).
- Cache-key bump (v1 → v2-homograph) invalidates existing F48 cache
  entries. On next run, every previously-cached suspect token re-runs
  through Gemma. ADR-033 §Cap allows this; observable as a one-time
  bump in `cache_hit_chain[2]` rate. Not a correctness risk; a one-day
  cost spike.

### Operational

- F51 ships with a regression fixture
  `tests/fixtures/homographs.yaml` carrying the 6 bench sentences plus
  ~24 additional cases (her-mother, her-book, her-daughter,
  acronym-vs-word, mother-without-prefix, etc.) for ≥30 cases total.
  CI runs the cascade on the fixture and asserts strict-score ≥ 28/30
  (~93%).
- The S1 sentence stays in the fixture but is marked
  `gold: ambiguous, accepted: [option_1, option_2]` to encode that
  either reading is acceptable. This requires a small extension to the
  bench harness's gold-checker and a parallel extension to ADR-035 for
  marking ambiguous tokens in `corrections.json` — tracked as the
  ambiguity-flagging issue.

## Implementation order (one PR per task ID)

1. **F51 T-01** — Move `tirvi/homograph/possessive_mappiq.py` from
   research grade (already shipped) to production grade: add it to the
   F51 traceability.yaml, ensure CC ≤ 5 on every function, extend
   tests to cover the trigger lexicon's edge cases.
2. **F51 T-02** — Wire the rule into `tirvi/adapters/nakdan/inference.py`
   between option selection and NFD normalisation. New helper
   `_apply_context_rules(entry, sentence, nlp_tokens) -> str | None`,
   called from `_project_with_context`.
3. **F51 T-03** — Add `tirvi/correction/prompts/he_homograph_judge/v1.txt`
   + `_meta.yaml` declaring `prompt_template_version: v1-homograph`.
   Production wiring (`OllamaHomographJudge` ICascadeStage) is a
   follow-up; T-03 ships the artifact only.
4. **F51 T-04** — Regression fixture `tests/fixtures/homographs.yaml`
   (≥30 cases) and CI assertion in `tests/integration/
   test_homograph_cascade.py`.
5. **F51 T-05** — `she-conjoined-adjective` rule. Conditional on T-04
   showing the harness prompt alone doesn't already handle this case
   100% — if it does, T-05 is dropped.

## References

- `docs/UAT/UAT-2026-05-02-homograph-pipeline.md` — research findings,
  before/after measurements, latency budget.
- ADR-025 — Dicta-Nakdan REST integration (the source of the
  bare-string option shape that Finding 1 tracks).
- ADR-026 — DictaBERT-Morph as the NLP backbone.
- ADR-033 — F48 correction cascade architecture.
- ADR-034 — LLM reviewer prompt template + cache-key strategy (this
  ADR adds the `v2-homograph` template under that scheme).
- ADR-035 — `corrections.json` schema (new `stage: "context_rule"`
  entry shape).
- `tirvi/homograph/possessive_mappiq.py` — research-grade rule shipped
  in the round-2 bench; promoted to production by F51 T-01.
- `scripts/prompts/gemma_he_judge_v2.txt` — research-grade harness
  prompt; promoted to `tirvi/correction/prompts/he_reviewer/v2.txt`
  by F51 T-03.
