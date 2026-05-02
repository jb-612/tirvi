---
title: Research brief — pipeline requirements for Hebrew exam reading with reading disabilities
status: brief
intended_runner: cloud session (claude.ai/code), Opus 4.7 high effort, deep-research skill
parallel_to: F51 implementation (this is independent and can run concurrently)
date_drafted: 2026-05-02
drafted_by: Claude Opus 4.7 (1M context, local CLI)
related_uat: docs/UAT/UAT-2026-05-02-homograph-pipeline.md
---

# Reading-disability requirements for the tirvi pipeline — research brief

This is a **paste-ready brief** for a cloud research session. The
homograph work in F51 only addresses point 7 of the user's framing
("prevent ambiguity in reading"). This brief scopes points 1-11 as a
research project across the pipeline, not just the NLP layer.

## Background — user-stated requirements

The product is a webapp that reads Hebrew exam PDFs aloud for students
with reading accommodations (per `docs/PRD.md`, `docs/HLD.md`). Its
defensible layer is OCR → Hebrew linguistic interpretation → reading
plan → TTS, not naive OCR + TTS.

The user (a domain expert in this audience) stated the following
non-negotiables for reading-disabled students. Each is a *barrier* to
exam access; the product must remove the barrier without changing the
exam's cognitive content (the **red line**).

> מה חשוב במיוחד ללקויי למידה
> כאן צריך להיזהר. לא מספיק להקריא את אותו טקסט.
> צריך לייצר גרסת בחינה שמיעתית תקינה, כלומר:

1. משפטים קצרים יותר — *shorter sentences*
2. פחות מבנים תחביריים עמוסים — *less syntactic load*
3. קריאה נכונה של מספרים, שמות, ראשי תיבות וסימנים — *correct reading
   of numbers, names, acronyms, signs*
4. אפשרות לעצור אחרי כל שאלה — *pause-per-question affordance*
5. חזרה על הוראות — *repeat-instructions affordance*
6. חלוקה ברורה בין הוראה, שאלה, נתונים ותשובות — *clear separation
   between instruction / question / data / answers*
7. מניעת דו־משמעות בהקראה — *prevent ambiguity in reading* (the
   homograph layer; partially addressed by F51)
8. סנכרון בין טקסט מודפס לשמע — *print↔audio sync*
9. סימון חזותי של חלקים חשובים — *visual marking of important parts*
10. גרסה "ידידותית להקראה" שאינה משנה את התוכן הנבחן — *"reading-
    friendly version" that does not change tested content*

> הקו האדום הוא לא לפשט את הבחינה באופן שפוגע בתקפות הפדגוגית. כלומר,
> לא להוריד רמת קושי קוגניטיבית, אלא להסיר חסם קריאה.

**Red line**: do not reduce cognitive difficulty; only remove the
reading barrier. This rules out: paraphrasing the question, simplifying
vocabulary, removing distractors, dropping content.

## Research goals

For each of the 11 points, the research session should produce:

1. **Pipeline mapping** — which existing or planned tirvi feature(s)
   in the workitem map (`.workitems/N00..N05/*`) own this concern. If
   no feature owns it, name the gap.
2. **Acceptance criteria** — what does "good" look like in measurable
   terms? Examples: ≤ 22 words per audio chunk; pause minimum 800 ms
   between question N and question N+1; acronym expansion latency
   ≤ 200 ms; sync drift ≤ 100 ms across a 10-minute read.
3. **Existing literature / standards** — Israeli Ministry of Education
   accommodation guidelines (התאמות בבחינות בגרות), academic literature
   on dyslexia/dysgraphia text-to-speech aids (van der Bom 2018;
   Wood 2018; Eshet-Alkalai), WCAG 2.2 SC 1.4.x relevant to TTS,
   Israeli ADHD/learning-disability NGO recommendations (NITE/מרכז
   ארצי לבחינות והערכה accommodation matrices).
4. **Existing tirvi adapters that need extension** — e.g., F23 SSML
   shaping must emit `<break time="800ms"/>` between question blocks
   for point 4; F22 plan.json must expose block_kind ∈
   {instruction, question, datum, answer_blank} for point 6.
5. **Things explicitly OUT of scope by the red line** — e.g., text
   simplification, distractor removal, question paraphrase. The
   research must enumerate "tempting but disallowed" interventions to
   prevent scope creep at design time.
6. **Recommended next workitems** — concrete F-numbered features to
   add to N02 / N03 / N04, in priority order.

## Per-point research questions

### Point 1 — shorter sentences

- How short is "shorter"? Is there an empirical threshold for
  reading-disabled audio comprehension (e.g., < 15 words / sentence
  triggers a chunking heuristic)?
- Hebrew exam corpus reality check: average sentence length in Bagrut
  history / civics / literature exams. Use `data/Economy.pdf` and any
  other in-tree exam fixtures as a base rate.
- Mechanism options: (a) automatic clause splitting at known
  conjunctions (`כיוון ש`, `מאחר ש`, `אף על פי ש`, `במידה ו`); (b)
  punctuation-driven SSML breaks; (c) human-edit pass on the reading
  plan output. Hybrid is likely.
- **Risk to red line**: clause splitting that changes the meaning is
  red-line violation. Punctuation-driven breaks are safe; clause
  rewriting is not.

### Point 2 — less syntactic load

- Hebrew-specific syntactic-load markers: nested possessive chains,
  long object phrases, reduced relative clauses without `ש`.
- DictaBERT dependency parser (already in scope per F17) emits the
  syntactic tree; we have signal but no consumer for syntactic depth.
- Should depth > N trigger a "complex sentence" warning surfaced to
  the human reviewer (F50 portal), or an automatic chunking action,
  or both?

### Point 3 — numbers, names, acronyms, signs

- Numbers: `num2words` Hebrew is in F14 normalization; verify it
  handles dates, ranges, percentages, decimals correctly. Bagrut
  fractions and unit conversions are common.
- Names: proper nouns from DictaBERT NER (F17). What's the audio
  expectation — keep Hebrew pronunciation for Hebrew names, switch
  to English for Latin-script names? F24 lang-switch-policy is the
  consumer.
- Acronyms: F15 acronym lexicon already covers Otzar Roshei Tevot.
  Coverage gap analysis on Bagrut-frequent acronyms (e.g., `ת"א`
  Tel Aviv vs `תל"א` taliyah; `מד"א`; `צה"ל`).
- Signs: math (`±`, `≤`, `√`), currency (`₪`, `$`), units (`ק"ג`).
  F25 content-templates is the consumer.

### Point 4 — pause-per-question

- Accommodation guideline (NITE): students with reading disabilities
  are entitled to time extensions. The audio version should not
  *force* a continuous read; pause-on-demand is the floor, automatic
  pause-after-question is the ceiling.
- F23 SSML: emit `<break time="..."/>` after each question's last
  word AND `<mark name="question_end_<n>"/>` so the F35 player can
  optionally auto-pause.
- F36 accessibility-controls: keyboard shortcut (e.g., space bar) to
  pause, in addition to time-based pauses.

### Point 5 — repeat instructions

- Instruction text in Bagrut is often the first paragraph of each
  section. Player should expose "repeat instructions for current
  section" affordance.
- Requires F22 plan.json to tag `block_kind: instruction` distinctly
  from `block_kind: question` and `block_kind: data`.
- F18 disambiguation: the word `הוראות` itself is unambiguous, but
  detecting the *boundary* of an instruction block needs heuristics
  or layout cues from F11 block-segmentation.

### Point 6 — clear separation: instruction / question / data / answers

- The most architectural of the 11. Requires F22 plan.json to model:
  - `instruction` — set-up text the student must understand to answer
  - `question` — the prompt
  - `datum` — supporting text/table/image (the "data" in `נתונים`)
  - `answer_blank` — the empty space the student fills in
  - `multi_choice_options` — for closed questions
- Audio mechanism: distinct prosody contour per block_kind (slower
  for instruction, neutral for question, faster monotone for datum,
  silent for answer_blank, enumerated cleanly for multi_choice).
- Visual mechanism: F33 viewer highlights the current block_kind
  with a coloured frame (instruction = blue, question = green,
  datum = grey, etc.).

### Point 7 — prevent ambiguity in reading (HOMOGRAPH LAYER)

- Already partially addressed by **F51** (this branch).
- Open follow-ups: GitHub issues #27 (dormant DictaBERT integration)
  and #28 (ambiguity flagging in corrections.json).
- Larger gaps the research should enumerate: stress placement
  (`תַ֣עֲשׁוֹת` vs `תַעֲשׂ֣וֹת`), kamatz katan disambiguation, vocal-shva
  vs nax-shva (handled by F20 Phonikud — verify coverage), and
  loanwords (`קומפיוטר` vs `מחשב`).
- Research target: build a 200-300 case held-out homograph test set
  drawn from real Bagrut exams over the last 10 years; measure F51
  cascade against it; identify the top 20 hardest cases for human
  curation in F21 lexicon.

### Point 8 — print↔audio sync

- F35 word-sync-highlight already in scope (N04). Latency budget
  needs measurement: word-highlight should advance ≤ 100 ms after the
  audio frame it represents.
- WhisperX or Aeneas alignment fallback (per F31) when MarkSet from
  Cloud TTS is unavailable.
- Reading-disabled students may slow / speed audio (F36
  accessibility-controls). Sync must hold under 0.5x and 2.0x speeds.

### Point 9 — visual marking

- Highlight the *current* word (yellow underline) AND the *current*
  block_kind frame.
- Optionally: pre-highlight the next sentence in faint colour so the
  student knows what's coming. Research whether this helps or distracts.
- Interaction with F38 WCAG conformance: contrast ratios must hold for
  highlight + base text combinations.

### Point 10 — reading-friendly version

- THE RED-LINE QUESTION. What changes count as "reading-friendly"
  versus "exam content modification"?
- Allowed: SSML breaks, prosody contour, pause-per-question, sync
  highlights, repeat-on-demand, speed control.
- Disallowed: paraphrase, vocabulary substitution, removing
  distractors, simplifying questions, hint surfacing, automatic
  answer-blanking.
- Edge cases for research:
  - Acronym expansion (F15) — is reading "צבא הגנה לישראל" instead of
    `צה"ל` an exam-content modification, or just rendering? (Probably
    just rendering — but a research call.)
  - Number reading — is reading `12.05` as "twelfth of May" instead
    of "twelve point oh five" a modification? (Depends on date vs
    decimal context — F14 normalization decides.)
  - Sentence chunking — is splitting a 40-word sentence into two
    20-word audio segments a modification? (Likely safe if no word
    re-ordering; needs explicit guideline.)

## Recommended deliverable shape

A document at `docs/research/reading-disability-pipeline-roadmap.md`
with:

1. The 11-point matrix (point → owning feature → gap → priority).
2. A red-line decision register (table of "tempting interventions"
   and explicit allow/disallow decisions with rationale).
3. A priority-ordered list of new workitems to open (likely under
   N02 for NLP/SSML changes and N04 for player changes).
4. Citations to Israeli Ministry of Education accommodation guidance
   and at least 3 peer-reviewed papers on dyslexia-aware TTS.
5. A "phase 0" recommendation — the smallest set of changes that
   provides material accommodation benefit, separate from the
   "phase 1 / phase 2" full roadmap.

## How to run this in a cloud session

1. Open `claude.ai/code` (web), pick Opus 4.7 (high effort), enable
   the `deep-research` skill.
2. Paste this brief verbatim as the first message.
3. Allow the session to run unattended; expected duration 30-90
   minutes for the research synthesis.
4. The session should land its output as a PR opening
   `docs/research/reading-disability-pipeline-roadmap.md` (per the
   memory `feedback_unattended_cloud_runs` — push to `claude/<run-id>`,
   not `werbeH`).
5. After landing, the human reviewer accepts or rejects the
   recommended workitems and the research is folded into the next
   sprint planning.

## Why this is parallelizable with F51 implementation

F51 (this branch) is local-CLI work touching `tirvi/homograph/`,
`tirvi/adapters/nakdan/`, `tirvi/correction/prompts/`. The research
above touches no production code — it is an analysis document. There
is no merge conflict surface, and the cloud session does not need
local environment state.
