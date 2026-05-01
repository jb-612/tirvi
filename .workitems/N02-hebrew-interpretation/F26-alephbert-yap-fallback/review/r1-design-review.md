# R1 Design Review — N02/F26 AlephBERT + YAP Fallback NLP Path

- **Feature:** N02/F26 (YAP HTTP-server fallback for NLPBackend)
- **Reviewer:** R1 multi-role (6 specialist roles synthesized)
- **Date:** 2026-05-01
- **Inputs reviewed:** design.md, tasks.md, traceability.yaml, ontology-delta.yaml,
  user_stories.md, functional-test-plan.md, behavioural-test-plan.md,
  docs/diagrams/N02/F26/alephbert-yap-fallback.mmd,
  ADR-002, ADR-026, ADR-027, ADR-029,
  HLD §3.3/Worker, HLD §4/AdapterInterfaces, HLD §5.2/Processing

---

## Role 1 — Contract Alignment

### Finding 1: prefix_segments = None on YAP path — downstream F17 assumption risk
- **Area:** contract
- **Issue:** design.md §HLD Deviations notes "prefix_segments always None on YAP path."
  F17 DE-03 (prefix segmentation from BIO labels) is a DictaBERT-morph-only feature.
  YAP does NOT emit BIO labels — it emits lattice segments. F18 disambiguation and F19
  Nakdan-context tilt read `NLPToken.prefix_segments`; both features must tolerate None.
  design.md documents this but does not verify the tolerance in the downstream designs.
- **Severity:** Medium
- **Recommendation:** Confirm F18 and F19 do not fail on `prefix_segments=None`. Add a
  note to F26 design.md §Risks: "F18 and F19 read prefix_segments; must tolerate None
  (verified in respective feature designs)."

### Finding 2: YAP must be started out-of-band — startup dependency undocumented
- **Area:** contract / operational
- **Issue:** YAP runs as a local HTTP server started out-of-band (`yap api`). F26 assumes
  YAP is already running at `TIRVI_YAP_URL`. If YAP is not running, `analyze_via_yap()`
  will get a `ConnectionRefusedError`. DE-05 handles YAP unreachable → degraded result.
  But the startup dependency is not documented in design.md.
- **Severity:** Low
- **Recommendation:** Add to §Dependencies: "YAP binary must be running (started
  out-of-band via `yap api`); unavailability → degraded NLPResult per DE-05."

---

## Role 2 — Architecture & Pattern

### Finding 3: YAP lattice parser CC risk — lattice_md walk is complex
- **Area:** architecture / complexity
- **Issue:** DE-02 walks `lattice_md` with per-edge extraction of surface, lemma,
  CPOSTag, FPOSTag, feats, and multi-edge token collapsing. This is 4-5 distinct
  operations in one function. CC ≥ 5 is likely.
- **Severity:** High
- **Recommendation:** Decompose DE-02 into: (a) `parse_lattice_md(response) ->
  list[YAPEdge]` (CC ≤ 3), (b) `collapse_edges(edges) -> list[YAPToken]` (CC ≤ 3),
  (c) `extract_feats(feats_str) -> dict[str, str]` (CC ≤ 2). Add these helpers to
  tasks.md T-02 hints and design.md DE-02.

### Finding 4: UD-Hebrew mapper contains raw_pos in morph_features — locked schema check
- **Area:** architecture
- **Issue:** T-03 hints say "Preserve original CPOSTag inside morph_features under key
  `raw_pos` for debugging." The locked F03 NLPToken.morph_features is typed as
  `dict[str, str] | None`. The canonical UD-Hebrew keys are: gender, number, person,
  tense, Definite, Case, VerbForm. `raw_pos` is not in this list. Adding it extends
  the schema beyond what the lock allows.
- **Severity:** Critical
- **Recommendation:** Remove `raw_pos` from morph_features. Store it separately (e.g.,
  in a debug log or a local variable during parsing) but do NOT add it to the locked
  NLPToken.morph_features. The locked schema must be honored exactly. Update T-03 hints.

---

## Role 3 — Test Coverage

### Finding 5: FT-131 (YAP client POST) double-anchored to T-01 and T-04
- **Area:** test coverage
- **Issue:** FT-131 is anchored to both T-01 (client test) and T-04 (adapter test).
  The FT should be attributed to the integration-level test — the adapter test exercises
  the full path. The unit-level client test covers the HTTP mechanics. Both are valid
  anchor points.
- **Severity:** Low (informational)

### Finding 6: No test coverage for lattice multi-edge token collapsing (DE-02)
- **Area:** test coverage
- **Issue:** T-02 describes multi-edge token collapsing ("collapse multi-edge tokens by
  surface form") but the test hints only mention extracting surface/lemma/CPOSTag/feats.
  A Hebrew prefix-decomposed token (e.g., כשהתלמיד may appear as 4 lattice edges) requires
  a specific collapsing strategy. No test case for this scenario is documented.
- **Severity:** Medium
- **Recommendation:** Add a T-02 test case with a multi-edge Hebrew input asserting that
  the collapser produces the expected number of output tokens.

---

## Role 4 — HLD Compliance

### Finding 7: F26 correctly honors PRD §9 (Hebrew NLP local-first)
- **Area:** HLD compliance
- **Issue:** YAP runs locally (127.0.0.1); no data egress. PRD §9 constraint satisfied.
- **Severity:** Low (confirmation)

---

## Role 5 — Security

### Finding 8: YAP_BASE_URL is configurable — injection risk if user-supplied
- **Area:** security
- **Issue:** `TIRVI_YAP_URL` env var sets the YAP base URL. If this URL is user-controlled
  (e.g., from a request header rather than server env), it could be used for SSRF.
  In the current architecture, it's a server-side env var — no user input reaches it.
- **Severity:** Low (confirmation, not a current risk)
- **Recommendation:** Document in design.md that `TIRVI_YAP_URL` is a deployment-time
  server config, not a runtime-adjustable parameter.

---

## Summary

| Finding | Severity | Area | Action |
|---------|----------|------|--------|
| F1: prefix_segments=None tolerance | Medium | Contract | Add risk note; verify F18/F19 tolerance |
| F2: YAP startup dependency | Low | Contract | Add to Dependencies |
| F3: DE-02 CC risk | **High** | Architecture | Decompose into 3 helpers |
| **F4: raw_pos in locked schema** | **Critical** | Architecture | Remove raw_pos from morph_features |
| F5: FT-131 double anchor | Low | Test | Informational |
| F6: multi-edge test case | Medium | Test | Add collapsing test case |
| F7: PRD §9 confirmed | Low | HLD | None |
| F8: TIRVI_YAP_URL env config | Low | Security | Add note to design |

**Critical (1):** F4 — raw_pos violates locked F03 NLPToken schema. Update T-03 hints and design.md.
**High (1):** F3 — decompose lattice parser.
