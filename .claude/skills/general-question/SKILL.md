---
name: general-question
description: Info-only answer lane. No artifact, no review, no design. Use for questions where the user wants information and does not intend to build or change anything yet. Offers an opt-in to save the exchange as an idea for @ideation.
argument-hint: "[the question]"
disable-model-invocation: false
---

Answer question $ARGUMENTS directly.

## When to Use

- "How does X work?"
- "What does Y do?"
- "Should I use A or B?"
- "Is this pattern common?"
- User wants to learn, not to commit to building anything

## When NOT to Use

- User wants to capture a new idea → `@ideation`
- User wants structured research across multiple sources → `@research` / `@deep-research`
- User wants to fix a bug → `@hotfix`
- User wants to modify existing behavior or add new behavior → `@design-pipeline`

## Instructions

### Step 1: Answer

Answer concisely. Use existing codebase / docs if relevant. Cite files with `path:line` so the user can navigate.

Do NOT:
- Produce a `.workitems/` artifact
- Produce an HLD / PRD / ADR
- Invoke `@code-review`, `@design-review`, or any review skill
- Run tests or gates

The entire ceremony is: read enough context to answer well, then answer.

### Step 2: Opt-in save

At the end of the answer, ask **once**:

> *Save this as an idea for `@ideation`?* (y/N)

- On **yes**: produce a minimal memo stub at `.workitems/ideas/{YYYY-MM-DD}-{slug}.md` containing:
  - `title:` the question
  - `Idea:` the answer's key takeaway (1–3 sentences)
  - `Open questions:` any follow-ups surfaced during the answer
  - `next: defer` — user can revisit later via `@ideation`
  
  Then hand off to `@ideation` for routing (or leave deferred).

- On **no** (default): nothing persists. The exchange exists only in the conversation transcript.

### Step 3: Stop

No further actions. No design, no tests, no commits.

## No Review Ceremony

General-question answers are **not reviewed**. They are conversational, not production collateral. If the user later decides the answer should shape a design, they invoke `@ideation` → `@concept` → `@design-pipeline`; review happens there, not here.

## Honest Asymmetry

Not every artifact needs review. Questions that produce no artifact definitionally need no review. This skill exists so the harness does not force a review gate onto a conversation that has nothing to gate.

## Cross-References

- `@ideation` — save-as-idea opt-in target
- `@research` / `@deep-research` — escalate if the question needs multi-source investigation
- `@documentation-lookup` — specific library / framework doc lookup
