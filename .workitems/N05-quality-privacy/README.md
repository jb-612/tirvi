# N05 — Quality & Privacy

**Window:** weeks 13–16 · **Features:** 9 · **Type:** integration + scaffolding

The benchmark, the MOS study, and the privacy posture. Without these,
"accommodation-grade" is a marketing claim. With them, every quality gate
in the previous phases gets a measurable bar to clear.

## Features

- **F39-tirvi-bench-v0** — 20 held-out exam pages with hand-curated ground truth (text, blocks, IPA)
- **F40-quality-gates-ci** — OCR / NLP / TTS / timing gates wired into CI per design principles
- **F41-mos-study** — blind MOS study with dyslexic teen panel (n ≥ 10) before v1
- **F42-latency-cost-profiling** — TTFA p50 / p95 + cost-per-page telemetry
- **F43-ttl-automation** — 24-hour default TTL on uploads + audio cache lifecycle
- **F44-dpia-process** — Data Protection Impact Assessment, parental-consent flow ≥ 14
- **F45-upload-attestation** — third-party-copyright attestation, DMCA-style takedown
- **F46-no-pii-logging** — log audit + redaction; no document text or accommodation data in logs
- **F47-feedback-capture** — "this word was read wrong" → `feedback/*.json` (no live retrain in MVP)

## Exit criteria

- All quality gates passing on tirvi-bench v0 at the MVP-tier thresholds (research §8.2)
- MOS ≥ 3.5 on dyslexic teen panel
- DPIA approved; no-PII logging audit clean
- TTFA p50 ≤ 30 s, p95 ≤ 90 s; cost ≤ $0.02/page amortized

## ADRs gated here

- ADR-005 TTL policy
- ADR-008 Auth in MVP (anonymous session)
