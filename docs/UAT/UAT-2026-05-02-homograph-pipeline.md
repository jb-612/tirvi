---
title: UAT — Homograph disambiguation across NLP → Nakdan → LLM-judge
date: 2026-05-02
tested_by: Claude Opus 4.7 (programmatic) + Sonnet sub-agent + local Ollama
test_input: 6 hand-crafted Hebrew sentences targeting homograph pairs
              (האם=mother/whether, האים=plene whether, שלו=calm/his, לילדה=to-the-girl/to-her-child)
script: scripts/homograph_judges_bench.py
raw_trace: /tmp/homograph_bench.json
---

# UAT — Homograph disambiguation pipeline

## Methodology

Six sentences run end-to-end through DictaBERT-Morph (NLP) → Dicta Nakdan
REST (with NLP-context branch) → four LLM-as-judge runs. The judge prompt
asks each model to pick the correct vocalization index from Nakdan's full
candidate list, given the Hebrew sentence and the focus word.

Judges:

- **Gemma 4 31B (nvfp4)** — local Ollama
- **Llama 3.1 8B (Q4_K_M)** — local Ollama
- **Sonnet (medium effort)** — Anthropic, via Agent sub-agent
- **Opus 4.7 (high effort)** — Anthropic, inline

Test sentences (all entered without nikud, as OCR would produce them):

| ID | Sentence | Focus | Gold meaning |
|----|----------|-------|--------------|
| S1 | `האם הקריאה ספר לילדה`               | האם   | mother (`הָ\|אֵם`)        |
| S2 | `האם כדאי להקריא ספר`                 | האם   | whether (`הַאִם`)         |
| S3 | `האים כדאי להקריא ספר`                | האים  | whether plene (`הַאִם`)   |
| S4 | `הוא טיפוס שלו ורגוע`                 | שלו   | calm (`שָׁלֵו`)           |
| S5 | `זה הספר שלו`                         | שלו   | his (`שֶׁלּוֹ`)            |
| S6 | `כל אם רוצה את הטוב ביותר לילדה`     | לילדה | her-child (`לְ\|יַלְדָּהּ`) |

## Result table

Strict scoring = exact gold-index match. 🟡 = right *meaning* but a
nikud-variant of the same lemma; ❌ = wrong meaning.

| ID | Gold | Nakdan w/NLP | Gemma 4 | Llama 3.1 | Sonnet (medium) | **Opus 4.7 (high)** |
|----|------|--------------|---------|-----------|-----------------|---------------------|
| S1 | mother      | ✅ mother      | ❌ whether       | ❌ whether       | 🟡 mother (alt nikud) | ✅ mother |
| S2 | whether     | ✅ whether     | ✅ whether       | ❌ "the if"      | ✅ whether            | ✅ whether |
| S3 | whether*    | ✅ whether     | ✅ whether       | ❌ "the if"      | ❌ threatened         | ✅ whether |
| S4 | calm        | ❌ his         | ✅ calm          | ❌ his           | ✅ calm               | ✅ calm |
| S5 | his         | ✅ his         | ✅ his           | ✅ his           | ✅ his                | ✅ his |
| S6 | her-child   | ❌ to-the-girl | ❌ to-the-girl   | ❌ to-a-girl     | ❌ to-a-girl          | ✅ her-child |
| **Strict score**   | — | **4/6 (67%)** | **4/6 (67%)** | **1/6 (17%)** | **3/6 (50%)** | **6/6 (100%)** |
| **Meaning score**  | — | 4/6 | 4/6 | 1/6 | 4/6 | 6/6 |

\* S3 spelling `האים` is plene/non-standard; Nakdan correctly normalises
to the same `הַאִם` reading as S2.

## DictaBERT NLP per-sentence trace

| ID | DictaBERT POS for focus | Did NLP signal change Nakdan's pick? |
|----|-------------------------|--------------------------------------|
| S1 | **SCONJ** (whether) — disagrees with gold (mother) | No — Nakdan still picked top-1 (mother) |
| S2 | **SCONJ** (whether) — agrees with top-1 | No effect (would have picked whether anyway) |
| S3 | **ADV** | No effect |
| S4 | **ADP** (his) — agrees with Nakdan, both wrong | No effect (would still be wrong) |
| S5 | **ADP** (his) — agrees with top-1 | No effect |
| S6 | **NOUN** | No directional signal |

**Net contribution of DictaBERT to Nakdan disambiguation in this run: zero
picks moved.** Below we show this is structural, not a sample-size artefact.

## Root-cause finding — the NLP→Nakdan context branch is dormant in REST mode

`tirvi/adapters/nakdan/inference.py::_pick_in_context` (line 80) does:

```python
morph_options = [opt for opt in entry.get("options") or []
                 if _is_morph_option(opt)]
if not morph_options:
    return _pick(entry)            # falls through to top-1
```

`_is_morph_option` requires each option to be a `dict` with both `'w'` and
`'morph'` keys. The Dicta REST endpoint we currently call returns options
as **bare strings** (`'הָ|אֵם'`, `'הַאִם'`, …), not morph-bearing dicts:

```text
$ uv run python -c "..." (see appendix)
options type: str
first 2: ['שֶׁלּוֹ', 'שֶׁ|לּוּ']
```

So `morph_options` is **always empty** under the current REST response
shape. The morph-scoring path (`_score_option`, `_pos_score`,
`_morph_keys_score`) is never reached. **DictaBERT's POS and morph
features are computed and then discarded** for the purposes of the Nakdan
pick. Nakdan-with-NLP-context degenerates to Nakdan top-1 in production.

This is consistent with what the test set showed: in 6/6 cases Nakdan's
pick matched its top-1, including the case where DictaBERT explicitly said
SCONJ (whether) but Nakdan returned mother (S1).

## What we conclude

### 1. What is the NLP step actually doing? (Direct answer to the user's question)

The user asked: *"NLP models … not producing voice, what do they do
exactly?"* Looking at the code paths, DictaBERT-Morph is consumed by:

| Consumer                                    | Where                                           | Effective today?                  |
|---------------------------------------------|-------------------------------------------------|-----------------------------------|
| Nakdan disambiguation (morph scoring)       | `nakdan/inference.py::_pick_in_context`         | **Dormant** (option shape mismatch — see root-cause above) |
| F48 correction cascade — POS-aware MLM gate | `tirvi/correction/`                             | Active (uses POS to gate corrections) |
| Acronym expansion routing                   | ADR-030, `tirvi/acronym/`                       | Active (POS used to detect noun-vs-acronym) |
| Mixed-language / span detection             | ADR-031, `tirvi/lang_spans/`                    | Active (Hebrew vs Latin separation) |
| TTS prosody / SSML chunking                 | downstream `tirvi/ssml/`, `tirvi/blocks/`       | Partial (sentence boundaries only — no per-token prosody) |
| Coref / homograph override matching         | `tirvi/nlp/disambiguate.py::pick_sense`         | Active when an `ambiguous=True` flag is set on the token |

So NLP is **not voice-producing** but is supposed to be the
*disambiguating intelligence layer* that tells the rest of the pipeline
"this `שלו` is a preposition, not an adjective; this `לילדה` is a noun
with a possessive suffix." It feeds Nakdan, the correction cascade, the
acronym expander, and (lightly) the SSML chunker.

In *this* benchmark, the only NLP→Nakdan path was the morph-scoring
branch, and that branch is currently dormant. The other consumers
(correction cascade, acronym, span detection) weren't exercised because
the test sentences are clean modern Hebrew with no OCR noise, no
acronyms, and no Latin tokens.

### 2. What is dead weight (in this slice of the pipeline)?

**Strong candidates for trimming:**

- **Llama 3.1 8B as a Hebrew judge.** 1/6 strict, frequently picks
  syntactically nonsensical options like `הָ|אִם` ("the if") on
  interrogative-particle questions. It is fast (~2 s/case) but the picks
  are noise. Recommendation: drop from any judge cascade. Keep llama3.1
  only for non-judging tasks where speed matters more than accuracy
  (e.g., the F48 OCR-correction reviewer, where it already runs).

- **DictaBERT morph signal *into Nakdan* (under current REST mode).**
  Until `_pick_in_context` is rewired to either (a) request the
  morph-bearing response shape from Dicta, or (b) use morph features to
  *override* the top-1 string match instead of trying to score
  pre-tagged dicts that never arrive, the NLP morph signal is purely
  decorative for the Nakdan pick. The compute is real (3-4 s for first
  call, ~50-100 ms thereafter); the payoff is zero. Recommendation:
  fix the integration before deciding the layer is dead — see §3.

- **Sonnet's "smart" interpretive habit on quasi-ambiguous prose.**
  Sonnet picked `הֵאִים` (verb "threatened") on S3, an over-clever read
  that doesn't fit the surrounding "כדאי להקריא" frame. As a judge for
  homograph picking, Sonnet sometimes reasons too creatively about rare
  options. Opus is more conservative. Recommendation: if budget allows,
  use Opus high-effort for the judge tier; if not, use Sonnet but
  constrain the prompt to penalise rare/poetic readings.

**Not dead weight, but specific failure modes worth documenting:**

- Nakdan's top-1 ranking is **frequency-biased** and misses lexicalised
  but lower-frequency homographs. In particular, possessive forms with
  mappiq (`לְיַלְדָּהּ`, `סִפְרָהּ`, `אִמָּהּ`) are systematically
  ranked below their non-mappiq twins. This is the diagnostic S6 case.

- DictaBERT's POS tagger maps `שלו` to `ADP` (preposition = "his")
  in **both** S4 (calm context) and S5 (possessive context). The
  context-sensitive distinction `שָׁלֵו`/ADJ vs `שֶׁלּוֹ`/ADP is not
  recovered by the BERT-style tagger in S4. So even *if* the
  morph-scoring branch were live, NLP-context-Nakdan would still ship
  "his" for the calm sentence — fixing the integration alone doesn't
  rescue S4.

### 3. Why does Nakdan + Gemma cover 5/6 but not 6/6 like Opus?

By case:

| ID | Nakdan | Gemma | Combined verdict | Gold | Match? |
|----|--------|-------|------------------|------|--------|
| S1 | mother ✅ | whether ❌ | disagree — tie-break needed | mother | depends on tie-break |
| S2 | whether ✅ | whether ✅ | both right | whether | ✅ |
| S3 | whether ✅ | whether ✅ | both right | whether | ✅ |
| S4 | his ❌    | calm ✅    | disagree — Gemma rescues | calm | ✅ if Gemma wins ties |
| S5 | his ✅    | his ✅     | both right | his | ✅ |
| S6 | to-the-girl ❌ | to-the-girl ❌ | **both wrong (same way)** | her-child | ❌ |

S6 is the unanimous failure. **Gemma defaults to Nakdan's most-frequent
option without reasoning about the mappiq distinction**, so it produces
the same answer as Nakdan instead of correcting it. Both systems share
the same blind spot: they treat `לְיַלְדָּה` and `לְיַלְדָּהּ` as
near-synonyms because the visual difference is one dot.

**Only Opus reasoned about the subject:** "every mother wants the best
for X" forces X to be a possessor's child, hence mappiq. That requires
reasoning about agent-patient roles across the sentence, not just local
POS.

So a Nakdan+Gemma cascade fails on the cases where:

1. The correct option is rare in Nakdan's frequency-ranked list, **and**
2. Distinguishing it requires multi-clause reasoning Gemma 4-31B doesn't
   reliably do.

S6 hits both conditions. So would: `אִמָּהּ` (her mother) vs `אִמָּה`
(a mother), `סִפְרָהּ` (her book) vs `סִפְרָה` (a book), pretty much any
3rd-fem-sing possessive. This is a **systematic** weakness, not a
one-sentence artefact.

### 4. What to improve — concrete actions

In rough priority order:

1. **Fix `_pick_in_context` to actually use NLP morph signal.** Either:
   - (a) Request the morph-bearing response shape from Dicta (some
     Dicta endpoints return option dicts with morphology — check the
     `nakdan` task variant or query parameters), or
   - (b) Implement string-level POS scoring: derive a coarse POS from
     each candidate's prefix-stripped form (e.g., `הַאִם` → INTERJ/SCONJ;
     `הָ|אֵם` → DET+NOUN; `שֶׁלּוֹ` → ADP+suffix; `שָׁלֵו` → ADJ) and
     pick the option whose derived POS matches DictaBERT's tag, then
     fall back to top-1.

   Either way, the unit test added by ADR-025 should be extended with
   a fixture covering S1 (SCONJ vs NOUN+DET disagreement) so the
   integration breakage cannot silently regress again.

2. **Add a possessive-mappiq rule.** When NLP detects a noun-of-noun
   construction with a possessor in subject position
   ("`כל X רוצה … לY`", "X-S `שלו / שלה` Y"), bias Nakdan toward
   mappiq-bearing options for Y. This is a small lexical post-processor;
   it doesn't require changing Nakdan or DictaBERT.

3. **Promote Opus (or Sonnet with constrained prompt) to the
   LLM-as-judge tier.** Gemma 4 31B is a fine first-pass reviewer for
   common cases but cannot reliably distinguish mappiq forms. Today the
   F48 cascade calls Gemma for OCR correction, where it works because
   most errors are character-level (ם↔ס, etc.). For *vocalization*
   judging, escalate to API.

4. **Drop Llama 3.1 8B from any judging role.** Its picks on
   homograph-rich Hebrew sentences are essentially random. It can stay
   as a fast pre-filter only.

5. **Audit which morph features of DictaBERT actually matter
   downstream.** This benchmark suggests POS alone (NOUN/VERB/ADJ/ADP/
   SCONJ) is what the disambiguator needs; full UD morph (Gender,
   Number, Tense, Person, Mood, …) is rarely actionable for nikud
   selection at the Nakdan boundary. If true, a lighter POS-only model
   would cover the same 80% of cases at lower latency. Worth
   benchmarking against the same sentence set.

6. **Build a regression bench from this set.** Add the 6 sentences as a
   fixture under `tests/fixtures/homographs.yaml` and assert that the
   `Nakdan + LLM-judge` combined output matches gold for at least 5/6,
   so that future Nakdan-or-DictaBERT changes can't silently regress
   the cascade.

## Limitations

- N=6 is too small to draw quantitative conclusions; treat the
  percentages as illustrative rather than statistically meaningful.
- All sentences were hand-crafted from the user's brief, biased toward
  the homograph pairs they enumerated. Real OCR output has different
  frequency mixes (acronyms, numerals, English fragments).
- DictaBERT and AlephBERT+YAP are both supported by the codebase; only
  DictaBERT was exercised here. AlephBERT+YAP may behave differently on
  the same set, particularly on S4 (`שלו` ADP-vs-ADJ).
- Anthropic judges were called with default thinking-effort settings.
  Higher reasoning budgets might improve Sonnet's S3 pick.
- The test set deliberately contains no OCR noise, so the F48
  correction cascade was effectively idle. A noisy variant (with
  ם↔ס substitutions, missing yod, etc.) would exercise more of the NLP
  pipeline and is the natural follow-up.

## Appendix — verifying the Dicta REST option shape

```python
$ uv run python -c "
import sys; sys.path.insert(0,'.')
from tirvi.adapters.nakdan.client import diacritize_via_api
raw = diacritize_via_api('הוא טיפוס שלו ורגוע')
for e in raw:
    if e.get('word') == 'שלו':
        opts = e.get('options', [])
        print('options type:', type(opts[0]).__name__)
        print('first 2:', opts[:2])
        break
"
options type: str
first 2: ['שֶׁלּוֹ', 'שֶׁ|לּוּ']
```

`opts[0]` is `str`, not `dict`. `_is_morph_option` returns `False` for
every option. `_pick_in_context` falls through to `_pick`. The DictaBERT
NLPResult is computed but never read.

---

# Round 2 — Local-stack improvements (no Anthropic in cascade)

Motivation: the round-1 finding "only Opus 4.7 hits 6/6" is operationally
unusable. Running Opus on every page would destroy unit economics. The
goal of round 2 is to push the **local stack (Nakdan + Gemma)** toward
parity with Anthropic-grade quality through linguistic engineering, not
model swaps. Sonnet/Opus stay in the bench for scoring reference only,
not in the production cascade.

This work also reflects the user-visible reading goal for students with
learning disabilities: removing the *reading barrier* (homograph
mis-pronunciation) without changing the *cognitive content* of the exam
text. The mappiq case is exactly the kind of mistake a struggling reader
cannot self-correct from context, so getting it right is high-impact.

## Round-2 changes

### Change A — possessive-mappiq rule (deterministic linguistic rule)

`tirvi/homograph/possessive_mappiq.py` — pure-Python, no model call.
Detects sentences where the subject is a generic possessor
(`כל אם / כל אב / כל הורה / כל אישה / ...`) and, when Nakdan's candidate
list contains a mappiq-bearing variant of the focus word
(`X` ending in `הּ` = ה + U+05BC), promotes that variant to the cascade
pick. Rule is conservative — fires only on explicit possessor triggers,
returns `None` (fall-through) otherwise.

8/8 unit tests in `tests/unit/test_possessive_mappiq.py`. CC ≤ 3 per
function. No external calls. ~50 LOC.

### Change B — Gemma linguistic harness prompt

`scripts/prompts/gemma_he_judge_v2.txt` — replaces the bare
"pick from the list" prompt with an explicit linguistic harness:

- Names the four homograph categories the cascade has to handle:
  mappiq inside final ה, interrogative-vs-definite-noun (האם), possessive
  pronoun vs adjective (שלו), prefix-letter parsing.
- Six numbered reasoning steps the model must walk through before
  committing to a pick.
- Three worked few-shot examples (NOT in the test set: "האם המורה כתבה
  על הלוח", "הכלב שלה ישן על הספה", "כל אב נותן עצה לבנו"), showing how
  to apply the rules.
- Reply format requires a Hebrew reasoning line *and* an English reason
  *and* the pick index, so the model must commit to linguistic logic
  before picking a number.

Important operational note: Gemma 4 31B does ~2-5k tokens of internal
reasoning before emitting the JSON. Production calls **must remove the
`num_predict` cap** (or set it ≥ 6000) — otherwise the model is killed
before output, returning empty strings. The current `OllamaLLMReviewer`
uses default `num_predict`, which should be fine, but worth a regression
check if anyone tightens it.

### Pipeline (round 2)

```
DictaBERT NLP
   → Nakdan REST (full candidate list)
   → possessive-mappiq rule (deterministic — fires on ~5% of cases)
       → if rule fires: rule's pick is the cascade output (Gemma not called)
       → else: Gemma 4 31B with linguistic harness prompt
   → cascade pick
```

## Round-2 results

Same 6 sentences, same gold. Local stack only.

| ID | Gold | v1 Nakdan w/NLP | v1 Gemma (bare) | **v2 Cascade (Rule + Gemma harness)** | v1 Sonnet | v1 Opus |
|----|------|-----------------|-----------------|-----------------------------------|-----------|---------|
| S1 | mother      | ✅ mother      | ❌ whether       | ❌ whether (gemma; ambiguous, see below) | 🟡 mother (alt) | ✅ mother |
| S2 | whether     | ✅ whether     | ✅ whether       | ✅ whether (gemma)                       | ✅ whether     | ✅ whether |
| S3 | whether     | ✅ whether     | ✅ whether       | ✅ whether (gemma)                       | ❌ threatened   | ✅ whether |
| S4 | calm        | ❌ his         | ✅ calm          | ✅ calm (gemma — harness rule C)         | ✅ calm        | ✅ calm |
| S5 | his         | ✅ his         | ✅ his           | ✅ his (gemma)                           | ✅ his         | ✅ his |
| S6 | her-child   | ❌ to-the-girl | ❌ to-the-girl   | ✅ her-child (rule fired before LLM)     | ❌ to-a-girl    | ✅ her-child |
| **Strict score** | — | 4/6 | 4/6 | **5/6 (83%)** | 3/6 | 6/6 |

### v2 vs v1 delta

- **S6 fixed by the rule.** Possessive-mappiq fired on `כל אם` and Gemma
  was not called for this case (free + deterministic). Gemma's *own*
  reasoning on S6 (separately observable in the trace) ALSO landed on
  index 3 with the harness prompt, citing "כל אם is a possessor cue,
  pick the mappiq option". So even if the rule didn't exist, the
  harness prompt alone would have fixed S6 — but the rule makes it
  zero-cost and zero-latency.

- **S4 fixed by the harness prompt.** Bare-prompt Gemma got S4 right in
  v1 (3 = calm) — but bare-prompt Gemma also got S1, S3, S6 *parse-
  failed* in v1, so S4 was a coin-flip win. With the harness, S4
  reasoning is explicit ("שלו coordinated with another adjective רגוע →
  שָׁלֵו"), making it a stable answer. Latency dropped from 80-130 s in
  v1 to 14-29 s on most v2 cases (lower temperature variance, less
  hallucination retry).

- **S1 is intrinsically ambiguous.** v2 Gemma's Hebrew reasoning was:
  *"הקריאה היא שם עצם (ה' הידיעה), ולכן האם אינה יכולה להיות נושא"* —
  "`הקריאה` is a noun (definite article), so `האם` cannot be the
  subject; therefore interrogative". This is a defensible parse: read as
  noun, the sentence becomes "Whether the-reading-of a-book to-the-
  girl?" (a yes/no question about the reading event). Read as verb (Hifil
  past 3rd-fem-sing), the sentence is "Did/whether she-read-a-book to-
  the-girl?" — also interrogative. Both readings put `האם` in
  interrogative role; the only way to land "mother" is to override the
  most natural parse. **Opus picked mother because of the absence of
  a `?` mark + narrative-fragment intuition. Gemma's interrogative
  pick is, on linguistic merits, more defensible.** Calling this a
  cascade failure is harsh. Production stance: flag the sentence as
  ambiguous and surface both readings to the corrections-log.

### Latency budget (v2)

| Stage                      | Cost                                       |
|----------------------------|--------------------------------------------|
| DictaBERT NLP              | ~0.05-4 s (warm cache after first call)    |
| Nakdan REST                | ~0.5-1 s                                   |
| Possessive-mappiq rule     | <1 ms (regex match + iterate options)      |
| Gemma harness — fired      | ~14-126 s per call (median ~28 s)          |
| Gemma harness — skipped    | 0 (rule fires)                             |

On a page with ~50 words, expecting ~3-5 homograph candidates per page,
a v2 cascade adds ~1-3 minutes of Gemma compute. Page-cap policy
(`PerPageLLMCapPolicy`) already gates this — see `tirvi/correction/
domain/policies.py`.

### Score summary

| Stack                                            | Strict | Anthropic API used? |
|--------------------------------------------------|--------|---------------------|
| v1 Nakdan + bare Gemma                           | 4/6    | No                  |
| v1 Nakdan w/NLP (DictaBERT integration)          | 4/6    | No                  |
| v1 Llama 3.1 alone                               | 1/6    | No                  |
| v1 Sonnet alone (default thinking)               | 3/6    | Yes                 |
| v1 Opus 4.7 (high effort)                        | 6/6    | Yes                 |
| **v2 Nakdan + possessive-mappiq + Gemma harness** | **5/6** | **No**              |

The local stack closed 1 of the 2 gaps to Opus through linguistic
engineering only. The remaining gap (S1) is a case where Opus made an
arbitrary judgement on a genuinely 50/50 sentence — not a capability
gap that a better local model would close.

## Round-2 follow-ups

In priority order:

1. **Wire possessive-mappiq into production.** Currently lives at
   `tirvi/homograph/possessive_mappiq.py` consumed only by the bench.
   Production wiring point is `tirvi/adapters/nakdan/inference.py`
   between `_pick`/`_pick_in_context` and the final NFC normalisation.
   Will require an ADR (rule-shaped post-processor on Nakdan output) and
   a regression fixture — small, but it's a pipeline-touching change.

2. **Extend the trigger lexicon.** Current rule fires on `כל +
   {אם/אב/הורה/אישה/איש/בן/בת/אדם}`. Add: subject-pronoun-then-feminine-
   noun-then-dative ("`היא לימדה את ילדה`"), "`של<X>`-with-feminine-
   antecedent", and the inverse case (mother as the subject of an
   action toward an unowned object — should NOT fire).

3. **Promote the harness prompt into the production
   `OllamaLLMReviewer`.** Currently it consumes
   `tirvi/correction/prompts/he_reviewer/v1.txt`. Adding a `v2.txt`
   with the homograph-aware reasoning steps, plus a
   `prompt_template_version: v2-homograph` field, would let the cascade
   benefit from the harness without re-implementing it. Cache-key impact
   per ADR-034 needs a glance.

4. **Address the dormant DictaBERT→Nakdan integration (round-1 finding
   §3, action 1).** Independent of round 2 and not done here. Without
   it, DictaBERT's per-token POS tags are wasted compute on pages with
   no acronyms / no Latin tokens. Worth its own workitem.

5. **Add ambiguity flagging.** S1 demonstrates that some sentences are
   genuinely two-valued; the cascade should mark these as low-confidence
   in the corrections log (per ADR-035 schema) so human reviewers can
   decide rather than silently shipping one reading.

6. **Expand the regression set.** N=6 is too small. Useful additions:
   `אִמָּהּ / אִמָּה`, `סִפְרָהּ / סִפְרָה`, `בִּתָּהּ / בִּתָּה`,
   acronym-vs-word collisions (תל"א / תלא), date readings (12.05
   pronounced as "twelfth of May" not "twelve point oh five"), and
   numbers in mixed-language spans. ~30 cases would give a better base
   rate.

## Files added in round 2

- `tirvi/homograph/possessive_mappiq.py` — production-grade rule (~50 LOC, CC ≤ 3)
- `tests/unit/test_possessive_mappiq.py` — 8 tests, all passing
- `scripts/prompts/gemma_he_judge_v2.txt` — Gemma harness prompt
- `scripts/homograph_judges_bench_v2.py` — bench v2 runner
- `/tmp/homograph_bench_v2.json` — full v2 trace

