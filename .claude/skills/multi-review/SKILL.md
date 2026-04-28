---
name: multi-review
description: Launch parallel AI code reviews with multiple reviewers, then synthesize results.
argument-hint: "[scope or file-path]"
---

# Multi-Review: Parallel AI Code Review

Launch multiple parallel reviewers, then synthesize results.

## Step 1: Determine Parameters

Parse `$ARGUMENTS` for scope.

## Step 2: Launch Reviews

Launch 3+ reviewer agents in parallel, each focused on a different aspect:
- Architecture compliance (project patterns, interface adherence)
- Code quality + security (OWASP, complexity, naming)
- Test coverage (gaps, quality, isolation)

## Step 3: Synthesize Results

After all reviewers complete:
1. **Deduplicate findings** — merge overlapping issues, keep highest severity
2. **Categorize** — Critical, High, Medium, Low, Info
3. **Cross-reference** — note reviewer consensus (higher confidence)
4. **Summarize** — overall assessment

Write synthesis with:

```markdown
## Executive Summary

## Critical & High Findings

## Medium Findings

## Low & Informational

## Reviewer Agreement Matrix

## Statistics
- Total unique findings: N
- By severity: CRITICAL: N, HIGH: N, MEDIUM: N, LOW: N
```

## Step 4: Create Issues (Optional)

Create tracking issues for Critical/High findings as needed.

## Cross-References

- `@code-review` — Standard 2-phase review
- `@security-review` — Security-focused review
