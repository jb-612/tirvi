---
feature_id: N02/F21
feature_type: domain
status: designed
hld_refs:
  - HLD-§5.2/Processing
prd_refs:
  - "PRD §6.3 — Hebrew NLP"
adr_refs: []
biz_corpus: true
biz_corpus_e_id: E05-F03
---

# Feature: Hebrew Homograph Override Lexicon

## Overview

YAML-backed curated lexicon of Hebrew homographs that overrides Dicta-Nakdan's
output for known-bad cases. F19 Nakdan adapter already contains the override
hook (`entry.word in HOMOGRAPH_OVERRIDES` in `_pick()`); F21 owns the lexicon
data, schema, and loader. POC scope: 2 seed entries — `כל → כֹּל` (from v3
user feedback) and `ספר` with POS=VERB guard. Full 500-entry production lexicon
is MVP scope (ADR not needed; design decision captured here).

## Dependencies

- Upstream: none — this is a data + loader feature, no upstream adapter required.
- Downstream: F19 (`tirvi/adapters/nakdan/overrides.py` imports
  `HOMOGRAPH_OVERRIDES` dict from this module's `load_overrides()`).
- External services: none — YAML file on disk, loaded once at startup.

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.lexicon.homograph` | `HomographEntry` | frozen dataclass | surface_form, vocalized_form, pos_filter: str|None |
| `tirvi.lexicon.homograph` | `load_overrides(path)` | function | reads YAML, validates, returns dict[str, str] (POC: no-POS-filter entries only) |
| `tirvi.lexicon.homograph` | `HOMOGRAPH_OVERRIDES` | module-level dict | singleton; imported by F19 overrides.py |
| `data/homograph-lexicon.yaml` | — | data file | versioned YAML; each entry has surface_form, vocalized_form, pos_filter (optional) |

`HOMOGRAPH_OVERRIDES` is a plain `dict[str, str]` for POC (surface → vocalized).
POS-filtered lookups are MVP scope — F19's `_pick()` can only check word-in-dict
(it doesn't receive an NLPToken for the current entry). Full POS-filtered lookup
requires F18 disambiguation to supply per-word POS — deferred.

## Approach

1. **DE-01**: `HomographEntry` frozen dataclass — `surface_form: str`,
   `vocalized_form: str`, `pos_filter: str | None`. Immutable once loaded.
   Schema validated against `data/homograph-lexicon.yaml` YAML shape.
2. **DE-02**: `load_overrides(path) -> dict[str, str]` — reads YAML list of
   entries; for POC returns only entries with `pos_filter: null` as a flat dict
   (surface → vocalized). Malformed YAML raises `ValueError` with the offending
   key. `FileNotFoundError` raises with a descriptive message naming the expected
   path (e.g., "data/homograph-lexicon.yaml not found — check repo checkout or
   TIRVI_DATA_PATH"). Load time ≤ 200 ms per FT-162 (checked in T-02 test).
3. **DE-03**: `HOMOGRAPH_OVERRIDES` module-level constant — set at module import
   time by calling `load_overrides(default_path)`. F19 `tirvi/adapters/nakdan/overrides.py`
   imports `HOMOGRAPH_OVERRIDES` from here; existing POC seed dict (`{"כל": "כֹּל"}`)
   is replaced by the YAML-loaded version.
4. **DE-04**: POC seed data — `data/homograph-lexicon.yaml` ships with 2 entries:
   (a) `כל → כֹּל` (no POS filter, corrects qamatz-qatan per v3 user feedback issue #20);
   (b) `ספר → סָפַר` with `pos_filter: VERB` (documented but not applied in POC flat-dict
   mode — included as the schema exemplar for maintainers).

## Design Elements

- DE-01: homographEntryType (ref: HLD-§5.2/Processing)
- DE-02: lexiconLoader (ref: HLD-§5.2/Processing)
- DE-03: overrideDictSingleton (ref: HLD-§5.2/Processing)
- DE-04: pocSeedData (ref: HLD-§5.2/Processing)

## Decisions

No new ADR required — override-wins priority policy is documented in F19 DE-03.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| POS-filtered lookup | POC uses flat dict only; POS filter ignored | F19 `_pick()` has no NLPToken context at override check time; full POS-aware lookup requires F18 integration (MVP) |
| Top-500 lexicon | POC ships 2 seed entries | POC demo uses Economy.pdf; 2 entries cover known demo failures per v3 feedback |
| Bench coverage report (BT-105) | No bench in POC | N05 quality bench deferred |

## HLD Open Questions

- POS-filtered lookup → deferred MVP (requires F18 NLP context at F19 call site).
- Per-domain lexicon split (Tanakh, civics, science) → deferred MVP.

## Risks

| Risk | Mitigation |
|------|-----------|
| Malformed YAML silently ignored | DE-02 raises ValueError on load; surfaced at startup |
| Override regresses Nakdan (worse pronunciation) | Bench (N05) measures per-entry contribution; PR review gate |
| Lexicon grows beyond flat-dict pattern | POS-filter aware lookup designed in DE-04 schema; no rework needed at MVP |

## Diagrams

- `docs/diagrams/N02/F21/homograph-lexicon.mmd` — maintainer → YAML → loader → HOMOGRAPH_OVERRIDES → F19 _pick()

## Out of Scope

- POS-filtered lookup (deferred MVP — needs F18 NLP context at F19 call site).
- Top-500 production lexicon (MVP scope).
- Bench coverage report (N05).
- Monthly feedback correction flow (E11-F05 deferred).
- YAML diff alert when lexicon version changes (deferred MVP).
