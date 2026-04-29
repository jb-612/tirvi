# E02-F01 — Per-Feature Design Review

| Reviewer | Severity | Area | Finding | Files | Must-fix |
|----------|---------|------|---------|-------|----------|
| Product Strategy | Medium | Product | Adapter is invisible to user; quality-of-OCR is felt downstream. | — | No |
| DDD | Medium | Domain | `OCRResult` lives in `extraction` BC; clarify aggregate root. | business-taxonomy.yaml | Yes |
| Functional Testing | High | Test | Confidence threshold not yet evidence-backed; bench must justify. | functional-test-plan | Yes — link to bench. |
| Behavioural UX | Medium | Behaviour | BT-040 abandonment metric undefined. | behavioural-test-plan | Yes |
| Architecture | Medium | Arch | Deskew location open. | stories OQ | Yes — pick. |
| Data and Ontology | Low | Onto | `Word`, `BBox` taxonomy needed. | business-taxonomy.yaml | Yes |
| Security and Compliance | Low | Security | Tesseract self-host; no third-party send. | — | No |
| Delivery Risk | Medium | Delivery | tessdata version drift; pin in image. | stories | Yes |
| Adversarial | High | Risk | RTL post-processor failure modes under stress unstated. | functional-test-plan | Yes — add stress tests. |
| Team Lead Synthesizer | High | All | Two High; queue. | — | Yes |

## Aggregate Severity
- Critical: 0  High: 2  Medium: 5  Low: 2
- Status: 6 revisions queued for iteration 1.
