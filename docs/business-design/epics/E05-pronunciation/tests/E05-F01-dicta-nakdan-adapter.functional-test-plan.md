# E05-F01 — Dicta-Nakdan Adapter: Functional Test Plan

## Scope
Verifies diacritization with NLP-context conditioning, lexicon override
applied after, and fallback when Nakdan unavailable.

## Source User Stories
- S01 NLP-conditioned diacritization — Critical
- S02 lexicon override — Critical

## Test Scenarios
- **FT-146** Verb context "ספר התלמיד שיר" → verb diacritization. Critical.
- **FT-147** Noun context "ספר על המדף" → noun diacritization. Critical.
- **FT-148** Lexicon override beats Nakdan. Critical.
- **FT-149** Numbers / English skipped. High.
- **FT-150** Word-level accuracy ≥ 85% on bench. Critical.
- **FT-151** API failure → fallback path. High.

## Negative Tests
- Tokens with unknown surface; fallback to undecorated.
- Adapter produces empty result; manifest flag.

## Boundary Tests
- 1-token; 5000-token page.

## Permission and Role Tests
- API minimum-payload assertion.

## Integration Tests
- E05-F01 ↔ E04 (NLP context) ↔ E05-F03 (lexicon).

## Audit and Traceability Tests
- Per-token provider stamped; lexicon version logged.

## Regression Risks
- Nakdan upstream regression; bench catches.

## Open Questions
- API vs local model.
