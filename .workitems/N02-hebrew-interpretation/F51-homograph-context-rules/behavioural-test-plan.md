<!-- Authored 2026-05-02 as Phase-0 design backfill; F51 was already merged in PR #29. -->

# N02/F51 — Homograph Context-Rules: Behavioural Test Plan

## Patterns Covered

| Behaviour                                                    | Persona               | Risk                                          | Test    |
|--------------------------------------------------------------|-----------------------|-----------------------------------------------|---------|
| Student listens to a "כל אם" sentence with a possessive child | P01 (ל"ל student)    | hears "the girl" instead of "her child"       | BT-300  |
| Maintainer extends trigger lexicon for a new possessor noun   | P11 (NLP maintainer)  | over-firing on metaphoric usage               | BT-301  |
| Reviewer audits a rule-overridden token in F50 portal         | P08 (QA / teacher)    | invisible rule decision                       | BT-302  |
| Pipeline encounters S1-style genuinely ambiguous sentence     | P01 + P08             | system commits to one of two valid readings   | BT-303  |
| Gemma harness prompt called for hard case                     | P11                   | num_predict cap kills the response             | BT-304  |
| F19 Nakdan REST returns a malformed response                  | P11                   | rule layer crashes downstream                  | BT-305  |

## Scenarios

- **BT-300** Student listens to "כל אם רוצה את הטוב ביותר לילדה"
  on Economy.pdf-style content. Audio plays "le-yald-AH"
  (with mappiq) — the "her child" reading. Behavioural log shows
  `context_rule: possessive-mappiq fired, picked_index=3`.
  Student understands the sentence as a generic statement about
  every mother and her own child, not "to the girl" (which would
  imply a specific identified girl).

- **BT-301** Maintainer proposes adding `סבא` (grandfather) to
  the trigger lexicon. PR review surfaces the question: does
  "כל סבא רוצה X לבת" really fire mappiq? Reviewer adds a fixture
  case AND a negative case (`כל סבא קונה לבת מתנה ביום הולדתה` —
  could mean "to a granddaughter" not "to her granddaughter").
  PR adjusts the case set; lexicon grows with caution.

- **BT-302** Teacher reviewing a Bagrut page in F50 portal sees
  a token where the rule fired. Tooltip shows ADR-038 reference,
  the trigger lexicon match, and the picked index. Teacher
  agrees the override is correct; no action needed. Behavioural:
  audit trail enables silent verification, not just error
  detection.

- **BT-303** A page contains the user-flagged S1 sentence
  ("האם הקריאה ספר לילדה" — genuinely ambiguous between mother
  and whether). The deterministic rule does NOT fire (no possessor
  trigger). Nakdan top-1 picks one reading. The Gemma harness
  prompt (when wired in via the deferred OllamaHomographJudge)
  would emit `verdict: "ambiguous"` per ADR-040 — surfacing both
  readings to F50. Until that consumer ships, the cascade
  silently picks one. Documented limitation; tracked by issue
  #28 and the deferred judge.

- **BT-304** Hard homograph case in production: F48 OCR reviewer
  calls Gemma. With `num_predict` capped to default (no cap),
  Gemma emits a 30-character JSON after ~3000 tokens of internal
  reasoning. With `num_predict=256`, the same call returns an
  empty string (Gemma killed mid-thought). Mitigation: F48
  callers must NOT cap below ~6000; documented in
  `_meta.yaml`.

- **BT-305** F19 Nakdan REST returns a malformed JSON (vendor
  outage / partial response). The vendor-boundary contract test
  catches the shape change; cascade falls to the legacy-string
  options path. F51 rule layer sees a degraded option list;
  rule may not find mappiq variants; returns None; legacy
  Nakdan top-1 wins. Audio still plays (degraded) — never
  crashes.

## Edge / Misuse / Recovery

- **Edge: trigger word at end of sentence**. `כל אם רוצה
  לילדה ספר טוב, כל אם.` — second `כל אם` is at the end. Rule
  fires once (the regex finds the first match); first fragment
  resolves correctly. Subsequent fragment also passes through
  the chunker (F53) and may be rule-overridden again per its
  own `apply_rule` call.
- **Edge: focus word that is NOT a noun**. The rule only
  inspects mappiq presence in the candidate list — it doesn't
  validate that the focus is noun-shaped. If a verb candidate
  happens to end in `ה`+mappiq (rare), the rule could fire.
  Documented; not yet observed in fixture.
- **Misuse: developer adds a regex wildcard to the trigger
  lexicon** (e.g., `\bכל\s+\w+\b`). Architecture forbids;
  reviewer rejects in PR. The conservative approach is the
  point.
- **Recovery: rule raises**. Should not happen — pure regex +
  list iteration. If it does, F19 inference layer's caller
  catches and falls through to top-1.

## Collaboration Breakdown

- **F19 maintainer changes Nakdan response shape** (PR #31
  did exactly this — `task: nakdan` → `task: morph`). F51
  consumes Nakdan options as either str or dict; `_apply_context_rules`
  extracts the `w` field for dicts. Coordinated in PR #31.
- **F48 reviewer prompt template version bumps**. F51's
  homograph judge prompt template is at v1-homograph-ambiguous;
  cache-key isolation per ADR-034 protects against version
  collisions.
- **Future OllamaHomographJudge implementation team**.
  Currently the harness prompt has no production consumer.
  When the team builds it, F51 must surface the threading
  contract: prompt → JSON → dispatch on `pick_index` vs
  `alternatives_indices`. Documented in ADR-040.

## Open Questions

- **Q-01 (BT-303)**: When OllamaHomographJudge ships, should
  ambiguous-flagged tokens get a player UI affordance (e.g.,
  "two readings; tap to switch")? Defer to F50 + F36 design.
- **Q-02**: Should the rule lexicon be language-tagged (Hebrew-
  only currently)? If F24 lang-switch ever activates for
  loanwords, the rule may need to skip mixed-language tokens.
  Defer until F24 work begins.
- **Q-03 (BT-301 follow-up)**: At what trigger-lexicon size do
  we move from Python-frozen to YAML-loaded? F21 (the related
  static lookup) is YAML-loaded. F51 stays Python until either
  size grows beyond ~30 entries OR a non-developer needs to
  contribute.
