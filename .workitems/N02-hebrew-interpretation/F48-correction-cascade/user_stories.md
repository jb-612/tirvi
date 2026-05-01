# N02/F48 — Hebrew Correction Cascade — User Stories (Index)

## Source Basis
- ADR: `docs/ADR/ADR-033-hebrew-correction-cascade.md` (the contract).
- UAT: `docs/UAT/UAT-2026-05-01-tts-quality.md` — 9 symptom classes from listening session.
- UAT: `docs/UAT/UAT-2026-05-01-why-models-miss.md` — root-cause analysis showing hardcoded `_KNOWN_OCR_FIXES` does not scale.
- PRD: `docs/PRD.md` §6.4 (reading plan), §7.1 (accommodation quality), §9 (privacy).
- HLD: `docs/HLD.md` §10 (NLP chain), §12-OQ2 (TTS quality target), §3 (on-device-only constraint).
- Adjacent F50 inspector (under design) — surface for review trail and feedback.

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Dyslexic Hebrew Student | primary listener | hear the exam read correctly | OCR errors → mispronunciation breaks comprehension | ≥ 90% of OCR errors that affect TTS pronunciation are silently corrected; nothing leaves the M4 Max |
| P02 Accommodation Coordinator / Teacher-QA | reviews pronunciation, marks errors | confirm corrections are right | no audit trail of why a word changed | every correction has reasoning trail; can override in F50 inspector |
| P15 Pipeline Engineer | tunes thresholds, prompts, model versions | improve recall/precision per cohort | hardcoded fix list grows unbounded | adjust knobs + re-run; corrections.json shows before/after |

(P15 is new for F48; appended to `ontology/business-domains.yaml` under `personas`.)

## Collaboration Model
1. **Primary actor**: the pipeline itself runs autonomously per page; the student is a passive listener.
2. **Supporting**: teacher-QA via F50 inspector OCR tab; pipeline engineer via CLI.
3. **System actors**: `NakdanWordList` (CO13), `DictaBERTMLMScorer` (CO14), `LLMReviewer` (CO15) — all on-device.
4. **Agentic actors**: Gemma 3 27B / 4B reviewer running locally via Ollama. Optional Llama 3.1 8B fast-tier.
5. **Approvals**: none at runtime; teacher-QA approves *post-hoc* in inspector.
6. **Handoffs**: cascade output → F19 Nakdan → F20 Phonikud → F23 SSML.
7. **Escalation**: low-confidence correction → escalate to next stage; final-stage tie → keep original + log.
8. **Failure recovery**: Ollama down → degrade to NakdanGate + DictaBERT-MLM with stricter threshold; Final fallback to deprecated `_KNOWN_OCR_FIXES`.

## Behavioural Model
1. **Hesitation**: teacher uncertain whether a Gemma correction is real or a hallucination.
2. **Rework**: engineer raises MLM threshold after a noisy run; expects deterministic re-evaluation from cache.
3. **Partial info**: Ollama half-loaded mid-page; system must not block.
4. **Misunderstanding**: student hears something odd, doesn't know why; reasoning trail must explain it.
5. **Competing priorities**: latency vs. recall — engineer wants knobs not code changes.
6. **Approval delays**: feedback loop accumulates 3+ "no" votes → suggests rule promotion *only after* threshold.
7. **Manual override**: teacher marks "no" in inspector → original restored; preference cached.
8. **Abandoned flow**: teacher walks away mid-review; partial feedback persists.
9. **Retry**: same input + same model version → same output (cache by `sentence_hash + prompt_hash`).
10. **Error correction**: same OCR confusion appears 3× → system *suggests* (does not auto-promote) a permanent rule.

## Story Files (split — see file headers)
| File | Bounded Context / Sub-feature | Stories |
|------|-------------------------------|---------|
| `user_stories.nakdan-gate.md` | hebrew_text — NakdanGate | S01 |
| `user_stories.mlm-scorer.md` | hebrew_text — DictaBERTMLMScorer | S02 |
| `user_stories.llm-reviewer.md` | hebrew_text — LLMReviewer | S03 |
| `user_stories.correction-log.md` | hebrew_text + privacy_compliance — CorrectionLog | S04 |
| `user_stories.feedback-loop.md` | hebrew_text + player — Feedback Loop | S05 |
| `user_stories.degradation.md` | hebrew_text — Offline / degradation modes | S06 |

Story IDs: `F48-S01..F48-S06`. Every story traces to ADR-033 §Decision row + UAT root cause.

## Sibling Feature Dependencies
- F14 (normalization), F17 (DictaBERT adapter), F19 (Dicta-Nakdan), F20 (Phonikud), F22 (reading plan), F23 (SSML).
- F47 (feedback capture) consumes F48's `corrections.json` schema.
- F50 (inspector — under design) renders the OCR tab using F48 outputs.

## Ontology Refs
See `ontology/business-domains.yaml` `business_objects` ids `BO49..BO56` and `collaboration_objects` `CO13..CO16` (appended for F48).
