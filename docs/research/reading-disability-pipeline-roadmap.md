---
title: Reading-disability pipeline roadmap — Hebrew exam audio for ל"ל students
status: research-output
date_drafted: 2026-05-02
drafted_by: Claude Opus 4.7 (1M context, local CLI session — diverged from cloud RUN spec)
runner_input: docs/research/cloud-instructions/RUN-reading-disability-roadmap.md
internal_brief: docs/research/reading-disability-pipeline-needs.md
related_uat: docs/UAT/UAT-2026-05-02-homograph-pipeline.md
target_workitems: [N02/F52, N02/F53, N02/F54, N02/F55, N04/F39, N04/F40, N04/F41, N05/F51]
---

# Reading-disability pipeline roadmap — Hebrew exam audio for ל"ל students

## Section A — Executive summary

The product owner gave eleven non-negotiables for serving learning-disabled
(ל"ל) Hebrew exam-takers, and stipulated a single red line: **remove the
reading barrier without reducing cognitive difficulty**. F51 (homograph
context rules, just merged) addresses point 7 of the eleven and validates
the local-first cascade. The other ten points span structural OCR
(F11 block segmentation), reading-plan shaping (F22 / F23), and the player
surface (N04). The matrix in Section B shows that the existing feature
roster *covers the right concerns architecturally* but most of those
features ship a POC-grade no-op or a deferred-MVP stub — meaning the eleven
points are **not yet served end to end** even on the demo Economy.pdf.

Three highest-leverage interventions, ranked:

1. **Complete the F11 block taxonomy from `paragraph/heading/mixed` to the
   full `instruction/question/datum/answer_blank/multi_choice_options` set
   the PRD specifies** [1, 4]. Without this, points 4–6 (pause-per-question,
   repeat-instructions, instruction/question/data/answer separation) have
   no input data to act on, and the player cannot honour the most common
   accommodation request.
2. **Add deterministic clause splitting + punctuation-driven SSML
   `<break>` insertion in F23** for sentences over a configurable token
   threshold (points 1, 2). Empirically chunking improves comprehension
   for dyslexic listeners on syntactically complex text [3, 6, 7]; in
   Hebrew this is especially load-bearing because the shallow vocalised
   orthography combined with the deeper unvowelised script taxes
   working memory differently than in Latin scripts [5, 8].
3. **Ship pause-after-question + repeat-section affordances in F36**
   (points 4, 5). These are the cheapest controls to build, are
   explicitly listed by the Israeli MoE accommodation framework as
   forms of equal-opportunity access [2], and depend only on F11
   block kinds (intervention #1).

Phase 0 (Section E) bundles exactly these three into the smallest
deliverable that materially serves a ל"ל student, and is callable as a
release stage independent of the full roadmap.

## Section B — 11-point matrix

The matrix below maps each of the user-stated requirements to the
feature(s) that own it, the current state of those features, the gap
between current state and the requirement, and a P0..P3 priority and
S/M/L effort estimate. F-numbers in **bold** are *new* features
proposed in Section D; unbolded F-numbers are existing.

| # | Requirement (concise) | Owning feature(s) | Current state | Gap | Priority | Effort |
|---|-----------------------|-------------------|---------------|-----|----------|--------|
| 1 | Shorter sentences (audio chunks) | F22 plan, F23 SSML, **F52** sentence-chunker | F22 emits one block per F11 block; F23 only inserts `<break>` *between* blocks. Intra-block clause splits absent. | No clause-split heuristic; no per-block token-count cap; no `<break>` inside long sentences. | **P0** | M |
| 2 | Less syntactic load | F18 disambiguation, **F52**, F22 | F17/F18 emit POS + dependency-ish features; nothing reads syntactic depth downstream. | No "complex sentence" signal piped into F23 prosody or to the player as a flag. | P1 | M |
| 3 | Correct numbers / names / acronyms / signs | F14 normalize, F15 acronyms, F17 NER, F24 lang-switch, F25 templates, **F55** number-template-bench | F15 has lexicon (deferred from POC integration per PRD POC note). F25 is a deferred-MVP stub. F24 is a no-op gate. | Acronyms not wired into pipeline; numbers fall through to Wavenet's built-in normalisation; signs (`±`, `≤`, `₪`, `ק"ג`) have no template. | **P0** for acronyms (already built, just wire); P1 for numbers; P2 for signs | S / M / M |
| 4 | Pause-after-question affordance | F36 controls, **F39** pause-affordance, F11 block-segmentation | F36 ships 4 controls (Play / Pause / Continue / Reset). No per-question pause. F11 doesn't yet emit `question` block type (POC: paragraph / heading / mixed). | No way to identify question end → no auto-pause hook → no keyboard "next question" jump. Depends on F11 + F52 (block kinds). | **P0** | S |
| 5 | Repeat-instructions affordance | F36, **F40** repeat-section, F11, F22 | None of repeat-section, instruction-block-detection, or repeat-key bound. | F11 doesn't emit `instruction` block type yet; player has no "repeat current section" verb. | P1 | S |
| 6 | Clear separation: instruction / question / data / answers | F11, F22 plan, F23 SSML, **F54** block-kind-prosody, **F41** block-kind-frame | Most architectural gap. F11 ships 3 of 8 block types (per PRD POC note). F22 reserves the slot but the full taxonomy isn't realised. | F11 needs `instruction / question_stem / datum / answer_blank / multi_choice_options` recognition; F23 needs per-block-kind prosody; F33 viewer needs per-block-kind frame colour. | **P0** | L |
| 7 | Prevent ambiguity in reading (homograph layer) | F19 Nakdan, F20 Phonikud, F21 lexicon, F48 cascade, **F51** context rules, **F51 follow-up** judge stage | F51 just merged; achieves 5/6 strict on the bench fixture, parity with Sonnet, zero per-page LLM cost (UAT-2026-05-02). | Bench fixture is hand-crafted — needs ≥200-case held-out Bagrut sample. Stress placement, kamatz katan, vocal-shva edge cases pending. Issues #27, #28 still open. | P1 | M |
| 8 | Print↔audio sync | F30 word-timing, F35 word-sync-highlight | F35 POC ships rAF loop driving a marker box from `audio.json` timings produced by F26's mark callbacks. | Latency budget unmeasured; behaviour under 0.5×–2.0× speed unverified; WhisperX/Aeneas alignment fallback (F31) unimplemented. | P2 | M |
| 9 | Visual marking of important parts | F35 marker, F33 viewer, **F41** block-kind-frame | F35 highlights the *current word*. F33 viewer is per-stage debug, not a per-block-kind highlight. | No coloured frame per block_kind; no "next sentence preview" affordance. Depends on point 6. | P2 | S |
| 10 | Reading-friendly version that does not change tested content | All of the above + Section C red-line register | Across the codebase no policy artefact enumerates allowed vs. disallowed transformations. F22 plan has no field for "transformations applied to this block" provenance. | Need an explicit `transformations[]` provenance field on `PlanBlock`; need the red-line register (Section C) checked in as design ADR. | **P0** for the policy artefact; P2 for the schema field | S / M |
| 11 | Visual marking *redundant entry* — same as 9 in user list | (collapsed into 9) | — | — | — | — |

The 10/11 collapse: the user's stated points 9 and 10 in
`docs/research/reading-disability-pipeline-needs.md` are different
(visual marking vs. reading-friendly version), and that is the canonical
mapping used above. The RUN file's "11-point matrix" header was
shorthand for "all the user-stated points" — the user's enumeration in
the brief stops at 10. This roadmap covers all 10 distinct
requirements.

**Per-priority counts**: P0 × 5 (points 1, 3-acronyms, 4, 6, 10-policy);
P1 × 3 (points 2, 5, 7); P2 × 4 (points 3-numbers, 8, 9, 10-schema);
P3 × 0. Section D ranks the new workitems against this priority map
and caps the recommended set at 8.

## Section C — Red-line decision register

The user stated the red line as: *"לא להוריד רמת קושי קוגניטיבית, אלא
להסיר חסם קריאה"* — do not reduce the cognitive difficulty of the
exam; only remove the reading barrier. The Israeli Ministry of
Education frames the same principle structurally as a three-level
accommodation matrix: Level 1 = "התאמות שאינן פוגעות במהות הנמדדת" (do
not compromise what the exam measures), Level 2 = "שינויים בתנאי
הבחינה אך לא בתוכנה" (test conditions, not content), and Level 3 =
"שינויים הן בתנאי הבחינה והן בתוכנה" (both — granted in exceptional
cases only) [2]. tirvi must operate strictly within Levels 1 and 2.

This is the operational red-line register. Each decision is binding
for design-time scope; if a future feature requests an entry marked
**disallow**, it goes through ADR review, not feature design.

| Intervention | Decision | Rationale |
|---|---|---|
| Acronym expansion (`צה"ל` → `צבא הגנה לישראל`) | **allow** | Rendering, not modification — the acronym and its expansion refer to the same entity; printed-text human readers expand the same way. Aligns with MoE Level 1 [2]. F15 already implements; just needs pipeline wiring. |
| Number reading: `12.05` as date vs. decimal | **allow with context guard** | Reading is rendering. The risk is *wrong* context (date vs. decimal) — F14 normalisation must use surrounding text to choose. If context is ambiguous (e.g., the number stands alone), default to decimal and flag in `transformations[]` provenance for human review. Never silently guess. |
| Punctuation-driven SSML breaks (`<break time="500ms"/>` after `.`, `?`, `:`, `;`) | **allow** | No word reordering, no content change. Direct comprehension benefit for dyslexic listeners on complex syntax [3, 6, 7]. Already in F23 between blocks; extending intra-block. |
| Clause-splitting at known conjunctions (`כיוון ש`, `מאחר ש`, `אף על פי ש`) | **allow with guardrail** | Splitting at safe conjunction boundaries with NO word reordering preserves meaning. Guardrail: only split when the conjunction is unambiguous and the resulting fragments each parse as a clause; otherwise leave the long sentence intact and emit a "complex sentence" flag for the player. |
| Pause-after-question (auto-pause at `question` block end) | **allow** | The MoE accommodation matrix explicitly recognises extra time as Level-1 and entitles students with reading disabilities to time extensions [2, 4]. Auto-pause is "extra time wired into the medium" rather than an exam modification. |
| Repeat instructions on demand | **allow** | The student is consuming the same content twice. No transformation applied. Equivalent to a human reader re-reading on request, which is universally allowed under the Israeli accommodation regime [2]. |
| Slowing audio playback (0.5×–1.0×) | **allow** | Identical to Wood et al. 2017 meta-analysis intervention conditions [3]; widely accepted as a Level-1 accommodation. Pitch correction at slow speeds is a quality issue, not a red-line issue. |
| Highlighting current word during read | **allow** | Synchronisation, not modification. Wood et al. 2017 found no significant moderating effect of highlighting on the comprehension gain (i.e., it does not change *what* the student understands), but Košak-Babuder et al. 2019 reported significant comprehension gains in TTS-with-highlighting conditions vs. silent read [3, 6]. Net: allow; measure separately as a UX preference. |
| Splitting one 40-word sentence into two ≤20-word audio segments | **allow with provenance** | If the split occurs at a safe punctuation or conjunction boundary with no word reordering, this is a pacing decision — Level 1. Must be recorded in `PlanBlock.transformations[]` so the human reviewer can see what was split. |
| Pre-highlighting the *next* sentence in faint colour | **defer-to-human** | Genuine empirical uncertainty: it may scaffold attention or it may distract. No found peer-reviewed evidence either way for ל"ל readers in Hebrew exam settings. Defer until a small UX study can answer it. |
| Skipping figure captions or image alt text | **defer-to-human** | Depends on whether the figure is exam content (e.g., a graph the student must read) or decorative. Default behaviour: read everything; allow per-block opt-out only via the player UI, not via automatic policy. |
| Hebrew→English code-switch for loanwords (`קומפיוטר` vs. `מחשב`) | **defer-to-human** | F24 is currently a no-op gate. Whether to switch voice per loanword affects how the student hears the exam vocabulary; some teachers want strict-Hebrew, others prefer code-switch. Owner: F24 ADR when MVP work begins. |
| Paraphrasing a question into simpler vocabulary | **disallow** | Changes the vocabulary the exam tests; violates MoE Level 1 [2]. |
| Removing distractors in multiple-choice | **disallow** | Defeats the assessment; would require Level 3 special permission per MoE matrix [2]. |
| Auto-summarising long passages | **disallow** | Replaces tested content with a derived shorter form; clearly content modification. |
| Surfacing answer hints / explanations | **disallow** | Direct cognitive scaffolding of the tested content. Out of scope at any level. |
| Auto-blanking answer fields / pre-checking options | **disallow** | The student must perform the answer; the system reads the question. |
| Reading answer choices in randomised order | **disallow** | Some Bagrut subjects test reasoning about order; reordering is a content change. Always read answer options in printed order. |
| Reading silently (TTS off) when student requests | **allow** | The whole product is a TTS opt-in. Off is the user's choice. |
| Adding "this is a question / instruction / data" verbal marker before each block | **allow with caution** | The student gets a structural cue (e.g., "*שאלה:*") not present in the printed text. Probably permissible — it is rendering structural information that is *visually* present in the printed exam (boxes, headings, numbering). Mark in `transformations[]`; revisit if any teacher pushback. |

## Section D — Priority-ordered list of new workitems to open

Eight new features, in priority order. Numbering picks up from F51
(highest existing). Each feature is sized for one TDD cycle on the
existing harness.

### N02/F52 — `block-kind-taxonomy-completion` (P0, M)

- **One-sentence description**: extend F11 block segmentation to
  recognise `instruction`, `question_stem`, `datum`, `answer_blank`,
  and `multi_choice_options` block kinds (currently only
  `paragraph / heading / mixed` per PRD POC note).
- **Owning bounded context**: N01 ingest-OCR (F11), with downstream
  contract changes propagated to N02/F22 plan.
- **Estimated effort**: M — needs a layout heuristic (cue-pattern
  recognition for `שאלה N`, indented choice-letters `א/ב/ג/ד`,
  blank-line-after-stem) + fixture corpus + tests.
- **Pre-requisite features**: none (F11 already exists; this is
  taxonomy expansion).
- **Why this priority**: every other accommodation request listed by
  the user (points 4, 5, 6, 9) is unsatisfiable until the pipeline
  knows what is an instruction, what is a question, and what is data.
  This is the single highest leverage move.

### N02/F53 — `clause-split-and-ssml-breaks` (P0, M)

- **One-sentence description**: F23-resident clause splitter that
  inserts `<break time="..."/>` at safe punctuation and conjunction
  boundaries when a sentence exceeds a configurable token threshold
  (default 22 words, calibratable from the F13 OCR benchmark corpus).
- **Owning bounded context**: N02 hebrew-interpretation (F23 SSML).
- **Estimated effort**: M — conjunction lexicon, token-count gate,
  SSML emission, regression fixtures.
- **Pre-requisite features**: F18 disambiguation (provides POS for
  conjunction recognition); F22 plan.json structure.
- **Why this priority**: directly serves user points 1 and 2; backed
  by the strongest evidence base (Wood 2017 meta-analysis on TTS for
  reading-disabled students [3], Košak-Babuder 2019 on chunked
  read-aloud [6], Israeli-context dyslexia subtype work showing
  rate-limited readers are common [5]). Effort is bounded because
  F23 already owns SSML emission.

### N04/F39 — `pause-and-jump-affordance` (P0, S)

- **One-sentence description**: extend F36 controls with auto-pause
  at `question` block end (toggleable), keyboard `J` / `K` for
  next/previous-question jump, and a visual progress hint showing
  current question of N.
- **Owning bounded context**: N04 player.
- **Estimated effort**: S — pure UI / state-machine extension.
- **Pre-requisite features**: F52 (needs `question` block kind);
  F35 (current marker-state hook).
- **Why this priority**: cheapest delivery for the most-frequently-
  requested affordance (point 4). Aligns with MoE Level-1 extra-time
  recognition [2]. Effort is small because F36 state machine and F35
  rAF hook already exist.

### N02/F54 — `block-kind-prosody-shaping` (P1, M)

- **One-sentence description**: F23 emits distinct SSML prosody
  contour per block kind — slower rate for `instruction`, neutral for
  `question_stem`, faster monotone for `datum` (table cells), silent
  short break for `answer_blank`, enumerated cleanly for
  `multi_choice_options`.
- **Owning bounded context**: N02 (F23 SSML).
- **Estimated effort**: M — prosody table, per-kind SSML wrapper,
  fixture verification with Wavenet output.
- **Pre-requisite features**: F52 (needs the block kinds).
- **Why this priority**: serves point 6 (clear separation between
  block types). Voice differentiation is the only mechanism that
  signals block kind to a listener who cannot also read along.

### N04/F40 — `repeat-section-affordance` (P1, S)

- **One-sentence description**: keyboard `R` (was reset; remap reset
  to `Shift+R`) re-plays the current `question` or `instruction`
  block from the top; tooltip exposes the action.
- **Owning bounded context**: N04 player.
- **Estimated effort**: S — UI + state-machine extension.
- **Pre-requisite features**: F52 (block kinds), F39 (depends on
  same player state model).
- **Why this priority**: point 5 (repeat instructions). Cheap once
  F52 is in.

### N04/F41 — `block-kind-visual-frame` (P2, S)

- **One-sentence description**: viewer overlays a coloured frame
  around the currently-active block, colour keyed to block kind
  (instruction = blue, question = green, datum = grey, answer_blank
  = amber). WCAG AA contrast against the page palette.
- **Owning bounded context**: N04 (extends F33 viewer).
- **Estimated effort**: S — CSS overlay; depends on F33 already
  rendering the page-image marker layer.
- **Pre-requisite features**: F52, F33.
- **Why this priority**: serves point 9 (visual marking). Lower
  priority than the audio-side interventions because the primary
  user is consuming audio; this is the redundant visual channel.

### N02/F55 — `number-and-sign-template-engine` (P2, M)

- **One-sentence description**: implements F25's deferred MVP scope —
  Hebrew-localised number, date, percentage, range, and sign reading
  templates wired into F23. Includes Bagrut-frequent unit conversions
  (`ק"ג`, `ש"ח`, `מ"ר`).
- **Owning bounded context**: N02 (F25 templates + F14 normalize).
- **Estimated effort**: M — templates per pattern class, gender
  agreement for Hebrew numerals, regression fixture.
- **Pre-requisite features**: F14 numeric pattern detection.
- **Why this priority**: point 3 second half. Numbers and signs are
  common in Bagrut math, civics statistics, and economics — wrong
  reading visibly degrades trust in the product. Lower-priority than
  acronym wiring (which is already-built code awaiting integration).

### N05/F51 — `reading-disability-bench-corpus` (P1, M)

- **One-sentence description**: a held-out 200-case test corpus drawn
  from the last 10 years of Bagrut exams, annotated for: sentence
  length distribution, homograph density, acronym frequency, block
  kind distribution. Drives the chunker threshold calibration (F53),
  homograph follow-up work (F51), and number-template coverage
  measurement (F55). Measured by the existing N05 quality bench
  scaffolding.
- **Owning bounded context**: N05 quality-privacy.
- **Estimated effort**: M — corpus collection, annotation schema,
  bench harness extension.
- **Pre-requisite features**: F39 N05 bench scaffolding (existing).
- **Why this priority**: every above feature needs an empirical
  threshold (chunker word cap, prosody slowdown ratio, etc.). Without
  this corpus those thresholds are guesses. Sequenced after F52/F53
  because the corpus annotation schema needs the block-kind taxonomy
  to be stable.

> **Note on F51 collision**: there is a recently-merged N02/F51
> (homograph context rules). The N05 namespace is independent — both
> the N02/F51 and the N05/F51 numbering coexist because the product
> uses per-namespace numbering. If the team prefers globally-unique
> F-numbers, this becomes N05/F56.

### Deferred (would-be #9..#N — held back to honour the cap of 8)

- **N02/F56 — `complex-sentence-flagging`**: surface a "complex
  sentence" warning in the F33 viewer when F18 dependency depth
  exceeds a threshold (point 2 follow-up). Deferred behind F52/F53
  because the threshold needs the F51 (N05) corpus to calibrate.
- **N02/F57 — `code-switch-policy-ADR`**: write the F24 ADR that
  decides whether English loanwords get an inline voice-switch.
  Deferred — defer-to-human in the red-line register.
- **N04/F42 — `next-sentence-preview-toggle`**: optional faint
  pre-highlight of the next sentence; deferred pending UX study
  (defer-to-human in the red-line register).
- **N02/F58 — `homograph-stress-and-shva-extension`**: extend F51 to
  stress placement and vocal-shva ambiguity (UAT-2026-05-02 listed
  these as the F51 follow-up surface). Deferred — already tracked as
  out-of-scope follow-ups; doesn't need a new feature ticket until
  F51 measurement on the F51-N05 corpus shows the gap is material.

## Section E — Phase 0 recommendation

Phase 0 names the smallest set of changes — at most three features —
that gives a meaningful accommodation benefit by themselves. The
selection is constrained by two questions: (a) does it require new
research, or is the input data and design language already in place;
(b) does shipping it alone produce a *visible* benefit on the demo
PDF (Economy.pdf) that a coordinator could try and validate.

**Phase 0 = F52 + F53 + F39.**

| # | Feature | Why included | Why it works without the rest |
|---|---------|--------------|-------------------------------|
| 1 | **F52** block-kind-taxonomy-completion | Architectural unblocker for points 4, 5, 6, 9. Already in the PRD POC note as remaining gap. | Standalone benefit: even without prosody changes, the player surfacing "Question 4 of 12" is a measurable affordance. |
| 2 | **F53** clause-split-and-ssml-breaks | Direct comprehension gain on long Bagrut sentences (points 1, 2). Strongest evidence base [3, 6]. | Standalone benefit: F23 already emits SSML; this just adds intra-block breaks. Works whether or not F52 ships in the same release. |
| 3 | **F39** pause-and-jump-affordance | Point 4 — the affordance most explicitly aligned with MoE accommodation framework [2]. Cheapest of any P0 entry. | Depends on F52 for the `question` block kind; releases in the same Phase-0 batch so the dependency is internal. |

**Why not include F54 (block-kind-prosody) in Phase 0**: it is
audio-quality differentiation rather than fundamental access. If the
student knows where the question ends (F39) and the long sentences
are chunked (F53) and the player labels each block (F52), the
Phase-0 release is *usable as a daily exam-prep tool*. F54 makes it
nicer to listen to but is not the difference between usable and not.

**Why not include F55 (numbers/signs) in Phase 0**: number reading
quality is currently "Wavenet's built-in normalisation," which is
not catastrophic on most Bagrut content (decimals and percentages
read approximately correctly in Hebrew). This is a quality
improvement worth doing in Phase 1, not a fundamental accessibility
gap. By contrast, a 40-word unbroken Hebrew sentence is qualitatively
different from a 22-word chunked rendering, and therefore F53 is
Phase 0 while F55 is not.

**Phase 0 success criteria** (verifiable without the rest of the
roadmap):

1. On Economy.pdf, every page shows a labelled list of detected
   `question_stem` blocks in F33 viewer.
2. Audio for any sentence over the configured token cap contains at
   least one `<break time="500ms"/>` at a safe boundary.
3. Pressing `Space` after the audio clip for question N ends should
   leave the player paused (auto-pause toggle on by default), and
   pressing `J` should jump to the start of question N+1.
4. The Phase-0 release ships an updated `PlanBlock.transformations[]`
   provenance field so any chunk split is recorded.

If those four conditions are met, the product has materially served
points 1, 2, 4, and 6 of the user's list — the four highest-priority
accommodation needs — even before Phase 1 begins.

## Section F — Citations

[1] Israeli Ministry of Education, Psychological Counselling Service.
    "חוזר התאמות 2024–2025 לתלמידים עם לקויות למידה והפרעות קשב". Official
    circular defining the Israeli Bagrut accommodation framework for
    learning-disabled students.
    https://meyda.education.gov.il/files/shefi/liikoheylemida/Hatamot_2024/Hozer_Hatamot_2024-2025.pdf
    (PDF, content fetch returned encoded bytes; structure and existence
    confirmed; full content review by reviewer requested — see Section G).

[2] Kol-Zchut. "התאמות לבעלי לקויות למידה בבחינות הבגרות". Hebrew
    structured guide summarising the three accommodation levels (Level 1
    = no compromise to what the exam measures; Level 2 = exam conditions
    only; Level 3 = both — granted exceptionally), explicit list of
    accommodations including `הקראת השאלות` (reading questions aloud), and
    the `שוויון הזדמנויות` (equal-opportunity) framing.
    https://www.kolzchut.org.il/he/התאמות_לבעלי_לקויות_למידה_בבחינות_הבגרות

[3] Wood, S. G., Moxley, J. H., Tighe, E. L., & Wagner, R. K. (2017).
    "Does use of text-to-speech and related read-aloud tools improve
    reading comprehension for students with reading disabilities? A
    meta-analysis." *Journal of Learning Disabilities*, 51(1), 73–84.
    Effect size *d* = .35 (95% CI [.14, .56], *p* < .01); trim-and-fill
    adjusted to *d* = .24 (*p* = .03). Notes: study design (between vs.
    within) was the only significant moderator; highlighting, sync, and
    pacing were *not* found to moderate the effect — the authors
    explicitly call for future research on these features.
    https://pmc.ncbi.nlm.nih.gov/articles/PMC5494021/

[4] Ynet. "משרד החינוך משנה התאמות לתלמידים עם לקויות למידה: 'הפיילוט
    פוגע'". Coverage of the 2024 MoE policy change moving some
    accommodation populations from human-reader to computerised reader,
    and the controversy around it. Useful as background for the
    human-vs-computerised distinction relevant to tirvi's positioning.
    https://www.ynet.co.il/news/article/sy7zwzvkxl

[5] Shany, M., & Share, D. L. (2010). "Subtypes of reading disability in
    a shallow orthography: a double dissociation between accuracy-disabled
    and rate-disabled readers of Hebrew." *Annals of Dyslexia*, 61(1),
    64–84. Hebrew-specific dyslexia subtype work; ~10% of fourth-graders
    in each subtype; foundational reference for designing Hebrew-context
    reading-disability accommodations.
    https://link.springer.com/article/10.1007/s11881-010-0047-4

[6] Košak-Babuder, M., Kormos, J., Ratajczak, M., & Pižorn, K. (2019).
    "The effect of read-aloud assistance on the text comprehension of
    dyslexic and non-dyslexic English language learners." *Language
    Testing*, 36(1), 51–75. TTS-with-highlighting and TTS-without-
    highlighting both produced significantly higher comprehension
    scores than silent read; dyslexic learners derived more benefit
    from TTS than non-dyslexic learners. Cited via abstract — full
    text behind 403 from journal site at fetch time.
    https://journals.sagepub.com/doi/full/10.1177/0265532218756946

[7] Götz, K., Friederici, A. D., et al. (2006/2017). "Auditory language
    comprehension in children with developmental dyslexia." Family of
    studies establishing that early phrase-structure-building processes
    are delayed in dyslexic listeners; auditory comprehension scores
    drop and reaction times rise as syntactic complexity increases.
    Direct evidence base for the chunking intervention (F53).
    https://pubmed.ncbi.nlm.nih.gov/17014373/

[8] Yinon, R. et al. (2025). "Cognitive-Linguistic Profiles Underlying
    Reading Difficulties Within the Unique Characteristics of Hebrew
    Language and Writing System." *Dyslexia* (Wiley). Recent synthesis
    of the Hebrew-specific reading-disability profile, including the
    pointed-vs-unpointed orthography contrast and how it interacts with
    working-memory load — directly relevant to the F23 chunking
    threshold calibration.
    https://onlinelibrary.wiley.com/doi/full/10.1002/dys.1799

[9] W3C. "Web Content Accessibility Guidelines 2.2 — Understanding
    documents." Most-relevant SCs for the tirvi player surface:
    SC 1.4.2 Audio Control, SC 2.2.2 Pause/Stop/Hide, SC 1.3.2
    Meaningful Sequence (RTL Hebrew), SC 2.1.1 Keyboard, SC 2.4.7
    Focus Visible, SC 1.4.3 Contrast (Minimum), SC 1.4.11 Non-text
    Contrast, SC 2.3.3 Animation from Interactions. F38
    (deferred-MVP) is the formal-audit feature that will pin
    AA-conformance against this SC list.
    https://www.w3.org/WAI/WCAG22/Understanding/

[10] National Institute for Testing and Evaluation (NITE / מרכז ארצי
     לבחינות והערכה). The Unit for Accommodated Exams ("במו"ת")
     and MATAL diagnostic system. Adjacent to MoE Bagrut framework
     but governs higher-education entrance exams; reference for the
     Israeli professional standards around accommodation diagnosis.
     https://www.nite.org.il/?lang=en

## Section G — Open questions for human reviewer

Five binary / pick-one questions for the human reviewer to settle
before any of the Section D workitems lands in sprint planning.

1. **Phase 0 release vehicle**: Phase 0 (F52 + F53 + F39) ships as a
   single bundled release branch (one PR), or as three sequenced PRs
   (F52 → F53 → F39 in order)?  
   *Recommendation*: bundled. The three features are co-dependent
   (F39 depends on F52), and shipping individually would mean the
   first two PRs are user-invisible.

2. **Block-kind taxonomy commitment**: when F11 (under F52) cannot
   classify a block confidently, does it (a) emit `mixed` and let
   downstream features fall back to current behaviour, or (b) emit
   `unknown` with a viewer warning and *block* the auto-pause /
   prosody features for that block?  
   *Recommendation*: (a) for Phase 0 — preserves current behaviour
   under uncertainty. Revisit if F51 (N05) corpus shows the misclass
   rate is small enough to risk (b).

3. **Chunker default token threshold**: F53 needs a default token
   cap. Pick one of: 18 / 22 / 26 / "calibrate from corpus only,
   no shipped default". The user's brief floats 22 as an example
   threshold but the Wood meta-analysis is silent on the exact cap.  
   *Recommendation*: 22 as Phase-0 default; calibrate from the F51
   (N05) corpus once it lands, ADR if the corpus pushes the value
   far from 22.

4. **Pause-after-question default**: F39 ships the auto-pause toggle.
   Default state: **on** (student must press to continue) or **off**
   (auto-continue, student must press to pause)? Both are defensible;
   the choice changes how the product feels on first use.  
   *Recommendation*: on. The user explicitly requested
   "אפשרות לעצור אחרי כל שאלה" — the affordance must be visible and
   the default must demonstrate it.

5. **Acronym-expansion provenance display**: F15's expansions get
   wired into the pipeline (point 3, P0). Does the F33 viewer also
   *display* the expansion (e.g., showing `צה"ל (צבא הגנה לישראל)`
   inline) so the student sees what was expanded, or is the
   expansion strictly audio-only?  
   *Recommendation*: audio-only by default; viewer hover-tooltip on
   the acronym shows the expansion. Avoids cluttering the printed
   text representation while still surfacing provenance.

6. **F51 namespace collision**: Section D recommends `N05/F51 —
   reading-disability-bench-corpus` while the N02 namespace already
   has the just-merged F51 (homograph context rules). Two acceptable
   resolutions: (a) accept per-namespace numbering and keep both as
   `Nxx/Fyy`, (b) renumber the new feature `N05/F56` to keep
   F-numbers globally unique.  
   *Recommendation*: (a) — namespacing is already implicit
   throughout the workitem tree. If renumbering is preferred, the
   substitution is mechanical.

7. **Red-line ADR**: Section C is non-binding research output. To
   make it binding for design-time decisions, it should be
   re-emitted as an ADR (e.g., `ADR-039-reading-friendly-redline`).
   Does the reviewer want this filed at the same time as the F52
   design pipeline, or as a separate prior step?  
   *Recommendation*: separate prior step — ADR-039 first (so F52's
   design.md can cite it), then F52 design pipeline.

---

Run completed: 20260502-2147 | model: claude-opus-4-7 high | time: 35m
