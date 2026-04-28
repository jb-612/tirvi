---
name: reverse-prd
description: Reverse-engineer a Product Requirements Document from an existing codebase. Reconstructs product vision, personas, user stories, and business processes by analyzing code structure (ACM), runtime behavior (Sweep), and domain context. Part of the Brownfield Refactoring Toolkit.
argument-hint: "<project-root or sweep-output-dir>"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
---

# Reverse PRD — Reconstruct Product Intent from Code

Reverse-engineer the product requirements for the codebase at `$ARGUMENTS`.

## Purpose

In brownfield projects, the original PRD is missing, outdated, or was never
written. This skill reconstructs:

- **What the product was supposed to do** (vision, goals)
- **Who it was built for** (personas)
- **What workflows it supports** (business processes)
- **What each feature does and why** (user stories)
- **What's incomplete or divergent** (gaps between intent and implementation)

This becomes the baseline for characterization testing — tests can validate
both *code behavior* (what it does) and *product intent* (what it should do).

## Prerequisites

- ACM ingested for the target project (`acm ingest` completed)
- Runtime Sweep output exists (optional but strongly recommended)
- Behavioral spec exists (optional — from sweep-analytics skill)

## Input Sources

The skill reads from multiple evidence layers, weighted by reliability:

| Source | Weight | What it reveals |
|--------|--------|-----------------|
| **Code structure** (ACM graph) | High | Modules, functions, classes, dependencies — the "what exists" |
| **Runtime behavior** (Sweep JSON) | High | API endpoints, UI pages, interaction patterns — the "what runs" |
| **Behavioral spec** (if exists) | High | Endpoint→code mapping, shared dependencies |
| **Domain docs** (Core/, Brain/) | Medium | Goals, projects, constraints, relationships — the "why" |
| **Config files** (YAML, JSON) | Medium | Feature flags, enabled capabilities, integration points |
| **UI structure** (screenshots, a11y) | Medium | User-facing features, navigation, information architecture |
| **Commit history** | Low | Feature evolution, what was added when |
| **Code comments/docstrings** | Low | Developer intent (often stale) |

## Workflow

### Step 1: Gather Evidence

Read all available sources. For each, extract intent signals:

```
# ACM — what exists structurally
acm stats                    → layer distribution, coverage
acm search "" --layer code   → all modules and classes
acm communities              → natural feature clusters

# Sweep — what runs
Read sweep-result.json       → pages, elements, API catalog
Read behavioral-spec.md      → endpoint→code mapping

# Domain context
Read Core/01_OHAD_CURRENT_GOALS.md
Read Core/06_OHAD_PROJECTS_AND_OPPORTUNITIES.md
Read Core/02_OHAD_WORK_CONTEXT.md
Scan Brain/ for relevant notes
```

### Step 2: Identify Product Boundaries

From the evidence, determine:

1. **What is this product?** — One-sentence definition
2. **Who are the users?** — Primary, secondary, system users
3. **What problem does it solve?** — The pain point it addresses
4. **What are the major feature areas?** — Group by ACM communities or UI pages

### Step 3: Reconstruct Personas

For each identified user type, write:

```markdown
### Persona: [Name]
- **Role:** [What they do]
- **Goals:** [What they want to achieve]
- **Evidence:** [How we know this persona exists — UI pages, API patterns, config]
- **Key workflows:** [What they do in the system]
```

Evidence sources:
- UI pages with distinct interaction patterns → different personas
- API endpoints that serve different data shapes → different consumers
- Config files with role-based settings → explicit persona support
- Domain docs mentioning user types

### Step 4: Reconstruct Feature Map

For each major feature area (from ACM communities + UI pages):

```markdown
### Feature: [Name]
- **What it does:** [Observable behavior from sweep + code]
- **Why it exists:** [Inferred intent from domain docs + code context]
- **UI surface:** [Pages, elements, interactions]
- **API surface:** [Endpoints, data shapes]
- **Data surface:** [DB tables, state files]
- **Dependencies:** [Other features it relies on]
- **Completeness:** [Fully built / Partially built / Stubbed]
```

### Step 5: Write User Stories

For each feature, reconstruct user stories:

```markdown
**US-001:** As a [persona], I want to [action], so that [benefit].

**Acceptance criteria:**
- Given [context], when [action], then [result]
- Evidence: [sweep observation or code path that proves this works]

**Status:** Implemented / Partially implemented / Broken / Missing
**Code path:** [ACM node IDs for the implementing functions]
```

Mark each story with its evidence source:
- `[OBSERVED]` — seen in sweep runtime data
- `[INFERRED]` — deduced from code structure + domain context
- `[DOCUMENTED]` — found in existing docs (Core/, Brain/)
- `[MISSING]` — expected from domain context but not found in code

### Step 6: Reconstruct Business Processes

For multi-step workflows (e.g., "agent dispatch cycle", "daily briefing flow"):

```markdown
### Process: [Name]

**Trigger:** [What starts the process]
**Steps:**
1. [Step] → [API/code path] → [outcome]
2. [Step] → [API/code path] → [outcome]
...
**End state:** [What should be true when done]

**Mermaid diagram:**
sequenceDiagram
    participant User
    participant Dashboard
    participant Scheduler
    ...
```

### Step 7: Identify Gaps and Anomalies

Compare intent (from domain docs) with implementation (from code/sweep):

```markdown
### Gap Report

| ID | Intent (from docs) | Implementation (from code) | Status |
|----|-------------------|---------------------------|--------|
| G-001 | "Agents should post FYI messages" | FYI code exists in mailbox | Implemented |
| G-002 | "Cost tracking per agent" | Cost table exists, no UI display | Partial |
| G-003 | "WhatsApp integration" | MCP configured but no UI surface | Stubbed |
```

### Step 8: Write the Reverse PRD Document

Assemble all findings into a single document:

```
docs/research/reverse-prd.md
├── Executive Summary
├── Product Vision & Goals
├── Personas (with evidence)
├── Feature Map (with completeness status)
├── User Stories (grouped by feature, with status tags)
├── Business Process Maps (with Mermaid diagrams)
├── Gap Report (intent vs implementation)
├── Technical Constraints (from code review)
└── Appendix: Evidence Sources
```

## Output Files

| File | Content |
|------|---------|
| `docs/research/reverse-prd.md` | Complete reverse-engineered PRD |
| `docs/diagrams/business-processes.mmd` | Mermaid sequence diagrams for key workflows |
| `docs/diagrams/feature-map.mmd` | Feature area relationship diagram |

## Quality Criteria

The reverse PRD is good when:
- Every feature has at least one user story with evidence tag
- Every user story has a code path (ACM node ID) or is marked MISSING
- Gap report identifies at least 3 intent-vs-implementation divergences
- Business processes cover the top 5 most-used workflows (by sweep frequency)
- Personas are grounded in observable behavior, not speculation

## Integration with Testing

The reverse PRD feeds directly into the `behavioral-testing` skill:
- User stories become test scenarios
- `[OBSERVED]` stories → characterization tests (pin current behavior)
- `[MISSING]` stories → gap tests (document what's not implemented)
- `[INFERRED]` stories → need user validation before testing
- Gap report → prioritized test backlog
