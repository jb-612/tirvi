---
name: pdf-export
description: Generate PDF from Markdown with Mermaid diagrams. Pre-renders Mermaid to SVG, manages page breaks, converts via md-to-pdf.
argument-hint: "[source.md]"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

Generate PDF from Markdown source $ARGUMENTS:

## When to Use

- Converting a Markdown document to a professional PDF
- The source contains Mermaid diagrams that must render as images
- Generating printable documentation, tutorials, or reports

## When NOT to Use

- Creating or editing Mermaid diagrams → use `@diagram-builder`
- Creating or updating docs in `docs/` → use `@documentation`

## Prerequisites

```bash
mmdc --version          # Mermaid CLI
npx md-to-pdf --version # md-to-pdf converter
python3 --version       # Python 3 for render script
pdftoppm -v             # Poppler utils for visual audit
```

## Step 1: Prepare Source

1. Verify YAML frontmatter with `pdf_options`
2. Check for page breaks
3. Scan for duplicate consecutive page breaks

## Step 2: Validate Mermaid

For every mermaid block:
1. No `block-beta` syntax (unsupported)
2. No `graph TD` chains with 5+ vertical nodes
3. Test-render each diagram:

```bash
echo '<diagram-code>' > /tmp/test.mmd && mmdc -i /tmp/test.mmd -o /tmp/test.svg --quiet
```

## Step 3: Pre-Render Mermaid

```bash
python3 .claude/skills/pdf-export/scripts/render-mermaid.py <source.md> <rendered.md>
```

## Step 4: Generate PDF

```bash
NODE_OPTIONS="--max-old-space-size=4096" npx md-to-pdf <rendered.md>
```

## Step 5: Visual Audit

```bash
pdftoppm -png -r 150 -l 5 <output.pdf> /tmp/pdf-audit
```

## Step 6: Clean Up

```bash
rm <rendered.md>
```

## Cross-References

- `@diagram-builder` — Create/edit Mermaid diagrams first
- `@documentation` — Create/update docs in `docs/`
