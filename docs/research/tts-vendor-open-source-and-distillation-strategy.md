---
tier: 5
version: 1.0
created: 2026-05-30
updated: 2026-05-30
status: current
---

# TTS/OCR Vendor Open-Source Scan & Distillation Strategy

## Purpose

Two questions, settled in one place:

1. Do the commercial OCR/TTS vendors we evaluated ship anything open / self-hostable?
2. Should we "use a paid model to train our own open model" — and is it worth it?

Bottom line: **the bottleneck in tirvi is contextual (homograph/niqqud disambiguation),
not waveform generation.** That reframes the distillation question — the teacher worth
learning from is a reasoning **LLM** producing *contextual labels*, not a **TTS** producing
*audio*. TTS itself is a swappable commodity backend.

See also: `hebrew-homograph-complexity.md`, `reading-disability-pipeline-needs.md`,
`scripts/homograph_judges_bench.py`, `scripts/cascade_demo.py`, `data/homograph-lexicon.yaml`.

---

## 1. Vendor open-source scan (May 2026)

**None of the six open-source their production model.** All are API-only/proprietary for
the core product; "open" activity is peripheral.

| Vendor | Core | Open weights of prod model? | What is actually open | Self-host real product? |
|---|---|---|---|---|
| Reducto | OCR/parsing | No | `RolmOCR` (Apache-2.0, *not* their prod model); SDKs; **RD-TableBench** dataset | No — on-prem = licensed binary |
| ElevenLabs | TTS/STT | No | API client SDKs / MCP / CLI only | No |
| Deepgram | ASR/TTS | No | Client SDKs + on-prem **deploy configs** | "Self-host" = license-gated private **containers** of closed models, not open weights |
| Cartesia | TTS (Sonic) | No (TTS) | Open SSM **language** models (Rene/Llamba/Mamba) + `edge` — *not* Sonic | No — TTS on-prem = enterprise deal |
| Deepdub | Dubbing | No | `audiosample` audio util + API wrappers | No — on-prem = enterprise license |
| MiniMax | TTS (Speech-02) | No (TTS) | Open **LLMs** (M1/M2) + a TTS **test-set** + text utils — *not* the TTS model | No — TTS API-only |

Two traps: Cartesia and MiniMax open-source **LLMs**, *not* their TTS; Reducto's open
`RolmOCR` is explicitly "separate from the models we use in production." "Self-hosted" ≠
open source.

## 2. Why distilling a paid TTS is the wrong tool

- A paid TTS outputs **audio** — it does not expose the contextual decision (which reading)
  we lack. Distilling it transfers voice timbre, the one thing that isn't our problem.
- **Legal blocker (not legal advice):** the TTS vendors' terms forbid exactly this.
  ElevenLabs' Prohibited Use Policy bans using output "as input for machine learning or
  training of AI models" and to "develop products/models that compete with ElevenLabs."
  Most peers carry equivalent anti-distillation clauses.
- **Open Hebrew TTS already exists**, so we adopt rather than build:
  `facebook/mms-tts-heb` (VITS), Roboshaul/SASpeech (+ open dataset), `israwave`, HebTTS
  (diacritic-free LM approach). Keep Google Wavenet for the POC; these are the open
  migration path if cost/privacy demand it.

## 3. The distillation that *is* worth it

Reframe teacher = frontier **LLM** (Claude/GPT); distill **text labels**, not sound:

- Use the LLM to generate/verify **vocalization + homograph disambiguation + phrasing**
  on Hebrew exam text → supervised data for a small, self-hosted Hebrew reading-disambiguation
  model.
- This is the layer CLAUDE.md calls defensible (OCR → interpretation → reading plan → TTS),
  and we already prototype it (`homograph_judges_bench*.py`, `discover_homograph_cases.py`,
  `cascade_demo.py` = LLM-as-judge over Hebrew cases).
- Build on the **open Dicta foundation** already in the pipeline — DictaBERT + Nakdan
  (inspector `dictabert-morph` / `dictabert-syntax` / `Nakdan` tabs) — not from zero.
- Caveats: (1) check the *LLM's* ToS (labels for a non-competing niche model is more
  defensible than cloning a competitor, but read the clause); (2) student exam content is
  sensitive — confine paid-API use to one-time training-data generation on non-sensitive /
  synthetic corpora, never per-request inference.

## 4. Recommendation

| Option | Worth it? | Rationale |
|---|---|---|
| Distill paid **TTS** → open TTS | **No** | Off-target, ToS-prohibited, open Hebrew TTS exists |
| Paid **LLM** → train open **contextual** model (niqqud/homograph/prosody) | **Yes** | Hits the actual bottleneck; builds the moat; extends existing prototypes; on open Dicta base |
| TTS engine | **Adopt, don't build** | Wavenet now; MMS / Roboshaul / israwave as open backend |

**Invest in the contextual layer; treat TTS as a swappable backend.**

## Open questions

- Hebrew TTS backend bake-off: Wavenet vs. MMS-TTS-heb vs. Roboshaul vs. israwave — quality
  + niqqud-input handling + licensing. (Separate study.)
- Which LLM(s) permit teacher-label use under ToS for a non-competing Hebrew reading model.
- Dataset scope: exam-domain corpus size + human-verification budget for hard homograph cases.

## Sources

- ElevenLabs Prohibited Use Policy — <https://elevenlabs.io/use-policy>
- Nakdan (ACL 2020) — <https://aclanthology.org/2020.acl-demos.23/>; Dicta — <https://en.wikipedia.org/wiki/Dicta_(organization)>
- MMS-TTS-heb — <https://huggingface.co/facebook/mms-tts-heb>
- Roboshaul / SASpeech — <https://github.com/maxmelichov/Text-To-speech>
- israwave — <https://github.com/thewh1teagle/israwave>
- HebTTS — <https://pages.cs.huji.ac.il/adiyoss-lab/HebTTS/>
- Reducto RolmOCR — <https://huggingface.co/reducto/RolmOCR>; RD-TableBench — <https://huggingface.co/datasets/reducto/rd-tablebench>
- Deepgram self-hosted — <https://developers.deepgram.com/docs/self-hosted-introduction>
- Cartesia open models — <https://github.com/cartesia-ai>
- MiniMax speech tech report — <https://arxiv.org/pdf/2505.07916>
