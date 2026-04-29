# Severity-Ranked Fix List — tirvi Business & Functional Design Phase

Mirror of the Severity-Ranked Fix List section of
`global-review-synthesis.md`, kept as a standalone file per skill template
contract. Source of truth is the synthesis; if these diverge, synthesis wins.

| ID | Severity | Area | Finding | Status | Files Fixed | Issue / Deferred Row |
|----|---------|------|---------|--------|------------|---------------------|
| AC-02 / R-01 | Critical | Security | Audio cache cross-user exemption requires Israeli counsel sign-off | Deferred | — | D-AUDIO-CACHE-LEGAL |
| AC-03 / R-06 | Critical | Product | n=10 MOS panel cannot defend ≥ 90% PRD pronunciation claim | Deferred | — | D-PRD-MOS-LANGUAGE-REWRITE |
| AC-01 / R-02 | Critical | Architecture | Hebrew Wavenet `<mark>` reliability requires CI-mandatory failover smoke test | Fixed | `epics/E07-tts-adapters/stories/E07-F01-google-wavenet-adapter.stories.md`; `ontology/functional-test-ontology.yaml` (FT-194) | — |
| AC-05 / R-04 | Critical | Security | Server-side attestation enforcement (modal-only insufficient) | Fixed | `epics/E11-privacy-legal/stories/E11-F03-upload-attestation.stories.md`; `epics/E11-privacy-legal/reviews/E11-F03-upload-attestation.design-review.md` | — |
| R-03 | Critical | Functional Test | Adversarial bench pages (busy bg, math, civics) required | Deferred (gating v1.0) | — | D-OCR-BENCH-RUN |
| AC-04 | High | Functional Test | Tesseract `heb` block-recall verification on real bench | Deferred | — | D-OCR-BENCH-RUN |
| AC-06 | High | Architecture | DictaBERT footprint vs Apple Silicon dev floor | Fixed | `epics/E00-foundation/stories/E00-F05-dev-resource-floor.stories.md` (24 GB Apple Silicon recommendation; doctor warning) | — |
| R-05 | High | Functional Test | Schema-bump migration coverage on NLPResult / OCRResult | Fixed | `epics/E02-ocr-pipeline/tests/E02-F03-ocr-result-contract.functional-test-plan.md`; `epics/E04-nlp-disambiguation/tests/E04-F03-per-token-pos-morph.functional-test-plan.md` | D-SCHEMA-V-OCR; D-SCHEMA-V-NLP (first migration test deferred) |
| R-07 | High | Architecture | Hash bump procedure / voice rotation cache invalidation | Fixed (ops rehearsal deferred) | `epics/E08-word-timing-cache/reviews/E08-F03-content-hash-audio-cache.design-review.md` | D-VOICE-ROTATION-PLAYBOOK |
| R-08 | High | Delivery | E## ↔ F## cross-walk to canonical PLAN.md | Fixed | `ontology/business-taxonomy.yaml` (`plan_md_cross_walk` section) | — |
| AC-07 | Medium | DDD | Block taxonomy missing footnote / sidenote / rubric | Deferred (v1.1) | — | D-BLOCK-TAXONOMY-V1 |
| AC-08 | Medium | Security | Per-IP rate limit on uploads | Fixed | `epics/E01-document-ingest/reviews/E01-F01-signed-url-upload.design-review.md` | — |
| AC-09 | Medium | Behavioural UX | Coordinator persona overlap with student | Fixed (MVP scope) | `epics/E01-document-ingest/reviews/E01-F01..F04 design-reviews` | D-COORD-BULK-V1 (full v1) |
| AC-10 | Medium | Architecture | Schema versioning procedure | Fixed | `epics/E02-ocr-pipeline/tests/E02-F03-ocr-result-contract.functional-test-plan.md`; `epics/E04-nlp-disambiguation/tests/E04-F03-per-token-pos-morph.functional-test-plan.md` | D-SCHEMA-V-OCR; D-SCHEMA-V-NLP |
| AC-11 | Medium | Functional Test | Latin-transliteration FP rate unmeasured | Deferred | — | D-TRANSLIT-BENCH |
| AC-12 | Medium | Architecture | Voice rotation cache-miss flood | Fixed | `epics/E08-word-timing-cache/reviews/E08-F03-content-hash-audio-cache.design-review.md` | D-VOICE-ROTATION-PLAYBOOK |
| R-09 | Medium | DDD | Manifest annotated as read model of Document | Fixed | `ontology/business-taxonomy.yaml` (BO03 description) | — |
| R-10 | Medium | Ontology | dependency-map → FUT-* future implementation anchors | Fixed | `ontology/dependency-map.yaml` (DEP-041..DEP-045) | — |
| R-11 | Medium | Product | PRD §10 language soften | Deferred (PRD edit out of scope) | — | D-PRD-MOS-LANGUAGE-REWRITE |
| R-12 | Medium | Adversarial | Latin-transliteration FP rate quantified | Deferred | — | D-TRANSLIT-BENCH |
| Coref-MVP | Medium | Delivery | E04-F04 MVP vs v1.1 decision | Deferred | — | D-COREF-MVP-SCOPE |

**Tally**:
- Critical: 5 (2 fixed / 3 deferred — all 3 deferreds tracked with explicit re-evaluation triggers)
- High: 4 (3 fixed / 1 deferred to v1.0 prep)
- Medium: 12 (7 fixed / 5 deferred — all to v1 / v1.1 with rows)
