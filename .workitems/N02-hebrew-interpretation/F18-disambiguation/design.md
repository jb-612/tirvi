---
feature_id: N02/F18
feature_type: domain
status: drafting
hld_refs:
  - HLD-§4/AdapterInterfaces
  - HLD-§5.2/Processing
prd_refs:
  - "PRD §6.4 — Reading plan"
adr_refs: [ADR-014, ADR-017, ADR-026, ADR-027, ADR-029]
biz_corpus: true
biz_corpus_e_id: E04-F03
issue_refs:
  - "GH#20 — gender / homograph diacritization regressions (e.g., כל qamatz-qatan, gender mis-pick on ambiguous verb forms)"
wave: 2
---

# Feature: Disambiguation — context-aware morphological refresh + NLPResult v1 contract

## Overview

Wave-2 **refresh** of N02/F18. The original feature shipped a confidence-margin
sense-pick over a hypothetical top-K from `dictabert-large-joint`. Wave-1
ADR-026 re-routed F17 to `dicta-il/dictabert-morph` (no joint head, no top-K —
single best-token output with `confidence: float | None` and `ambiguous: bool`
already populated by F17 DE-04). This refresh re-scopes F18 to the
responsibilities that remain meaningful under the morph-only pipeline:

1. **Input-contract enforcement** for the NLPResult emitted by F17 (primary,
   `provider="dictabert-morph"`) and F26 (fallback, success path
   `provider="alephbert+yap"` per ADR-027 §implementation; degraded path
   `provider="degraded"`). v1 invariant whitelists all valid producer strings;
   the legacy `"dictabert-large-joint"` is rejected by `assert_nlp_result_v1`
   so stale fixtures fail fast.
2. **Context-aware homograph hook** — for tokens F17 marks `ambiguous=True`,
   F18 consults a morph-keyed homograph table to force a single
   `(pos, morph_features, lemma)` triple before the result reaches F19
   (Dicta-Nakdan). The hook addresses the GH#20 trigger (wrong gender / wrong
   sense surfacing as wrong nikud at Nakdan, e.g., `כל`, `הספר`, ambiguous
   participle/finite-verb pairs). The override table is morph-keyed (not
   surface-keyed like F19's `HOMOGRAPH_OVERRIDES` lexicon) so the same surface
   string can produce different sense picks under different morph contexts.
3. **`pick_sense` rule** — for the morph-only path, `pick_sense` is a
   pass-through when `ambiguous=False`; when `ambiguous=True`, it consults the
   morph-keyed override table and falls back to top-1 if a legacy
   `candidates` list is supplied, otherwise preserves F17's pick.
4. **NLPResult v1 fixture builder** — YAML-driven `NLPResultBuilder.from_yaml`
   for downstream test seeding (parallel to F10's OCR builder, ADR-017).

POC scope (per `.workitems/POC-CRITICAL-PATH.md` + R2 promotion of T-05):
**T-00 (migration) + T-01/T-02/T-03/T-05 are demo-critical**; T-04 (fixture
builder) is the only deferred slot. T-05 was promoted from POC-deferred to
demo-critical because it is the only contract-boundary test that catches the
five Wave-2 cross-feature bugs (provider whitelist mismatches, morph-key
spelling clash, legacy provider rejection). The homograph-override hook is
in-scope only as a **call site + empty stub**; production override entries
land in F21 lexicon work.

Fixture builder mirrors F10's YAML pattern (ADR-017). All vendor symbols stay
out of `tirvi.nlp.*` per ADR-029 — F18 is pure domain logic on the NLPResult
emitted by F17/F26.

## Migration: wave-1 → wave-2 (T-00)

The wave-1 scaffold landed F18 production code at `tirvi/nlp/` (not
`tirvi/disambiguate/` as the wave-1 design.md said). The wave-2 design adopts
**path (a)** — keep the wave-1 module path; legacy code becomes a
deprecated alias alongside the v2 implementation:

| Concern | Wave-1 (on disk today) | Wave-2 |
|---|---|---|
| Module package | `tirvi/nlp/` | `tirvi/nlp/` (unchanged — design refreshed to match disk) |
| `pick_sense` | `tirvi/nlp/disambiguate.py::pick_sense(candidates) -> tuple[NLPToken, bool]` (GREEN, 6 passing tests) | rename to `_legacy_pick_sense` + `@deprecated` marker; add v2 `pick_sense(token, candidates=None) -> NLPToken` alongside |
| `assert_nlp_result_v1` | `tirvi/nlp/contracts.py` (NotImplemented stub with TODOs INV-NLP-CONTRACT-001..004) | T-05 lifts the stub at the same path |
| Morph whitelist | `tirvi/nlp/morph.py::MORPH_KEYS_WHITELIST = {"gender","number","person","tense","def","case"}` (lowercase, no `VerbForm`) | T-02 replaces with UD-canonical TitleCase set (see Morph-key contract below) |
| Errors | `tirvi/nlp/errors.py::DisambiguationError`, `MorphKeyOutOfScope` | inventory only — reuse both; reuse existing `tirvi.errors.SchemaContractError` for legacy-provider rejection (no new error type) |
| Existing 6 tests in `tests/unit/test_disambiguate.py` | pin `pick_sense(candidates) -> tuple` shape | T-00 retargets the 6 imports to `_legacy_pick_sense`; tests stay green; T-03 writes new tests against v2 shape |
| `tirvi/disambiguate/`, `tirvi/fixtures/nlp.py`, `tirvi/nlp/overrides.py` | do not exist on disk | T-04 + T-03 create `tirvi/nlp/overrides.py` (override stub) + `tirvi/fixtures/nlp.py` (builder, deferred for POC) |

Migration deliverables (T-00):
- Rename `tirvi/nlp/disambiguate.py::pick_sense` → `_legacy_pick_sense` and add
  `@deprecated("use pick_sense(token: NLPToken) -> NLPToken")` marker (use
  `warnings.warn` if no `@deprecated` decorator is available pre-3.13).
- Update the 6 imports in `tests/unit/test_disambiguate.py` to point at
  `_legacy_pick_sense`. Tests stay green (pin the legacy shape until F22/F19
  callers migrate or until F18 wave-3 retires the alias).
- Add a CI grep gate (extend the existing import-boundary test or add a small
  pytest case) that fails if any module **outside** `tests/unit/test_disambiguate.py`
  imports `_legacy_pick_sense` — this is the safety net that prevents the
  alias from leaking into production callers.
- Confirm `tirvi/nlp/contracts.py` is still a NotImplemented stub at T-00 end
  (T-05 fills it in a later phase).

The wave-1 → wave-2 path is **NOT** a deletion + rewrite; it's a controlled
deprecation with the legacy alias preserved for one wave. This bounds the
blast radius for the demo-critical wire while letting F22/F19/etc. migrate
to the v2 shape on their own schedule.

## Morph-key contract (UD v2 canonical)

F17 emits morphology in UD v2 canonical TitleCase (per F17 design.md DE-02
and CoNLL-U convention). Wave-1 F18 wrote a lowercase whitelist that does
not match what F17 produces; the producer-consumer mismatch would crash the
v1 invariant on every real F17 token.

**F18 wave-2 adopts UD v2 canonical TitleCase across the morph-key
whitelist.** F17 is committed; F18 aligns. Every fixture, test, and design
spec under F18 uses the TitleCase form:

```python
MORPH_KEYS_WHITELIST: frozenset[str] = frozenset({
    "Gender", "Number", "Person", "Tense",
    "Definite", "Case", "VerbForm",
})
```

Reference: <https://universaldependencies.org/u/feat/index.html>. CoNLL-U
column 6 (FEATS) uses TitleCase keys; the lowercase form was a wave-1
ad-hoc choice with no UD provenance. Wave-2 F22 (reading plan) and F19
(Dicta-Nakdan context tilt) consume morph features through the locked
NLPToken dataclass — they read whatever F18 validates, so this pin
propagates downstream automatically.

If a future F17 design refresh deviates from TitleCase, the F18 invariant
will reject it loudly — that's the desired forcing function, not a bug.

## Dependencies

- Upstream: N00/F03 (`NLPResult` dataclass — locked), N02/F17
  (DictaBERT-morph adapter — emits **single token per word** with
  `ambiguous` and `confidence` already populated per F17 DE-04). N02/F26
  (AlephBERT/YAP fallback — same shape; success-path provider
  `"alephbert+yap"` per ADR-027; degraded-path provider `"degraded"`
  with `tokens=[]`).
- Adapter ports consumed: none — F18 is pure domain logic on the
  NLPResult emitted by F17 / F26 (per ADR-029 vendor-boundary).
- External services: none.
- Downstream: **F19 (Dicta-Nakdan REST diacritization)** — F18-validated
  NLPResult feeds F19's `diacritize_in_context(text, nlp_context)` per
  F19 DE-02 NLP-context conditioning. F22 (reading plan reads lemma +
  sense — POC tolerates `lemma=None` per ADR-026 deferral). F23 (SSML
  reads pronunciation hint).
- **Issue trigger**: GH#20 — gender / homograph regressions surfaced as
  wrong nikud at F19 (e.g., `כל` qamatz-qatan, gender mis-pick on
  ambiguous verbs). F19 fixed the surface-keyed override path; F18 fixes
  the morph-keyed pre-Nakdan signal.

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.results.NLPToken` | `pos: str`, `lemma: str \| None`, `morph_features: dict[str, str] \| None`, `prefix_segments: tuple[str, ...] \| None`, `confidence: float \| None`, `ambiguous: bool` | locked dataclass | F03 schema; F17 / F26 populate. Lemma is `None` in POC per ADR-026 |
| `tirvi.nlp` | `pick_sense(token: NLPToken, candidates: list[tuple[NLPToken, float]] \| None = None) -> NLPToken` | function (v2) | morph-only path: `ambiguous=False` ⇒ pass-through; `ambiguous=True` ⇒ consult morph-keyed override; legacy `candidates` opt-in falls through to top-1 on miss |
| `tirvi.nlp` | `_legacy_pick_sense(candidates, margin_threshold=None) -> tuple[NLPToken, bool]` | deprecated alias | wave-1 shape preserved for the 6 existing tests; `@deprecated` marker; CI grep-gate prevents production callers |
| `tirvi.nlp.overrides` | `MORPH_HOMOGRAPH_OVERRIDES: dict[tuple[str, frozenset[tuple[str,str]]], NLPToken]` | dict | POC-empty stub keyed by `(surface, frozenset((token.morph_features or {}).items()))`; F21 ships entries |
| `tirvi.fixtures.nlp` | `NLPResultBuilder.from_yaml(path) -> NLPResult` | builder | parallel to F10's OCR builder; raises `MorphKeyOutOfScope` on UD-key mismatch. **POC-deferred** (T-04) |
| `tirvi.nlp.contracts` | `assert_nlp_result_v1(result: NLPResult)` | helper | provider whitelist, UD-Hebrew POS whitelist, morph key whitelist, `lemma is None or str`, `confidence is None or 0 ≤ confidence ≤ 1`. Lifts the existing wave-1 NotImplemented stub at the same path |
| `tirvi.nlp.contracts` | `ALLOWED_PROVIDERS: frozenset[str]` | constant | `{"dictabert-morph", "alephbert-yap", "alephbert+yap", "fixture", "degraded"}` (see Provider whitelist below) |

## Provider whitelist

`assert_nlp_result_v1` accepts the following provider strings:

| Provider | Source | Notes |
|---|---|---|
| `"dictabert-morph"` | F17 success path (ADR-026) | primary NLP backbone |
| `"alephbert+yap"` | F26 success path (ADR-027 §implementation) | F17 fallback — emitter uses `+` |
| `"alephbert-yap"` | legacy / spec-doc form | accepted for transitional compatibility — both spellings valid until F26 implementation freezes one canonical form |
| `"fixture"` | F18 T-04 builder, ADR-017 | test seed |
| `"degraded"` | F26 graceful-fallback path (ADR-027) | tokens=[]; relaxed sub-invariant |

The legacy `"dictabert-large-joint"` is **rejected** with
`SchemaContractError("legacy provider 'dictabert-large-joint' was renamed to 'dictabert-morph' per ADR-026")`.

The `"degraded"` branch carries a relaxed sub-invariant: `tokens` MUST be
empty and `confidence` MUST be `None`. This matches ADR-027's graceful
shape and prevents the v1 gate from crashing when F17 is unavailable.

## Approach

1. **DE-01**: Per-token semantic anchors — UD-Hebrew POS string
   (whitelist), `morph_features: dict[str, str] | None` (UD TitleCase
   keys whitelisted; see Morph-key contract above), `lemma: str | None`
   (POC tolerates None per ADR-026), `confidence: float | None`
   (range `0 ≤ confidence ≤ 1` when not None). Existing F03 dataclass;
   F18 only tightens validation.
2. **DE-02**: morph_features dict shape — UD v2 canonical TitleCase
   subset `{Gender, Number, Person, Tense, Definite, Case, VerbForm}`;
   unknown keys raise `MorphKeyOutOfScope`. Existing wave-1 lowercase
   whitelist is REPLACED by T-02 (this is not "done"; the wave-1
   spelling clashed with F17 producer).
3. **DE-03**: Context-aware sense pick — `pick_sense(token, candidates=None)`:
   - If `token.ambiguous == False`: pass-through (F17 already chose).
   - If `token.ambiguous == True`: probe `MORPH_HOMOGRAPH_OVERRIDES`
     keyed by `(token.text, frozenset((token.morph_features or {}).items()))`.
     Override hit ⇒ return overridden NLPToken. Override miss with
     `candidates` provided ⇒ return top-1 by score (legacy top-K
     fallback). Override miss with `candidates=None` ⇒ pass-through
     (preserve F17's pick + flag).
   - **Python idiom note**: the key uses `(token.morph_features or {}).items()`
     — NOT `token.morph_features.items() or ()` — because `morph_features`
     can be `None` per F03 dataclass; the latter raises `AttributeError`.
   - The empty-table case is itself a positive test pin: with
     `MORPH_HOMOGRAPH_OVERRIDES = {}` an ambiguous token without
     candidates passes through unchanged. F21 will fill the table; F18
     ships the empty-table behavior as the POC contract.
4. **DE-04**: NLP YAML fixture builder — `NLPResultBuilder.from_yaml`,
   raises `MorphKeyOutOfScope` on UD-key mismatch and rejects legacy
   provider strings; lives under `tests/fixtures/nlp/`. **POC-deferred**
   per POC-CRITICAL-PATH; tests can hand-construct NLPToken (the
   wave-1 tests already demonstrate this).
5. **DE-05**: v1 invariant assertion — `assert_nlp_result_v1` runs in
   F03's `assert_adapter_contract` after structural check. Checks (in
   order):
   - `result.provider in ALLOWED_PROVIDERS`; legacy
     `"dictabert-large-joint"` raises
     `SchemaContractError("legacy provider ... renamed to 'dictabert-morph' per ADR-026")`.
   - If `result.provider == "degraded"`: `tokens == ()` and
     `confidence is None`; skip per-token checks.
   - Else: per-token loop:
     - `token.pos in UD_POS_WHITELIST`
     - `token.morph_features is None or set(token.morph_features) ⊆ MORPH_KEYS_WHITELIST`
     - `token.lemma is None or isinstance(token.lemma, str)`
     - `token.confidence is None or 0.0 ≤ token.confidence ≤ 1.0`
   - **Note (R-4 resolution):** the wave-1 design's "ambiguous flag
     consistency with confidence margin" check is REMOVED. F17 owns
     the `ambiguous` flag; F18 trusts the producer. The env var
     `TIRVI_DISAMBIG_MARGIN` no longer participates in DE-05; it lives
     only on the legacy `_legacy_pick_sense` re-evaluation path.
6. **DE-06**: provider stamp on NLPResult — F17 writes
   `provider="dictabert-morph"` (ADR-026); F26 success writes
   `provider="alephbert+yap"` (ADR-027 §implementation; transitional
   `"alephbert-yap"` also accepted); F26 graceful fallback writes
   `provider="degraded"` (ADR-027); fixtures stamp `provider="fixture"`.
   Legacy `"dictabert-large-joint"` is rejected by DE-05 so stale wave-1
   fixtures fail loudly under wave-2 invariants.

## Design Elements

- DE-01: perTokenSemanticFields (ref: HLD-§5.2/Processing)
- DE-02: morphFeatureDict (ref: HLD-§5.2/Processing)
- DE-03: contextAwareSensePick (ref: HLD-§5.2/Processing)
- DE-04: nlpYamlFixtureBuilder (ref: HLD-§4/AdapterInterfaces — adapter
  output shape, even though F18 itself is not an adapter)
- DE-05: v1NlpInvariantAssertion (ref: HLD-§4/AdapterInterfaces — same
  rationale)
- DE-06: providerStamp (ref: HLD-§4/AdapterInterfaces)

## Decisions

- D-01: NLP primary = DictaBERT-morph (single best, no top-K) →
  **ADR-026** (model-id pivot; supersedes ADR-002 narrative for F18
  scope. ADR-002 file does not yet exist on disk; ADR-026 carries the
  binding decision).
- D-02: schema versioning policy → **ADR-014** (existing; contract test).
- D-03: fixture builder format = YAML → **ADR-017** (existing; same pattern
  as OCR builder).
- D-04: F26 AlephBERT/YAP fallback path produces NLPResult that F18 must
  also validate → **ADR-027** (existing; F18 whitelist accepts
  `"alephbert+yap"` success + `"degraded"` graceful fallback +
  transitional `"alephbert-yap"`).
- D-05: F18 contains no vendor SDK imports; all upstream NLP comes
  through the `NLPResult` value type → **ADR-029** (existing
  vendor-boundary discipline; F18 is a clean domain consumer).

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Multi-model voting | POC accepts only single-best from F17 (or F26 fallback) | ADR-026 — `dictabert-morph` has no joint head; vote across F17+F26 deferred MVP |
| `Definite` (definiteness) field | Included in morph dict | Biz S01 OQ resolved positively — needed by F22 reading plan |
| Dependency-parse heads | Out of scope (no edge metadata) | Biz S01 OQ resolved negatively — POC reading plan does not consume deps |
| `lemma` always populated | POC accepts `lemma=None` per F17 ADR-026 deferral | `dictabert-morph` has no lemma head; F22 + F19 degrade gracefully |
| Top-K candidate stream into `pick_sense` | Pass-through in POC (single best from F17). HLD §5.2 originally implied "score candidate readings" — F18 wave-2 is a flag-driven re-router rather than a context scorer because the producer (F17) collapsed top-K to single-best in DE-04. The "scoring" semantically moved into F17's per-attribute confidence + `ambiguous` flag; F18 reads the flag and overrides where the morph signature warrants. | ADR-026 collapses top-K at the producer; legacy `candidates` arg kept for backward compat behind `_legacy_pick_sense` |
| Surface-keyed homograph overrides | F18 uses **morph-keyed** overrides, F19 uses surface-keyed | Different layers: F18 forces morph signal upstream (gender/state); F19 picks Dicta diacritization options downstream. Composes — they target different sources of GH#20 |
| HLD §4 adapter table doesn't list a Disambiguation row | F18 ships no adapter; HLD-§4 trace edges remain valid because DE-04 + DE-05 enforce **adapter-emitted** schema (the contract surface), not because F18 ships an adapter | Trace edge intent is "what shape adapters must emit"; F18 is the gatekeeper |

## HLD Open Questions

- Dependency-parse heads → resolved: out of scope per HLD Deviation row.
- Definiteness field → resolved: included in DE-02 morph keys.
- Lemma availability → resolved: optional in POC per ADR-026; F22 / F19
  consumers tolerate None.
- Override-table population — deferred to **F21 homograph-overrides**;
  F18 ships an empty stub + the call site.

## Risks

| Risk | Mitigation |
|------|-----------|
| F17 confidence is poorly calibrated → wrong `ambiguous` flag → wrong sense | F17 owns the flag; F18 trusts producer (R-4). Threshold `TIRVI_DISAMBIG_MARGIN` lives on `_legacy_pick_sense` only; bench in N05 |
| UD-key whitelist drifts vs `dictabert-morph` outputs | DE-05 invariant runs on every adapter; CI catches |
| Fixture stale after morph schema bump (e.g., legacy `dictabert-large-joint` provider) | DE-04 builder validates on load + DE-05 raises `SchemaContractError` with substring "legacy provider"; T-05 pins the substring as a regression test |
| F26 fallback path emits a different morph dialect than F17 | DE-05 whitelist is provider-agnostic on UD keys; F26 design pins `yap_to_nlpresult` to UD-canonical TitleCase. If F26 deviates, DE-05 raises — desired forcing function |
| Morph-keyed override table overlaps with F19's surface-keyed lexicon | Hooks fire at different layers: F18 pre-Nakdan (morph), F19 inside Nakdan response selection (surface). Run order is deterministic — no cycle |
| Issue #20 regressions resurface under different morph signature | DE-03 override entries are scoped per-morph; new morph signatures get their own row in F21 lexicon |
| Wave-1 `_legacy_pick_sense` alias leaks into production callers | T-00 adds CI grep gate; only `tests/unit/test_disambiguate.py` may import the legacy alias |
| Cross-feature integration test (F17 → F18 → F19) not in scope for F18 step 3 | Intentional per workflow Track C ordering: integration tests fire after both sides exist. Marker: integration test for F17→F18→F19 lands in the same Track C wave as F19 T-02 (`diacritize_in_context`). Until then, T-05 is the only contract gate covering the wire |

## Acceptance Criteria — GH#20 regression coverage

The biz corpus (E04-F03) ships AC-01 (schema v1) and AC-02 (builder
determinism). Wave-2 refresh adds the following ACs that explicitly tie
F18 mechanics back to GH#20 regression cases:

### AC-N02/F18/US-01/AC-02 — `כל` qamatz-qatan override-hook smoke
```gherkin
Given the surface form `כל` is emitted by F17 with
  morph_features={"Definite": "Cons"} and ambiguous=True
And MORPH_HOMOGRAPH_OVERRIDES contains an entry for
  ("כל", frozenset({("Definite", "Cons")}))
When pick_sense(token) is called
Then the returned NLPToken matches the override-table value
And the v1 invariant passes on the resulting NLPResult
And the regression case "issue#20: כל qamatz-qatan" is documented in
    tests/unit/test_disambiguate.py as `test_kol_homograph_override`
```
F21 owns the override-table entry; F18 owns the call site + the empty-table
pass-through behavior (so absent F21 the test pins the override-miss path).

### AC-N02/F18/US-01/AC-03 — gender mis-pick on ambiguous participle
```gherkin
Given F17 emits an NLPToken with morph_features={"Gender":"Fem","Number":"Sing","VerbForm":"Part"}
  and ambiguous=True
When pick_sense(token) is called with no override entry matching
Then the returned NLPToken is the original token (pass-through)
And assert_nlp_result_v1 accepts the result
And the regression case "issue#20: ambiguous participle gender" is
    pinned in tests/unit/test_disambiguate.py as `test_ambiguous_participle_passthrough`
```

### AC-N02/F18/US-01/AC-04 — F26 graceful-fallback provider acceptance
```gherkin
Given F26 returns NLPResult(provider="degraded", tokens=(), confidence=None)
  because F17 model load failed
When assert_nlp_result_v1(result) runs inside assert_adapter_contract
Then the assertion passes (no SchemaContractError)
And the regression case "issue#20: cross-feature crash on F17 unavailable"
    is pinned in tests/unit/test_nlp_v1_invariants.py
```

### AC-N02/F18/US-01/AC-05 — legacy provider rejection
```gherkin
Given an NLPResult with provider="dictabert-large-joint"
When assert_nlp_result_v1(result) runs
Then SchemaContractError is raised
And the error message contains the substring "legacy provider"
And the substring "ADR-026" appears in the error message for traceability
```

### AC-N02/F18/US-01/AC-06 — F26 success-path provider with `+` separator
```gherkin
Given F26 returns NLPResult(provider="alephbert+yap", ...) per ADR-027 §implementation
When assert_nlp_result_v1(result) runs
Then the assertion passes
And the transitional spelling "alephbert-yap" is also accepted (regression
    test covers both)
```

These ACs collectively ensure that the GH#20 regression class — not just the
schema — is verified at the contract boundary. Without them, F18 could ship
"all tests green" while the trigger regression persisted.

## Diagrams

- `docs/diagrams/N02/F18/disambiguation.mmd` — F17/F26 → F18 pick_sense
  + override → assert_nlp_result_v1 → F19 Nakdan input contract.

## Out of Scope

- Multi-model voting (F17 + F26 ensemble) — deferred MVP.
- Dependency-parse edges (deferred per HLD Deviation).
- User-feedback-driven sense correction (deferred MVP).
- Numeric `schema_version` field (deferred per ADR-014; contract test stays).
- **Production homograph-override entries** — owned by F21
  homograph-overrides; F18 only ships the call site + empty stub.
- Vendor SDK introspection (NLPBackend / DictaBERT / AlephBERT imports
  stay inside their adapter packages per ADR-029).
- Lemma backfill via `dictabert-lex` — deferred MVP per ADR-026.
- F17 → F18 → F19 integration test — deferred to Track C alongside
  F19 T-02 `diacritize_in_context`.
- Vendor-import lint test for F18 itself — A-3 deferred (F18 has no
  vendor symbols by construction; ruff banned-api covers the broader rule).
- Promotion of `_legacy_pick_sense` to a permanent API — deletion target
  for F18 wave-3 once F22/F19 callers migrate.
