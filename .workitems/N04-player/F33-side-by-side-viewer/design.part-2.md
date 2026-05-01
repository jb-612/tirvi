---
feature_id: N04/F33
part: 2-of-2
continued_from: design.md
---

# Feature Design (Part 2): N04/F33 — HLD Deviations, Risks, Out of Scope

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Player panel layout | HLD §3.1 implies single-pane player; this adds two side panels | Admin review + feedback workflow required before MVP |
| `output/` directory | Not in HLD §5.2 storage model | Local-only audit artifact path; production uses GCS; no cloud topology impact |
| Feedback in player | F47 was scoped to N05; folded forward | Feedback must be available where the admin listens, not in a separate tool |

## Risks

| Risk | Mitigation |
|------|-----------|
| HTTP POST not supported by `python -m http.server` | Demo server already wraps `SimpleHTTPRequestHandler`; add `do_POST /feedback` in `scripts/run_demo.py` |
| Audit sink doubles pipeline runtime | Sink is `--review` only; default runs unchanged |
| Auth gate not in place | ADR-036 documents the constraint; portal is localhost-only until auth NFR ships |
| `markId` path injection | Validated against `[a-zA-Z0-9-]+` regex before use in filename (T-05) |

## Out of Scope

- Multi-run comparison diff view (DE-07 deferred to v0.1).
- Server-side feedback aggregation (N05/F47 residual scope).
- Edit-and-replay (modify diacritization in-place and re-run TTS).
- WCAG audit of the new panels — F38 owns formal a11y review.
- Authentication / authorization — ADR-036 deferred NFR.

## Diagrams

- `docs/diagrams/N04/F33/review-portal-layout.mmd` — component layout
- `docs/diagrams/N04/F33/annotation-flow.mmd` — admin annotation sequence
