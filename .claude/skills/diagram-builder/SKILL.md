---
name: diagram-builder
description: Creates and updates Mermaid diagrams for architecture, workflows, and data flows. Auto-invoked during planning for architecture diagrams.
argument-hint: "[diagram-type or feature-id]"
---

Create or update Mermaid diagram for $ARGUMENTS:

## Auto-Invocation Triggers

This skill is automatically invoked when:
- **Design pipeline creates design.md** — Generate architecture diagram
- **New graph layer or component added** — Update component diagram
- **Workflow changes** — Update workflow diagram

## Step 1: Understand Context

Before creating a diagram:
- Read relevant source files to understand the feature/component
- Identify components, relationships, and data flows
- Check existing diagrams in `docs/diagrams/` for consistency
- Review design.md for architectural decisions

## Step 2: Select Diagram Type

| Type | Use For | Example |
|------|---------|---------|
| `flowchart` | Workflows, processes, decision trees | Ingestion pipeline, query flows |
| `sequenceDiagram` | Interactions, API flows | Agent communication, CLI commands |
| `classDiagram` | Component relationships, interfaces | Schema types, backend interface |
| `stateDiagram` | State machines, lifecycle | Graph build lifecycle |

## Step 3: Generate Diagram

Follow conventions:
- Use subgraphs to group related components
- Add class definitions for consistent styling
- Include descriptive labels on connections

## Step 4: Save Diagram

```bash
docs/diagrams/{name}.mmd
```

Naming: kebab-case, descriptive: `ingestion-pipeline.mmd`, `schema-hierarchy.mmd`

## Step 5: Update References

- Update `design.md` to reference the diagram
- Update `docs/diagrams/README.md` index

## Cross-References

- `@design-pipeline` — Invokes this skill at Stage 4
- `@pdf-export` — Converts diagrams to PDF
