---
name: research
description: Multi-perspective research with parallel agents — web research, codebase analysis, graph queries, and cost/risk analysis — synthesized into a structured report for design decisions.
argument-hint: "<research-question> [--perspectives explorer,architect,critic,cost,precedent] [--depth quick|standard|deep]"
allowed-tools: Read, Glob, Grep, Bash, Agent, WebSearch, WebFetch
---

# Research Skill

Conduct multi-perspective research on: $ARGUMENTS

## Phase 0: Scope Gate

Before any research, clarify the SDLC context. Ask (or infer from the question):

1. **Intent**: Refactor existing code? Evaluate a library/pattern? Design a new
   module? Compare architectural approaches?
2. **Codebase area**: Which bounded context, module, or layer is affected?
3. **Constraints**: Team size, timeline, existing tech stack commitments,
   deployment model?
4. **Decision type**: Build vs adopt? Pattern selection? Migration strategy?

If the question is ambiguous, present 2-3 scoped interpretations and ask the
user to pick before proceeding. A 30-second scope check prevents a 10-minute
research detour.

## Phase 1: Parse Arguments

Parse the input to extract:
- **Research question**: everything before the first `--` flag
- **`--perspectives`**: comma-separated list of agents to spawn (default: all five — `explorer,architect,critic,cost,precedent`)
- **`--depth`**: controls search budget and clarification rounds:
  - `quick`: 3 web searches per agent, 0 clarification rounds
  - `standard` (default): 5 web searches per agent, 1 clarification round
  - `deep`: 10 web searches per agent, 2 clarification rounds

## Phase 2: Gather Internal Context

Before spawning research agents, gather project context that all agents will need.

### 2a. Graph Context (if `.acm_graph.json` exists)

Spawn the `graph-analyst` agent:

> "Summarize the project architecture from the graph: what bounded contexts, aggregates, domain events, and code modules exist? Include event publisher/consumer relationships and cross-layer summary."

### 2b. Read Project State

Read these files to build project context:
- `CLAUDE.md` — architecture and conventions
- `.workitems/master-plan.md` — feature roadmap and dependencies
- Any existing research in `docs/research/` related to the question (search by keyword)

### 2c. Context Verification Gate

Before assembling context, verify that key inputs exist. This prevents agents
from wasting search budget on questions already answered in the codebase.

| Input | Check | If Missing |
|-------|-------|------------|
| `CLAUDE.md` | File exists and has architecture section | Note "project conventions unknown" |
| `.acm_graph.json` | File exists | Skip graph context, note "no graph available" |
| `.workitems/master-plan.md` | File exists | Note "no roadmap context" |
| `docs/research/` | Related prior research exists | Note "no prior research on this topic" |
| Existing tests for affected area | `grep -r` for test files | Note "no test coverage baseline" |

If 3+ inputs are missing, warn the user: "Limited project context available —
research confidence will be lower. Consider running `reverse-prd` or
`sweep-analytics` first."

### 2d. Assemble PROJECT_CONTEXT

Combine graph findings, CLAUDE.md summary, and master plan into a `PROJECT_CONTEXT` blob (~500 words max) that every research agent receives.

## Phase 3: Spawn Research Team

Spawn agents **in parallel** (all in a single message with multiple Agent tool calls). Each agent receives:
1. The research question
2. The PROJECT_CONTEXT blob
3. The depth setting
4. Their perspective-specific instructions (from their agent definition)

### Agents to Spawn

Only spawn agents listed in the `--perspectives` flag (default: all five):

| Agent | Perspective | Definition |
|-------|------------|------------|
| `research-explorer` | Landscape — what options exist | `.claude/agents/research-explorer.md` |
| `research-architect` | Architecture fit — how options integrate | `.claude/agents/research-architect.md` |
| `research-critic` | Devil's advocate — what can go wrong | `.claude/agents/research-critic.md` |
| `research-cost` | Cost analysis — what it actually takes | `.claude/agents/research-cost.md` |
| `research-precedent` | Evidence — who has done this successfully | `.claude/agents/research-precedent.md` |

Use `model: sonnet` for all research agents. Use `run_in_background: false` — wait for all agents to complete.

**Agent spawn template:**
```
Agent(
  subagent_type="general-purpose",
  name="research-{perspective}",
  model="sonnet",
  mode="default",
  prompt="""
You are the {perspective} agent on a research team.

## Research Question
{question}

## Project Context
{PROJECT_CONTEXT}

## Depth
{depth} — you have {N} WebSearch calls and {M} WebFetch calls.

## Your Instructions
Follow the process defined in your agent definition (.claude/agents/research-{perspective}.md).
Return your findings in the output format specified in your definition.
"""
)
```

## Phase 4: Clarification Round (standard and deep only)

If any agent's output includes explicit questions or gaps marked "needs clarification":
1. Collect all questions from all agents
2. Present them to the user as a batch
3. If the user answers, relay relevant answers to the requesting agents via `SendMessage`
4. Skip this phase at `quick` depth

At `deep` depth, repeat Phase 4 up to 2 times.

## Phase 5: Synthesize Report

After all agents complete, synthesize their findings into a single research report.

### Report Structure

Write the report to `docs/research/{topic-slug}.md` where `{topic-slug}` is a kebab-case slug of the research question (max 50 chars).

```markdown
---
tier: 5
version: 1.0
created: {today's date}
updated: {today's date}
status: current
research_question: "{full question}"
perspectives: [{agents used}]
depth: {depth}
decision: pending
---

# {Research Question Title}

## Executive Summary
[3-5 sentences: question, key finding, recommendation, confidence level]

## Research Question
[Full question with context — why this matters to the project]

## Project Context
[Condensed PROJECT_CONTEXT — existing architecture relevant to this question]

## Landscape
[From research-explorer: categories, option map, notable findings]

## Architecture Fit
[From research-architect: evaluation matrix, per-option integration analysis]

## Risks and Concerns
[From research-critic: risk register, per-option red flags, showstoppers]

## Cost Analysis
[From research-cost: cost comparison, TCO, build vs buy, breakeven]

## Precedent and Evidence
[From research-precedent: evidence summary, case studies, community health]

## Comparison Matrix
[Synthesized from all agents — options vs weighted criteria]

| Criterion | Weight | Option A | Option B | Option C |
|-----------|--------|----------|----------|----------|
| Stack compatibility | 25% | ... | ... | ... |
| Implementation effort | 20% | ... | ... | ... |
| Risk profile | 20% | ... | ... | ... |
| Cost (18-month) | 15% | ... | ... | ... |
| Production evidence | 10% | ... | ... | ... |
| Community health | 10% | ... | ... | ... |

## Recommendation
[Synthesized: which option to pursue, with rationale referencing all 5 perspectives]

## Open Questions
[Unresolved questions that need further investigation or user decision]

## Decision Trail
[Link to ADR if decision is made, otherwise "Pending — feeds into ADR-NNN"]

## Sources
[All URLs from all agents, organized by section, with access date]
```

### Synthesis Guidelines

- **Resolve contradictions** — if the explorer is bullish on an option but the critic found showstoppers, note both and take the conservative position
- **Weight evidence tiers** — a T1 production case study outweighs a T4 vendor claim
- **Highlight consensus** — when 3+ agents agree on something, it's a strong signal
- **Flag minority dissent** — when one agent disagrees with the majority, note it explicitly
- **Assign confidence** — High (strong evidence, expert consensus), Medium (mixed signals), Low (limited evidence)
- **Escalate business decisions** — when agents disagree on high-stakes items (migration cost vs speed, build vs adopt), frame it as a user decision, not a synthesis. Write: "Experts disagree on X — [explorer rationale] vs [critic rationale]. This is a business/team decision."

### Evidence Tie-Back Matrix

Add this section to the report after the Comparison Matrix. For each
recommendation, show which agents and sources support or oppose it:

```markdown
## Evidence Tie-Back

| Recommendation | Supporting Agents | Opposing Agents | Key Sources | Confidence |
|----------------|-------------------|-----------------|-------------|------------|
| Adopt library X | explorer, precedent, architect | critic (maintenance risk) | [URLs] | High |
| Build custom Y | architect, cost | explorer (alternatives exist) | [URLs] | Medium |
```

This makes it easy to see if a recommendation relies on a single perspective or
has broad support. Recommendations backed by only one agent should be flagged.

## Phase 5.5: Adversary Challenge (standard and deep only)

At `standard` depth, run 1 round. At `deep` depth, run all 3 rounds.
Skip entirely at `quick` depth.

Spawn an adversary agent to challenge the synthesis:

**Round 1 — Challenge technical assumptions:**
- "Is the recommended library actually maintained? Check last 6 months of commits."
- "What migration cost are you not accounting for?"
- "Does the integration effort assume ideal conditions?"

**Round 2 — Stress-test the recommendation (deep only):**
- "What happens when this dependency breaks on upgrade?"
- "Show a production deployment at comparable scale."
- "What's the fallback if adoption fails midway?"

**Round 3 — Defend or revise (deep only):**
- Synthesizer responds to all challenges
- Revise recommendations where the adversary raised valid concerns
- Note unresolved debates in the Open Questions section

Update the report's Recommendation and Open Questions sections with adversary
findings. Do not remove the adversary's concerns even if the defense is strong.

## Phase 6: Handoff

Present the user with:

```
## Research Complete: {Topic}

**Report**: docs/research/{topic-slug}.md
**Recommendation**: {one-sentence recommendation}
**Confidence**: {High/Medium/Low}

### Suggested Next Steps
- [ ] {Recommended action — e.g., "Write ADR-003 based on this research"}
- [ ] {Alternative — e.g., "Run /research --depth deep on narrowed question"}
- [ ] {If applicable — "Proceed to /feature-spec for implementation"}
```

## Error Handling

- If an agent fails or times out, note it in the report: "[Perspective] agent did not return findings — this section is incomplete"
- If WebSearch returns no results for a query, the agent should note the gap rather than inventing findings
- If `.acm_graph.json` does not exist, skip Phase 2a and note "Graph context unavailable" in PROJECT_CONTEXT
- If `--perspectives` is invalid, default to all five agents
