# High-Level Design — tirvi

## 1. Architectural principle

Do **not** build:

```
PDF → OCR → TTS
```

Build:

```
PDF → OCR → Hebrew linguistic interpretation → reading plan → TTS
```

The middle layer (normalization + NLP + reading plan) is the defensible part of the product and is the only layer that must be fully under our control. Everything around it — OCR, TTS, storage — is hidden behind small adapter interfaces so we can swap vendors or substitute open-source equivalents later.

## 2. System overview

```
                ┌────────────────────────────┐
                │ Browser (Next.js / React)  │
                │  upload · player · UI      │
                └─────────────┬──────────────┘
                              │ HTTPS
                              ▼
                ┌────────────────────────────┐
                │ FastAPI app (Cloud Run)    │
                │  REST + signed-URL handout │
                └─────┬───────────┬──────────┘
                      │           │
        enqueue job   │           │ read/write objects
                      ▼           ▼
          ┌────────────────┐  ┌────────────────────┐
          │ Cloud Tasks /  │  │ Cloud Storage      │
          │ Pub/Sub        │  │  pdfs/             │
          └────────┬───────┘  │  pages/  (json)    │
                   │          │  plans/  (json)    │
                   ▼          │  audio/  (mp3/ogg) │
        ┌────────────────────┐└────────────────────┘
        │ Worker (Cloud Run  │
        │  job, same image)  │
        │  ┌──────────────┐  │
        │  │ OCR adapter  │──┼──► Document AI / Tesseract
        │  ├──────────────┤  │
        │  │ Normalizer   │  │
        │  ├──────────────┤  │
        │  │ NLP: AlephBERT│ │   (local model server in dev)
        │  │      YAP/HebPipe│ │
        │  ├──────────────┤  │
        │  │ Reading plan │  │
        │  ├──────────────┤  │
        │  │ TTS adapter  │──┼──► Google Cloud TTS / Vertex
        │  └──────────────┘  │
        └────────────────────┘
```

## 3. Component breakdown

### 3.1 Frontend

- **Stack:** Next.js (React, TypeScript), Tailwind, a small audio engine (`<audio>` element + Web Audio API for word-sync highlighting).
- **Pages:**
  - `/` — upload + recent documents (session-scoped in MVP).
  - `/doc/[id]` — split view: page image left, structured text right, playback controls.
- **Sync model:** the player loads the per-block `reading_plan.json` and the matching `audio.mp3`; word timings are produced by the TTS step (Google TTS returns word/timepoint marks for SSML `<mark>` tags) and stored alongside the audio.
- **Accessibility:** keyboard-first, ARIA roles for the player, `prefers-reduced-motion` honored, focus ring always visible.

> **POC note (2026-05-01):** The POC ships a vanilla HTML/JS player in `player/`; Next.js/React/TypeScript is deferred to MVP.

### 3.2 Backend API (FastAPI)

- Endpoints:
  - `POST /uploads` → returns a signed GCS URL for direct browser → bucket upload.
  - `POST /documents` → registers the uploaded object, enqueues processing.
  - `GET /documents/{id}` → status + manifest of pages/blocks.
  - `GET /documents/{id}/pages/{n}` → cleaned text + reading plan.
  - `GET /documents/{id}/audio/{block_id}` → signed URL to cached audio.
  - `POST /documents/{id}/feedback` → "word X was read wrong" capture.
- Stateless. All durable state is in GCS (and optionally a tiny SQLite/Cloud SQL row for user accounts if we add them).

> **POC note (2026-05-01):** The FastAPI BFF is not yet implemented. In the POC the pipeline is invoked directly via `scripts/run_demo.py`; no HTTP endpoints exist yet.

### 3.3 Worker

- Same Docker image as the API, started with a different entrypoint.
- In dev: a single in-process queue (Redis or just `asyncio` for the smallest case).
- In prod: Cloud Tasks pushes to a Cloud Run worker service, or Cloud Run Jobs run per-document.
- Pipeline stages, each idempotent and resumable, each writing its output to GCS:
  1. `rasterize` → per-page images (PDF → PNG via `pdf2image`)
  2. `ocr` → `pages/{doc}/{page}.ocr.json` (Tesseract `heb` + layout post-processing)
  3. `nakdan_cascade` → diacritized + corrected tokens (Nakdan REST API → DictaBERT-MLM scorer → Gemma LLM reviewer)
  4. `plan` → `plans/{doc}/{page}.plan.json`
  5. `synthesize` → `audio/{doc}/{block_hash}.mp3` + `.timings.json`

> **POC note (2026-05-01):** In the POC all five stages run as a single monolithic `run_pipeline()` call in `tirvi/pipeline.py` (no per-stage idempotency or GCS writes). Output lands in a local `drafts/` directory. The `AuditSink` (F33) captures per-stage debug manifests locally during review runs (`--review` flag).

### 3.4 Storage layout (Cloud Storage as primary store)

```
gs://tirvi-{env}/
  pdfs/{doc_id}.pdf
  pages/{doc_id}/{page}.ocr.json
  pages/{doc_id}/{page}.norm.json
  pages/{doc_id}/{page}.nlp.json
  plans/{doc_id}/{page}.plan.json
  audio/{block_hash}.mp3
  audio/{block_hash}.timings.json
  manifests/{doc_id}.json   ← processing status, page list, block index
  feedback/{doc_id}/{ts}.json
```

- Object lifecycle rule: auto-delete `pdfs/`, `pages/`, `plans/`, and `manifests/` after the configured TTL (default 7 days). `audio/` may live longer because it's keyed by content hash and is shareable across users.
- No relational DB in MVP. If user accounts are added, they go into Cloud SQL Postgres at the smallest tier; document state stays in GCS.

> **POC note (2026-05-01):** The POC uses a local `drafts/<sha>/` directory rather than GCS. The `gs://tirvi-{env}/` layout above is the production target.

## 4. Adapter interfaces (vendor isolation)

All external services are reached through narrow Python interfaces. The domain code never imports a Google SDK directly.

```python
class StorageBackend(Protocol):
    def put(self, key: str, data: bytes, content_type: str) -> None: ...
    def get(self, key: str) -> bytes: ...
    def signed_url(self, key: str, ttl_s: int, method: str) -> str: ...

class OCRBackend(Protocol):
    def ocr_pdf(self, pdf_bytes: bytes) -> list[OCRPage]: ...

class TTSBackend(Protocol):
    def synthesize(self, ssml: str, voice: VoiceSpec) -> Synthesis: ...
        # returns audio bytes + word/mark timings

class CorrectionCascadeService(Protocol):
    def correct_tokens(self, tokens: list[str]) -> list[str]: ...
    # Nakdan word-list gate → DictaBERT-MLM scorer → Gemma 3 4B LLM reviewer

class ProgressReporter(Protocol):
    def stage_started(self, name: str) -> None: ...
    def stage_completed(self, name: str, elapsed_s: float, metric_label: str) -> None: ...
    def stage_error(self, name: str, exc: Exception) -> None: ...
    def token_tick(self, token: str, stage: str, word_count: int) -> None: ...
    def summarize(self) -> None: ...

class AuditSink(Protocol):
    def write_stage(self, stage: str, payload: dict) -> None: ...
```

Concrete implementations:

| Interface | Dev (in single Docker)                         | Prod (GCP)                           |
| --------- | ---------------------------------------------- | ------------------------------------ |
| Storage   | `fakegcs` / local volume                       | Cloud Storage                        |
| OCR       | Tesseract `heb` (default)                      | Document AI / Vision OCR             |
| TTS       | Google Cloud TTS (online)                      | Google Cloud TTS / Vertex            |
| Queue     | in-process / Redis                             | Cloud Tasks                          |
| NLP/Cascade | Nakdan REST + DictaBERT-MLM + Gemma (Ollama) | same, baked into image               |
| Progress  | `NoOpProgressReporter` / `RichProgressReporter` | `NoOpProgressReporter`              |
| Audit     | `FileAuditSink` (review mode, F33)             | deferred                             |

The worker reads `TIRVI_BACKEND=local|gcp` and wires the right implementations.

## 5. The reading-plan layer (the differentiator, in detail)

### 5.1 Input

`pages/{doc}/{page}.norm.json` — cleaned, block-segmented Hebrew text with metadata (block type, language spans, math regions, table structure).

### 5.2 Processing

1. **Rasterize:** PDF → per-page images (`pdf2image`).
2. **OCR:** Tesseract `heb` on each page image → `OCRResult` (tokens, bounding boxes, raw text). A layout post-processor corrects RTL column order and strips OCR artifacts (slash suffixes, wrapping quotes, etc.).
3. **Nakdan + Correction Cascade (F48):**
   - **Nakdan REST API** applies diacritization to all OCR tokens, producing a candidate word-list.
   - **DictaBERT-MLM** (`dicta-il/dictabert-mlm`) scores each candidate using masked-language-model probability in sentence context (e.g., is `ספר` a noun or a verb here?).
   - **Gemma 3 4B** (via Ollama) acts as an LLM reviewer for tokens where MLM confidence is below threshold.
   - The cascade is gated: Nakdan word-list → MLM scorer → LLM reviewer (progressive fallback, cost-controlled via call cap).
   - A curated homograph lexicon (`data/homograph-lexicon.yaml`) is available for high-frequency ambiguous words; wiring into the cascade is a next integration step.
4. **SSML shaping:**
   - Wrap question numbers in a slower, emphasized template.
   - Insert `<break>` between answer options.
   - Switch `xml:lang` on detected English spans.
   - Use `<mark name="block-{id}-word-{i}"/>` so word timings come back from TTS for highlighting.
5. **TTS synthesis:** SSML → Google Cloud TTS returns audio bytes + word/mark timings.

> **POC note (2026-05-01):** Acronym expansion (F15) and mixed-language detection (F16) are TDD-built modules but are **not yet wired into `run_pipeline()`** — deferred to the next integration milestone. SSML shaping (step 4) is partial: `xml:lang` switching and `<mark>` tags are generated; prosody/emphasis shaping is not yet implemented.

### 5.3 Output

```json
{
  "block_id": "p3-q4",
  "block_type": "question",
  "ssml": "<speak>...</speak>",
  "tokens": [
    { "i": 0, "text": "ספר", "lemma": "ספר", "pos": "VERB", "diacritized_text": "סָפַר", "ipa": "saˈfar" },
    { "i": 1, "text": "את",  "lemma": "את",  "pos": "ACC",  "diacritized_text": null,    "ipa": null }
  ]
}
```

### 5.4 Feedback loop

- The player exposes "this word was read wrong → suggest correct reading."
- Corrections go to `feedback/...json` in GCS. Out of band, they feed lexicon updates and an evaluation set — no live retraining in MVP.

## 6. OCR decision

Open question from the PRD: open-source Hebrew OCR vs. Document AI.

**Plan:** ship MVP behind the `OCRBackend` interface with **two** implementations. The default in dev is Tesseract `heb` plus a layout post-processor (column detection, RTL fix-ups). Run a benchmark on a held-out set of 20 representative exam pages comparing:

- Word error rate
- Block-segmentation recall (questions, answers, tables)
- End-to-end "playable page" success rate

Pick the winner per-page-type. If Tesseract is acceptable for digital-born PDFs but weak on scans, route by document type. The decision is data-driven and reversible because of the adapter.

## 7. Deployment topology (GCP)

- **Cloud Run service** `tirvi-api` — FastAPI, autoscale 0→N, public HTTPS.
- **Cloud Run service** `tirvi-worker` — same image, different entrypoint, triggered by Cloud Tasks.
- **Cloud Tasks queue** `tirvi-jobs` — one queue per pipeline stage so retries are isolated.
- **Cloud Storage bucket** `tirvi-{env}` — see §3.4.
- **Secret Manager** for the GCP TTS / Document AI keys.
- **Logging** to Cloud Logging; **no** third-party analytics.
- **Cost posture:** scale-to-zero for both Cloud Run services; lifecycle rules on the bucket; aggressive audio caching by content hash.

> Note: the user requested "GCP App Service." GCP doesn't ship a product by that name; the closest managed equivalents are **Cloud Run** (recommended — request-driven, scale-to-zero, container-native) and **App Engine Standard/Flex** (older, more opinionated). HLD assumes Cloud Run; flag for confirmation before infra work begins.

> **POC note (2026-05-01):** The POC is not deployed to GCP. It runs entirely locally via `scripts/run_demo.py`. The topology above is the production target.

## 8. Single-container dev environment

One `docker compose up` brings up:

- `web` — Next.js dev server.
- `api` — FastAPI with `--reload`.
- `worker` — same image, worker entrypoint, in-process queue.
- `models` — a small FastAPI sidecar that loads AlephBERT + YAP once and exposes `/morph` and `/disambiguate`. This keeps model weights out of the API/worker hot-reload loop.
- `storage` — `fake-gcs-server` mounted to a local volume so the GCS adapter is exercised end-to-end.

Optional `compose.gcp.yml` overlay swaps `storage` for real GCS via ADC and uses the real TTS/OCR adapters; useful when iterating on the prod path locally.

The user's "single docker" requirement is honored either as one Compose project (preferred, still one `up`) or, if strictly required, as one image with a process supervisor — Compose is the cleaner default and is recommended.

> **POC note (2026-05-01):** In the POC, DictaBERT-morph (`dicta-il/dictabert-morph`) and DictaBERT-MLM (`dicta-il/dictabert-mlm`) run in-process; Gemma 3 4B is served by a separately-started Ollama instance. There is no `models` sidecar container and no `docker compose up` yet. The sidecar/Compose architecture above is the production target.

## 9. Data flow (happy path)

1. Browser asks API for a signed upload URL → uploads PDF straight to GCS.
2. Browser POSTs `/documents` with the object key.
3. API writes a manifest, enqueues `ocr` task.
4. Worker runs OCR → writes `*.ocr.json`, enqueues `normalize`.
5. Worker normalizes → writes `*.norm.json`, enqueues `nlp`.
6. Worker runs NLP → writes `*.nlp.json`, enqueues `plan`.
7. Worker builds reading plan → writes `*.plan.json`, enqueues `synthesize` per block.
8. Worker calls TTS → writes `audio/{hash}.mp3` + `.timings.json`. If hash already exists, skip.
9. Manifest is updated; browser polls (or subscribes) and starts playing as soon as the first block is ready.

## 10. Risks & mitigations

| Risk                                  | Mitigation                                                                        |
| ------------------------------------- | --------------------------------------------------------------------------------- |
| OCR Hebrew layout errors              | Keep page coordinates; show original alongside extracted text; benchmark per §6.  |
| Wrong pronunciation                   | Curated lexicon + Nakdan diacritization + DictaBERT-MLM/Gemma correction cascade + user feedback capture. |
| Tables / math read as flat text       | Detect in normalization; route through dedicated reading templates.               |
| TTS ignores pronunciation hints       | Pre-process aggressively; encode in SSML where supported; measure per release.    |
| Exam privacy                          | Short TTL on documents; minimum payload to third parties; no log capture of text. |
| Vendor lock-in                        | All vendors live behind adapters; Hebrew TTS is the only acknowledged exception.  |
| Cost spike from re-synthesis          | Content-hash audio cache in GCS, shared across users.                             |
| Single-container dev gets too heavy   | Models live in a sidecar so the API/worker stays light; GPU optional, not assumed.|

## 11. What we are explicitly deferring

- AuthN/AuthZ beyond anonymous sessions.
- Cloud SQL / Postgres — only added if user accounts justify it.
- Real-time WebSocket updates — polling is fine for MVP.
- Multi-region deployment.
- Custom voices / voice cloning.
- A formal accessibility audit pipeline (manual checklist for MVP).

## 12. Open items requiring user confirmation

1. Confirm "GCP App Service" → **Cloud Run** (see §7).
2. Confirm single-Docker = `docker compose up` (preferred) vs. one image with supervisord.
3. Confirm 7-day TTL default for uploaded documents.
4. Confirm we may evaluate Tesseract `heb` first and only fall back to Document AI if it underperforms.
