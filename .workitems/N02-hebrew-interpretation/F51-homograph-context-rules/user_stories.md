---
feature_id: N02/F51
status: designed
---

# User Stories — N02/F51 Homograph Context Rules

## US-01 — Reading-disabled student hears the right possessive form

> **As a** student with reading disabilities listening to a Hebrew exam
> read aloud,
> **I want** the audio to say "her child" (לְיַלְדָּהּ) when the
> sentence is about a mother and her child, and "to a girl"
> (לַיַּלְדָּה) when the sentence is about an unspecified girl,
> **so that** the meaning matches what a fluent reader would
> understand from the printed text.

### F51-S01/AC-01

**Given** the sentence `כל אם רוצה את הטוב ביותר לילדה` (every mother
wants the best for her child),
**when** the pipeline diacritizes the focus word `לילדה`,
**then** the resolved form is `לְיַלְדָּהּ` (to her child, with
mappiq), not `לַיַּלְדָּה` (to the girl).

### F51-S01/AC-02

**Given** the sentence `המשחק הזה מתאים לכל ילד או ילדה` (this game
fits every boy or girl),
**when** the pipeline diacritizes the focus word `ילדה`,
**then** the resolved form is the indefinite/definite girl form, NOT
the mappiq-bearing possessive — the rule must NOT over-fire on
sentences without a possessor.

## US-02 — Reviewer sees clearer reasoning in corrections.json

> **As a** human reviewer working through `corrections.json` after a
> page run,
> **I want** to see which deterministic rule (if any) overrode
> Nakdan's pick,
> **so that** I can audit whether the rule fired correctly and
> trust-or-correct it.

### F51-S02/AC-01

**Given** the F51 rule fires on a token,
**when** the page's `corrections.json` is written,
**then** the token's `entries[].stages[]` contains an entry
`{stage: "context_rule", rule: "<rule_name>", picked_index: <int>,
fired: true, cache_hit: false}` per the ADR-035 schema.

## US-03 — Pipeline maintainer knows the cascade is regression-free

> **As a** pipeline maintainer adding new rules or model versions,
> **I want** a CI fixture that runs the full cascade against ≥30
> homograph cases,
> **so that** I can detect regressions before merge.

### F51-S03/AC-01

**Given** the regression fixture `tests/fixtures/homographs.yaml` with
≥30 cases,
**when** `tests/integration/test_homograph_cascade.py` runs in CI,
**then** strict-pick == gold for ≥ 28/30 cases (≥ 93%) within a 5-minute
latency budget. Sentences marked `gold: ambiguous` pass on either of
the listed acceptable picks.

## US-04 — שלו is read as "calm" when context demands it (conditional)

> **As a** student listening to "הוא טיפוס שלו ורגוע" (he is a calm
> and relaxed person),
> **I want** the audio to say "shalev" (calm), not "shelo" (his),
> **so that** the sentence is intelligible.

### F51-S04/AC-01

**Given** the sentence `הוא טיפוס שלו ורגוע` and the F51 cascade is
running,
**when** the focus word `שלו` is diacritized,
**then** the resolved form is `שָׁלֵו` (calm), not `שֶׁלּוֹ` (his).

**Conditional**: this AC is satisfied either by T-05 (deterministic
rule) or by T-03 (v2 harness prompt) — whichever lands first in the
regression fixture passes the AC.
