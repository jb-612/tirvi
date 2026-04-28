---
name: documentation
description: Create, update, classify, and archive docs in docs/. Enforces naming, versioning, folder placement, and lifecycle rules.
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
argument-hint: "[action] [path-or-topic]"
---

Create, update, classify, or archive documentation for $ARGUMENTS:

## When to Use

- Creating a new document in `docs/`
- Updating an existing document
- Archiving a superseded document
- Creating an ADR in `docs/decisions/`

## When NOT to Use

- Creating feature planning artifacts in `.workitems/` -> use `@design-pipeline`
- Creating Mermaid diagrams -> use `@diagram-builder`
- Reviewing design documents -> use `@design-review`

## Document Classification

| Tier | Folder | Purpose |
|------|--------|---------|
| 1 — Architecture | `docs/architecture/` | System design, infrastructure |
| 2 — Decisions | `docs/decisions/` | ADRs |
| 3 — Features | `docs/features/` | Post-ship feature reference |
| 4 — Operations | `docs/operations/` | Runbooks, CLI usage |
| 5 — Research | `docs/research/` | Exploratory, future work |

## Versioning

Every document includes YAML frontmatter:

```yaml
---
tier: 1
version: 1.0
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: current
---
```

## Key Principle: Design Docs != System Docs

| | Design Docs (`.workitems/`) | System Docs (`docs/`) |
|---|---|---|
| **When created** | Before implementation | After implementation |
| **Lifecycle** | Closed when feature ships | Long-lived, versioned |
| **Size** | <= 100 lines per file | No limit |

## Cross-References

- `@design-pipeline` — Owns `.workitems/` planning artifacts
- `@diagram-builder` — Owns `docs/diagrams/`
- `@feature-completion` — Triggers `@documentation` at Step 6
