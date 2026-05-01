---
title: Model configuration YAML — centralized per-stage model settings
created: 2026-05-01
status: raw
next: design
---

## Idea

A `config/models.yaml` file declares the model name, endpoint, and
non-secret parameters for every pipeline stage (OCR engine, Nakdan/diacritizer,
MLM scorer model ID, LLM reviewer model + endpoint, TTS voice). Secrets
(API keys, service account paths) remain in `.env`. `make_poc_deps()` reads
the YAML at startup so operators swap models without editing Python.

## Why now

Models are currently hardcoded in `make_poc_deps()` and
`_build_poc_correction_cascade()`. Every model swap requires a code change
and commit. With `RichProgressReporter` now surfacing per-stage timing,
the team will start experimenting with different models; a config file makes
that workflow viable without touching source.

## Open questions

- Schema: flat top-level keys per stage or nested `stages.ocr.engine`?
- Override hierarchy: YAML < env vars < CLI flags?
- Validation on load (Pydantic, marshmallow, or plain assertions)?
- Hot-reload or load-once at startup?
- Stub deps: should stub mode ignore the YAML entirely, or use it for
  non-model fields (e.g., TTS voice name)?

## Suggested next step

Run `@sw-designpipeline` — biz corpus not needed; scope is purely
infrastructure/config. ~6–8 tasks. Feature type: integration.
