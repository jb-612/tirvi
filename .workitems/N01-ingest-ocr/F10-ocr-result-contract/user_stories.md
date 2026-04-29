<!-- DERIVED FROM docs/business-design/epics/E02-ocr-pipeline/stories/E02-F03-ocr-result-contract.stories.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T20:36:51Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E02-F03 — `OCRResult` Contract With BBoxes + Confidence + Lang Hints

## Source Basis
- HLD: §4 Adapter interfaces; §3.3 Worker pipeline
- Research: src-003 §3 architecture change #4 (rich result objects)
- Assumptions: none new

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P08 Backend Dev | consumes OCR | bbox + conf + lang | bytes-only ports lose detail | rich result type |
| P10 Test Author | seeds fixtures | realistic OCRResults | hand-coding bboxes | fixture builder |
| P11 SDK Maintainer | guards port shape | schema stability | adapter drift | versioned schema |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: SDK maintainer.
3. System actors: OCR adapters, downstream normalization (E03), block detector (E02-F04).
4. Approvals: schema bump → ADR slot.
5. Handoff: `OCRResult` to normalization.
6. Failure recovery: schema-validation error reports field name + adapter.

## Behavioural Model
- Hesitation: dev unsure whether to add a field; reviews schema.
- Rework: dev returns flat string; reviewer rejects.
- Partial info: provider can't fill `lang_hint`; nullable.
- Abandoned flow: dev half-implements result shape; CI contract test fails.

---

## User Stories

### Story 1: `OCRResult` schema is the contract between adapters and consumers

**As a** SDK maintainer
**I want** `OCRResult` to declare bboxes, confidence, lang hints, and per-word metadata
**So that** every downstream stage has the data it needs without provider knowledge.

#### Preconditions
- Adapter port definition documented.

#### Main Flow
1. `OCRResult` schema defined: `pages[]`, each with `words[]` (`text`, `bbox`, `conf`, `lang_hint`), `lang_hints[]` (page-level), `provider`.
2. Schema versioned (`v1`).
3. Adapter contract test runs against schema.

#### Edge Cases
- Provider gives only text without bbox: adapter returns `bbox=null` + downgrade flag.
- Provider gives multi-resolution bboxes; adapter scales to 1× page.

#### Acceptance Criteria
```gherkin
Given a Tesseract adapter and a Document AI adapter
When both run on the same page
Then both return an `OCRResult` matching the v1 schema
And only `provider` and `confidence` differ in shape
```

#### Data and Business Objects
- `OCRResult`, `OCRPage`, `OCRWord`, `BBox` (x, y, w, h, units).

#### Dependencies
- DEP-INT to E00-F03 (port definitions), E02-F01/F02 (adapters).

#### Non-Functional Considerations
- Portability: zero vendor SDK leakage.
- Testability: fixture builder.

#### Open Questions
- Should we include OCR engine version per page for reproducibility?

---

### Story 2: Fixture builder seeds deterministic test data

**As a** test author
**I want** a fixture builder that produces realistic `OCRResult` instances
**So that** functional tests across stages are deterministic.

#### Preconditions
- Schema v1 finalized.

#### Main Flow
1. Library `tirvi-fixtures` exports `OCRResult.builder()`.
2. Builder accepts a YAML / JSON template; emits valid result.
3. Used by E03 / E04 / E05 / E06 functional tests.

#### Edge Cases
- Builder with missing required field; raises typed error.
- Builder with deprecated fields; warning emitted.

#### Acceptance Criteria
```gherkin
Given a fixture template for a 2-column Hebrew page
When `OCRResult.builder().from_template(t)` runs
Then the resulting object passes schema validation
And contains 2 columns with words in RTL order
```

#### Dependencies
- DEP-INT to E00-F03 fakes (registry consumes the same builder).

#### Non-Functional Considerations
- Reliability: deterministic across CI runs.
- DX: builder API is fluent (not procedural).

#### Open Questions
- Builder reads YAML or DSL? Pick one.
