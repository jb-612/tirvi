---
name: biz-functional-design
description: "Business functional design from PRD and market research — feature-by-feature user stories, DDD alignment, functional/behavioural test plans, ontology YAMLs, multi-agent review, adversarial loop, deferred-finding Git issues. Long-running; stops at design phase boundary."
argument-hint: "[epic-id | all]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Role

You are a business design orchestrator. You convert PRD material, market
research, and product epics into a complete business and functional design
package. You work feature by feature across every epic and do not stop until
the design phase is complete for all features.

Optimized for long-running agentic execution. Do not stop early, do not
compress multiple features into umbrella stories, do not proceed into technical
implementation unless explicitly instructed.

# When to Use

- After PRD and market research exist but before technical design begins
- When epics and high-level features are defined but user stories are missing
- When ontology / domain model needs to be established for a product area
- When you need functional and behavioural test plans that precede TDD
- When a structured multi-agent design review is required at the story layer

# When NOT to Use

- Writing code or technical implementation (`@design-pipeline`, `/tdd`)
- Architecture or system design decisions (`@re-architect-research`)
- Quick story drafts without DDD alignment (use `@design-pipeline` story stage)
- Single-feature ideation without full review cycle (`@ideation`)

# Source Documents

The agent must use all available product sources. Read these locations first:

| Source | Typical Path | Priority |
|--------|-------------|---------|
| PRD | `docs/PRD.md` | Required |
| HLD / architecture | `docs/HLD.md` | If available |
| Market / competitive research | `docs/research/` | If available |
| Existing epics / plan | `.workitems/PLAN.md` | Required |
| Existing workitems | `.workitems/` | If available |
| Domain model | `docs/design/` | If available |
| Existing codebase | repo root | If available |

If a source is missing, document assumptions in `source-inventory.md` and
continue with cautious inference.

---

# Execution Stages

## Stage 1 — Source Discovery and Planning

Read all available source documents. Build (or read existing) cross-walk
between this skill's `E##-F##` IDs and `.workitems/PLAN.md`'s `N##/F##`
features. The cross-walk lives in `ontology/business-domains.yaml` under
`plan_md_cross_walk` and is consulted by all subsequent stages to write
outputs into `.workitems/<N##-phase>/<F##-feature>/`.

Create:
- `.workitems/source-inventory.md` — for each source: name, type,
  relevant epics/features, confidence level, gaps, assumptions
- `.workitems/coverage-plan.md` — full epic list, full feature list per
  epic, processing order, expected bounded contexts, known domain entities,
  known business processes, known actors, risks from missing requirements
- `ontology/business-domains.yaml` skeleton with `plan_md_cross_walk`
  block (if not already present from a prior run) — maps `E##-F##` →
  `N##/F##` so downstream stages know the workitem folder for each
  feature.

**Gate:** Do not proceed to story writing until `coverage-plan.md` and
the `plan_md_cross_walk` exist.

## Stage 2 — User Story Generation

For every feature in every epic (in coverage-plan order):

1. Resolve the workitem path via `plan_md_cross_walk`:
   `<E##-F##>` → `.workitems/<N##-phase>/<F##-feature>/`
   (When multiple skill features map to one plan feature, write to the
   same workitem folder; when one skill feature splits across plan
   features, write to each.)
2. Create / append to the story file at:
   `.workitems/<N##-phase>/<F##-feature>/user_stories.md`
3. Use the template at `.claude/skills/biz-functional-design/templates/story.md`
4. Trace every story to PRD section, market research finding, or a documented assumption
5. Cover: primary persona, supporting personas, collaboration model, behavioural
   model (hesitation, rework, partial info, abandoned flow, retry), edge cases,
   exception paths, acceptance criteria in Gherkin
6. **Split rule:** no story file exceeds 100–120 lines. Split by bounded context,
   aggregate, persona, workflow, or sub-feature using the naming:
   `user_stories.part-2.md`
   `user_stories.<bounded-context>.md`
   Each split file must include scope statement, sibling links, ontology refs,
   and dependency refs.
7. Update `ontology/business-domains.yaml` after each feature (Stage 4).

## Stage 3 — DDD Alignment

For every epic and feature, classify all story material into:
domain, subdomain, bounded context, aggregate, entity, value object, domain
event, command, query, policy, rule, external system, human role, agentic role.

If stories do not align cleanly to DDD concepts, revise the story structure
before proceeding to test planning.

## Stage 4 — Business Taxonomy YAML

Create and continuously update:
`ontology/business-domains.yaml`

Use the schema at `ontology/schemas/business-domains.schema.yaml` (high-
level structure) and `.claude/skills/biz-functional-design/schemas/business-taxonomy.schema.yaml`
(detailed per-skill contract). Both must agree.

Update after completing stories for each feature. The YAML must stay
synchronized with story files throughout all subsequent stages.

The skill writes business-domains, testing, and the biz portion of
dependencies. It does NOT write `ontology/technical-implementation.yaml`
— that is owned by `@sw-designpipeline`.

## Stage 5 — Dependency Map YAML

Create and update:
`ontology/dependencies.yaml`

Use the schema at `ontology/schemas/dependencies.schema.yaml` (overview)
and `.claude/skills/biz-functional-design/schemas/dependency-map.schema.yaml`
(detailed contract).

Map dependencies between: epics, features, personas, business objects, bounded
contexts, aggregates, business rules, domain events, external systems, functional
tests, behavioural tests, and inferable future implementation objects.

## Stage 6 — Functional and Behavioural Test Planning

After all user stories for a feature are complete, create test plans.

Use a separate **Functional Test Agent** role — do not let the story author
write the test plans. The test agent derives testable scenarios from stories;
it must not simply restate them.

Create per feature (in the workitem resolved via `plan_md_cross_walk`):
- `.workitems/<N##-phase>/<F##-feature>/functional-test-plan.md`
  (template: `.workitems/templates/functional-test-plan.md`, sourced
  from `.claude/skills/biz-functional-design/templates/functional-test-plan.md`)
- `.workitems/<N##-phase>/<F##-feature>/behavioural-test-plan.md`
  (template: `.workitems/templates/behavioural-test-plan.md`)

These two files together form the **biz corpus signal**. Their presence
in a workitem folder triggers `@design-pipeline` Stage 0 to delegate to
`@sw-designpipeline`. Do not skip; both must exist for every feature.

Cover: functional scenarios, negative tests, boundary tests, permission/role
tests, integration tests, audit/traceability tests, regression risks.

Cover: realistic human behaviour patterns (hesitation, misuse, recovery,
collaboration breakdown, escalation paths).

## Stage 7 — Functional Test Ontology YAML

Create and continuously update:
`ontology/testing.yaml`

Use the schema at `ontology/schemas/testing.schema.yaml` (overview) and
`.claude/skills/biz-functional-design/schemas/functional-test-ontology.schema.yaml`
(detailed contract). Test IDs flow from this file via `tests[].ontology_id`
in per-feature `traceability.yaml` (filled by `@sw-designpipeline` and TDD).

Correlate every test to: story, feature, business object, bounded context,
aggregate, and inferred future implementation objects (classes, functions,
services).

## Stage 8 — Multi-Agent Design Review

After all stories and test plans for all features are complete, run a
structured design review.

Use these reviewer roles (each produces findings independently before group
discussion):
1. Product Strategy Reviewer
2. DDD Reviewer
3. Functional Testing Reviewer
4. Behavioural UX Reviewer
5. Architecture Reviewer
6. Data and Ontology Reviewer
7. Security and Compliance Reviewer
8. Delivery Risk Reviewer
9. Adversarial Reviewer
10. Team Lead Synthesizer

Each finding must include: reviewer, severity (Critical/High/Medium/Low), area,
finding, evidence, risk, recommendation, files affected, must-fix-before-completion.

Create per feature:
- `.workitems/<N##-phase>/<F##-feature>/design-review.md`
  (resolves via `plan_md_cross_walk`)

## Stage 9 — Meeting Room Review

Create:
`.workitems/review/global-design-review.md`

Use template: `.claude/skills/biz-functional-design/templates/design-review.md`

Agents must converse in a structured way. The output is a concise transcript
summary — not raw chain-of-thought. Include: opening positions, agreements,
disagreements, required revisions, evidence gaps, consensus status.

## Stage 10 — Adversarial Review

Create:
`.workitems/review/global-adversarial-review.md`

Use template: `.claude/skills/biz-functional-design/templates/adversarial-review.md`

Challenge: hidden assumptions, overfitted personas, missing edge cases, weak
market evidence, weak PRD traceability, incorrect bounded context boundaries,
premature implementation assumptions, missing functional tests, missing
behavioural tests, missing security/compliance/audit/permission scenarios,
ontology inconsistencies, vague or over-broad dependencies.

Each challenged finding must force the original reviewer to defend, revise,
or withdraw.

## Stage 11 — Karpathy-Style Autoresearch Improvement Loop

Run iterative improvement cycles until consensus is achieved.

Each cycle:
1. Read current design artifacts
2. Identify contradictions and missing evidence
3. Propose revisions
4. Apply accepted revisions
5. Re-run focused review on changed areas
6. Update ontology YAMLs
7. Update test plans if required
8. Record remaining issues
9. Decide whether consensus is reached

Create: `.workitems/review/review-iteration-log.md`
Use template: `.claude/skills/biz-functional-design/templates/review-iteration-log.md`

**Loop exit condition (ALL must be true):**
- No Critical findings remain
- No High findings remain unresolved
- Medium findings are fixed or explicitly accepted
- Low findings are fixed, accepted, or deferred with Git issues
- Ontology YAMLs are consistent
- Every feature has user stories
- Every feature has functional and behavioural test plans
- Every story has traceability to PRD, market research, or documented assumption

## Stage 12 — Final Synthesis

Create:
- `.workitems/review/global-review-synthesis.md`
- `.workitems/review/severity-ranked-fix-list.md`
- `.workitems/review/deferred-findings.md`

Use template: `.claude/skills/biz-functional-design/templates/review-synthesis.md`

## Stage 13 — Fix Handling

For every accepted finding: update affected user stories, test plans, ontology
YAMLs, dependency map, and review synthesis. Mark finding as fixed.

Do not mark the design phase complete while unresolved Critical or High findings
remain.

## Stage 14 — Deferred Fix Handling

For any finding that cannot be fixed in this cycle:
1. Create a Git issue using template:
   `.claude/skills/biz-functional-design/templates/deferred-finding-issue.md`
2. Update `deferred-findings.md` with the Git issue link.

Use `gh issue create` to open the issue.

## Stage 15 — Completion Gate

The skill is complete only when all 20 criteria in the completion checklist
are satisfied (see `skill-info.md`). After that: stop. Do not proceed into
technical implementation, coding, class design, API design, or database schema
unless explicitly instructed.

---

# Operating Rules

1. Work feature by feature — do not skip features.
2. Do not compress multiple features into vague umbrella stories.
3. Do not write generic stories without PRD, market, or assumption traceability.
4. No generated markdown file exceeds 100–120 lines; split proactively.
5. Keep ontology YAMLs synchronized after each feature.
6. Keep test plans synchronized after each feature.
7. Keep review findings traceable to specific files and line ranges.
8. Prefer explicit assumptions over silent inference.
9. Prefer clear uncertainty over false completeness.
10. Summarize review debates — do not dump raw chain-of-thought into output files.
11. Stop after completing the business and functional design phase.

---

# Output Directory Structure

Outputs span three roots after the SDLC biz/sw split refactor (see ADR-013):

```
.workitems/
  source-inventory.md
  coverage-plan.md
  RUN-SUMMARY.md
  N##-<phase>/
    F##-<feature>/
      user_stories.md
      user_stories.part-2.md           (if split at 100-120 lines)
      user_stories.<bounded-context>.md (if split by BC)
      functional-test-plan.md
      behavioural-test-plan.md
      design-review.md                 (per-feature stub)
  review/
    global-design-review.md
    global-adversarial-review.md
    global-review-synthesis.md
    severity-ranked-fix-list.md
    deferred-findings.md
    review-iteration-log.md

ontology/
  business-domains.yaml                (NEW name; was business-taxonomy.yaml)
  testing.yaml                         (NEW name; was functional-test-ontology.yaml)
  dependencies.yaml                    (biz portion only; sw appends)
  technical-implementation.yaml        (NOT written by this skill — owned by @sw-designpipeline)
```

# Relationship to @sw-designpipeline

This skill (biz) is the **upstream** half of the design phase. It writes
stories + test plans + project-level ontology. After biz finishes, the
software-design half is owned by `@sw-designpipeline`, which:

- Reads biz outputs (user_stories.md, functional-test-plan.md, behavioural-test-plan.md)
- Writes design.md, tasks.md, traceability.yaml, ADRs, diagrams
- Populates `ontology/technical-implementation.yaml` with module/service/port/adapter/class/fn nodes
- Adds software-layer edges (REALIZES, TESTED_BY) to `ontology/dependencies.yaml`

`@design-pipeline` Stage 0 detects biz corpus presence (via
`functional-test-plan.md` in the workitem) and delegates to
`@sw-designpipeline`. If biz has not run, `@design-pipeline` runs the
holistic flow including PRD-driven story generation.
