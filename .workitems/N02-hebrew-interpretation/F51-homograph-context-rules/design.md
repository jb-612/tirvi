---
feature_id: N02/F51
feature_type: domain
status: designed
hld_refs:
  - HLD-§5.2/Processing
prd_refs:
  - "PRD §6.3 — Hebrew NLP"
adr_refs:
  - ADR-038
  - ADR-025
  - ADR-033
  - ADR-034
  - ADR-035
biz_corpus: false
research_findings: docs/UAT/UAT-2026-05-02-homograph-pipeline.md
gh_issues:
  - "https://github.com/jb-612/tirvi/issues/25"
  - "https://github.com/jb-612/tirvi/issues/26"
---

# Feature: Homograph Context Rules (sibling of F21)

## Overview

A rule-based context layer between Dicta-Nakdan output and the F48
correction cascade. Where F21 is a static surface→vocalized lookup, F51
operates on `(sentence, focus_word, candidates[])` triples and uses
sentence-context patterns (regex over Hebrew text) to deterministically
override Nakdan's frequency-ranked top-1 when a hard linguistic rule
applies. F51 also ships the v2 LLM-reviewer prompt template — the
"linguistic harness" that engineers Gemma 4 31B's reasoning around the
same homograph categories.

Driven by the round-2 research bench (UAT-2026-05-02) which showed that
the local stack reaches 5/6 strict against a hand-crafted homograph
fixture using Nakdan + the F51 rule + the harness prompt — the same
score as Anthropic Sonnet, at zero per-page API cost. This is the
critical engineering work that keeps the business model local-first.

## Problem statement (single line)

Nakdan's frequency ranking and the v1 reviewer prompt mis-handle three
homograph categories that matter for learning-disabled readers:
mappiq-bearing possessive forms, `שלו` calm-vs-his, and `האם`
mother-vs-whether.

## Dependencies

- **Upstream**: F19 (Nakdan adapter — supplies the candidate list and
  hosts the rule-application call site), F17 (DictaBERT — supplies
  per-token POS used by future rules), F48 (correction cascade — the
  reviewer prompt path being upgraded).
- **Downstream**: F22 (`plan.json` — receives the rule-resolved
  diacritized text), F23 (SSML — emits the audio).
- **External services**: Dicta REST (per ADR-025) for Nakdan; Ollama
  localhost for Gemma. No new external dependencies.

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.homograph.possessive_mappiq` | `apply_rule(sentence, focus, options) -> int \| None` | function | Already shipped at research grade. Promoted to production by T-01. |
| `tirvi.homograph.context_rules` | `apply_context_rules(sentence, focus, options) -> int \| None` | function | New registry introduced by T-02. Composes rules in fixed order; first non-`None` wins. |
| `tirvi.adapters.nakdan.inference` | `_apply_context_rules(entry, sentence) -> str \| None` | helper | New call site between option selection and NFD normalisation. |
| `tirvi.correction.prompts.he_reviewer.v2` | template file | data | Linguistic harness — promotes `scripts/prompts/gemma_he_judge_v2.txt`. |
| `tirvi.correction.prompts.he_reviewer._meta` | `prompt_template_version: v2-homograph` | yaml field | ADR-034 cache-key isolation. |
| `tests.fixtures.homographs` | yaml fixture | data | ≥30 cases for CI regression. |

## Design Elements

### DE-01 — possessive-mappiq rule (production grade)

`tirvi/homograph/possessive_mappiq.py`. Conservative regex-trigger
lexicon (`\bכל\s+(אם|אב|הורה|אישה|איש|בן|בת|אדם)\b`). When fired AND
candidates contain a stem ending `הּ` (ה + U+05BC), pick the first such
variant. Returns `None` (fall-through) when trigger absent or no
mappiq variant present. Fully deterministic, no model call, < 1 ms.

Already implemented at research grade with 8 unit tests passing
(`tests/unit/test_possessive_mappiq.py`). T-01 audits CC ≤ 5,
extends edge-case coverage, and re-anchors the file in F51's
traceability.

**Acceptance**: rule fires on S6 of the bench fixture and picks the
mappiq option; does NOT fire on the negative case
"המשחק מתאים לכל ילד או ילדה".

### DE-02 — production wiring in Nakdan inference

`tirvi/adapters/nakdan/inference.py::_apply_context_rules` — new private
helper. Called from `_project_with_context` for non-separator entries:
look up the focus word's candidate list, dispatch to the rule registry,
and if a rule returns an index, return the resolved string (with prefix
marker stripped) before NFD normalisation. Rules ALWAYS run in
non-separator entries; their `None` return path is the no-op.

When the rule fires, an audit row is emitted in `corrections.json`
(per ADR-035 schema) at `entries[i].stages[]` as
`{stage: "context_rule", rule: "<rule_name>", picked_index: <int>,
fired: true, cache_hit: false}`. ADR-035's schema is open to new
stage entries with no version bump.

**Acceptance**: no test in the existing F19 suite regresses; the bench
fixture S6 case produces `לְיַלְדָּהּ`; CC ≤ 5 on the new helper and
on the modified `_project_with_context`.

### DE-03 — homograph judge prompt template (new namespace)

The existing `tirvi/correction/prompts/he_reviewer/v1.txt` is the
OCR-correction reviewer (verdict: OK/REPLACE; variables sentence,
original, candidates). The homograph harness answers a different
question — "which nikud option fits this sentence" — so it lives in
a NEW namespace, not as a `v2` of the OCR reviewer (which would
conflate two concerns).

`tirvi/correction/prompts/he_homograph_judge/v1.txt` — promoted from
`scripts/prompts/gemma_he_judge_v2.txt`. The "linguistic harness"
prompt: names the four homograph categories (mappiq, prefix-letters
ב/כ/ל/מ/ה/ו, calm/his, mother/whether), enumerates 6 reasoning steps,
includes 3 worked few-shot examples NOT in the regression fixture.
`_meta.yaml::prompt_template_version` is `v1-homograph`. Per ADR-034,
the cache key automatically isolates this from any current or future
OCR-reviewer template version.

T-03 ships the prompt artifact only. The production wiring (an
`OllamaHomographJudge` ICascadeStage that reads this template) is a
follow-up — left out of T-03 because F51's deterministic rule + the
existing F48 reviewer chain already closes 5/6 of the bench cases,
and the dedicated judge stage may be unnecessary depending on T-04's
fixture-level measurement.

**Acceptance**: prompt artifact present at the new path; `_meta.yaml`
declares `v1-homograph`; isolation test confirms `v1-homograph` and
the OCR reviewer's `v1-scaffold` are distinct strings (so
ADR-034's cache key cannot collide).

### DE-04 — regression fixture + CI assertion

`tests/fixtures/homographs.yaml` — ≥30 cases covering: the 6 bench
sentences (mother / whether / whether-plene / calm / his / her-child),
~10 additional 3rd-fem-sing possessive cases (`אִמָּהּ`, `סִפְרָהּ`,
`בִּתָּהּ`, `אַחֲיָהּ`, `יָדָהּ`, ...), ~5 negative cases
("לכל ילד או ילדה" — no possessor; "האם המורה" without verb-feminine
agreement; etc.), and ~10 cross-cutting cases (acronyms, prefix-letter
variants, mixed-language tokens).

`tests/integration/test_homograph_cascade.py` runs the full
N→F51-rule→F48-reviewer cascade against the fixture and asserts strict
score ≥ 28/30 (≥ 93%). Latency budget: ≤ 5 minutes total for the
fixture (CI tolerance).

### DE-05 — she-conjoined-adjective rule (conditional on T-04)

A second rule, `tirvi/homograph/she_conjoined_adjective.py`. Trigger:
focus token is `שלו` AND its sentence has the bigram pattern
`שלו (ו|ב)<adj>` where `<adj>` is in a small adjective lexicon (רגוע,
שמח, בטוח, ...). Action: pick `שָׁלֵו` (calm) over `שֶׁלּוֹ` (his).

Conditional: this rule ships ONLY IF T-04's regression run shows the
v2 harness prompt does not handle this case 100% across the fixture.
If the prompt handles it, T-05 is dropped to keep the rule layer
minimal.

## Out of scope

- The dormant DictaBERT→Nakdan integration
  (`_pick_in_context` morph-options gating). Tracked in
  [issue #27](https://github.com/jb-612/tirvi/issues/27) — independent
  work, neither blocks F51 nor is blocked by F51.
- Ambiguity flagging for genuinely two-valued sentences like S1.
  Tracked in [issue #28](https://github.com/jb-612/tirvi/issues/28) —
  refines ADR-035 schema, complementary to F51 but separate.
- Translating the v2 prompt for the F26 AlephBERT+YAP fallback path
  (different POS schema). F26 stays on v1.

## Risks

- **Over-firing trigger lexicon.** Mitigation: conservative initial
  lexicon (8 nouns), regex anchored on word boundaries, explicit
  negative tests in `test_possessive_mappiq.py`.
- **Prompt v2 reasoning stalls Gemma.** Mitigation: ≥6000
  `num_predict` regression test (research showed empty-string
  responses when capped to 256). F48 currently uses Ollama defaults
  (no cap), so this is a guardrail, not an active bug.
- **Cache-key collision** between v1 and v2 entries. Mitigation:
  ADR-034 already includes `prompt_template_version` in the key;
  T-03 adds an explicit isolation test.
