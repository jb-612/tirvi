---
feature_id: N04/F38
feature_type: ui
status: designed
hld_refs:
  - HLD-§3.1/Frontend
prd_refs:
  - "PRD §7.1 — Accessibility"
adr_refs: []
biz_corpus_e_id: E09-F06
gate: deferred_mvp   # not scheduled for POC; activate when MVP accessibility audit begins
---

# Feature: WCAG 2.1 AA Conformance Audit and Remediation

## Overview

F38 is the formal WCAG 2.1 AA accessibility audit and remediation pass
over the entire player surface (N04/F35 + F36 + F33 + F34). It covers
automated audit tooling (axe-core, WAVE, Lighthouse a11y), manual
screen-reader testing (NVDA + Hebrew TTS, VoiceOver), and remediation
of any failures. This feature is **deferred to MVP** — the POC ships a
basic accessibility floor (ARIA labels, focus rings, prefers-reduced-motion)
but no formal audit pipeline.

## Dependencies

- Upstream features: N04/F35, F36, F33, F34 (all player features must be
  implemented before the audit pass).
- Adapter ports consumed: none — audit is a quality gate, not a code feature.
- External services: axe-core (npm), Playwright (browser automation for
  automated audit); NVDA + VoiceOver for manual testing.

## Interfaces

- DE-01: automatedAuditPipeline — axe-core / Playwright runner that
  loads `player/index.html`, executes the audit, and emits a structured
  report of WCAG 2.1 AA violations (ref: HLD-§3.1/Frontend).
- DE-02: remediationTasks — a task breakdown of each violation found in
  DE-01's report, one TDD task per WCAG criterion failure
  (ref: HLD-§3.1/Frontend).

## Approach

TBD — fill via `@design-pipeline` when MVP accessibility audit begins.
Key design questions: which WCAG 2.1 AA success criteria are most at risk
for an RTL Hebrew player (SC 1.3.2 Meaningful Sequence, SC 1.4.3 Contrast
Minimum, SC 2.1.1 Keyboard, SC 4.1.2 Name Role Value); whether the audit
runs as a CI step or a manual gate.

## Design Elements

- DE-01: automatedAuditPipeline (ref: HLD-§3.1/Frontend)
- DE-02: remediationTasks (ref: HLD-§3.1/Frontend)

## Decisions

TBD — pending MVP design cycle.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| WCAG AA audit pipeline | Not in POC scope | HLD §11 explicitly defers formal a11y audit to MVP |

## HLD Open Questions

- CI integration for axe-core — TBD at MVP.
- Hebrew RTL-specific WCAG criteria priority order — TBD.

## Risks

TBD — assessed at MVP design time. Primary risk: Hebrew RTL text direction
(SC 1.3.2) is not tested by standard axe-core rules and requires manual
screen-reader verification.

## Out of Scope

- POC: formal audit entirely deferred (POC ships only basic a11y floor
  from F35-DE-06 and F36-DE-06).
- WCAG AAA compliance — out of scope entirely; AA only.
