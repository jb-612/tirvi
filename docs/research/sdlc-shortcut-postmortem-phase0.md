---
title: SDLC shortcut postmortem — Phase 0 reading-disability features
date: 2026-05-02
status: published
authors: jbellish + Claude Opus 4.7 (CLI)
related_prs:
  - "#29 (F51 homograph context-rules)"
  - "#33 (Phase-0 scaffold ADR-041 + workitems)"
  - "#34 (F52 block-kind taxonomy)"
  - "#35 (F53 clause-split SSML chunker — F53 backfill on this branch)"
  - "#36 (this — F51/F52/F39 backfill + methodology alignment)"
related_adrs:
  - ADR-041 (red-line decision register)
related_rules:
  - .claude/rules/workflow.md (amended in PR #36 to make 3 artifacts mandatory)
---

# Phase-0 SDLC shortcut — what happened, what we did about it

## TL;DR

Phase 0 (F51 homograph context-rules + F52 block-kind taxonomy + F53
clause-split chunker + F39 player pause-after-question) shipped with
a **reduced design ceremony** compared to the project's documented
SDLC. Specifically, three artifacts that F21 set as precedent were
omitted from the F51/F52/F53/F39 workitem folders:
`functional-test-plan.md`, `behavioural-test-plan.md`,
`ontology-delta.yaml`.

The shortcut was acknowledged at PR #35 review; the user
(jbellish) elected **option A** of three remediation paths: don't
mechanically backfill the meeting-room / review / STD artifacts that
are most ceremony-heavy AND least useful in retrospect, but DO
mandate the three foundational design artifacts for every feature
going forward and backfill them across F51/F52/F53/F39.

This document records the decision so it shows up in `git log` /
`docs/research/` rather than dissolving into a memory the next
maintainer has to reconstruct.

## What was skipped vs. what was kept

| Artifact                          | F21 (precedent) | F51 (merged) | F52 (merged) | F53 (PR #35) | F39 (scaffold) |
|-----------------------------------|:---------------:|:------------:|:------------:|:------------:|:--------------:|
| ADR (binding scope)               | none/n.a.        | ADR-038      | ADR-041      | ADR-041      | ADR-041        |
| `design.md`                       | ✅              | ✅            | ✅            | ✅            | ✅              |
| `tasks.md`                        | ✅              | ✅            | ✅            | ✅            | ✅              |
| `user_stories.md`                 | ✅              | ✅            | ✅            | ✅            | ✅              |
| `traceability.yaml`               | ✅              | ✅            | ✅            | ✅            | ✅              |
| **`functional-test-plan.md`**     | ✅              | ❌ → backfilled | ❌ → backfilled | ❌ → backfilled | ❌ → backfilled |
| **`behavioural-test-plan.md`**    | ✅              | ❌ → backfilled | ❌ → backfilled | ❌ → backfilled | ❌ → backfilled |
| **`ontology-delta.yaml`**         | ✅              | ❌ → backfilled | ❌ → backfilled | ❌ → backfilled | ❌ → backfilled |
| `meeting-room/` (synthesis)       | ✅              | ❌            | ❌            | ❌            | ❌              |
| `review/R1/R2/R3` trails          | ✅              | ❌            | ❌            | ❌            | ❌              |
| STD.md (`@test-design`)           | (varies)        | ❌            | ❌            | ❌            | ❌              |

The three rows in **bold** are now mandatory for every workitem (per
the workflow.md amendment in PR #36). The four rows below them
(meeting-room, review, STD) stay deferred for Phase 0 — see "What
remains skipped" below.

## What did happen at design time (why it wasn't catastrophic)

The design ceremony was reduced, not absent. What stood in for the
missing artifacts:

- **PR #30 (research roadmap)** — multi-source synthesis of the 11
  user-stated reading-disability requirements + 20-row red-line
  decision register + priority-ordered workitem list + Phase 0
  recommendation (F52 + F53 + F39). Reviewer-approved via 7 explicit
  questions.
- **ADR-041** — codified the 20-row red-line register as a binding
  ADR before any feature design touched code. Filed first per Q7
  reviewer answer.
- **PR #33 (scaffold)** — populated each workitem's `design.md`,
  `tasks.md`, `user_stories.md`, `traceability.yaml` with non-trivial
  content drawn from the roadmap. design.md per feature included
  problem statement, dependencies, interfaces, design elements,
  out-of-scope, and risks.
- **High test coverage** — F52 ships at 30/30 strict on its synthetic
  corpus; F53 ships at 22/22; F51 was already at 29/31 (with two
  documented xfails). The full test suite stayed at 0 regressions
  through every Phase-0 PR.

The three foundational artifacts, when backfilled now, document
*what already exists in the code and the reviewer-approved roadmap*.
They are not adding new design intent — they are pulling existing
intent into the canonical workitem shape so a future maintainer
finds it where they expect to.

## What remains skipped (deliberate)

| Artifact                                 | Why deferred                                                                                                           |
|------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| `meeting-room/` synthesis trail           | The roadmap PR #30 + the user-reviewer Q&A on PR #30 + the in-conversation reviewer pass acted as the synthesis. Filing fresh meeting-room artifacts retroactively would be performative — no real synthesis occurred at meeting-room time. |
| `review/R1/R2/R3` rounds                  | F52 and F53 are already merged with high test coverage and zero regressions. Running an adversary review against shipped, tested code is unlikely to surface anything actionable; "concerns" filed retroactively don't get fixed. F39 has no code yet — its review will happen forward, not backfilled. |
| STD.md (`@test-design`)                   | Functional + behavioural test plans (now backfilled) cover the WHAT-to-test layer. STD.md adds an epic-level view + traceability test-entry shape that F21 has but is genuinely heavyweight. Defer to Phase-1+ when multi-feature epics need it.    |

The decision is honest, not lazy: **adding paper that nobody reads
or acts on is worse than admitting the work was light and codifying
the rule going forward.**

## What changes for Phase 1+ (F54, F40, F41, F55, N05/F51-bench)

Going forward, every new workitem MUST include:

- The three previously-mandatory artifacts (`design.md`,
  `tasks.md`, `user_stories.md`, `traceability.yaml`).
- The three NEWLY-mandatory artifacts (`functional-test-plan.md`,
  `behavioural-test-plan.md`, `ontology-delta.yaml`).

For features that route through `@biz-functional-design` →
`@sw-designpipeline`, the first two of the new three are produced
automatically by the biz half. For features that don't have a biz
corpus (most internal-tooling and player work), the maintainer
authors them at design time, not at backfill time.

The workflow.md amendment in PR #36 makes this load-bearing. A
future PR that omits any of these artifacts should be flagged at
review.

## Lessons for the agent (Claude Code) and the user

1. **"Implement as new feature in existing epics" is ambiguous.** It
   could mean "use the full pipeline" or "scaffold a workitem and
   ship". I picked the lighter reading; the user accepted at "go"
   but flagged it later. Clearer signal next time: when a request
   crosses the 3-module / non-trivial threshold from
   `workflow.md`, the agent SHOULD ask which design lane to take
   (full / lite / scaffold-only) rather than infer.
2. **The merged research roadmap is a strong design artifact.** It
   carried the per-feature design intent through reviewer Q&A. The
   gap was not "no design happened"; the gap was "the canonical
   workitem-shape artifacts were not authored". The fix is the
   shape, not the substance.
3. **High test coverage doesn't substitute for design ceremony.**
   F52's 30/30 corpus and F53's 22/22 corpus catch implementation
   bugs, not design errors. The functional-test-plan + behavioural-
   test-plan ARE the design-error catchers. They get authored
   even when the implementation is already green.
4. **Retrospective adversary review has diminishing returns.** If
   the design ceremony was reduced, file the postmortem honestly
   and tighten the rule. Don't pantomime the missing rounds against
   shipped code.
5. **Harness-meta drift is a real failure mode.** Discovered after
   the F39 backfill landed: F39's design artifacts referenced
   `flutter_app/lib/components/player/*.dart` with Riverpod —
   completely wrong stack. The actual player is **vanilla JS +
   vitest**, mandated by ADR-023, with F33/F35/F36 already shipped
   in that stack. The harness rules `coding-standards.md` and
   `tdd-rules.md`, plus `.claude/skills/ddd-7l-scaffold/references/
   README.md` all carried Flutter/Dart-specific assumptions
   (e.g., `flutter_app/lib/**/*.dart` paths in frontmatter,
   "Flutter app under `flutter_app/lib/`" in the references README)
   that pattern-matched onto F39 even though the project doesn't
   use Flutter. The error compounded: long context + harness rules
   that conflated "tooling exists" with "project uses tooling" →
   F39 design referenced fictional `.dart` files that the workflow
   ceremony was supposed to catch but didn't.

   **Corrective actions taken in PR #37**:

   - `.claude/rules/coding-standards.md` — restructured into
     "Universal Rules" (apply to every project, every language) +
     "Per-language sections" (templates the agent reads ONLY when
     the hosting project's CLAUDE.md declares the language as in
     use). Frontmatter `paths:` removed (project-set, not
     harness-set). Added `### TypeScript / JavaScript` section
     since most browser-side projects need it.
   - `.claude/rules/tdd-rules.md` — abstracted the TDD entry-point
     to "the router detects language from the task's test_file
     path and the project's CLAUDE.md, then delegates to the
     matching per-language TDD skill". Removed the hard-coded
     "@tdd-go or @tdd-flutter" delegation. Three-agent role
     separation stays as a universal pattern; per-language path
     matrices live in the corresponding TDD skill's SKILL.md, not
     in this rule.
   - `.claude/skills/ddd-7l-scaffold/references/README.md` —
     removed the "Notes for tirvi specifically" section that
     incorrectly claimed tirvi has `flutter_app/lib/`. Replaced
     with a "How the agent picks a reference" section that
     explicitly mandates project-CLAUDE.md inspection + repo `ls`
     before assuming any language is in use.

   **The F39 design artifacts themselves still need correction**
   — they were authored in PR #33 + backfilled in PR #36 against
   the wrong stack. That correction is its own follow-up PR
   (out of scope for PR #37), and SHOULD start from a fresh
   conversation context to avoid re-importing the long-context
   drift that produced the original error.

## Sign-off

This document, the workflow.md amendment, and the three backfilled
artifacts per feature are the explicit closure of the Phase-0 design-
ceremony gap. PR #36 is the carrier; F53's same-three artifacts
ride on PR #35. PR #37 follows with the harness-meta corrections
described in lesson 5. Subsequent feature PRs MUST include all seven
workitem files at merge time.
