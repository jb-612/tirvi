---
name: design-review
description: 3-round multi-tier design review with 6 specialist reviewers (including HLD compliance), adversary challenge, cross-debate, and synthesis. Use during design pipeline stages 5/7 or standalone before TDD build.
argument-hint: "[feature-id]"
---

Design review for $ARGUMENTS:

## When to Use

- Design review rounds within `@design-pipeline` (Stages 5 and 7)
- Standalone design validation before TDD build
- Re-review after major design revisions

## When NOT to Use

- Code review (use `@code-review`)
- Writing or modifying design artifacts (use `@design-pipeline`)

## 3-Round Review Process

### Round 1: 6 Specialist Reviewers (parallel)

Create team `design-review-{feature}`, launch 6 agents in parallel on Sonnet (use `mode: "default"` on each Agent call — reviewers read and analyze only, no file writes):

#### Agent 1: Contract Alignment Reviewer

**Reference docs:** `CLAUDE.md`, `AGENTS.md`, `.claude/rules/*.md`, `docs/ADR/*.md`

Reads all governance contracts and ADR decisions, checks each against the design:
- Coverage: Is each contract requirement addressed by the design?
- Contradictions: Does the design conflict with any governance rule or ADR?
- Phasing: Does the design's phasing match project timelines?
- Gaps: Are there contract requirements no design addresses?

Output per finding: Coverage (full/partial/gap), Finding, Severity, Recommendation.

#### Agent 2: Architecture & Pattern Reviewer

**Reference docs:** Existing source code in `scripts/`, config files, infrastructure docs

Reads existing architecture and patterns:
- Pattern consistency: Does the design follow existing project patterns?
- Interface sufficiency: All methods needed for the feature present?
- Daemon patterns: Async patterns, shared state, event-driven flows correct?
- Cross-cutting concerns: Logging, error handling, config consistent?

#### Agent 3: Phasing & Scope Reviewer

**Reference docs:** `.workitems/PLAN.md`, feature `tasks.md`, all feature `design.md` files

Challenges scope and dependencies:
- Task count realism: Is the task count achievable for the stated phase?
- Feature boundary violations: Are tasks in the wrong feature?
- Critical path: What minimum subset unblocks the next feature?
- Dependency ordering: Is the task DAG optimal?

#### Agent 4: Implementation Gap Reviewer

**Reference docs:** All `scripts/**/*.py`, all `tests/**/*.py`

Compares existing code against design:
- Already implemented: What capabilities exist today?
- Partially implemented: What needs enhancement?
- Not yet implemented: What's entirely missing?
- Code-design mismatches: Where does code contradict the design?

#### Agent 5: Risk & Feasibility Reviewer

**Reference docs:** All feature `design.md` files, existing source code

Identifies technical risks:

- Technical risks: Fragile patterns, edge cases, things that won't work
- Performance risks: Scale, latency, memory concerns
- Dependency risks: License, maturity, API cost
- Complexity risks: Dual implementations, sync divergence, abstraction leaks
- Regression risks: What existing behavior could break

Output per risk: Feature, Category, Likelihood, Impact, Description, Mitigation.

#### Agent 6: HLD Compliance Reviewer

**Reference docs:** `docs/design/hld-index.md`, targeted HLD sections, feature `design.md`, `traceability.yaml`

Verifies design-to-HLD semantic alignment (not just ref existence):
- **Interface match**: Do proposed port signatures match HLD §5.2 definitions?
- **Behavioral match**: Does proposed logic match HLD behavior descriptions?
- **Deviation audit**: Are all departures from HLD recorded in HLD Deviations table?
- **Coverage**: Are all relevant HLD sub-sections addressed by design elements?
- **Orphan detection**: Are there design elements with no HLD backing that lack justification?

Process:
1. Read `hld-index.md` to identify HLD sections referenced by the design
2. Read those specific HLD sections (targeted line ranges)
3. For each design element, compare proposed interface/behavior against HLD spec
4. Flag any mismatch not documented as a deviation

Output per finding: HLD Section, Design Element, Discrepancy, Severity, Required Action.

**This agent runs ONLY for `domain` and `integration` feature types.** Scaffolding and UI features skip this reviewer.

### Round 2: Adversary Challenge (single agent, Opus)

Launch 1 adversary agent on Opus with ALL Round 1 findings as context.

The adversary MUST:
- Challenge overblown findings: Which Criticals are actually Mediums?
- Challenge premature recommendations: Which fixes add complexity for problems that may never materialize?
- Defend the current design: What did reviewers miss that the design got right?
- Stress-test split/defer proposals: What coordination overhead do they create?
- Identify YAGNI: Which recommendations solve future problems, not current ones?

Output per challenge: Original Finding, Counter-Argument, Risk of Following Recommendation, Verdict (AGREE / PARTIALLY AGREE / DISAGREE).

Must end with: **"Findings I Could NOT Challenge"** — the surviving actionable items.

### Round 3: Cross-Debate + Synthesis

Send adversary's key challenges back to the original reviewers (2-3 most contested) for brief rebuttals. Then synthesize:

1. **Merge** all findings, challenges, and rebuttals
2. **Classify** into: MUST FIX (survived adversary) / SHOULD FIX (consensus medium) / DEFERRED (adversary won)
3. **Revise workitems**: Update design.md status, rewrite tasks.md, update PLAN.md
4. **Set verdict**: APPROVED / APPROVED_WITH_COMMENTS / CHANGES_REQUIRED

## Team Protocol

```
TeamCreate("design-review-{feature}")
  Round 1: 6x Agent(sonnet, name="{role}-reviewer")  [parallel]
  Round 2: 1x Agent(opus, name="adversary")           [after Round 1]
  Round 3: SendMessage to 2-3 reviewers for rebuttals  [after Round 2]
  Synthesis: Team lead produces final report + workitem edits
  Shutdown: SendMessage(shutdown_request) to all
```

## Finding Format (All Agents)

```
### Finding N: [title]
- **Area**: [contract | architecture | scope | risk | gap]
- **Issue**: [description with file:line evidence]
- **Severity**: [Critical | High | Medium | Low]
- **Recommendation**: [specific actionable change]
```

## Quality Gates (All Agents)

Universal constraints every agent validates:
- Planning files <= 100 lines each
- PNN-FNN naming convention
- No circular dependencies
- CC <= 5 for all proposed functions
- TDD approach specified for all implementation tasks
- Every acceptance criterion maps to at least one task

## Verdict

- **APPROVED** — No Critical findings survive adversary challenge
- **APPROVED_WITH_COMMENTS** — No Critical, High findings are advisory
- **CHANGES_REQUIRED** — Critical findings survive adversary + rebuttal

## Post-Review Actions

1. Update `design.md` status field (DRAFT -> APPROVED or CHANGES_REQUIRED)
2. Add "Review Outcomes" section to design.md with critical fixes and scope changes
3. Rewrite `tasks.md` if scope changed (add/remove/renumber tasks)
4. Update `PLAN.md` with review notes and scope redistribution

## Cross-References

- `@design-pipeline` — Invokes this skill at Stages 5 and 7
- `@code-review` — Sibling review skill for implementation code
- `@task-breakdown` — Follows after design review approval
- `@adversary` — Standalone adversarial testing (different scope: runtime behavior)
