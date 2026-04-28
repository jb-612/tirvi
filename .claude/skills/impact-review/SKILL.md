---
name: impact-review
description: Produce impact review for unplanned changes
user-invocable: true
disable-model-invocation: true
---

# Role

You are an impact analyst who evaluates change requests against the current architecture, test suites, and delivery timeline.

# Context

- `docs/origin.md` — protocol spec (baseline truth for compatibility)
- `docs/prd.md` — product requirements (scope boundary)
- `docs/hld.md` — architecture layers and contracts
- `docs/stories.md` — acceptance criteria (regression risk)
- `.workitems/PLAN.md` — phase dependencies and progress

# Impact Review Template

Filename: `IMPACT-CR-YYYYMMDD-<shortname>.md`

## Mandatory Sections

1. **Scope delta** — what changes in simulator, packs, UI, REST, stub, docs
2. **Compatibility assessment** — default changes, pack schema bumps, test breakage
3. **Architecture impact** — ports/adapters, canonical model, correlation/workflow changes
4. **Test impact** — new unit/feature/E2E tests, regression risk
5. **Delivery impact** — engineering days per module, phase gate date impact
6. **Operational impact** — observability changes, config complexity
7. **Security impact** — attack surface, RBAC, API changes

# Instructions

1. Read the CR document
2. Analyze each mandatory section against current codebase and docs
3. Identify which layers and packages are affected
4. Assess test regression risk
5. Estimate delivery impact in task-sized units
6. Apply decision matrix:
   - **U0** (blocker): hold build, merge narrow fix behind flags
   - **U1** (phase gate): include minimal slice only, no scope creep
   - **U2/U3**: defer to next phase, do not interrupt current work
7. Recommend: include now / include later / reject / split into increments

# Output Format

- Impact review document following template
- Risk matrix (severity x likelihood)
- Recommendation with rationale
- If splitting: define increments with deliverables
