# Product Requirements Document — tirvi

## 1. Summary

**tirvi** is a web app that reads Hebrew exam PDFs aloud for students with dyslexia and other reading accommodations. The user uploads a scanned or digital exam, and the system returns a synchronized listen-and-read experience: the original page is shown side by side with cleaned Hebrew text, and the student can play any sentence, question, paragraph, or table on demand.

The core insight is that an accessible Hebrew exam reader is **not** "OCR → TTS." It is "OCR → Hebrew linguistic interpretation → reading plan → TTS." The middle layer — disambiguating Hebrew homographs, handling acronyms, and structuring questions vs. answer choices — is the product.

## 2. Problem

Hebrew is hard to read aloud automatically because:

- It is written without vowels (ניקוד), so the same letters can be pronounced multiple ways depending on context (`ספר` = "book" / "count" / "tell").
- Exam PDFs mix RTL Hebrew with LTR numbers, English, and math.
- Scanned exams contain layout artifacts (multi-column, tables, answer bubbles) that break naive OCR + TTS pipelines.
- Hebrew acronyms (`ד״ר`, `מס׳`, `ת״ז`, `עמ׳`) are read incorrectly by generic TTS.
- Existing accessibility tools either skip Hebrew, mispronounce it, or read the entire page as one unbroken stream — which is unusable in a timed exam setting.

Students with dyslexia who are entitled to a reader accommodation often depend on a human reader. tirvi aims to provide a reliable, on-demand, exam-shaped alternative.

## 3. Target users

**Primary**

- Hebrew-speaking high-school and university students with dyslexia or other formal reading accommodations who need exam material read aloud.

**Secondary**

- Accommodation coordinators and learning-support teachers who prepare practice materials.
- Adult learners working through Hebrew study material.

## 4. Goals & non-goals

### Goals (MVP)

1. Upload a Hebrew exam PDF (scanned or digital).
2. Display the original page next to extracted, cleaned Hebrew text.
3. Play audio for the page, paragraph, question, answer choice, or sentence the student selects.
4. Pronounce common ambiguous words and acronyms correctly often enough to be trusted in practice.
5. Provide accessibility-grade playback controls (speed, repeat, highlight current word, enlarge text).
6. Run the entire dev environment in a single Docker container.
7. Deploy on GCP managed services with cost-conscious storage choices.

### Non-goals (MVP)

- Multi-tenant institutional admin, SSO, or roles beyond "student" + "anonymous".
- Real-time collaboration or shared sessions.
- Native mobile apps (web-responsive only).
- Live exam proctoring or anti-cheating features.
- Languages other than Hebrew (and inline English/numbers as needed).
- Generating ניקוד as a user-facing feature; ניקוד is internal to the reading plan.
- Long-term storage of student documents (see §8 Privacy).

## 5. Use cases

1. **Whole-page read.** Student opens a page and presses play; tirvi reads the page in logical order.
2. **Per-question read.** Student taps "question 4"; tirvi reads only the question stem.
3. **Read answer choices.** Student taps "answers"; tirvi reads each option with a short pause between them.
4. **Repeat sentence.** Student didn't catch the last sentence; one tap repeats it.
5. **Spell a word.** Student long-presses a word; tirvi spells it letter by letter.
6. **Read a table.** Student opens a question containing a table; tirvi reads it row by row using a table template, not as flat text.
7. **Adjust pace.** Student lowers playback speed and increases text size for dense passages.

## 6. Functional requirements

### 6.1 Upload & document handling

- Accept PDF uploads up to a configured size limit (target: 50 MB MVP).
- Show per-document processing status (uploaded → OCR → normalized → reading-plan → audio-ready).
- Allow the user to delete a document; deletion removes PDF, audio, and derived artifacts.

### 6.2 Extraction

- OCR every page, preserving page coordinates and reading order.
- Detect Hebrew RTL flow and not corrupt it with embedded English/numbers.
- Segment each page into structural blocks: heading, instruction, question stem, answer option, paragraph, table, figure caption, mixed.
- Tag question numbers and answer-option letters/numbers.

> **POC note (2026-05-01):** The POC recognises 3 of 8 block types: `paragraph`, `heading`, and `mixed`. The remaining types (`instruction`, `question_stem`, `answer_option`, `table`, `figure`) are scaffolded but not fully implemented in the OCR post-processor.

### 6.3 Hebrew normalization

- Repair common OCR artifacts: broken lines, stray punctuation, wrong directionality.
- Expand recognized acronyms into spoken form (`ד״ר` → `דוקטור`, `עמ׳` → `עמוד`).
- Normalize numbers, dates, percentages, and ranges into spoken form.
- Detect mixed Hebrew/English spans and mark language for the TTS layer.
- Detect math expressions and route them through a math-reading template.

> **POC note (2026-05-01) — deferred features:** Acronym expansion (F15) and mixed-language detection (F16) are implemented as TDD-tested modules but are not yet integrated into the pipeline. Number normalization handles OCR artifact repair (broken lines, stray punctuation) but does not convert Arabic numerals, dates, or percentages to spoken Hebrew form. Both are deferred to the next integration milestone.

### 6.4 Reading plan (the differentiator)

- Produce, per block, a structured "reading plan" with:
  - Token text
  - Morphological role (POS, lemma) where confidence is high
  - Pronunciation hint (partial ניקוד or phoneme sequence) for ambiguous tokens
  - SSML-shaping cues (pause, emphasis, language switch)
- Use a three-stage correction cascade to correct OCR tokens: Dicta-Nakdan REST API (diacritization), DictaBERT-MLM (`dicta-il/dictabert-mlm`, masked-LM scoring), and Gemma 3 4B via Ollama (LLM reviewer for low-confidence tokens).
- Allow user feedback: "this word was read wrong" → captured for offline improvement (no live model retraining in MVP).

### 6.5 TTS

- Synthesize audio per block (not per page) so playback granularity matches segmentation.
- Use SSML to inject pauses, language switches, and pronunciation hints.
- Cache synthesized audio in Cloud Storage keyed by content hash so re-reads cost nothing.

> **POC note (2026-05-01):** The POC does not implement content-hash audio caching; TTS is called on every pipeline run. The cache described above is a production feature.

### 6.6 Player UI

- Side-by-side: original page image + cleaned text.
- Click any sentence/question/answer to play.
- Word-level highlight synchronized with audio.
- Controls: play/pause, speed (0.5×–1.5×), repeat sentence, next/previous block, larger text, high-contrast mode.
- Distinct affordances for "read question only" and "read answer options".
- No flashing animation, no autoplay surprises, keyboard-navigable.

## 7. Non-functional requirements

### 7.1 Accessibility

- WCAG 2.2 AA as the baseline target.
- Keyboard reachable for every action.
- Respects `prefers-reduced-motion`.
- Visible focus states; minimum 4.5:1 contrast.

### 7.2 Performance

- First page playable within ~30 s of upload for a typical 5-page scanned exam.
- Sentence-level playback latency under 300 ms for cached audio.
- Player UI interactive (TTI) under 2 s on a mid-range laptop.

### 7.3 Reliability

- Document processing is resumable; a worker crash does not require re-upload.
- Failed pages are surfaced individually; one bad page does not block the rest.

### 7.4 Cost

- Default to Cloud Storage for documents, audio, and derived JSON. Avoid databases for MVP unless required for queries.
- Reuse cached audio aggressively (content-hash keyed).
- Scale processing workers to zero when idle.

### 7.5 Portability (minimum vendor lock)

- All app code is portable Python/TypeScript with no GCP-only SDKs in the domain layer.
- GCP services are reached through thin adapter interfaces (`Storage`, `OCR`, `TTS`) so they can be swapped for local/OSS equivalents.
- The dev environment runs entirely in one Docker container with no GCP dependency for code paths that have an OSS substitute.

## 8. Privacy & data handling

- Exams may be confidential. Default retention: documents and audio auto-delete after a configurable TTL (MVP default: 7 days).
- No third-party analytics in MVP.
- Uploads are scoped to the uploading session/user; no cross-user access.
- Only the minimum text needed for synthesis is sent to the TTS provider; full documents are never sent to third parties beyond OCR/TTS.
- Logs do not contain document content.

## 9. Constraints

- **Models — local-first:** Hebrew NLP (morphology, diacritization, contextual correction) uses open-source models running locally: `dicta-il/dictabert-morph` (DictaBERT-morph, morphological analysis), Dicta-Nakdan via REST API (diacritization), and `dicta-il/dictabert-mlm` (DictaBERT-MLM, correction scoring). Gemma 3 4B (via Ollama) acts as an LLM reviewer in the correction cascade.
- **Hebrew TTS — Vertex / Google Cloud TTS:** open-source Hebrew TTS quality is not yet good enough for accommodation-grade reading; this is the deliberate exception.
- **Hebrew OCR:** prefer open-source if a tested option meets the quality bar on Hebrew exam PDFs (e.g., Tesseract `heb` with layout post-processing); otherwise fall back to GCP Document AI / Vision OCR. Decision recorded in HLD.
- **Single Docker dev environment:** one `docker compose up` (or `docker run`) brings up frontend, backend, worker, and any local model server.
- **Deployment — GCP managed services:** Cloud Run for the app and worker; Cloud Storage for blobs; Cloud Tasks or Pub/Sub for async; no self-managed VMs.
- **Storage shape — Cloud Storage > DB for MVP:** documents, page JSON, reading plans, and audio live as objects in GCS. A small relational store may be introduced only if needed for user accounts; early MVP can live without one.

## 10. Success metrics

- **Pronunciation accuracy** on a curated Hebrew exam test set: ≥ 90% words pronounced correctly, ≥ 95% on common acronyms.
- **OCR structural recall**: ≥ 95% of question stems and ≥ 90% of answer choices correctly segmented.
- **Time-to-first-audio** for a 5-page exam: ≤ 30 s p50, ≤ 90 s p95.
- **Cost per processed page**: target under \$0.02 amortized over typical caching.
- **User-reported "wrong word" rate**: tracked as a north-star quality signal.

## 11. Out-of-scope risks (acknowledged, not addressed in MVP)

- Formal accessibility certification by Israeli education authorities.
- Custom voice cloning or a teacher's-voice option.
- Offline mode.
- Long-form non-exam content (textbooks, novels) — the reading-plan layer assumes exam-shaped structure.

## 12. Open questions

1. Do we need user accounts in MVP, or is anonymous + browser-local session enough?
2. Which open-source Hebrew OCR (if any) clears the quality bar — Tesseract `heb`, Kraken, or a hybrid? (Decided in HLD §6 with a benchmark task.)
3. Should the user-feedback "this word was wrong" loop write back to a corrections store immediately, or only ship in v1.1?
4. Acceptable maximum cost per minute of synthesized audio before we revisit OSS Hebrew TTS?
