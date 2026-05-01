---
feature_id: N02/F25
feature_type: domain
status: designed
hld_refs:
  - HLD-§5.2/Processing
prd_refs:
  - "PRD §6.3 — Hebrew NLP"
adr_refs: []
biz_corpus: true
biz_corpus_e_id: E03-F05
---

# Feature: Content Reading Templates (Math + Table) — Deferred MVP

## Overview

SSML reading templates for structured content: math expressions (Hebrew-localized
number/operator templates) and table cells (header-row reading policy). **POC scope:
deferred** per PLAN-POC.md. Economy.pdf may contain numbers but the POC reads them
as plain text via Wavenet's built-in TTS normalization. Full math/table template
engine is MVP scope (requires pattern detector in F14/normalization and dedicated
template library).

## Dependencies

- Upstream: N02/F14 (math region flags in NormalizedText), N02/F22 (ReadingPlan block type).
- Downstream: N02/F23 (SSML shaping reads template output), N03 TTS.
- External services: none.

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| tirvi.templates | apply_content_template(block: PlanBlock) -> PlanBlock | function | POC: identity passthrough; MVP: math/table branch |
| tirvi.templates | TEMPLATES_ENABLED | bool constant | POC: False; env TIRVI_TEMPLATES |

## Approach

1. DE-01: Template gate — TEMPLATES_ENABLED env flag; POC: False; identity passthrough.
2. DE-02 (MVP): Math template — regex pattern match for digit sequences, operators;
   emit Hebrew-localized spoken form (e.g., "3.5%" -> "שלוש נקודה חמש אחוז").
3. DE-03 (MVP): Table template — emit header label before each cell ("עמודה: ...").

## Design Elements

- DE-01: contentTemplateGate (ref: HLD-§5.2/Processing)
- DE-02: mathReadingTemplate (ref: HLD-§5.2/Processing) [MVP only]
- DE-03: tableReadingTemplate (ref: HLD-§5.2/Processing) [MVP only]

## Decisions

No ADR required — stub; full design deferred to MVP.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Math SSML template | Not implemented in POC | POC relies on Wavenet built-in TTS normalization for numbers; deferred per PLAN-POC.md |
| Table reading template | Not implemented in POC | Table detection in F14 is post-POC |

## HLD Open Questions

- Hebrew math vocabulary coverage (LaTeX-light vs plain) -> MVP design.
- Hebrew number gender agreement in templates -> complex; MVP.

## Risks

| Risk | Mitigation |
|------|-----------|
| Wavenet mispronounces percentages or fractions | Known limitation in POC; documented; N05 quality bench tracks |

## Diagrams

None required for stub.

## Out of Scope (POC)

- Math expression detection and template application.
- Table cell header reading templates.
- All FTs in F25 functional-test-plan.md — deferred MVP.
