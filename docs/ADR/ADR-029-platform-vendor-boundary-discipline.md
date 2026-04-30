# ADR-029: Vendor-boundary discipline — vendor SDK imports confined to `tirvi.adapters.<vendor>.**`

**Status:** Proposed

**Captures an unwritten convention** that has been propagated by mis-citation as "ADR-014 vendor boundary" across multiple feature designs and ADRs. ADR-014 governs **result-object schema versioning via contract tests**; it does not address the import-location question. This ADR formalizes the discipline as its own decision so the trace edges and citations are accurate.

## Context

The codebase wires concrete vendor SDKs (`transformers`, `torch`, `pytesseract`, `pdf2image`, `phonikud`, `google-cloud-texttospeech`) behind hexagonal-architecture ports defined in `tirvi/ports.py`. PRD §9 requires Hebrew NLP local-first; HLD §4 calls for vendor isolation behind small adapter interfaces specifically so we can swap vendors later. ADR-014 ratifies this swap-via-contract-tests: the result-object schema is the contract; adapters implement it.

But ADR-014 does not say **where** vendor imports may live. In practice the team has consistently followed an unwritten rule:

> Vendor SDK imports must live inside `tirvi.adapters.<vendor>.**` only. No vendor types appear in the public signature of any port; no vendor symbols are imported anywhere outside the adapter package.

This rule has been cited as "ADR-014 (vendor boundary)" in F17 design.md, F19 design.md, F20 design.md, F26 design.md, ADR-025, ADR-026, ADR-027, and several `tirvi/adapters/**/__init__.py` docstrings. The citation is wrong — ADR-014 does not contain those words. The rule is real; the trace path was misattributed.

Three downstream ADRs (ADR-025 Nakdan REST, ADR-027 YAP HTTP-server) extend the discipline to **HTTP endpoint URLs**: third-party endpoints are also vendor concerns and stay inside the adapter module. That extension is correctly captured in those ADRs but mis-attributed to ADR-014.

This ADR codifies the rule, so traceability edges (`spec → adr` INFLUENCED_BY, `adapter → adr` REALIZES) point at the right node.

## Decision

The vendor-boundary discipline has the following invariants:

1. **Vendor imports stay inside the adapter package.** `import transformers`, `import torch`, `import pytesseract`, `import pdf2image`, `import phonikud`, `from google.cloud import texttospeech` may only appear inside files under `tirvi/adapters/<vendor>/**`. They must never appear under `tirvi/blocks/`, `tirvi/normalize/`, `tirvi/plan/`, `tirvi/ssml/`, `tirvi/pipeline.py`, or `tirvi/ports.py`.
2. **Vendor types stay inside the adapter package.** Types from vendor packages (e.g., `transformers.PreTrainedModel`, `pdf2image.exceptions.PDFInfoNotInstalledError`) may not appear in public function signatures, return-type annotations, or dataclass fields anywhere outside the adapter package.
3. **Lazy import inside function bodies.** Vendor imports occur at first call (inside the function body), not at module load time. This keeps `tirvi/adapters/<vendor>/loader.py` importable without the vendor package present, which makes test stubbing via `sys.modules.setdefault(...)` viable. Pattern reference: `tirvi/adapters/dictabert/loader.py`, `tirvi/adapters/nakdan/loader.py` (now deprecated per ADR-025), `tirvi/adapters/wavenet/client.py`.
4. **Third-party HTTP endpoints are vendor concerns.** A `https://...` URL constant for a third-party API (Dicta REST, YAP HTTP server, Google TTS) lives only inside `tirvi/adapters/<vendor>/client.py` (or equivalent submodule). Other features that need diacritization / NLP / TTS go through the port, never construct URLs directly.
5. **Tests respect the boundary.** Unit tests stub vendor packages via `sys.modules.setdefault("transformers", MagicMock())` (or equivalent) before importing the adapter under test. This pattern is established in `tests/unit/test_dictabert_loader.py`, `tests/unit/test_nakdan_loader.py`, `tests/unit/test_tesseract_adapter_ocr_pdf.py`. Tests outside `tests/unit/test_<vendor>_*.py` must not stub vendor packages — that signals a leak.

The discipline composes with ADR-014: ADR-014 enforces the *shape* of what crosses the boundary (the result-object contract); ADR-029 enforces the *direction* (everything vendor stays on the adapter side).

## Consequences

Positive:

- **Trace edges are now accurate.** Designs and ADRs that previously cited "ADR-014 (vendor boundary)" can update to "ADR-029 (vendor boundary)" without changing any code; only the citations move.
- **The unwritten rule becomes inspectable.** New contributors discovering the codebase can find one ADR that explains the discipline, instead of inferring it from grep patterns.
- **MVP planning gains a hook.** Future ADRs that propose loosening the discipline (e.g., vendor types in public signatures for performance reasons) supersede this ADR explicitly rather than implicitly.

Negative:

- **One more ADR to maintain.** The trade-off is small — this ADR will rarely change; it captures a stable pattern.
- **Existing mis-citations need a sweep.** A one-time mechanical fix; tracked as a follow-up sweep in the wave-1 remediation pass.

## Alternatives

- **Extend ADR-014 to cover the boundary.** Rejected: ADR-014 is specifically about how the result-object schema evolves over time via contract tests. Stretching it to also govern import locations would conflate two orthogonal concerns. Per `.claude/rules/orchestrator.md`, ADRs should hold one material decision each.
- **Leave the rule unwritten.** Rejected: the mis-citations across F17/F19/F20/F26 + ADR-025/026/027 demonstrate that an unwritten rule produces false trace edges. The graph slice in `ontology/dependencies.yaml` is consumed by ACM queries; wrong edges return wrong answers.
- **Delete the discipline entirely (allow vendor imports anywhere).** Rejected: violates HLD §4 vendor-isolation goal and breaks ADR-014's swap-via-contract-tests promise. Vendor-locked sites can't be refactored to a different SDK without source-wide grep-and-replace.

## References

- HLD §1 (architectural principle — middle layer is defensible only if vendors are swappable)
- HLD §4 (adapter interfaces table — vendor isolation goal)
- PRD §9 (Hebrew NLP local-first constraint)
- ADR-014 — Result-object schema versioning (composes with this ADR; not superseded)
- Pattern references in code: `tirvi/adapters/dictabert/loader.py`, `tirvi/adapters/nakdan/client.py`, `tirvi/adapters/wavenet/client.py`, `tirvi/adapters/tesseract/invoker.py`
- Test pattern: `tests/unit/test_dictabert_loader.py` (sys.modules.setdefault stub pattern)
- Mis-cited from: F17/F19/F20/F26 design.md (wave 1, 2026-04-30); ADR-025, ADR-026, ADR-027
