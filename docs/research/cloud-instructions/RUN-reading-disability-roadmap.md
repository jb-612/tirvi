# RUN — Reading-disability pipeline roadmap (cloud session, unattended)

**This file IS your prompt.** Paste its contents into a fresh
`claude.ai/code` web session. Read every section before doing anything.
Do not skim.

---

## 0. Run context

You are running **unattended**. The human is offline and will not
respond to questions during this session. Your job is to deliver a
complete research artefact in one shot, then mark a PR ready for review
and stop.

- **Project**: tirvi — webapp that reads Hebrew exam PDFs aloud for
  students with reading accommodations. Defensible layer:
  OCR → Hebrew NLP → diacritization → reading plan → TTS. See
  `docs/PRD.md`, `docs/HLD.md`.
- **Model**: Opus 4.7, high reasoning effort.
- **Time budget**: 30–90 minutes wall-clock. Don't loiter.
- **Token budget**: aim for a deliverable in the 4-8k word range; cite
  sources concisely, don't pad.

## 1. Tools — allow / deny list

**Allowed**:
- `WebFetch`, `WebSearch` — primary research tools. Use them.
- `Read`, `Glob`, `Grep` — for repo context (workitems, ADRs, HLD).
- `Edit`, `Write` — to draft the deliverable in the repo.
- `Bash` — only for git operations and `gh pr` operations.
- `gh` (via Bash) — to open and update the PR.

**Forbidden**:
- `EnterPlanMode` / `ExitPlanMode` — HITL, will hang.
- `AskUserQuestion` — there is no human to ask.
- `TaskCreate` / `TaskList` / `TaskUpdate` — these block on user
  approval in some configurations; do not use.
- Any `Agent` invocation with an interactive subagent that may HITL.
- `agent-teams` / `TeamCreate` / `SendMessage` — known to hang in
  unattended runs.
- Any skill whose description contains the word "interactive",
  "approval", or "HITL".

If a tool you reach for is in the forbidden list, do the work without
it — write directly, not via a delegating agent.

## 2. Branch and PR policy

Per the project's documented unattended-run pattern (memory:
`feedback_unattended_cloud_runs`):

1. Branch off `main` to `claude/research-reading-disability-<run_id>`
   where `<run_id>` is `date +%Y%m%d-%H%M`.
2. **Never push to**: `main`, `werbeH`, `werbeH-design`, `meta/harness`,
   any `feat/*` branch, any other `claude/*` branch.
3. Open a single PR titled
   `research(N02): reading-disability pipeline roadmap` against `main`.
4. Mark the PR as **Draft** when opening. Convert to Ready-for-Review
   only when you've completed the deliverable and self-reviewed it.
5. Do not request reviewers; the human will review when they're back.
6. Do not delete the branch. The human decides.

## 3. The deliverable

A single new file: `docs/research/reading-disability-pipeline-roadmap.md`,
4-8k words, with these exact sections:

### Section A — Executive summary (1-2 paragraphs)

The 3 highest-leverage interventions with citation, as a hook for a
reviewer who only reads the first page.

### Section B — 11-point matrix

Reproduces the 11 user-stated requirements (see Section 6 below) and
maps each to:

| Point | Owning feature(s) | Current state | Gap | Priority (P0..P3) | Effort (S/M/L) |

If no current feature owns a point, name it explicitly as a gap. Use
existing F-numbers when applicable (F22 reading-plan-output, F23 SSML
shaping, F24 lang-switch-policy, F25 content-templates, N04/F33
side-by-side viewer, N04/F35 word-sync-highlight, N04/F36 accessibility-
controls, N04/F38 WCAG conformance, etc.) — explore `.workitems/`
before invoking.

### Section C — Red-line decision register

Table of "tempting interventions" mapped to **allow** / **disallow** /
**defer-to-human**, with one-line rationale. The user-stated red line:
*do not reduce cognitive difficulty; only remove the reading barrier*.

Examples to include (you may add more):
| Intervention | Decision | Rationale |
|---|---|---|
| Acronym expansion (read `צה"ל` as `צבא הגנה לישראל`) | ? | ? |
| Number reading (12.05 as decimal vs date) | ? | context-dependent |
| Splitting a 40-word sentence into two ≤20-word audio segments | ? | preserves order? |
| Pause-after-question | ? | clearly allowed |
| Paraphrasing a question into simpler vocabulary | ? | clearly disallowed |
| Removing distractors in multiple-choice | ? | disallowed |
| Repeating instructions on demand | ? | allowed |
| Slowing audio playback | ? | allowed |
| Auto-summarising long passages | ? | likely disallowed — content modification |

Don't dodge — make the call and justify it. If you genuinely can't
decide, mark `defer-to-human` and explain what evidence would settle it.

### Section D — Priority-ordered list of new workitems to open

Up to 8 entries, in priority order. Each entry:
- Proposed feature ID (e.g., `N02/F52`, `N04/F51`).
- One-sentence description.
- Owning bounded context.
- Estimated effort (S/M/L).
- Pre-requisite features.
- Why this priority.

Cap at 8 — pick the highest-leverage. If you have more than 8
candidates, list the surplus under a "deferred" sub-section.

### Section E — Phase 0 recommendation

The smallest set of changes (≤ 3 features) that gives material
accommodation benefit, callable as a Phase 0 deliverable separate from
the full roadmap. Justify why these 3.

### Section F — Citations

- Israeli Ministry of Education (משרד החינוך) accommodation guidelines
  for Bagrut exams. Look for: `התאמות בבחינות בגרות`, NITE/מרכז ארצי
  לבחינות והערכה accommodation matrices.
- ≥ 3 peer-reviewed papers on dyslexia-aware text-to-speech, audio-
  exam accommodations, or reading-disability assistive tech. Hebrew
  language preferred when available; English-language acceptable.
- WCAG 2.2 success criteria relevant to TTS and reading accommodation.
- At least 1 source on Hebrew-specific reading-disability literature
  (`לקויי למידה`, `לקויות קריאה`).

Format: `[N] Author (Year). "Title". Venue. URL.` — numbered, in the
order they're cited in the body.

### Section G — Open questions for human reviewer

3-7 specific questions the human reviewer should answer before
sprint-planning the workitems. Phrased as binary or pick-one
questions, not open-ended.

## 4. PR description shape

```markdown
## Summary
<one paragraph>

## What I read
- <list of URLs you fetched, with one-line summaries>
- <list of repo files you read, with relevance>

## What's in the deliverable
- <bullet per section A-G>

## Stats
- Time spent: <minutes>
- Word count: <n>
- Citations: <count>
- New workitems recommended: <count>

## Open questions for reviewer
<numbered list, same as Section G>
```

## 5. Working principles

- **Evidence over opinion.** Cite sources. When you must speculate,
  label it as such (`[speculation]:` prefix).
- **Surface contradictions, don't resolve them silently.** If two
  sources disagree, put both in the red-line register and pick one
  with rationale.
- **Be conservative on the red line.** When in doubt about whether an
  intervention modifies tested content, lean toward "disallow" and
  flag for human review.
- **Don't recommend more than 8 new workitems.** If you find more,
  defer the surplus.
- **Hebrew-first sources where available.** This is a Hebrew-product
  for Israeli students; Israeli MoE / NITE guidelines outweigh
  generic WCAG advice.

## 6. The research input — 11 user-stated requirements

Verbatim from the product owner (a domain expert in this user audience):

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
7. מניעת דו־משמעות בהקראה — *prevent ambiguity in reading*
   (partially addressed by F51 — see ADR-038 + UAT-2026-05-02)
8. סנכרון בין טקסט מודפס לשמע — *print↔audio sync*
9. סימון חזותי של חלקים חשובים — *visual marking of important parts*
10. גרסה "ידידותית להקראה" שאינה משנה את התוכן הנבחן — *"reading-
    friendly version" that does not change tested content*

> הקו האדום הוא לא לפשט את הבחינה באופן שפוגע בתקפות הפדגוגית. כלומר,
> לא להוריד רמת קושי קוגניטיבית, אלא להסיר חסם קריאה.

**Red line**: do not reduce cognitive difficulty; only remove the
reading barrier.

For the deeper per-point research questions and the existing pipeline
mapping, also read `docs/research/reading-disability-pipeline-needs.md`
in the repo — that is the *internal* research brief; this RUN file is
the *operational* instruction.

## 7. When stuck

- Do **not** pause and wait. The human is offline; "wait for input"
  resolves to "abort the run", which loses your work.
- If a tool fails 3 times: write what you tried + why it failed + what
  you would do next, in the deliverable's "Section G — Open questions"
  area, then move on.
- If you can't decide between two paths: pick the more conservative
  one. Document the alternative in Section G.
- If a citation is paywalled: cite the abstract / DOI and note
  "paywalled" — don't fabricate access.
- If the repo state is unexpected (e.g., merge conflicts on `main`):
  write what you observed in the PR description and stop. Do not
  attempt repair.

## 8. Self-review before marking the PR ready

Before flipping the PR from Draft → Ready-for-review:

- [ ] All 7 sections (A-G) are present and non-empty.
- [ ] Word count between 4-8k (use `wc -w`).
- [ ] At least 5 citations, including at least 1 Israeli source.
- [ ] Red-line register has at least 8 rows with a decision per row.
- [ ] No more than 8 new workitems recommended.
- [ ] Phase 0 names ≤ 3 features.
- [ ] PR description has the Stats section filled in.
- [ ] No mentions of "I'll do X next" / "this will be expanded later" —
      this is the deliverable, not a plan for one.
- [ ] No `<!-- TODO -->` markers anywhere.

When all 9 boxes tick, convert PR to Ready-for-review and stop.

## 9. Sign-off line

End the deliverable with this exact line on its own:

```
Run completed: <run_id> | model: claude-opus-4-7 high | time: <minutes>m
```

Stop after writing this line. Do not start a new task.

---

**End of RUN file. Begin work now.**
