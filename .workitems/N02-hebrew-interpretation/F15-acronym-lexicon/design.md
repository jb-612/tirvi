---
feature_id: N02/F15
feature_type: domain
status: drafting
hld_refs:
  - HLD-§5.2/Processing
  - HLD-§5.1/Input
prd_refs:
  - "PRD §6.3 — Hebrew normalization"
adr_refs: [ADR-017, ADR-019, ADR-030]
biz_corpus: true
biz_corpus_e_id: E03-F03
---

# Feature: Acronym Lexicon & Expansion (post-POC)

## Overview

Curated, deterministic lexicon-driven expansion of Hebrew acronyms
(ראשי תיבות) and abbreviations. F15 sits between F14 normalize and F17
DictaBERT NLP: whole-token acronyms (`ד״ר`, `עמ׳`) are replaced with
their full Hebrew form before NLP, so DictaBERT tokenisation never
wrestles with gershayim/geresh glyphs. Tokens that look like acronyms
but are not in the lexicon are flagged `spell_out=true` so F23 SSML
emits letter-by-letter playback (no silent mispronunciation).
Provenance — `original_form` + `lexicon_version` — round-trips through
`ExpandedText` so F22 reading plan and the player feedback affordance
can show "ד״ר → דוקטור". F15 is **deferred from POC** per
`.workitems/POC-CRITICAL-PATH.md`; design lands now so the MVP wave
picks it up without re-design ceremony.

## Dependencies

- Upstream: N02/F14 (`NormalizedText` input — spans + repair_log preserved).
- Adapter ports consumed: none — F15 is pure domain logic.
- External services: none — lexicon is in-repo YAML (`data/acronym-lexicon.yaml`).
- Sibling (different scope): N02/F21 governs per-word **diacritization**
  overrides; F15 governs whole-token **expansion**; registries do not overlap.
- Downstream: N02/F17 (DictaBERT consumes expanded text), N02/F22
  (reading plan stamps provenance per token), N02/F23 (SSML reads
  `spell_out`), E11-F05 (feedback corrections — post-MVP).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.acronym` | `expand(text: NormalizedText, lexicon: Lexicon) -> ExpandedText` | function | pure; deterministic over `(text, lexicon)` |
| `tirvi.acronym.results` | `ExpandedText(text, spans, repair_log, expansion_log, lexicon_version)` | dataclass | extends F14's `NormalizedText`; immutable |
| `tirvi.acronym.results` | `ExpansionLogEntry(original_form, expansion, src_word_indices, spell_out: bool)` | dataclass | per-token provenance; `spell_out=true` ⇒ SSML per-letter break |
| `tirvi.acronym.lexicon` | `Lexicon.from_yaml(path) -> Lexicon` | builder | YAML schema (ADR-017 pattern); raises `LexiconLoadError` |
| `tirvi.acronym.lexicon` | `Lexicon.lookup(token) -> AcronymEntry \| None` | method | exact whole-token match |
| `tirvi.acronym.lexicon` | `AcronymEntry(form, expansion, source, context_tags: tuple[str, ...])` | dataclass | `context_tags` reserved (v1 ignores; MVP routes domain) |
| `tirvi.acronym.matcher` | `is_acronym_candidate(token) -> bool` | function | geresh `׳` / gershayim `״` / all-Latin-uppercase heuristic |
| `tirvi.acronym.tagger` | `tag_and_expand(text, lexicon) -> ExpandedText` | function | DE-04 emitter; ties matcher + expansion + fallback |

`ExpandedText.lexicon_version` is stamped from `Lexicon.version` (YAML
top-level key) — enables FT-111 audit + offline review.

## Approach / Design Elements

- **DE-01** lexiconValueTypes (HLD-§5.2/Processing) — frozen
  `Lexicon(version, entries, _index)`, `AcronymEntry`, `ExpandedText`,
  `ExpansionLogEntry`.
- **DE-02** yamlLexiconLoader (HLD-§5.2/Processing) — `Lexicon.from_yaml`
  LRU-cached on `(path, mtime)`; entries in source order; `_index` built
  once at load.
- **DE-03** wholeTokenMatcher (HLD-§5.2/Processing) — strip-and-reattach
  trailing `.,?:!` (and Hebrew sof-pasuq), look up bare form, reattach
  stripped run to expansion. Geresh / gershayim never stripped. Exact
  match v1; sub-token `לדר״ר` deferred.
- **DE-04** expansionEmitter (HLD-§5.2/Processing) — on hit emit a span
  with expanded surface + `ExpansionLogEntry(original_form, expansion,
  src_word_indices, spell_out=False)`. Multi-word expansions
  (`ת״א → תל אביב`) form one logical span; F22 keeps it one `PlanToken`.
- **DE-05** urlSkipFilter (HLD-§5.2/Processing) — pre-filter URL spans
  (`://`, `www.`, `^[a-z]+\\.[a-z]`); short-circuit before lookup; no
  log entry.
- **DE-06** unknownAcronymFallback (HLD-§5.2/Processing) — when
  `is_acronym_candidate` and lookup is None, emit `ExpansionLogEntry(...,
  spell_out=True)`. Output text keeps the original form; F23 picks
  per-letter break. F17 NLP receives the original token (spell-out path
  bypasses pronunciation anyway).
- **DE-07** bboxSpanPreservation (HLD-§5.1/Input) — every output span
  carries original `src_word_indices`; union equals input union across
  punctuation strip-reattach and multi-word expansion.
- **DE-08** versionStampAndLint (HLD-§5.2/Processing) — `ExpandedText
  .lexicon_version = lexicon.version`; `python -m tirvi.acronym.lint`
  exits non-zero on malformed YAML (BT-072 maintainer PR workflow).

## Decisions

- D-01: Pipeline position = post-F14, pre-F17 → **ADR-030** (new). The
  alternative (post-NLP expansion) was rejected because DictaBERT
  tokenisation handles gershayim glyphs poorly.
- D-02: Lexicon format = YAML → **ADR-017** (matches OCR fixture pattern;
  consistent maintainer workflow).
- D-03: Deterministic rules + curated lexicon for v1 → **ADR-019** (no ML
  disambiguation; consistent with sibling F14 normalize).
- D-04: Domain-aware disambiguation deferred MVP — top lexicon pick;
  `context_tags` reserved on `AcronymEntry`. No ADR.
- D-05: Sub-token / embedded acronyms deferred MVP. No ADR.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| HLD §5.2 step 3 places acronym expansion alongside pronunciation-hint generation (after morphology) | F15 lifts expansion **upstream** of F17 NLP | DictaBERT tokenisation is brittle on gershayim; expanding before NLP simplifies F17/F19 |
| Domain-aware acronym disambiguation | v1 takes top lexicon pick; `context_tags` reserved | E03-F03 OQ; deferred MVP |
| Sub-token acronyms (`לדר״ר`) | Out of scope v1 | E03-F03 edge case; whole-token MVP-acceptable |
| Latin abbreviation expansion | v1 routes to `spell_out` only | POC content is Hebrew exam material |

## HLD Open Questions

- Domain-specific disambiguation (`חז״ל` vs `ת״ז`) → HLD §12; v1 uses
  lexicon priority + manual overrides; MVP wires `context_tags`.
- Repair-diff UI affordance → deferred MVP; F15 supplies the metadata.

## Risks

| Risk | Mitigation |
|------|-----------|
| False-positive expansion (coincidental geresh) | DE-03 lookup-first; non-lexicon geresh tokens take DE-06 spell-out |
| Lexicon drift breaks downstream fixtures | DE-02 mtime cache + DE-08 `lexicon_version` audit (FT-111) |
| Multi-word expansion breaks span map | DE-07 round-trip property |
| Maintainer commits malformed YAML | DE-08 lint CLI + loader fail-fast (BT-072) |

## Diagrams

- `docs/diagrams/N02/F15/acronym-expansion.mmd` — NormalizedText → URL
  skip → matcher → (lexicon hit | spell-out | pass-through) →
  ExpandedText with provenance + lexicon_version stamp.

## Out of Scope

- Sub-token / embedded acronym matching, ML or NLP-context disambiguation,
  per-domain context routing via `context_tags` (slot reserved), and
  E11-F05 feedback-driven lexicon updates — all deferred MVP.
- Latin-script abbreviation expansion (Latin → spell-out only in v1).
- Number-to-words — owned by F25 content templates.
- Domain-aware disambiguation bench — deferred N05.
- Production `data/acronym-lexicon.yaml` content bootstrap (which
  entries to seed for `ד״ר`, `עמ׳`, `ת״א`, etc.) — MVP wiring ticket;
  F15 ships with the parameterised loader + tests-only fixtures.
- Lint `--strict` mode with an `entries_sha256` lock file to close
  ADR-030 Negative-3 (silent version drift when a maintainer edits
  YAML but forgets to bump `version`) — MVP follow-up; v1 lint catches
  malformed YAML and duplicate `form` only.
