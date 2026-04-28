---
tier: 5
version: 1.0
created: 2026-04-28
updated: 2026-04-28
status: current
research_question: "Is the tirvi product approach (Hebrew exam reader with linguistic interpretation layer) and proposed architecture sound, and what is a defensible MVP scope?"
perspectives: [explorer, architect, critic, cost, precedent]
depth: standard
decision: pending
---

# tirvi — Product, Architecture & MVP Scoping Research

## Executive Summary

- **Market gap is real (high confidence).** Israel has 500k+ students with dyslexia; 54% of high-schoolers received Bagrut accommodations in 2021 (Taub Center, up from 35% in 2011). The 2024 MoE move to replace human readers with "computerized reading" drew public criticism for being "cold, rigid, not adjustable" — that *is* tirvi's wedge. No commercial product today combines Hebrew OCR, Hebrew NLP/disambiguation, and Hebrew TTS into an exam-shaped reader; building blocks (DictaBERT, Nakdan, Phonikud, Google he-IL TTS) all exist but no one has wired them together vertically.
- **Architecture is sound with six concrete changes** (top three: add a `WordTimingProvider` port with a forced-alignment fallback because Hebrew SSML `<mark>` support is unverified; add manifest objects with conditional writes for fan-in; expect to add a small relational DB once auth ships).
- **The PRD's tech picks need updates.** Replace `AlephBERT + YAP` primary with **DictaBERT 2.0 (large-joint)** — strict SOTA on UD-Hebrew as of 2024-25 — and add **Dicta-Nakdan** (diacritization) + **Phonikud** (G2P with stress/shva/IPA, June 2025) which were purpose-built to plug into TTS. Keep AlephBERT/YAP only as fallback. **TTS routing must be split**: Google Wavenet he-IL (SSML+timepoints) for word-sync UI; **Chirp 3 HD does NOT support SSML** so use it only when timing isn't needed. Evaluate **Azure `he-IL HilaNeural/AvriNeural`** as the cleaner word-timing path (`<bookmark>` + `WordBoundary` events).
- **Three risks rise to "treat as gating": (R1)** real-Bagrut use is likely *not* permitted on student-supplied SaaS — tirvi should be reframed as a **practice-and-prep tool**, not an in-exam tool, until an MoE pilot proves otherwise; **(R2)** the PRD's ≥90% pronunciation SLO is not defensible without an internal MOS study with dyslexic teens; **(R3)** uploading exam PDFs raises copyright (commercial practice books) and PPL Amendment 13 exposure on minors' data — default TTL should drop from 7 days to 24 hours.
- **Cost target conditionally passes.** First-time per-page is **$0.026 on Wavenet** (~30% over $0.02), **$0.008 on Standard**, **$0.047 on Chirp 3 HD**, **$0.075–$0.15 on ElevenLabs**. TTS is 92–96% of first-time cost. Aggressive content-hash audio cache gets amortized cost <$0.02 at any cache-hit >25%. Studio voices are not available for he-IL — ignore.
- **Recommended MVP shape:** "Standard MVP, practice-mode framing" (Option B below) — keeps the architecture as proposed, drops handwriting and accounts from MVP, treats real-Bagrut as a v2 milestone, and lands the moat in the **reading-plan + diacritization** layer rather than the TTS layer. Confidence **High** on direction; **Medium** on quantitative SLOs (need internal benchmarks).

## Research Question and Why It Matters

Is the tirvi product approach — a Hebrew exam reader built around an "OCR → Hebrew linguistic interpretation → reading plan → TTS" pipeline — sound? Specifically: does the market gap warrant building it; are the proposed tech stack and architecture appropriate; what design principles and benchmarks should govern it; and what is a defensible epic/feature-level MVP plan?

The matter is load-bearing because tirvi's defensibility hinges entirely on the linguistic-interpretation middle layer: the OCR and TTS pieces are commodities behind adapters, but if Hebrew NLP can't disambiguate homographs and acronyms in exam-shaped content well enough that dyslexic students *trust* the audio, the product fails — regardless of how clean the GCP architecture is.

## Project Context

tirvi (current PRD/HLD) is a web app where a student uploads a Hebrew exam PDF and gets back a synchronized listen-and-read experience. Stack: Next.js/React frontend, FastAPI on Cloud Run, Cloud Tasks for async, Cloud Storage as primary store (no DB in MVP), Tesseract `heb` (with Document AI fallback) for OCR, AlephBERT + YAP for Hebrew NLP, Google Cloud TTS he-IL for synthesis. All dev runs in one Docker compose. PRD targets: ≥90% words pronounced correctly, ≥95% on common acronyms, time-to-first-audio ≤30 s p50 / ≤90 s p95 for a 5-page scanned exam, sentence-level cached-audio playback <300 ms, ≤$0.02 per processed page amortized, 7-day default TTL. Primary users: Hebrew-speaking high-school + university students in Israel with formal reading accommodations.

## 1. Market Evidence — The Gap Is Real

**Population & policy.** ~500k Israeli students with dyslexia; **54% of high-schoolers received Bagrut accommodations in 2021** (vs. 35% in 2011 and ~15% international LD prevalence; Taub Center, 2024). Level-1 accommodations alone jumped 8% → 40% (2016→2021) and explain the entire rise in Bagrut qualification rates 2016–2020. Accommodations are governed by MoE pedagogical-administration circulars (חוזר נהלים — אגף לקויות למידה / שפ"י), with three levels: Level 1 (extra time, font enlargement) approved by the school; Levels 2–3 (reading aloud — הקראה, dictation, modified content) approved by **district accommodation committees (ועדות התאמות מחוזיות)**. Universities run separate ועדות לקויות למידה; TAU/HUJI/BGU all have dedicated diagnostic + accommodations offices.

**The 2024 flashpoint.** MoE announced students with dyscalculia/dysgraphia would lose human readers in math Bagrut, replaced by "computerized reading" (הקראה ממוחשבת). Public outcry from parents and educators: the replacement is "cold, rigid, not adjustable in real time" — explicitly missing replay-this-sentence, slow-this-word, jump-back-to-question. **This is direct evidence that (a) policy is moving toward digital readers, and (b) current digital readers are perceived as inadequate substitutes.** That gap is tirvi's wedge.

**Existing tools, ranked by Hebrew-exam fit:**

| Tool | Hebrew | Strength | Gap for exam reading |
|---|---|---|---|
| ElevenLabs (v3, Flash v2.5) | Yes (TTS in 70+ langs) | Best voice naturalness; ~75 ms latency; word-level timestamps | No exam structure; no diacritization; STT WER 10–25% ("Good") — TTS quality proportional |
| Speechify | Hebrew via TTS pipeline | Origin product for dyslexia | Generic article reader; no question/answer structuring; no math handover |
| NaturalReader | Hebrew (Israel) listed | Mature, dyslexia-positioned | Generic doc TTS; no exam-aware OCR |
| Voice Dream Scanner | **Excluded** | Strong on iOS for dyslexia | Hebrew OCR path unsupported |
| Microsoft Immersive Reader / Edge Read-Aloud | Limited | Free, classroom-deployed | RTL layout known issues; no exam structure |
| Kurzweil 3000 | Not listed for Hebrew | Gold-standard exam-prep tool in US | Hebrew not a listed voice |
| Read&Write (Texthelp) | No public Hebrew listing | Strong UK/US ed-tech foothold | No first-class Hebrew |
| Dicta tools (Nakdan, DictaLM, Phonikud) | **Native** | SOTA Hebrew NLP building blocks (Bar-Ilan) | Not a reader product — components only |
| MoE 2024 "computerized reading" pilot | Native, official | In-Bagrut sanctioned | Criticized as "cold, rigid, not adjustable" |

**Where Hebrew tools fail today (every claim cited in the precedent agent's report; full URLs in §Sources):**
- No diacritization or homograph disambiguation in commercial Hebrew TTS — none of ElevenLabs/Speechify/NaturalReader pipes through a Nakdan-equivalent.
- No exam structural awareness: question stem vs. answer choices vs. table cells vs. footnotes are read top-to-bottom.
- Acronym/abbreviation handling: Hebrew has unusually heavy acronym density (ד״ר, ביה״ס, חז״ל) — generic TTS spells them letter-by-letter.
- Hebrew/English/math switching: in-line script switching is the norm in Bagrut English/math/physics; even ElevenLabs handles it imperfectly, and **Google's `<lang>` SSML tag does not support Semitic switches** per Google's own docs.

**Distribution & GTM channels in Israel** (ranked by realism for MVP):
1. **High-school מרכזי למידה + מורי שילוב + רכזי התאמות** — first-touch for student/parent; the natural pilot bed.
2. **NGOs**: Nitzan (אגודת ניצן), Marom (מרום), dyslexia.org.il community.
3. **University accessibility deans** (TAU, HUJI, BGU, Sapir, Ono) — direct procurement; each has a דקאנט/מרכז נגישות with budgets.
4. **Bagrut prep / private tutoring market** — large private spend, fastest direct-to-parent SaaS path.
5. **MoE Exams Department** (אגף הבחינות / שפ"י) — eventual pilot, *not* MVP entry.

## 2. Hebrew Tech Landscape — 2025–2026

This section overrides parts of the PRD's stack §9.

### 2.1 OCR

| Tool | Hebrew quality | Layout-aware | License | Cost | Notes |
|---|---|---|---|---|---|
| **Tesseract `heb` (tessdata_best)** | Decent on clean print; degrades on scans | Basic (PSM modes); no native RTL columnar tables | Apache-2.0 | Free | Best free baseline |
| **Google Document AI / Cloud Vision OCR** | Strong; layout-aware (Form Parser, OCR processor handles tables/columns) | Yes | Commercial | ~$1.50/1k pages | Strongest paid baseline |
| Azure AI Vision Read OCR (he) | Hebrew supported; lines+words+regions | Yes | Commercial | ~$1/1k pages | Decent; less common in Hebrew lit |
| **DeepSeek-OCR (2025)** | Architecturally supports RTL; 100+ langs; 97% retention with 10× compression | Yes (dynamic resolution) | MIT | Self-host GPU | New 2025 VLM; no published Hebrew score yet — **watch-list** |
| olmOCR / olmOCR 2 (AI2) | English-tuned base; not Hebrew-evaluated | Best-in-class for math/tables (2025) | Apache-2.0 | Self-host GPU (7B VLM) | **Math/tables** advantage but unproven on he |
| Surya OCR (Datalab) | 90+ langs incl. RTL — but **Datalab's own benchmark explicitly skipped RTL**, which is a yellow flag | Yes — layout, reading order, table rec | Modified Apache (free <$5M rev) | Self-host GPU | Caution flag |
| Kraken | Strong on historical Hebrew/Yiddish (Jochre 3) | Line-based | Apache-2.0 | Free | Better for historical/handwritten than modern exams |
| EasyOCR / PaddleOCR | Hebrew supported but weaker | Weak layout | Apache-2.0 | Free | Often weaker than Tesseract on Hebrew |

**Recommendation:** Keep the PRD's "Tesseract default, Document AI fallback" but **also pilot DeepSeek-OCR** as an alternate self-host option behind the same `OCRBackend` port — the 2025 VLM era is rewriting this comparison and tirvi should benchmark on its own real exam pages before committing. olmOCR-2 is a strong watch-list item specifically for math-heavy Bagrut content.

**Critical gap:** there is no published peer-reviewed Hebrew-specific OCR benchmark. A 20-page held-out tirvi benchmark (digital-born + scanned + handwriting) is mandatory before any vendor lock-in conversation.

### 2.2 NLP / Morphology / Disambiguation / Diacritization

| Model | Tokenize | Morph/POS | Disambiguation | NER | Diacritization | License |
|---|---|---|---|---|---|---|
| AlephBERT (Onlplab, Bar-Ilan) | Yes | SOTA in 2021 | Good | Good | No | CC |
| AlephBERTGimmel (Dicta) | Yes (52k vocab) | Strong | Strong | Strong | No | CC |
| **DictaBERT 2.0 / large-joint (Dicta)** | Yes | **SOTA on UD-Hebrew (2024-25)** | **SOTA** | **SOTA** | (separate Nakdan) | CC |
| HeBERT / HeRO | Yes | Competitive | — | — | No | Open |
| HebPipe | Marmot-based | UPOS 96.43%, UFeats 90.77%, LAS 89.95% on UD_Hebrew-IAHLTwiki | Good | Yes | No | Open |
| YAP | Yes | Older (rule+ML) | Older | — | No | Apache-2.0 |
| Stanza Hebrew / Trankit | Yes | Decent | Decent | Yes | No | Apache-2.0 |
| Nakdimon | — | — | — | — | Strong; recommended for SASPEECH | Open |
| **Dicta Nakdan** | — | — | — | — | **Hybrid neural+rules; up to ~86.86% word-level accuracy** | API + research |
| D-Nikud | — | — | — | — | Faster than Dicta/Nakdimon | Open |
| **Phonikud (June 2025)** | — | — | — | — | **G2P with stress + vocal-shva, IPA output, real-time** | Open |
| MenakBERT | — | — | — | — | Competitive in domain | Open |

**Recommendation (this is the biggest stack revision):**
- **Replace AlephBERT primary with `dicta-il/dictabert-large-joint`** — covers prefix segmentation, morphological disambiguation, lemma, dependency parsing, NER from one model.
- **Add Dicta-Nakdan** as the diacritization stage (best free professional diacritizer, tracked across published work).
- **Add Phonikud** between diacritization and TTS — purpose-built for real-time Hebrew TTS, predicts stress and vocal shva, outputs IPA. This is the layer that makes the difference between "TTS that pronounces the right phonemes" and "TTS that emphasizes the right syllable."
- **Drop YAP** to a fallback or remove. HebPipe stays useful for CoNLL-U pipeline / coreference, but DictaBERT covers the daily path.

**Why this matters strategically.** Per the user's note (Bar-Ilan ONLP Lab pointer), Tsarfaty's research line is *"context-aware Hebrew reading through morphological disambiguation, pronunciation prediction, and exam-domain adaptation"* — *not* RL on Hebrew. The right academic framing for tirvi is the same: the moat is **per-domain Hebrew morphology + nikud + G2P**, not a novel TTS engine. That's the conversation that makes ONLP Lab, Dicta (Bar-Ilan), and HUJI's adiyoss-lab (HebTTS) potential collaborators rather than competitors. See §11.

### 2.3 TTS

| Provider | Hebrew voices | Naturalness | Word-timing API | Cost | Notes |
|---|---|---|---|---|---|
| **Google Cloud TTS he-IL Standard / Wavenet / Neural2** | 4–8 voices | OK / Good | **`<mark>` timepoints via v1beta1 SSML_MARK** — but **Hebrew support not explicitly documented**, and there are reported regressions (timepoints stop after first sentence on some voices) | $4 / $16 / $16 per 1M chars | Free 4M Standard + 1M Wavenet/month |
| **Google Cloud TTS he-IL Chirp 3 HD (2025)** | New tier | Best-in-class | **Chirp does NOT support SSML** — plain text only; no `<mark>`; no `<lang>` switch; pause control NOT available | $30 / 1M | Use only when word-sync isn't needed |
| **Azure Speech he-IL** | `he-IL-HilaNeural`, `he-IL-AvriNeural` | Good neural; HD voices add `WordBoundary` | **Yes — `<bookmark>` BookmarkReached + `WordBoundary` events**; supports `<lang xml:lang="en-US">` mid-utterance | $16 / 1M Neural | **Cleanest production word-timing API for he-IL** |
| Microsoft Edge TTS Hebrew | Same Hila/Avri via Edge endpoint | Same as Azure | Limited (no official mark API) | Free (TOS-limited) | Not for production |
| **ElevenLabs Hebrew (v3, Flash v2.5)** | Any voice via multilingual; Hebrew listed | Very high voice; Hebrew rated "Good" (10–20% WER STT proxy) | **Yes — "create speech with timestamps" returns char-level timing** | $50–$100 / 1M chars (Flash / Multilingual) | Pricey at scale |
| Roboshaul / SASPEECH (Imvelife) | One speaker (Shaul) | Decent for podcast voice | Self-built; no native mark | MIT/CC | Needs diacritized input |
| Coqui XTTS-v2 / Zonos-Hebrew (2025 fine-tune on SASPEECH+Phonikud) | Multi-speaker zero-shot | Improving 2025 | Requires aligner | Open | Promising self-host watch-list |
| Bark / Tortoise / OpenVoice / MMS | No first-class Hebrew | Poor on he | — | Open / CC-BY-NC | Not viable for production Hebrew exams |

**Recommendation:** split TTS routing — this is a hard-earned finding from the explorer + architect agents:

| Use case | Voice | Reason |
|---|---|---|
| Word-sync highlight player | **Google `he-IL-Wavenet-D`** (or Neural2 once verified) | SSML `<mark>` timepoints; cheaper |
| Premium "continuous play" mode | **Google `he-IL-Chirp3-HD`** | Highest naturalness, no word-sync needed |
| Production word-timing pipeline (recommended primary) | **Azure `he-IL-HilaNeural`** | Cleanest `<bookmark>` + `WordBoundary` API; supports inline `<lang>` switch |
| Premium tier upsell | **ElevenLabs Multilingual v2 + timestamps endpoint** | Optional |
| Forced-alignment fallback | **WhisperX + Hebrew wav2vec2** | When non-mark voices used |

**Big gotcha that the PRD must absorb:** Google `<lang>` SSML tag returns silence for Hebrew/Arabic/Persian, and `<mark>` timepoint support on he-IL is unverified end-to-end. Do not architect a one-vendor TTS path; design the `WordTimingProvider` port from day one with TTS-emitted-marks and forced-alignment adapters in parallel.

### 2.4 Acronym / Number / Math / Mixed-Language

- **Dicta acronym tools** — Dicta hosts an acronym expander; Otzar Roshei Tevot (Ashkenazi & Yarden) is the canonical lexicon to seed a curated dictionary.
- **`num2words` Hebrew** (`lang='he'`) — verify pin; supplement with custom rule layer for ordinals (ראשון, שני…) and gendered counters (סעיף ב, שאלה 3א).
- **Phonikud** handles ambiguous letters (בּ vs ב, וּ vs ו) and is the cleanest path to phoneme-level mixed-language pronunciation when a Hebrew sentence contains an English word.
- **Math** has no Hebrew-specific library; plan a Hebrew templating layer ("x בריבוע" for x²). MathSpeak / SRE handles English math and would need Hebrew localization work.
- **Mixed language**: because Google's `<lang>` doesn't support he, switch to Azure for inline `xml:lang="en-US"` blocks, or split the call and stitch.

## 3. Architecture Fit

**Verdict: SOUND-WITH-CHANGES.** Cloud Run + GCS + adapter-port skeleton is a defensible MVP shape. Six concrete changes ranked by importance:

1. **Add a `WordTimingProvider` port with two adapters from day one** — TTS-emitted timepoints (cheap, preferred) and WhisperX/MFA forced alignment (fallback). Hebrew `<mark>` support is unverified; without this, a missing-timepoint bug becomes architectural.
2. **Manifest objects with conditional writes (`x-goog-if-generation-match`) for fan-in.** Pure write-then-enqueue handles fan-out only; per-page parallelism (5 pages → 5 NLP tasks → wait → 1 plan) needs a coordinator. GCS gives strong read-after-write and atomic single-object overwrite, so a `manifests/{doc}.json` updated under preconditions is the smallest correct fix.
3. **Set `min-instances=1` and `--cpu-boost`** on the OCR/NLP worker during business hours. A Cloud Run worker with `min-instances=0` typically pays 3–5 s for Python import + model load on first hit; this protects the 30 s p50 target.
4. **Keep ports rich.** `OCRBackend.ocr_pdf()` returns an `OCRResult` with bboxes/conf/lang hints; `TTSBackend.synthesize()` returns a `TTSResult` with audio + timepoints + voice meta. Don't return `bytes`. Hexagonal's documented anti-pattern is interface explosion / lowest-common-denominator abstractions; tirvi specifically needs to keep timepoints and bbox/conf detail.
5. **Plan a small relational DB as a known-future addition** for `users`, `documents`, `sessions` once auth ships. GCS-as-DB is fine for the artifact layer (PDFs, audio, NLP outputs) — it breaks once you need "list this user's last 20 docs", dedup, full-text search, or any analytics.
6. **Document a 16 GB dev-machine floor** and gate the model sidecar behind a compose profile (`--profile models`) so a frontend dev can run `web` + mocked APIs cheaply. AlephBERT/DictaBERT (~500 MB on disk, ~1.2–1.5 GB resident) plus YAP plus runtimes plus `web`+`api`+`worker`+`fake-gcs-server` realistically lands at 8–12 GB resident.

**On Cloud Tasks vs. Pub/Sub vs. Workflows:** Cloud Tasks is correct for tirvi (explicit invocation, per-task target, dedup, per-queue rate caps). One queue per stage is the right retry-isolation pattern. Workflows would also fit and gives durable orchestration, but adds a second control plane and an extra delivery-guarantee seam — overkill for an MVP with five stages.

**On NFR alignment:** OCR is the long pole (3–8 s/page typical for Tesseract or Document AI). Five pages in parallel via Cloud Tasks fan-out → 6–10 s; NLP 2–4 s; TTS first-block 1–2 s if streamed. Total p50 ~15–25 s, comfortably inside the 30 s target *if* OCR retries don't compound. p95 ≤ 90 s is realistic only with fast-fail backoff capped at 30 s.

## 4. Risk Register

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| **R1** | Real-Bagrut use not permitted on student-supplied SaaS — product is only practice/prep | High | Critical | Reframe MVP as practice tool; pursue MoE pilot as v2 |
| **R2** | Hebrew TTS naturalness/accuracy below accommodation grade (≥90% target undefendable without internal MOS study) | High | Critical | Run a blinded MOS study with dyslexic teens before commit |
| **R3** | Homographs / mispronunciation on Tanakh, science, civics | High | High | Diacritization pre-pass (Dicta-Nakdan) per domain; Phonikud G2P |
| **R4** | Handwritten student answers OCR fails | High | Medium | Scope out handwriting in MVP — print only |
| **R5** | Bagrut content / publisher copyright on uploads | Medium-High | High | DMCA-style takedown; user attestation; never republish |
| **R6** | Privacy: minors uploading personal accommodation context (PPL Amendment 13 in force 14-Aug-2025; PPA 2025 AI Guidelines) | High | High | DPIA, parental consent ≥14, minimize accommodation data |
| **R7** | 7-day TTL too long for confidential exam content | Medium | Medium | **Default TTL = 24h**; 7-day opt-in only |
| **R8** | ≤30 s p50 first audio infeasible on 5-page scan | Medium | Medium | min-instances=1; pre-warm; stream first block |
| **R9** | Vendor lock-in to Google Cloud TTS pricing/voices | Medium | Medium | Adapter pattern; cache audio aggressively; route Wavenet vs. Chirp by use case |
| **R10** | Adoption without school partnership | High | High | Go-to-market via accommodation coordinators, not ASO |
| **R11** | Single-Docker compose with all NLP weights | Medium | Low | Make NLP service optional in dev (compose profile) |
| **R12** | Cybersecurity-of-minors regulatory tightening | Medium | Medium | Age-gate; parental consent; minimal data |

**Top 3 (gating):**

**R1 — Real-Bagrut allowance.** MoE administers הקראה ממוחשבת on its own systems. There is no public source confirming a third-party cloud TTS may be used in a live Bagrut session; combined with the obvious cheating-vector concern (an internet device in an exam room), the most realistic path is that tirvi cannot replace the human reader during a real Bagrut. This means the PRD's framing "accommodation-grade exam reading" over-promises. The honest MVP is a **practice-and-prep** tool used at home; SLOs (≥90% pronunciation, ≤30 s first audio) should be re-derived from "students studying at home" needs, not "students under timed exam stress."

**R2 — TTS quality empirical gap.** No published MOS comparing Google Cloud he-IL Neural2/Chirp3 against any reference; no published WER for a Hebrew TTS reading bagrut content. The HebTTS Interspeech 2024 paper (HUJI adiyoss-lab) explicitly identifies diacritic-free Hebrew TTS as an open problem. **The PRD's ≥90% word-accuracy and ≥95% acronym SLOs are aspirational rather than evidence-backed**; without an internal user study (dyslexic Hebrew teens listening blind to bagrut passages, rating intelligibility, counting mispronunciations), tirvi has no defensible accommodation claim.

**R3 — IP/privacy exposure.** Past Bagrut papers are state-published, but practice books (bagrut11.com, מטח, Kineret, etc.) are protected under the 2007 Copyright Act. PPL Amendment 13 (in force 14-Aug-2025; GDPR-aligned; PPA enforcement fines) and the April-2025 PPA AI Guidelines require privacy-by-design, transparency, and storage limitation. A 7-day TTL on minors' uploaded exam content is hard to justify under data-minimization. Need: DPIA, DMCA path, "do not upload third-party copyrighted material" attestation, default 24 h TTL.

## 5. Cost Model

**Calculations for a 5-page exam, 1500 chars/page = 7500 chars total.**

| Component | Unit cost | Per-page cost |
|---|---|---|
| OCR (Document AI Enterprise) | $1.50 / 1k pages | **$0.00150** |
| OCR (Tesseract self-host) | compute only | ~$0.0002 |
| NLP (DictaBERT/AlephBERT + YAP, ~10 s/page CPU) | $0.000024 / vCPU-s | ~$0.0003 |
| TTS — Google Standard he-IL | $4 / 1M chars | **$0.0060** |
| TTS — Google Wavenet/Neural2 he-IL | $16 / 1M | **$0.0240** |
| TTS — Google Chirp 3 HD he-IL | $30 / 1M | **$0.0450** |
| TTS — ElevenLabs Multilingual v2 (Hebrew) | $100 / 1M | $0.150 |
| TTS — ElevenLabs Flash v2.5 (Hebrew) | $50 / 1M | $0.075 |
| Storage (GCS Standard, 6 MB/exam, 30-day) | $0.020 / GB-mo | ~$0.00002 |
| Compute (Cloud Run worker, ~30 s @ 1 vCPU + 1 GiB) | $0.000024/vCPU-s + $0.0000025/GiB-s | ~$0.00016 |
| Cloud Tasks ops | $0.40/M after 1M free | negligible |
| Egress (audio playback ~5 MB) | ~$0.12 / GB | ~$0.00012 |
| **Per-page total — Standard voice** | | **≈ $0.008** |
| **Per-page total — Wavenet/Neural2** | | **≈ $0.026** |
| **Per-page total — Chirp 3 HD** | | **≈ $0.047** |

Studio voices ($160/1M) are **not offered for he-IL**, so ignore. Free tiers (4M chars Standard, 1M Wavenet, 1M Chirp 3 HD per month) further reduce real cost at MVP scale — first ~600 exams/month are essentially free on Wavenet.

**Cache-hit total: ~$0.00014/page** (~180× cheaper than first-time Wavenet). At 60% cache-hit rate, amortized = **$0.0105/page** — comfortably under $0.02 even on Wavenet.

**Sensitivity:** TTS dominates 92–96% of first-time cost. The only lever that matters is TTS unit price × characters synthesized.

**Verdict on $0.02 target:** **Conditional pass.** Three paths:
1. **Default to Standard voices** ($0.008/page). Quality may not satisfy the dyslexia UX bar.
2. **Wavenet + cache.** Any cache-hit >25% brings amortized cost ≤ $0.02. Realistic since audio re-reads are likely.
3. **Hybrid:** Standard for full-document playthrough, Wavenet/Chirp HD on user request or for short snippets.

Chirp 3 HD ($0.047/page) and ElevenLabs ($0.075–$0.15) **do not** fit the $0.02 budget without aggressive caching.

**Comparable consumer pricing** (anchors what the market bears): Speechify Premium $11.58/mo annual; NaturalReader Premium $9.99/mo, Plus $19.99/mo; Read&Write K-12 ~$17.25/license/year. Israeli parent/student is anchored at **~₪35–110/month (~$10–30)**. At that ARPU, a student processing 50 pages/month gives $0.20–$0.60/page revenue — comfortably above any per-page cost.

## 6. Comparison Matrix and Evidence Tie-Back

| Criterion | Weight | Current PRD pick | Recommended pick | Notes |
|---|---|---|---|---|
| Hebrew NLP backbone | 25% | AlephBERT + YAP | **DictaBERT-large-joint + Dicta-Nakdan + Phonikud** | SOTA on UD-Hebrew 2024-25; Phonikud purpose-built for TTS pipeline |
| OCR | 15% | Tesseract + Document AI fallback | Same, **plus DeepSeek-OCR pilot** | Watch-list 2025 alternate behind same port |
| TTS | 20% | Google Cloud TTS he-IL | **Google Wavenet (mark-supporting) + Azure he-IL alt for word-sync** | Chirp 3 HD doesn't support SSML; Hebrew `<mark>` unverified end-to-end |
| Compute / async / storage | 10% | Cloud Run + Cloud Tasks + GCS | Same | Sound; add manifest conditional writes |
| Word-timing | 10% | TTS marks only | **TTS marks + WhisperX fallback adapter** | Hebrew mark support unverified |
| Privacy / TTL | 10% | 7-day TTL | **24-hour TTL default** | PPL Amendment 13 + PPA AI Guidelines 2025 |
| MVP scope | 10% | Includes scanned + handwritten implicitly | **Print only; no handwriting; no auth** | Reduces R4, R6 |

### Evidence Tie-Back

| Recommendation | Supporting Agents | Opposing Agents | Confidence |
|---|---|---|---|
| Replace AlephBERT primary with DictaBERT-large-joint | explorer, precedent (Bar-Ilan ONLP→Dicta lineage) | none | High |
| Add Dicta-Nakdan + Phonikud pre-TTS | explorer, critic (R3 mitigation) | none | High |
| Split TTS routing (Wavenet for sync, Chirp 3 HD continuous, Azure as alt) | explorer, architect | cost (Chirp 3 HD overspend) | High |
| Add WordTimingProvider port w/ forced-alignment fallback | architect | none | High |
| Reframe as practice-and-prep tool, not real-Bagrut | critic | precedent (still credible market gap) | High |
| Default TTL 24 h | critic | (operational convenience) | High |
| min-instances=1 on worker (NFR) | architect | cost (small uptick) | Medium |
| GCS-only at MVP, RDB later for auth | architect | (none for MVP) | High |
| $0.02/page pass on Wavenet+cache hybrid | cost | none | Medium-High |

## 7. Recommended Design Principles

1. **The reading plan is the product.** The OCR and TTS are commodities behind adapters; the moat is per-domain Hebrew morphology + diacritization + G2P + structural reading templates. Optimize engineering effort accordingly: 3× as much code in `domain/reading_plan/` as in `adapters/`.
2. **Vendor adapters return rich result objects, not bytes.** `OCRResult`, `TTSResult`, `WordTimingResult` — never lose timepoints, bboxes, or confidence at the port boundary.
3. **Idempotent, resumable, GCS-backed pipeline stages.** Each stage writes its output object, then enqueues the next; reruns are safe; no in-memory state survives a stage.
4. **Cache by content hash, share across users.** This is the single biggest cost lever and the only way the $0.02/page target survives Wavenet voices.
5. **All confidential data has a short default TTL.** 24 h auto-delete; opt-in for longer; no logs of document text.
6. **Privacy-by-design, GDPR-aligned, minor-aware.** PPL Amendment 13 + PPA AI Guidelines 2025 are not optional. DPIA, parental-consent flow ≥14, minimal accommodation context.
7. **Accommodation-grade UX or nothing.** Keyboard-first, WCAG 2.2 AA, `prefers-reduced-motion`, no autoplay, no flashing, visible focus, ≥4.5:1 contrast, font enlargement preset.
8. **Benchmark before commit.** No vendor pick (OCR, TTS, NLP) is final until tirvi's own held-out benchmark says so.
9. **Practice-and-prep first; real-Bagrut later.** Don't ship into a regulatory gap; ship into the studying gap.
10. **The academic story matches the engineering story.** Frame the moat as "context-aware Hebrew reading through morphological disambiguation, pronunciation prediction, and exam-domain adaptation" — that's what wins ONLP Lab / Dicta / HUJI conversations and grant funding (see §11).

## 8. Recommended Benchmarks and Quality Gates

These should become tirvi's internal SLOs and gate every release. Aim to publish them — that's part of the credibility moat.

### 8.1 Tirvi-Hebrew-Exam Benchmark Suite v0

A held-out set of 20 Bagrut-style pages, balanced across:
- 8 digital-born PDFs (clean text)
- 8 scanned PDFs (varied scanner quality)
- 4 handwriting-mixed (post-MVP)
- Subjects: Hebrew literature, civics, math, science, English, Tanakh
- Each page has hand-curated ground truth: text, structural blocks (question/answer/table), pronunciation transcript (IPA), word boundaries

### 8.2 Quality Gates per Stage

| Stage | Metric | MVP gate | Post-MVP gate |
|---|---|---|---|
| OCR | Word Error Rate on tirvi-bench | ≤ 3% digital, ≤ 8% scanned | ≤ 2% / ≤ 5% |
| OCR | Block-segmentation recall (Q stems / A choices / tables) | ≥ 95% Q / ≥ 90% A | ≥ 98% / ≥ 95% |
| Diacritization | Word-level accuracy (Dicta-Nakdan + Phonikud combined) | ≥ 85% | ≥ 90% |
| Disambiguation | Homograph correct-pronunciation rate | ≥ 85% | ≥ 92% |
| Acronym expansion | Coverage on curated 200-acronym list | ≥ 95% | ≥ 98% |
| TTS | Mean Opinion Score (blind, 5-point scale, dyslexic teen panel n=10) | ≥ 3.5 | ≥ 4.0 |
| Word-timing | Mean alignment error vs. ground truth | ≤ 80 ms | ≤ 50 ms |
| Time-to-first-audio | p50 / p95 on 5-page scan | ≤ 30 s / ≤ 90 s | ≤ 15 s / ≤ 60 s |
| Cached playback latency | First byte | ≤ 300 ms | ≤ 200 ms |
| Cost per processed page | Amortized across 30-day window | ≤ $0.02 | ≤ $0.01 |

The MOS study **must run before the v1 launch**; without it, every other gate is form over substance.

## 9. Scoping Alternatives — Three MVP Shapes

### Option A — "Slim MVP" (digital-born only, Standard voice, no word-sync)

- **Scope:** PDFs with embedded text only (no OCR for scanned). Standard he-IL TTS. Page-level playback only (no per-question, no word highlight).
- **Pro:** Cheapest; fastest to market; no OCR risk; cost ~$0.008/page; ships in ~6 weeks.
- **Con:** Misses scanned exam content (the typical Bagrut practice book is scanned). Misses the structural reading-plan differentiator. Easy for ElevenLabs/Speechify to copy.
- **Fit:** Useful as an alpha for a school partnership only; **not recommended as the public MVP** — undersells the moat.

### Option B — "Standard MVP, practice-mode framing" (RECOMMENDED)

- **Scope:** PDFs (digital + scanned, no handwriting). Tesseract + Document AI fallback. **DictaBERT + Dicta-Nakdan + Phonikud** Hebrew NLP. Google Wavenet primary TTS + Chirp 3 HD continuous-play. WordTimingProvider with TTS-marks + WhisperX fallback. Per-block playback, repeat sentence, speed control, font size, word-sync highlight, side-by-side viewer. Anonymous session model (browser-local). 24-hour default TTL. **Practice/study tool framing — not in-Bagrut.**
- **Pro:** Lands the moat (structural reading + diacritization). Fits cost target via cache. Ships an accommodation-grade UX. Defensible against ElevenLabs.
- **Con:** ~16-week build; needs internal MOS study before v1; school-partnership distribution is slow.
- **Fit:** **This is the recommended MVP.**

### Option C — "Practice-and-prep premium tier with academic anchor"

- **Scope:** Option B + collaborator pilot with one of {Bar-Ilan ONLP Lab, Dicta, HUJI adiyoss-lab}; co-published Hebrew-exam benchmark; "powered by DictaBERT/Phonikud" credibility; consumer subscription tier (~₪50/month).
- **Pro:** Strong academic credibility; differentiated product narrative; potential grant funding (CHE / חוק שוויון / KAMIN Industrial NLP grants); harder for big-tech to replicate.
- **Con:** Adds 2–3 months of partnership + co-design. Not a unilateral build.
- **Fit:** Recommended **as the v1.1 milestone after Option B ships** — the academic conversation can start now (per the user's email-drafting context) but should not block MVP.

## 10. Recommended Epic / Feature Implementation Plan (Option B)

Eleven epics, ~38 features. Each epic is a coherent slice with its own design pipeline + design review; features map to TDD tasks. **Detailed design happens in `.workitems/` per the SDLC harness, not here.**

### Phase 0 — Setup (week 0)

- E0 — **Foundation & DevX**
  - F0.1 Single-Docker compose (`web` / `api` / `worker` / `models` / `fake-gcs-server`)
  - F0.2 Cloud Run + Cloud Tasks + GCS skeleton (Terraform)
  - F0.3 Adapter ports + fakes (StorageBackend, OCRBackend, TTSBackend, WordTimingProvider, NLPBackend)
  - F0.4 CI/CD with TDD gate, complexity gate (CC ≤ 5), security scan
  - F0.5 16 GB dev floor documented; `--profile models` compose profile

### Phase 1 — Ingest & OCR (weeks 1–3)

- E1 — **Document ingest**
  - F1.1 Signed-URL upload flow (≤ 50 MB)
  - F1.2 Manifest object with conditional writes
  - F1.3 Per-document status + per-page status
  - F1.4 Delete-with-cascade (PDF + derived artifacts)
  - F1.5 24-hour TTL + bucket lifecycle rules
- E2 — **OCR pipeline**
  - F2.1 Tesseract `heb` adapter (LSTM + tessdata_best, layout post-processor)
  - F2.2 Document AI adapter (paid fallback)
  - F2.3 OCRResult contract with bboxes + confidence + lang hints
  - F2.4 Block-level structural detection (heading, instruction, question stem, answer option, paragraph, table, figure caption)
  - F2.5 Question-number / answer-option-letter tagging
  - F2.6 OCR benchmark harness against tirvi-bench v0

### Phase 2 — Hebrew Interpretation Core (weeks 4–8) — THE MOAT

- E3 — **Normalization**
  - F3.1 Repair OCR artifacts (broken lines, stray punctuation, directionality)
  - F3.2 Number/date/percentage/range to spoken form (`num2words` + custom rules)
  - F3.3 Acronym lexicon (curated from Otzar Roshei Tevot + Dicta) with expansion
  - F3.4 Mixed Hebrew/English/math span detection + language tagging
  - F3.5 Math expression detection + Hebrew math template
- E4 — **NLP & disambiguation**
  - F4.1 DictaBERT-large-joint adapter (segmentation, morph, lemma, NER)
  - F4.2 Optional AlephBERT + YAP fallback path
  - F4.3 Per-token POS + morph + lemma in `nlp.json`
  - F4.4 HebPipe CoNLL-U fallback for coreference (post-MVP gate)
- E5 — **Pronunciation prediction**
  - F5.1 Dicta-Nakdan adapter (diacritization)
  - F5.2 Phonikud adapter (G2P, stress, vocal shva, IPA)
  - F5.3 Curated homograph lexicon override (top 500 Hebrew homographs)
  - F5.4 Confidence scoring on disambiguation
- E6 — **Reading plan generator**
  - F6.1 Block-typed reading plan output (`plan.json` with tokens + lemma + pos + hint)
  - F6.2 SSML shaping per block type (question slow/emphasized; `<break>` between answers)
  - F6.3 Inline `<lang xml:lang="en-US">` switching for English spans (Azure path)
  - F6.4 Math reading template
  - F6.5 Table reading template (row-by-row with column headers)

### Phase 3 — Audio Synthesis & Word-Sync (weeks 9–11)

- E7 — **TTS adapters**
  - F7.1 Google Wavenet he-IL adapter (SSML + `<mark>` timepoints via v1beta1)
  - F7.2 Google Chirp 3 HD he-IL adapter (continuous-play mode, no SSML)
  - F7.3 Azure he-IL `HilaNeural`/`AvriNeural` adapter (`<bookmark>` + `WordBoundary`)
  - F7.4 Voice selection policy (per-block by use case)
- E8 — **Word-timing & cache**
  - F8.1 WordTimingProvider port (TTS-emitted + forced-alignment adapters)
  - F8.2 WhisperX Hebrew adapter (fallback alignment)
  - F8.3 Content-hash audio cache in GCS
  - F8.4 Sentence-level cache key (cross-document reuse)

### Phase 4 — Player UI (weeks 11–13)

- E9 — **Accessibility-grade player**
  - F9.1 Side-by-side viewer (PDF page image + cleaned text)
  - F9.2 Per-block play affordances (read question only / read answers only)
  - F9.3 Word-sync highlight (Web Audio API + word-timing)
  - F9.4 Controls: play/pause, speed (0.5×–1.5×), repeat sentence, next/prev block, font size, high-contrast mode
  - F9.5 Long-press to spell a word letter-by-letter
  - F9.6 WCAG 2.2 AA conformance (keyboard, focus, contrast, `prefers-reduced-motion`)

### Phase 5 — Quality, Privacy, Closure (weeks 13–16)

- E10 — **Quality validation**
  - F10.1 Tirvi-Hebrew-Exam Benchmark v0 (held-out 20 pages)
  - F10.2 OCR / NLP / TTS quality gates wired into CI
  - F10.3 Blind MOS study with dyslexic teen panel (n=10)
  - F10.4 Latency profiling against ≤30 s p50 / ≤90 s p95
  - F10.5 Cost telemetry per processed page
- E11 — **Privacy & legal**
  - F11.1 24-hour default TTL + lifecycle automation
  - F11.2 DPIA + parental-consent flow (≥14)
  - F11.3 Upload attestation (no third-party copyrighted material)
  - F11.4 No-PII logging audit
  - F11.5 Feedback capture ("word X was read wrong") → `feedback/*.json` (no live retraining)

### Deferred to v1.1 / v2

- Handwriting OCR (Bagrut handwritten answers)
- User accounts (move to small Cloud SQL)
- Real-time WebSocket status (currently polling)
- Custom voices / teacher's voice
- Long-form non-exam content (textbooks)
- Live correction loop (write feedback → lexicon updates)
- MoE pilot toward in-Bagrut use
- Custom Zonos-Hebrew TTS self-host (open-source TTS path)
- Math/SRE Hebrew localization
- Mobile-native apps

### Sequencing rationale

Phases 0 → 1 → 2 → 3 → 4 → 5 are mostly serial because of dependencies: OCR feeds NLP feeds reading plan feeds TTS feeds player. **The exception is the player UI (E9), which can start in week 9 in parallel with E7/E8 by mocking the TTS+timing layer with fixtures.** Phase 5 quality work (E10) starts as soon as E2 produces real OCR — its benchmark harness should be in place before NLP development to keep regressions visible.

## 11. Academic Collaboration Pathways

Per the user's pointer, Bar-Ilan ONLP Lab (Reut Tsarfaty) has released the foundational Hebrew NLP stack — AlephBERT, YAP, Multilingual Seq2Seq for Hebrew (ACL 2023), HeTrue, Hebrew word2vec (Goldberg). The right academic framing for tirvi is **"context-aware Hebrew reading through morphological disambiguation, pronunciation prediction, and exam-domain adaptation"** — *not* RL, which isn't Tsarfaty's central line. Three concrete partnership candidates:

| Institution / Lab | Asset | Tirvi conversation |
|---|---|---|
| **Bar-Ilan ONLP Lab (Tsarfaty)** | AlephBERT, YAP, ACL 2023 Hebrew Seq2Seq | "Your morpho-syntactic disambiguation work is exactly what tirvi needs upstream of TTS — would you advise on exam-domain adaptation?" |
| **Dicta (Bar-Ilan, Koppel et al.)** | DictaBERT family, Dicta-Nakdan, DictaLM 2.0/3.0 | Direct dependency. "tirvi runs DictaBERT + Nakdan in production for accommodation-grade Hebrew TTS." Potentially APIs / partnership. |
| **HUJI adiyoss-lab (Adi & Yossi)** | HebTTS (Interspeech 2024), Phonikud (June 2025) | Phonikud is the G2P layer in tirvi's pipeline; HebTTS work is the closest published evaluation of Hebrew TTS quality. Co-publication of a Hebrew-exam TTS benchmark is plausible. |
| Bar-Ilan NLP (Goldberg) | Hebrew word2vec, broader NLP | Historical reference; not a direct dependency. |

**Suggested email opener** (per the user's "email" context): *"I noticed your lab has released open Hebrew NLP resources such as AlephBERT and YAP, which seem highly relevant to the problem of contextual disambiguation before speech synthesis."* That's an honest signal of homework done; pair with one specific question (e.g., "Have you observed how AlephBERTGimmel / DictaBERT performs on exam-domain text vs. news?") to make it a real research conversation rather than a generic outreach.

**Funding angles** to mention if it comes up: KAMIN Industrial NLP grants, ISF / Israel Science Foundation accessibility tracks, Magnet/Magneton, HUJI/BIU innovation centers, MoE Education Innovation grants. Tirvi can plausibly apply as either an industrial PI (DictaBERT-as-customer) or as a co-PI on an "exam-domain Hebrew NLP" track.

## 12. Open Questions for ADR Backlog

These are the decisions that should land as ADRs in `docs/ADR/` (each ADR captures option set + decision + rationale).

1. **ADR-001: TTS routing policy.** Wavenet-only vs. Azure-only vs. split (recommended). Hebrew `<mark>` validation experiment must precede.
2. **ADR-002: NLP backbone.** AlephBERT (PRD) vs. DictaBERT-large-joint (recommended). With migration plan.
3. **ADR-003: Diacritization + G2P.** Dicta-Nakdan + Phonikud (recommended) vs. lexicon-only (PRD). Quality gate informs.
4. **ADR-004: OCR primary.** Tesseract `heb` (PRD) vs. Document AI vs. DeepSeek-OCR pilot. Driven by tirvi-bench v0.
5. **ADR-005: TTL policy.** 7 days (PRD) vs. 24 hours default + opt-in 7 days (recommended). PPL Amendment 13 alignment.
6. **ADR-006: MVP framing.** Real-exam vs. practice-and-prep (recommended). Drives SLO derivation.
7. **ADR-007: Scope of handwriting.** Out (recommended for MVP) vs. in.
8. **ADR-008: Auth in MVP.** Anonymous session (recommended) vs. accounts. Drives DB introduction.
9. **ADR-009: Word-timing fallback.** WhisperX (recommended) vs. Aeneas vs. MFA. Hebrew acoustic-model availability matters.
10. **ADR-010: Compute primitive for NLP service.** Cloud Run CPU vs. Cloud Run GPU vs. fixed-instance VM. Sensitivity to first-block latency.

## Sources

All access dates **2026-04-28**. Numbered IDs are local to this report; full URLs in the per-perspective agent reports above.

**Market evidence** (precedent agent): Israel National News on dyslexia prevalence; Taub Center 2024 (Bagrut accommodations 35%→54%); MoE שפ"י circulars; Kol-Zchut Bagrut accommodations; Ynet on the 2024 computerized-reading pilot; ElevenLabs Hebrew docs; Speechify / NaturalReader / Voice Dream / Microsoft Immersive Reader documentation; Dicta tools (Nakdan, DictaLM); Phonikud (arXiv:2506.12311); HebTTS Interspeech 2024 (HUJI adiyoss-lab); Israel Dyslexia Association; Nitzan / Marom NGOs; Lotem.

**Tech landscape** (explorer agent): Tesseract `heb` / `tessdata_best`; Hartmann et al. OCR comparison (Springer 2022); Google Vision OCR languages; Azure AI Vision Read; Surya OCR (Datalab); olmOCR + olmOCR-2 (AI2, arXiv:2510.19817); DeepSeek-OCR (arXiv:2510.18234, comparison reviews); Jochre 3 (Yiddish OCR with Kraken); AlephBERT (arXiv:2104.04052); AlephBERTGimmel (NNLP-IL Hebrew Resources); DictaBERT (arXiv:2308.16687); `dicta-il/dictabert-large-parse`; HebPipe; D-Nikud (arXiv:2402.00075); Nakdan ACL 2020 demos; Phonikud (arXiv:2506.12311); Google Cloud TTS supported voices, SSML reference, release notes; Google Issue Tracker on Neural2 timepoints regression; Chirp 3 HD docs; Azure Speech language/voice support, SSML structure & events, HD voices; ElevenLabs models + create-speech-with-timestamps; Robo-Shaul / SASPEECH; Zonos-Hebrew (Medium, 2025); WhisperX (arXiv:2303.00747); Aeneas; MFA models; Dicta tools index.

**Architecture fit** (architect agent): Cloud Run "executing asynchronous tasks"; "Choose Cloud Tasks or Pub/Sub"; "Cloud Run Jobs vs Cloud Batch" (Mar 2026); Hexagonal Architecture (Cockburn); "Hexagonal Architecture in Python" (Medium / 2026 update); Cloud Tasks dual overview; "Queue workflow executions using Cloud Tasks"; Cloud Run optimize response times; Cloud Storage consistency; "Is object storage good for databases?" (Computer Weekly); SSML `<mark>` timepointing regression report; Cloud TTS SSML reference; WhisperX repo; forced-alignment ASR comparison (arXiv:2406.19363); Cloud Run min-instances; Speechify "Real-Time TTS at Scale"; YAP intro (NNLP-IL); AlephBERT (arXiv:2104.04052).

**Risk & critic** (critic agent): MoE Bagrut accommodations parents portal; Kol-Zchut accommodation framework; Bagrut accommodations practical overviews; HebTTS project page; Roth et al. "Diacritic-Free Hebrew TTS" Interspeech 2024; "Enhancing TTS Stability in Hebrew using Discrete Semantic Units" (arXiv:2410.21502); HandwritingOCR Tesseract vs. AI vs. Document AI; Israel data-protection regulation 2025-26 (PPL Amendment 13); DataGuidance Israel; MoE Bagrut archives; Israeli copyright law guide; D-Nikud diacritization; arnontl PPA AI Guidelines (28-Apr-2025); Cloud Run cold-start tips; FastAPI on Cloud Run tuning; GCP TTS pricing & release notes; AlephBERT base model card.

**Cost** (cost agent): Document AI pricing; Text-to-Speech pricing; Cloud Run pricing; Cloud Tasks pricing; Cloud Storage pricing; Cloud Run GPUs GA blog; CloudZero GCP storage guide 2026; Speechify Wavenet pricing guide; Chirp 3 HD docs; ElevenLabs API pricing + Flexprice breakdown; CheckThat.ai Speechify pricing; NaturalReader cost (Speechify blog); Texthelp pricing; Read&Write education cost; Dicta center; Cloud TTS supported voices and release notes.

---

## Decision Trail

This is a **research artifact** (Tier 5). The recommendations here are inputs to ADRs (§12) and `.workitems/` design pipelines. No engineering commits should be made directly from this document; each load-bearing recommendation must land an ADR first per `.claude/rules/orchestrator.md`.
