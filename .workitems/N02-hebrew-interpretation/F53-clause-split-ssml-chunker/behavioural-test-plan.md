<!-- Authored 2026-05-02 as Phase-0 design backfill. -->

# N02/F53 — Clause-Split SSML Chunker: Behavioural Test Plan

## Patterns Covered

| Behaviour                                                  | Persona                | Risk                                         | Test     |
|------------------------------------------------------------|------------------------|----------------------------------------------|----------|
| Student listens to a 30-word Bagrut sentence               | P01 (ל"ל student)     | comprehension fails on unbroken audio        | BT-220   |
| Maintainer adds CONJUNCTION_LEXICON entry                  | P11 (NLP maintainer)   | over-split on homograph                      | BT-221   |
| Reviewer audits a chunked page in F50 portal               | P08 (QA / teacher)     | invisible split decisions                    | BT-222   |
| Player skips back to a chunked sentence                    | P01                    | mid-sentence resume sounds wrong             | BT-223   |
| Pipeline runs in degraded NLP mode (F18 unavailable)       | P11                    | conjunction splits silently break            | BT-224   |
| Long unbreakable sentence in real Bagrut text              | P01                    | tirvi can't help on this case                | BT-225   |
| Acronym + chunked clause + acronym in one sentence         | P01                    | F15 expansion adds tokens, pushes over cap   | BT-226   |

## Scenarios

- **BT-220** Student listens to a 35-word economics question with
  a comma at index 18. The audio plays the first 19 tokens, takes a
  ~500ms pause, then plays the remaining 17 tokens. The student
  reports that the pause "let me hold the first half before the
  second came". Behavioural log shows
  `clause_split: reason=punctuation, fragment_word_count_after=17`.

- **BT-221** Maintainer proposes adding `כי` (single-word SCONJ
  causal) to `CONJUNCTION_LEXICON`. PR review surfaces FT-227 +
  multiple corpus cases where `כי` appears as a non-SCONJ
  particle. Maintainer either tightens the SCONJ guard or
  withdraws the addition. (Behaviour: PR + reviewer interaction;
  not an automated test, captured here as a process invariant.)

- **BT-222** Teacher reviewing a Bagrut page in F50 portal sees a
  long sentence flagged with two `clause_split` provenance
  entries. Tooltip shows `ADR-041 #9` link, the
  `at_token_index`, and the chosen `reason`. Teacher decides to
  override the lower-confidence split via the corrections.json
  edit interface. (Behaviour: portal interaction; F50 owns the
  UI.)

- **BT-223** Student presses `K` (previous-question, per F39) on a
  page that contains a chunked sentence. Marker advances to the
  start of the previous question_stem block — NOT to a chunked
  fragment within a question. F39 only navigates by `block_kind:
  question_stem`, never by clause split. (This is documented
  invariant; F39's keyboard handler asserts via test.)

- **BT-224** F17 DictaBERT fails to load; pipeline runs in
  degraded NLP mode emitting `pos=None` on every token. F53
  chunker drops to punctuation-only path. Long sentences with
  punctuation still split; long sentences with conjunction-only
  boundaries fall to the `clause_split_skipped` path.
  Behavioural log shows the `pos=None` source AND the
  punctuation-only resolution.

- **BT-225** A 45-word Bagrut sentence with no punctuation and no
  SCONJ conjunction in the lexicon (e.g., a list of paired noun
  phrases joined by `ו`). Chunker emits `clause_split_skipped`.
  Audio plays the unbroken 45-word sentence. Reviewer flags via
  F50 portal; this becomes a candidate to extend the lexicon
  (with SCONJ guard) — process loop closes via BT-221.

- **BT-226** Sentence: `המוסדות הציבוריים כצה"ל ומד"א פועלים
  בכל הארץ ולכן הם נדרשים לתחזוקה רציפה ויעילה`. F15 expands
  acronyms inline (`צה"ל → צבא הגנה לישראל`); now the sentence
  has 22 → 27 tokens. F53 sees over-threshold AND `ולכן` (not
  in lexicon) is the only non-punctuation candidate. The
  `,`-less sentence may emit `clause_split_skipped`. Behavioural
  log shows: F15 acronym expansion fired (per ADR-041 #1), then
  F53 attempted split, then F53 emitted skip provenance. F50
  reviewer sees both transformations chained.

## Edge / Misuse / Recovery

- **Edge: zero-token sentence**. `chunk_block_tokens([], 22)`
  returns `([[]], [])` — degenerate but non-crashing. Test
  FT-233.
- **Edge: punctuation as the FIRST token**. `_first_punct_index`
  returns 0; `_candidate_boundaries` emits `(1, "punctuation")`;
  the first fragment is just `[".",]`. Behaviourally noisy but
  not invalid; the player skips empty-content fragments at
  render time.
- **Misuse: developer passes raw `tuple` of tokens**. Function
  is type-hinted `list[PlanToken]`; runtime accepts both since
  Python iteration is duck-typed. Documented; not enforced.
- **Recovery: chunker raises**. Should not happen — pure
  function with no I/O. If it does (e.g., `PlanToken` shape
  changes upstream), F23 builder catches via the existing
  `try / except` around SSML emission and falls back to the
  pre-F53 (no-chunk) body shape. Not yet implemented; tracked
  as R-05 in the FT plan.

## Collaboration Breakdown

- **Two NLP maintainers concurrently extending CONJUNCTION_LEXICON**.
  Each adds their own entry; merge conflict surfaces in the
  frozenset literal. Resolution: alphabetise the lexicon, both
  entries land. Coordinated via mailbox before either pushes.
- **F18 maintainer changes POS tag schema**. F53 reads
  `PlanToken.pos == "SCONJ"`. If F18 renames the tag (e.g., to
  `"CONJ"`), F53 silently stops conjunction-splitting.
  Mitigation: contract test on the POS string is part of the F53
  unit suite (`test_clause_chunker.py::TestConjunctionBoundaries`).
- **F23 maintainer reorganises `populate_plan_ssml`**. F53's
  `_block_with_ssml_and_provenance` helper depends on F23's
  iteration order over `plan.blocks`. If F23 introduces parallel
  block emission, the `dataclasses.replace` call would race.
  Mitigation: F23 tests assert single-threaded block emission as
  an invariant (existing).

## Open Questions

- **Q-01 (BT-225 follow-up)**: How often does
  `clause_split_skipped` fire on real Bagrut corpus? If > 5% of
  long sentences, that's a calibration signal — extend the
  lexicon, lower the threshold, or accept the gap. Owner: F53
  T-06 measurement.
- **Q-02 (BT-226)**: Should F15 acronym expansion happen BEFORE
  or AFTER the chunker counts tokens? Currently F15 is upstream
  (per ADR-030). The chunker sees the post-expansion token
  count, which is the right measure for audio length. Confirmed
  invariant; documented here so future readers don't re-litigate.
- **Q-03**: Should the chunker return three-fragment splits
  (e.g., split at TWO safe boundaries)? Phase 0 emits at most
  one split per block (greedy first-boundary). If a 50-word
  sentence has 3 commas, only the first is used. Real corpus
  may demand multi-split; defer until measured.
