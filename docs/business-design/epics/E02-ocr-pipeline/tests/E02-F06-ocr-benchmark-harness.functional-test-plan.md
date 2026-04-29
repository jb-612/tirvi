# E02-F06 — OCR Benchmark Harness: Functional Test Plan

## Scope
Verifies `tirvi-bench run` returns deterministic per-page metrics and gates
PRs on regression.

## Source User Stories
- E02-F06-S01 per-adapter WER + block-recall — Critical
- E02-F06-S02 regression block — Critical

## Functional Objects Under Test
- Benchmark harness CLI
- Baseline store (last-green main run)
- Metrics report (JSON + markdown)

## Test Scenarios
- **FT-088** Run on 20-page tirvi-bench v0 → WER + recall per adapter. Critical.
- **FT-089** Two runs → identical results. High.
- **FT-090** Regression > 0.5% WER → CI fails. Critical.
- **FT-091** Block-recall drop > 2% → CI fails. Critical.
- **FT-092** `--with-paid` flag controls Document AI inclusion. High.
- **FT-093** 3-run median absorbs noise. Medium.

## Negative Tests
- Bench fixtures missing → fail-fast with actionable error.
- Adapter timeout → result tagged; not nan.

## Boundary Tests
- Single bench page; full 20-page set.
- Adapter with no Hebrew model → adapter skipped with reason.

## Permission and Role Tests
- Bench fixtures readable; ground truth not modifiable except via PR.

## Integration Tests
- Bench ↔ E10-F02 quality dashboard; ↔ E00-F04 CI gates.

## Audit and Traceability Tests
- Each run stamped with adapter version, fixture version, baseline ref.

## Regression Risks
- Bench fixture provenance drifts; nightly hash check.

## Open Questions
- Statistical significance threshold formalization.
