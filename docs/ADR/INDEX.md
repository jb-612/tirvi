# ADR Index

Architectural Decision Records for tirvi. Each ADR captures a material
design decision with context, choice, consequences, and alternatives.
Naming: `ADR-NNN-<bounded-context>-<short-name>.md`. Status transitions:
Proposed → Accepted | Superseded | Deprecated.

| ID | Title | Status | Bounded context | Related features |
|----|-------|--------|-----------------|------------------|
| ADR-001 | TTS routing (Wavenet/Chirp/Azure split) | Proposed | audio | F26, F27, F28, F29 |
| ADR-002 | NLP backbone (DictaBERT vs. AlephBERT) | Proposed | hebrew-interpretation | F17 |
| ADR-003 | Diacritization + G2P stack (Nakdan + Phonikud) | Proposed | hebrew-interpretation | F19, F20 |
| ADR-004 | OCR primary (Tesseract vs. Document AI vs. DeepSeek-OCR) | Proposed | ingest | F08, F09, F13 |
| ADR-005 | Document TTL policy (24 h vs. 7 d) | Proposed | privacy | F43 |
| ADR-006 | MVP framing (practice-and-prep vs. real-Bagrut) | Proposed | product | all |
| ADR-007 | Handwriting OCR scope (in/out of MVP) | Proposed | ingest | — |
| ADR-008 | Auth in MVP (anonymous session vs. accounts) | Proposed | platform | — |
| ADR-009 | Word-timing fallback (WhisperX vs. Aeneas vs. MFA) | Proposed | audio | F31 |
| ADR-010 | NLP compute primitive (Cloud Run CPU vs. GPU) | Proposed | hebrew-interpretation | F17 |
| ADR-011 | Dev container layout (Compose vs. supervisord) | **Accepted** | dev-platform | F01 |
| ADR-012 | Cloud compute primitive (Cloud Run vs. App Engine vs. Functions) | **Accepted** | cloud-platform | F02 |
| ADR-013 | SDLC harness — biz / sw design split + ACM ingestion | Proposed | sdlc | all (harness-wide) |
| ADR-014 | Result-object schema versioning (contract tests over numeric versions) | Proposed | platform | F03 |
| ADR-015 | WordTimingProvider fallback policy (automatic on schema mismatch) | Proposed | audio_delivery | F03, F30, F31 |
| ADR-016 | Tesseract deskew preprocessor lives inside the adapter | Proposed | ingest | F08 |
| ADR-017 | OCRResult fixture builder uses YAML, not a Python DSL | Proposed | platform | F10 |
| ADR-018 | Block segmentation uses heuristics for POC; learned model deferred | Proposed | ingest | F11 |
| ADR-019 | Normalization uses deterministic rules for POC; ML repair deferred | Proposed | hebrew-interpretation | F14 |
| ADR-020 | DictaBERT loaded in-process for POC; sidecar deferred to MVP | Proposed | hebrew-interpretation | F17 |

## Conventions

- One material decision per ADR. Split if a draft exceeds ~80 lines or
  spans ≥ 2 bounded contexts.
- Reference HLD section IDs in **Context** (e.g., `HLD-§8`, `HLD-§12-OQ2`).
- Cross-reference related ADRs in **References**, not in the body.
- ADRs are first-class graph nodes (`adr:NNN`) consumed by traceability.yaml.
