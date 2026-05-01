# Coverage Plan — tirvi Business & Functional Design

Drives the order in which features are processed, which bounded contexts
are touched, which actors recur, and which risks attach. Updated once at
Stage 1; per-feature traceability lives in `business-taxonomy.yaml`.

## Processing Order

The 12-epic plan from `docs/research/tirvi-validation-and-mvp-scoping.md`
§10 is processed in dependency order: foundation (E0) → ingest (E1) →
OCR (E2) → Hebrew interpretation core (E3–E6) → audio (E7–E8) →
player (E9) → quality+privacy (E10–E11). Per-feature stories are written
serially within each epic.

## Epic & Feature Inventory

| Epic | Name | Bounded Context | Features | Phase | Priority |
|------|------|-----------------|----------|-------|----------|
| E0  | Foundation & DevX            | platform              | F0.1–F0.5 (5)   | 0  | Critical |
| E1  | Document ingest              | document_ingest       | F1.1–F1.5 (5)   | 1  | Critical |
| E2  | OCR pipeline                 | extraction            | F2.1–F2.6 (6)   | 1  | Critical |
| E3  | Normalization                | hebrew_text           | F3.1–F3.5 (5)   | 2  | Critical |
| E4  | NLP & disambiguation         | hebrew_nlp            | F4.1–F4.4 (4)   | 2  | Critical |
| E5  | Pronunciation prediction     | pronunciation         | F5.1–F5.4 (4)   | 2  | Critical |
| E6  | Reading plan generator       | reading_plan          | F6.1–F6.5 (5)   | 2  | Critical |
| E7  | TTS adapters                 | speech_synthesis      | F7.1–F7.4 (4)   | 3  | High     |
| E8  | Word-timing & cache          | audio_delivery        | F8.1–F8.4 (4)   | 3  | High     |
| E9  | Player UI                    | player                | F9.1–F9.6 (6)   | 4  | Critical |
| E10 | Quality validation           | quality_assurance     | F10.1–F10.5 (5) | 5  | High     |
| E11 | Privacy & legal              | privacy_compliance    | F11.1–F11.5 (5) | 5  | Critical |

**Total:** 12 epics, 58 features, 12 bounded contexts.

## Bounded Contexts (DDD)

Anchored to the "reading plan is the product" principle (src-008 §7).
Core domain: `hebrew_text` + `hebrew_nlp` + `pronunciation` +
`reading_plan`. Supporting: `extraction`, `speech_synthesis`,
`audio_delivery`, `player`. Generic: `platform`, `document_ingest`,
`quality_assurance`, `privacy_compliance`.

## Recurring Personas

- **Dyslexic Hebrew student** (primary; ages 14–24; Bagrut prep or
  university). Owns most stories in E1, E2, E3–E6 (perceived behaviour),
  E9, E10.
- **Accommodation coordinator** (`רכז התאמות` / `מורה שילוב`); preps
  practice material; potentially distributes to multiple students.
  Stories in E1, E9, E11.
- **Parent / guardian** (gate for ≥14 PPL Amendment 13 consent flows);
  stories in E11.
- **Operator / SRE** (internal; cost dashboards, lifecycle, OCR
  benchmarks); stories in E0, E10.
- **Test panel participant** (dyslexic teen volunteer for MOS study);
  stories in E10.
- **Anonymous browser session** (system actor, not human); referenced
  across E1, E9.

## Recurring System / Agent Actors

- `OCR engine` (Tesseract, Document AI, DeepSeek-OCR pilot)
- `Hebrew NLP service` (DictaBERT-large-joint primary; AlephBERT/YAP fallback)
- `Diacritizer` (Dicta-Nakdan)
- `G2P engine` (Phonikud)
- `TTS provider` (Google Wavenet, Chirp 3 HD, Azure HilaNeural)
- `WordTimingProvider` (TTS-emitted marks; WhisperX fallback)
- `Storage adapter` (Cloud Storage / fake-gcs)
- `Queue adapter` (Cloud Tasks / in-process)
- `Manifest coordinator` (per-document fan-in)
- `Lifecycle manager` (TTL enforcement)
- `Lexicon maintainer` (offline curation actor)
- `MOS panel orchestrator` (E10)

## Known Domain Entities (Stage 4 seed)

- `Document` (uploaded PDF, lifecycle owner)
- `Page` (OCR result, normalization result, NLP result, plan result)
- `Block` (heading | instruction | question_stem | answer_option |
  paragraph | table | figure_caption | math_region)
- `Token` (text + lemma + POS + morph + diacritization + IPA hint)
- `ReadingPlan` (block_id + ssml + tokens + voice + timing target)
- `AudioObject` (block_hash + audio bytes + timings)
- `Manifest` (per-document status + page index + block index)
- `FeedbackEntry` (word-was-wrong report)
- `Lexicon` (acronyms + homographs)
- `BenchmarkSet` (tirvi-bench v0)
- `MOSStudy` (panel + ratings + voices compared)
- `ConsentRecord` (parental ≥14)
- `RetentionPolicy` (TTL value + reason)

## Known Business Processes

1. Upload exam → first audio block playable
2. Per-block playback with word-sync highlight
3. Re-read sentence with cached audio
4. Spell a word letter-by-letter
5. Read a table by row
6. Capture "word was read wrong" feedback
7. Auto-delete document after TTL
8. Run benchmark + quality gates in CI
9. Run blinded MOS study with dyslexic teens
10. Lifecycle / consent / DPIA flows for minors

## Known Risks Tracked Through Design

R1 real-Bagrut policy (frames product as practice tool; touches E10/E11).
R2 TTS quality empirical gap (gates E7/E10).
R3 mispronunciation on Tanakh/civics/science (gates E4/E5/E6).
R4 handwriting OCR (deferred; gates E2 scope).
R5 publisher copyright (gates E11 attestation).
R6 minors' privacy (gates E11 consent flows + ADR-005).
R7 7-day vs 24h TTL (gates E1/E11 lifecycle).
R8 latency p50/p95 (gates E0/E2 cold-start posture).
R9 TTS vendor lock (gates E7 router).
R10 distribution (out of scope here; product/GTM concern).
R11 dev-machine resource floor (gates E0 compose profile).
R12 minors' regulatory tightening (gates E11).

## F33 — Exam Review Portal (Admin Quality Review)

**Bounded context:** `bc:exam_review` (new — subordinate to existing `player` and `quality_assurance`)
**Personas:** University Admin (primary, new), Pipeline Developer (supporting), QA Reviewer (supporting), Content Preparer (supporting).
**Phase:** N04 (Player UI, weeks 11–13). Folds in N05/F47 feedback capture.

**Key processes added:**
1. Admin loads portal for a run → sees PDF side-by-side with audio player
2. Admin annotates per-word quality issues (category + note)
3. Admin browses artifact tree to diagnose pipeline stage output
4. Admin exports feedback as JSON
5. Developer drills artifact tree to find root cause
6. Admin compares two pipeline runs (before/after fix)
7. Admin reviews all flagged words before final export

**Risks specific to F33:**
- R-F33-01: Auth deferred — portal is open; documented as intentional deferral.
- R-F33-02: Feedback schema forward-compatibility with F39 benchmark harness.
- R-F33-03: Concurrent review not handled (single-user POC assumption).
- R-F33-04: Admin has zero pipeline knowledge — UX must be self-explaining.

**Test ID ranges allocated:**
- Functional: FT-316 to FT-330
- Behavioural: BT-209 to BT-218

## Out of Scope for This Design Phase

- Class diagrams, API specs, DB schemas, code samples (that is design-pipeline).
- Cost forecasting (research already covers it; design references gates).
- ADR authoring (research §12 enumerates slots; ADRs land separately).
- v1.1 deferred items (handwriting, accounts, Cloud SQL, custom voices,
  WebSocket, mobile-native, Zonos-Hebrew, MathSRE, MoE pilot).

## Stage Gate

Design phase advances to Stage 2 with the source inventory and this
coverage plan as the contract. Per-feature work writes to
`docs/business-design/epics/<epic-id>-<slug>/...` and updates the three
ontology YAMLs incrementally.
