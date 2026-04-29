# E02-F02 — Document AI Adapter (Paid Fallback)

## Source Basis
- PRD: §9 Constraints, §6.2 Extraction
- HLD: §6 OCR decision (paid alternative behind same port)
- Research: src-003 §2.1 row "Google Document AI"; ADR-004 slot
- Assumptions: ASM06

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P08 Backend Dev | wires Document AI | drop-in replacement | API auth complexity | unified `OCRResult` shape |
| P04 SRE | tracks cost | $1.50/1k pages capped | runaway fallback | per-doc budget guard |
| P01 Student | needs hard-to-OCR page | high-quality result | fallback latency | parallel run keeps total ≤ 30 s p50 |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: SRE budget guard.
3. System actors: Document AI Form Parser / OCR processor; budget guard.
4. Approvals: ADR-004 (OCR primary); budget threshold change (ADR slot).
5. Handoff: `OCRResult` shape identical to Tesseract path.
6. Failure recovery: API throttling → exponential backoff; Document AI quota reached → fail page with typed error.

## Behavioural Model
- Hesitation: dev unsure whether to run Document AI in dev (cost).
- Rework: schema mismatch between Tesseract and Document AI bbox conventions; adapter normalizes.
- Partial info: API rate-limited; backoff transparent to caller.
- Retry: per HLD §3.3 worker retries up to 3×.

---

## User Stories

### Story 1: Drop-in fallback returns identical shape

**As a** backend dev
**I want** Document AI to return the same `OCRResult` shape as Tesseract
**So that** downstream stages do not branch on provider.

#### Preconditions
- Document AI processor configured for Hebrew.
- Service account has `documentai.processor.user`.

#### Main Flow
1. Adapter accepts a single page or full-PDF input.
2. Calls Document AI; maps response to `OCRResult` with `provider="document-ai"`.
3. Bbox normalized to top-left origin; confidence rescaled to [0, 1].

#### Edge Cases
- Document AI returns no detected language; adapter sets `lang_hint=null`.
- Page exceeds Document AI dimensions; adapter splits and stitches.

#### Acceptance Criteria
```gherkin
Given page 3 was routed to Document AI
When the adapter completes
Then `OCRResult.pages[2]` has the same field shape as a Tesseract page
And the only differing field is `provider`
```

#### Dependencies
- DEP-EXT Document AI; DEP-INT to E00-F02 (TF for processor)

#### Non-Functional Considerations
- Cost: per-page ≤ $0.0015 amortized.
- Reliability: timeouts surfaced as typed error.
- Privacy: minimum payload (page only) sent to Document AI.

#### Open Questions
- Use Form Parser for tables specifically or stick with OCR processor?

---

### Story 2: Per-document budget guard

**As an** SRE
**I want** a per-document Document AI fallback budget cap
**So that** a pathological document cannot blow my monthly budget.

#### Preconditions
- Budget cap configured per environment (dev: 5 pages; prod: 20 pages).

#### Main Flow
1. Worker tracks fallback page count per `Document`.
2. On reaching cap, remaining pages stay on Tesseract result with low-confidence flag.
3. Manifest records `budget_capped=true`.

#### Edge Cases
- Pathological doc: every page low-confidence; cap hit early; user sees mixed-quality experience.
- Coordinator with batch upload: cumulative cost guarded by global budget.

#### Acceptance Criteria
```gherkin
Given a 30-page document and a fallback cap of 20
When pages 1-20 route to Document AI and the cap is reached
Then pages 21-30 use Tesseract result with low-confidence flag
And the manifest records `budget_capped=true`
```

#### Dependencies
- DEP-INT to E10-F05 (cost telemetry)

#### Non-Functional Considerations
- Cost: hard cap per environment.
- UX: user informed when budget capped.

#### Open Questions
- Should student be able to top-up budget for a critical document?
