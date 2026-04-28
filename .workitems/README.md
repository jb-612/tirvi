# `.workitems/` — Convention Guide

Per-feature design artifacts driven by the SDLC harness. Layout matches the
`require-workitem.sh` and `validate-hld-refs.sh` expectations and the
`design-pipeline` skill flow.

## Layout

```
.workitems/
├── PLAN.md                              # Master index — every F## listed
├── README.md                            # This file
├── templates/                           # Master templates copied per feature
│   ├── design.md
│   ├── user_stories.md
│   ├── tasks.md
│   └── traceability.yaml
├── N00-foundation/                      # Phase folder
│   ├── README.md                        # Phase scope + exit criteria
│   └── F01-docker-compose/              # Feature folder
│       ├── design.md                    # ≤ 120 lines — HLD-driven design
│       ├── user_stories.md              # ≤ 100 lines — PRD-driven stories
│       ├── tasks.md                     # ≤ 120 lines — atomic tasks ≤ 2h each
│       ├── traceability.yaml            # ACM-graph index (no line limit)
│       └── meeting-room/                # 3-agent draft + remarks + synthesis + vote
├── N01-ingest-ocr/
│   └── F05-upload-flow/...
├── N02-hebrew-interpretation/           # The moat
├── N03-audio-sync/
├── N04-player/
└── N05-quality-privacy/
```

## Naming

- **Phases:** `N##-kebab-name` — N00 through N05
- **Features:** `F##-kebab-name` — globally unique F## across all phases
- Feature numbers are assigned in `PLAN.md` and never reused

## Per-feature files

| File | Role | Limit |
|------|------|-------|
| `design.md` | HLD-driven design with named DEs (`DE-NN: name (ref: HLD-X.Y/El)`) | 120 lines |
| `user_stories.md` | PRD-driven stories with PRD refs and acceptance criteria | 100 lines |
| `tasks.md` | Atomic tasks (≤ 2h), each linked to a DE + AC | 120 lines |
| `traceability.yaml` | ACM-graph index (nodes, edges, refs) | none |
| `meeting-room/` | 3-agent drafts + remarks + synthesis + vote (audit trail) | none |

## Workflow

For any feature: run `@design-pipeline F##-name` and the 11-stage pipeline
walks the file from scaffold → design → stories (meeting-room) → review →
tasks → user gate → commit. See `.claude/skills/design-pipeline/SKILL.md`.

The `require-workitem.sh` hook gates production-source writes against the
first unchecked `F##` in `PLAN.md`. Move boxes from `[ ]` to `[x]` only
after the feature ships and its TDD build closes.

## Source references

- Master plan: `PLAN.md`
- Validation research: `docs/research/tirvi-validation-and-mvp-scoping.md`
- PRD: `docs/PRD.md`
- HLD: `docs/HLD.md`
- ADR backlog: `docs/ADR/` (10 queued)
