---
adr_id: ADR-014
title: Result-object schema versioning — contract tests over numeric versions
status: Proposed
date: 2026-04-29
deciders: [jbellish]
bounded_context: platform
hld_refs: [HLD-§4/AdapterInterfaces, HLD-§10/Vendor-lock-in]
related_features: [N00/F03]
related_adrs: [ADR-015]
---

# ADR-014 — Result-object schema versioning

## Status

**Proposed** (2026-04-29). Promotes to **Accepted** when N00/F03 ships
green. Resolves biz S01 open question: "Do we version result schemas with
explicit `version` field or rely on adapter contract tests?"

## Context

F03 introduces six rich result-object value types (`OCRResult`,
`NLPResult`, `DiacritizationResult`, `G2PResult`, `TTSResult`,
`WordTimingResult`) crossing the hexagonal port boundary. As the pipeline
evolves, fields will be added, renamed, or removed.

Two ways to manage that drift:

1. Embed an explicit `schema_version: int` in each result; adapters and
   consumers negotiate compatibility at runtime.
2. Pin shape with frozen dataclasses + a shared adapter contract test
   (`assert_adapter_contract`); rely on CI to catch drift at build time
   and treat any field change as a coordinated repo-wide PR.

Per ASM03 + biz BT-009/BT-011, the dominant failure mode is **silent fake
staleness** after a port evolves — not multi-version coexistence between
adapters running in parallel. There is one repository, one deployment
target, and adapters do not ship independently.

## Decision

**Adopt option 2 — contract-test-pinned schemas, no numeric version field.**

Each result type is a frozen `@dataclass` (Python). Schema drift is caught
by `assert_adapter_contract(adapter, port)` running in CI against every
real adapter and every fake. Field additions land as coordinated PRs that
update the dataclass, every adapter, every fake, and every consumer in the
same change.

The `provider` audit field on each result remains required; it is **not**
a schema version — it identifies which adapter produced the result.

## Consequences

**Positive**
- One source of truth (the dataclass); no version-skew logic in adapters.
- Forces tight coupling reviews when changing shared shapes — the right
  pressure for a small team.
- Contract tests double as living documentation of port shape.

**Negative**
- Independent adapter releases are not possible; all adapters move
  together. Acceptable while tirvi has one deployment target.
- A cross-cutting field rename touches every adapter + fake + consumer
  in one PR. The repo audit checklist (BT-011) lists each touchpoint.

## Alternatives

- **Numeric `schema_version` field**: rejected — adds runtime branching
  with no operational payoff while we have one deployment.
- **Pydantic models with `model_config.frozen = True`**: viable but heavier
  than dataclasses; defer until a result type needs JSON-Schema export.

## References

- HLD §4 — Adapter interfaces
- biz `behavioural-test-plan.md` BT-011 — SDK maintainer evolves a port
- biz `user_stories.md` S01 Open Question (versioning policy)
- ADR-015 (companion: WordTimingProvider fallback policy)
