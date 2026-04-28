---
name: design-evolution
description: Visualise the chain-of-thought of a design-pipeline run as light Mermaid diagrams. Reads a feature workitem's meeting-room + review-r1/r2/r3 markdown and emits 6 views (review DAG, meeting-room convergence, finding timelines, graveyard of overruled claims, traceability web, summary). Use after a design-pipeline run, or to retrofit a chain-of-thought view onto an existing feature.
argument-hint: "<workitem_dir>"
allowed-tools: Read, Glob, Bash, Write
---

Visualise the chain-of-thought of a design-pipeline run for $ARGUMENTS.

## When to Use

- After `@design-pipeline` produces a feature workitem with reviews
- To retrofit a visual record onto an existing workitem (e.g.
  `.workitems/N05/F05-page-migration/`)
- Before a code-review to share a one-glance picture of which claims
  survived adversary debate, which were overruled, and how findings
  cascaded into final tasks

## When NOT to Use

- For workitems with no `review-r{1,2,3}/` directories (skill emits
  empty placeholder views — not useful)
- To generate forward-looking architecture diagrams → use
  `@diagram-builder`
- To produce a PDF from existing Mermaid → use `@pdf-export`

## Output

Seven files written to `<workitem_dir>/cot-evolution/`:

| File | Type | Purpose |
|---|---|---|
| `00-summary.md` | markdown | Stats + view index |
| `01-meeting-room.mmd` | flowchart | 3-specialist (Product/Technical/Domain) convergence |
| `02-review-dag.mmd` | flowchart | R1 → R2 → R3 DAG, severity-coloured |
| `03-finding-timelines.mmd` | flowchart | Per-finding severity evolution |
| `04-graveyard.mmd` | flowchart | Overruled / killed claims with verification source |
| `05-traceability.mmd` | flowchart | Findings ↔ DE/AC/T/F/US citation web |
| `06-ideation-mindmap.mmd` | **mindmap** | Native Mermaid mindmap — bubbles from root → stages → categories → leaves, shows the ideation process maturing from high level to detail |
| `cot.json` | json | Raw extracted model (cached for re-render) |

Two Mermaid dialects are used deliberately. `flowchart` covers views 1–5
because it supports severity `classDef` colouring, edge labels
(`-.challenged.->`, `==upheld==>`), and round subgraphs. `mindmap` covers
view 6 because it produces true bubble-and-line ideation trees that show
how the discussion matured from a single root idea down to individual
specialist findings — at the cost of no colours or edge labels. The two
formats complement each other: use view 6 for one-glance "what was the
shape of the conversation?" and view 2 for "which claims survived?".

## Step 1: Verify Prerequisites

```bash
test -d "<workitem_dir>/meeting-room" || echo "WARN: no meeting-room/"
test -d "<workitem_dir>/review-r1"     || echo "WARN: no review-r1/"
python3 -c "import yaml" || echo "ERR: install pyyaml"
```

`pyyaml` is already in `pyproject.toml`. Python 3.11+ stdlib only otherwise.

## Step 2: Parse → cot.json

```bash
mkdir -p <workitem_dir>/cot-evolution
python3 .claude/skills/design-evolution/scripts/parse_design_pipeline.py \
  <workitem_dir> > <workitem_dir>/cot-evolution/cot.json
```

The parser walks `meeting-room/`, `review-r{1,2,3}/`, and root `design.md`,
then emits a JSON model with `findings`, `challenges`, `rebuttal_outcomes`,
`graveyard`, `meeting_room`, and `traceability` sections. Files that don't
match any expected prefix are silently skipped.

## Step 3: Render → Mermaid + Summary

```bash
python3 .claude/skills/design-evolution/scripts/render_mindmap.py \
  <workitem_dir>/cot-evolution/cot.json \
  --out <workitem_dir>/cot-evolution/
```

Six files are written. Open any `.mmd` in VS Code Mermaid preview, or
pipe `00-summary.md` through `@pdf-export` for a printable bundle.

## Step 4: Sanity Check

For a freshly-rendered output, eyeball:
- `02-review-dag.mmd` — should show one node per finding/challenge,
  coloured by severity, grouped into R1/R2/R3 subgraphs
- `04-graveyard.mmd` — should list claims that were debunked with
  `factually wrong` / `verified:` language in the source markdown
- `00-summary.md` — finding counts table should match a manual
  `grep -c '^### F' review-r1/*.md` spot check

If any view is empty or wrong, re-read the source markdown — the parser
is regex-based and lenient, so the most likely cause is a non-standard
heading or filename.

## Cross-References

- `@diagram-builder` — forward architecture diagrams (different concern)
- `@pdf-export` — bundles `00-summary.md` + the 5 `.mmd` files into a PDF
- `@design-pipeline` — produces the workitem this skill consumes

## Implementation Notes

- Parser at `scripts/parse_design_pipeline.py` (CC ≤ 5 per function)
- Renderer at `scripts/render_mindmap.py` (CC ≤ 5 per function)
- Tests at `tests/skills/design_evolution/` — `pytest tests/skills/design_evolution/`
- Designed for the file naming used by `@design-pipeline` outputs;
  non-standard layouts may need parser tweaks
