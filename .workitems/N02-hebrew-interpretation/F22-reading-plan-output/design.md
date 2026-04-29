---
feature_id: N02/F22
feature_type: domain
status: drafting
hld_refs:
  - HLD-§5.2/Processing
  - HLD-§5.3/Output
prd_refs:
  - "PRD §6.4 — Reading plan"
adr_refs: [ADR-014]
biz_corpus: true
biz_corpus_e_id: E06-F01
---

# Feature: Reading-Plan Output (`plan.json`)

## Overview

`plan.json` is the per-page contract between the Hebrew-interpretation
stack and the audio + UI stack. F22 owns the data structure: combines
F11's typed blocks, F18's NLP tokens (POS + lemma + morph), F19's
diacritization, and F20's IPA + stress hints into a single immutable
`ReadingPlan` that downstream stages consume. POC scope is the
minimum field set required by F23 (SSML) and F35 (player highlight):
tokens + lemma + pos + IPA hint + structural block type. SSML itself
is filled in by F23; F22 reserves the `ssml` field but leaves it
empty until then.

## Dependencies

- Upstream: N01/F11 (typed blocks), N02/F14 (NormalizedText spans),
  N02/F18 (NLPResult), N02/F19 (DiacritizationResult), N02/F20
  (G2PResult / PronunciationHint).
- Adapter ports consumed: none — F22 is pure domain assembly.
- External services: none.
- Downstream: F23 (SSML shaping fills `ssml` per block), F26 (TTS reads
  the SSML), F30 (word-timing port keys timing back to PlanToken IDs),
  F35 (player walks the plan for highlight).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.plan` | `build_plan(...)` | function | takes the four upstream results + page metadata; returns immutable `ReadingPlan` |
| `tirvi.plan.results` | `ReadingPlan(page_id, blocks)` | dataclass | top-level page plan |
| `tirvi.plan.results` | `PlanBlock(block_id, block_type, ssml, tokens, voice_spec)` | dataclass | one per F11 block; `ssml=""` until F23 fills |
| `tirvi.plan.results` | `PlanToken(id, text, lemma, pos, ipa, stress, src_word_indices, provenance)` | dataclass | per-token fact bundle |
| `tirvi.plan.invariants` | `assert_plan_v1(plan)` | helper | unique IDs, token→block linkage, token→span backreference |

`PlanToken.id` is the stable ID downstream (e.g., F30 word-timing keys to
this ID; F35 highlight box keys to this ID). `provenance` is a
`dict[str, str]` mapping field names to provider strings (e.g.,
`{"pos": "dictabert-large-joint", "ipa": "phonikud"}`) so consumers can
audit which adapter produced each fact.

## Approach

1. **DE-01**: Plan value types — `ReadingPlan / PlanBlock / PlanToken`,
   frozen dataclasses; `voice_spec` is a typed dict shaped by F26 needs.
2. **DE-02**: Plan generator — given block list (F11), normalized text
   spans (F14), NLP tokens (F18), diacritization (F19), G2P (F20),
   produce one `PlanBlock` per F11 block with the corresponding
   `PlanToken` list.
3. **DE-03**: Per-token provenance — for every PlanToken field, record
   the producing adapter's `provider` field; missing inputs map to
   `provenance["<field>"] = "missing"`.
4. **DE-04**: Plan invariant validator — `assert_plan_v1(plan)` checks
   unique block IDs and token IDs, every token's `src_word_indices`
   resolves to the page's word list, every block's `tokens` matches the
   normalized-text span ordering.
5. **DE-05**: Empty-block skip — block types with no token (e.g.,
   figure_caption with no caption text) emit `tokens=[]` and `ssml=""`;
   downstream F23 / F26 short-circuit on empty SSML.
6. **DE-06**: Deterministic JSON serialization — `plan.to_json()` orders
   keys alphabetically and emits with a stable indent so two
   runs over the same input produce byte-identical files (basis for
   the `drafts/<reading-plan-sha>/` content-hash directory in
   PLAN-POC.md).

## Design Elements

- DE-01: planValueTypes (ref: HLD-§5.3/Output)
- DE-02: planGenerator (ref: HLD-§5.2/Processing)
- DE-03: perTokenProvenance (ref: HLD-§5.3/Output)
- DE-04: planInvariantValidator (ref: HLD-§5.3/Output)
- DE-05: emptyBlockSkip (ref: HLD-§5.2/Processing)
- DE-06: deterministicJsonSerialization (ref: HLD-§5.3/Output)

## Decisions

- D-01: schema versioning policy → **ADR-014** (existing; contract test
  catches drift).

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| SSML field | F22 reserves but leaves empty; F23 fills | Separation of concerns — F22 owns data assembly, F23 owns prosody shaping |
| Plan size cap | No pagination in POC | Single-page demo; pagination deferred to MVP |
| `voice_meta` | Out of scope | F26 owns voice spec; `voice_spec` is a forward-compat slot |
| Block taxonomy | POC subset only (heading / paragraph / question_stem) | Inherited from F11 |

## HLD Open Questions

- Plan size cap → deferred MVP.
- SSML attribute namespace strictness → resolved in F23.

## Risks

| Risk | Mitigation |
|------|-----------|
| Provenance dict drifts across upstream adapter renames | DE-03 hardcodes provider names from F03 contract; refresh on adapter swap |
| Token ID instability between runs hurts content-hashing | DE-06 deterministic serialization; PlanToken.id derived from `(block_id, position)` |
| Validator misses invariant after schema field add | ADR-014 contract test runs in CI; new fields default-null and validator is updated together |

## Diagrams

- `docs/diagrams/N02/F22/reading-plan-assembly.mmd` — four upstream results + blocks → build_plan → ReadingPlan

## Out of Scope

- SSML shaping (F23 owns it).
- Plan pagination / chunking (deferred MVP).
- Voice metadata (F26 owns it).
- Numeric schema_version field (deferred per ADR-014).
- Plan diffing across runs (POC stores by reading-plan-sha but does not diff).
