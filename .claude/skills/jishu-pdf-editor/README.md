# Jishu PDF Editor — Skill bundle

A persona-skill for turning raw Markdown + Mermaid into a print-ready,
editorially-reviewed A4 PDF in the Jishu visual system.

## What's inside

```
jishu-pdf-editor/
├─ SKILL.md                     # The persona, workflow, and rulebook
├─ README.md                    # You are here
├─ brand/
│  ├─ colors_and_type.css       # Brand tokens (paper / ink / clay / fonts)
│  └─ pdf-options.json          # Puppeteer header/footer template
└─ scripts/
   ├─ render-mermaid.py         # Pre-render .mmd → .svg
   └─ md-to-pdf.js              # Puppeteer md → pdf
```

## Quick start

1. Drop the folder into your skills directory.
2. Place your source `.md` and `brand/` assets next to it.
3. Invoke the skill: it will run Phases 0–5 (brand intake, content
   organisation, diagram pre-rendering, pagination, editorial review,
   finalize-for-print) and emit `dist/<doc>.pdf` plus the
   intermediate HTML preview.

## Imports / dependencies

- `mermaid-cli` (`mmdc`) — `npm i -g @mermaid-js/mermaid-cli`
- `puppeteer` — `npm i puppeteer`
- Optional: `skills/pdf-export` and `skills/diagram-builder` siblings
  if you have them; the skill defers to them when present.

## Workflow (one-line)

`brand intake → content organise → diagram pre-render → paginate → review (editorial / style / language) → finalize`

See `SKILL.md` for the rulebook, anti-patterns, and the deliverable
checklist.
