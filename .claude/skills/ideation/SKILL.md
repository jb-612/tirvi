---
name: ideation
description: Produce a short idea memo for later research or design. Lightweight front door — no review ceremony, no design pipeline. Use when the user wants to capture a thought, not commit to building anything yet.
argument-hint: "[topic or one-line idea]"
disable-model-invocation: false
---

Capture idea $ARGUMENTS as a short memo.

## When to Use

- User has a thought they want recorded before forgetting it
- Pre-research phase — not yet worth `@research` or `@deep-research`
- Pre-concept phase — not yet committed to an HLD/PRD
- Routing unclear — "I'm not sure if this is a feature or a rethink of something"

## When NOT to Use

- Bug fix / hotfix — use `@hotfix`
- Deep technical/business question with existing signals — use `@research` or `@deep-research`
- Ready to produce HLD/PRD — use `@concept` (Phase B) or `@design-pipeline`
- Info-only question with no intent to build — use `@general-question`

## Instructions

### Step 1: Write a 1-page memo

Produce `.workitems/ideas/{YYYY-MM-DD}-{slug}.md` with this shape:

```markdown
---
title: {one-line title}
created: {YYYY-MM-DD}
status: raw
next: [research|concept|design|defer]
---

## Idea
{2–4 sentences — the thought itself}

## Why now
{1–2 sentences — what prompted this, what would change if this existed}

## Open questions
- {question 1}
- {question 2}

## Suggested next step
{routing — see below}
```

Keep it under 40 lines. No design, no tasks, no tests. If the idea demands more structure, it belongs in `@concept` or `@design-pipeline`, not here.

### Step 2: Suggest routing

Based on the memo, recommend one of:

| Suggested next | When |
|---|---|
| `@research` | Needs external facts / tech comparison / precedent scan |
| `@deep-research` | Needs multi-source deep dive (business + technical) |
| `@concept` | Clear enough to draft HLD + PRD — user ready for a structured interview |
| `@design-pipeline` | Large enough to warrant the full 11-stage design |
| `defer` | Not actionable yet — memo filed, revisit later |

Set the `next:` field in the memo frontmatter accordingly.

### Step 3: Hand off or stop

- If `next: defer` — stop. The memo is filed at `.workitems/ideas/`.
- Otherwise — offer to invoke the recommended next skill immediately. User confirms or declines; either way, the memo stays as the trail.

## No Review Ceremony

Ideation memos are single-author artifacts with no review gate. They are not production collateral — they are seeds. If an idea survives to `@concept` or `@design-pipeline`, those skills apply their own review rounds to the HLD/PRD/design that follows.

## Cross-References

- `@research` / `@deep-research` — next step when idea needs facts
- `@concept` — next step when idea is ready for structured HLD/PRD interview (Phase B)
- `@design-pipeline` — next step for full 11-stage design
- `@general-question` — if user decides this was really just a question, not an idea
