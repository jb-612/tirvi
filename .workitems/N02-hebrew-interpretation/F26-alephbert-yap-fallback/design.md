---
feature_id: N02/F26
feature_type: domain
status: drafting
hld_refs:
  - HLD-§3.3/Worker
  - HLD-§4/AdapterInterfaces
  - HLD-§5.2/Processing
prd_refs:
  - "PRD §6.4 — Reading plan"
  - "PRD §9 — Constraints"
adr_refs: [ADR-002, ADR-026, ADR-027, ADR-029]
biz_corpus: true
biz_corpus_e_id: E04-F02
---

# Feature: AlephBERT + YAP Fallback NLP Path

## Overview

Secondary `NLPBackend` implementation invoked when the F17 DictaBERT-morph
primary path raises `ImportError`/`OSError` (per ADR-029 vendor-boundary
discipline) or returns a degraded result. Wraps **YAP** (Bar-Ilan ONLP
Lab's morphological + dependency parser, github.com/OnlpLab/yap) running
in HTTP-server mode (`yap api`). YAP supplies POS + morph + lemma; the
adapter maps YAP's label set to the canonical `NLPResult` schema so
downstream consumers (F18 disambiguation, F19 Nakdan-context tilt, F22
reading plan) need no branching. AlephBERT-Gimmel embeddings for
ambiguity tie-breaking are deferred to MVP per ADR-027 — POC ships the
YAP-only path. PRD §9 ("Hebrew NLP local-first") is upheld: YAP runs as
a local HTTP server, no third-party data egress.

## Dependencies

- Upstream: N00/F03 (`NLPBackend` port, `NLPResult` shape — locked),
  N02/F14 (`NormalizedText` input).
- Sibling primary: **N02/F17 DictaBERT-morph** — F26 is invoked from
  F17's adapter on load failure (DE-06 in F17). Primary recovery on a
  later page returns control to F17.
- Adapter port consumed: `tirvi.ports.NLPBackend` (this feature's second
  implementer; F17 is the first).
- External services: locally-run YAP HTTP server on `127.0.0.1:8000`
  (default `yap api` port); user starts the binary out-of-band.
- Downstream: F18, F19, F22 (consume the canonicalized `NLPResult`
  irrespective of provider).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.adapters.alephbert` | `AlephBertYapFallbackAdapter` | class | implements `NLPBackend.analyze(self, text: str, lang: str) -> NLPResult` (port signature; `lang` param accepted but POC ignores it — YAP is Hebrew-only) |
| `tirvi.adapters.alephbert.client` | `analyze_via_yap(text, *, base_url, timeout)` | function | POSTs to `${base_url}/api/v0/joint`; returns parsed JSON |
| `tirvi.adapters.alephbert.mapper` | `yap_to_nlpresult(yap_response)` | function | YAP labels → canonical UD-Hebrew `NLPResult` |
| `tirvi.adapters.alephbert.config` | `YAP_BASE_URL` (env `TIRVI_YAP_URL`) | constant | default `http://127.0.0.1:8000` |

`NLPResult.provider == "alephbert+yap"` on success; `"degraded"` when YAP
unreachable. Each `NLPResult.tokens[i]` is the locked F03 `NLPToken`
dataclass: `text`, `pos`, `lemma`, `prefix_segments: tuple[str, ...] |
None` (always `None` on the YAP path — see HLD Deviations row), `confidence: float | None` (POC: `None` for all tokens since YAP doesn't
expose softmax margins), `morph_features: dict[str, str] | None` with
canonical UD-Hebrew keys (`gender`, `number`, `person`, `tense`,
`Definite`, `Case`, `VerbForm`), `ambiguous: bool = False`. **Same
locked schema as F17 emits** — downstream consumers do not branch on
provider.

## Approach

1. **DE-01**: YAP HTTP client — POST `{"text": text}` to
   `${YAP_BASE_URL}/api/v0/joint`; parse JSON with `lattice_md` (morph
   disambiguation) and `lattice_ma` (morphological analysis) sub-arrays.
   Stdlib `urllib.request` (no new vendor dep); 30s timeout.
2. **DE-02**: YAP response parser — walk the disambiguated lattice
   (`lattice_md`); extract per-token surface, lemma, CPOSTag, FPOSTag,
   feats string ("Definite=Def|Gender=Masc|..."); split feats into
   `morph: dict[str,str]`.
3. **DE-03**: UD-Hebrew schema mapper — YAP CPOSTag → canonical UD pos
   (e.g., `VB → VERB`, `NN → NOUN`); morph keys normalized
   (Definite, Gender, Number, Person, Case, Tense, VerbForm). Missing
   primary fields filled with `None` (per biz S02 AC).
4. **DE-04**: Fallback adapter wrapper — `AlephBertYapFallbackAdapter`
   implements `NLPBackend`; `analyze()` calls client → mapper → returns
   `NLPResult(provider="alephbert+yap", tokens=...)`.
5. **DE-05**: Connection-failed degraded path — on any of
   `URLError`/`socket.timeout`/`ConnectionRefusedError`/`json.JSONDecodeError`/`KeyError`/non-200
   HTTP status, return `NLPResult(provider="degraded", tokens=[],
   confidence=None)`. Downstream stages tolerate empty tokens (F22 plan
   and F19 Nakdan REST already do — verified by the integration assertion
   in T-09 below). Empty input (`text.strip() == ""`) is **not** a
   degraded case: it returns `provider="alephbert+yap", tokens=[]`. The
   provider-stamp matrix is part of the test pinning.
6. **DE-06**: Adapter contract conformance — passes
   `assert_adapter_contract` (deferred F03 task); provider stamp on every
   result; F17 owns the wiring (its DE-06 wraps `analyze()` in
   try/except). F26 only exposes the importable
   `tirvi.adapters.alephbert.AlephBertYapFallbackAdapter`.

7. **DE-07**: YAP availability health probe — on adapter `__init__`,
   issue a one-shot `GET ${YAP_BASE_URL}/` with 2s timeout; on failure
   log a single WARN line "YAP not reachable at <url> — start with
   `yap api`; pipeline will continue with degraded NLP". Independent of
   degraded behaviour — gives a single grep-able signal at run start
   instead of silent fall-through. Idempotent (one log per adapter
   instance).

## Design Elements

- DE-01: yapHttpClient (ref: HLD-§4/AdapterInterfaces)
- DE-02: yapResponseParser (ref: HLD-§5.2/Processing)
- DE-03: udLabelMapper (ref: HLD-§5.2/Processing)
- DE-04: fallbackAdapterWrapper (ref: HLD-§4/AdapterInterfaces, HLD-§3.3/Worker)
- DE-05: connectionFailedDegradedPath (ref: HLD-§3.3/Worker)
- DE-06: adapterContractConformance (ref: HLD-§4/AdapterInterfaces)
- DE-07: yapHealthProbe (ref: HLD-§3.3/Worker)

## Decisions

- D-01: YAP integration mode = local HTTP server (`yap api`) → **ADR-027** (new).
- D-02: AlephBERT-Gimmel embeddings deferred to MVP for ambiguity tie-breaking → captured in ADR-027 §Out of Scope.
- D-03: Vendor primary choice (DictaBERT) unchanged → **ADR-002** (existing).
- D-04: Vendor boundary applies to YAP HTTP calls (only this module touches the URL) → **ADR-029** (codifies the previously-implicit rule).

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| HLD §4 fallback row | "local AlephBERT + YAP" — POC ships YAP-only | ADR-027 — AlephBERT integration deferred for POC simplicity |
| Failover policy | Per-page granularity (biz S01 AC) deferred — POC is single-page demo | PLAN-POC.md scope; multi-page failover lands in MVP |
| Telemetry (E10-F05) | Provider stamp logged via `NLPResult.provider`; no external metrics export | E10 features deferred per PLAN-POC |

## HLD Open Questions

- Should fallback run in shadow during MVP for parity comparison? → Deferred to MVP (biz S01 OQ).
- Document fallback gaps explicitly in schema? → Resolved by DE-03: missing fields are explicit `None` (biz S02 OQ).
- Mid-doc primary recovery → Deferred per single-page POC.

## Risks

| Risk | Mitigation |
|------|-----------|
| YAP binary not built on developer machine | DE-05 returns degraded NLPResult; demo continues without context (matches current `_StubNLP` baseline) |
| YAP HTTP server crashes mid-call | DE-05 timeout + reconnection; per-call independence |
| YAP UD label set drifts from canonical | DE-03 mapper table; one place to update |
| AlephBERT integration creep into POC scope | ADR-027 explicit out-of-scope |

## Diagrams

- `docs/diagrams/N02/F26/alephbert-yap-fallback.mmd` — F17 ImportError → F26 client → YAP → mapper → NLPResult (provider stamp); degraded path on connection failure

## Out of Scope

- AlephBERT-Gimmel embeddings (deferred MVP per ADR-027).
- Failover policy with retries / circuit breaker (single-page POC).
- Telemetry (provider rate, fallback metrics) — E10 deferred.
- Shadow-run parity comparison with primary (deferred MVP).
- HebPipe-style multi-tool orchestration — owned by F27.
- Subprocess-per-call YAP invocation (rejected per ADR-027).
