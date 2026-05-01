---
feature_id: N02/F24
feature_type: domain
status: designed
hld_refs:
  - HLD-§5.2/Processing
prd_refs:
  - "PRD §6.4 — Reading plan"
adr_refs: []
biz_corpus: true
biz_corpus_e_id: E06-F03
---

# Feature: Inline Language Switching Policy (Deferred MVP)

## Overview

Defines the SSML shaping policy for mixed-language content (Hebrew + English
spans). **POC scope: deferred** per PLAN-POC.md (Economy.pdf demo is Hebrew-only;
POC ships single he-IL-Wavenet-D voice). Design is authored here as a planning
artifact for Wave 3 / MVP. Two paths: Azure path (inline lang xml:lang wrapping)
and Google path (split-and-stitch separate audio chunks). F16 mixed-language
detection provides the input spans; F23 SSML shaping is the consumer.

## Dependencies

- Upstream: N02/F16 (LangSpan list), N02/F22/F23 (SSML shaping context).
- Downstream: N03 TTS adapters (Wavenet, Azure TTS — consume policy-shaped SSML).
- External services: none.

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| tirvi.ssml.lang_switch | apply_lang_policy(ssml, lang_spans, voice_profile) | function | POC: identity (returns ssml unchanged); MVP: Azure/Google branch |
| tirvi.ssml.lang_switch | LANG_SWITCH_ENABLED | bool constant | POC: False; toggled via TIRVI_LANG_SWITCH env var |

## Approach

1. DE-01: Lang-switch gate — LANG_SWITCH_ENABLED = env("TIRVI_LANG_SWITCH") == "true".
   POC: False; apply_lang_policy() is identity when disabled.
2. DE-02 (MVP): Azure path — insert lang xml:lang="en-US" wrapping per English span.
   Nested spans collapsed to outermost.
3. DE-03 (MVP): Google path — split SSML at lang-span boundaries; synthesize separate
   audio chunks; stitch via F30 word-timing.

## Design Elements

- DE-01: langSwitchGate (ref: HLD-§5.2/Processing)
- DE-02: azureInlineLangWrap (ref: HLD-§5.2/Processing) [MVP only]
- DE-03: googleSplitAndStitch (ref: HLD-§5.2/Processing) [MVP only]

## Decisions

No ADR — feature is deferred; decision pending MVP voice capabilities validation.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| xml:lang SSML switch | Not implemented in POC | Economy.pdf demo is Hebrew-only; single voice; deferred per PLAN-POC.md |
| Split-and-stitch | Not implemented in POC | Complex audio assembly; deferred MVP |

## HLD Open Questions

- Cross-fade vs gap-zero for stitch seams -> MVP design decision.
- Google Wavenet support for lang on Semitic languages -> src-003 s2.3: not supported; split-and-stitch confirmed.

## Risks

| Risk | Mitigation |
|------|-----------|
| English spans detected mid-word | DE-02/DE-03 operate at word-boundary granularity (F16 emits word-aligned spans) |
| Stitch seam perceptible | FT-181 bench (30 ms perceived seam limit); deferred MVP |

## Diagrams

None required for stub — POC is a no-op passthrough.

## Out of Scope (POC)

- Inline lang wrapping (Azure MVP path).
- Split-and-stitch audio assembly (Google MVP path).
- FT-179, FT-180, FT-181, FT-182 — all deferred MVP.
