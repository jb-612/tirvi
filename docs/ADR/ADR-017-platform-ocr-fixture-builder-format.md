# ADR-017: OCRResult fixture builder uses YAML, not a Python DSL

**Status:** Proposed

## Context

`tirvi.fixtures.ocr.OCRResultBuilder` lets test authors seed deterministic
`OCRResult` instances for every downstream stage's unit tests. Two
candidate formats: (a) declarative YAML template files; (b) a Python
fluent DSL (`builder().column(...).word(...)`). Biz S02 / E02-F03 left
the format open. The choice affects test readability, IDE diff churn,
and how the artefacts evolve as the schema grows.

## Decision

Adopt **YAML** templates loaded by `OCRResultBuilder.from_yaml(path)`.
Each fixture file lives under `tests/fixtures/ocr/` and is keyed by a
short slug (e.g., `two_column_he_with_en_inline.yaml`). The builder
validates against `assert_ocr_result_v1` before returning.

## Consequences

Positive:
- YAML diffs render reviewably in PRs; bbox arrays line up.
- Fixtures are language-agnostic — non-Python tooling (the future Flutter
  player or a JS-side validator) can load the same files.
- Templating is data-driven; no Python module import for fixture state.

Negative:
- YAML lacks IDE autocomplete; a JSON schema sidecar is required for IDE
  hints (deferred to MVP).
- Slightly more verbose than a fluent builder for trivial cases.

## Alternatives

- **Fluent Python DSL.** Rejected: ties fixtures to a Python toolchain;
  diff noise on field reordering is high; less reusable across runtimes.
- **JSON.** Rejected: comments + multi-line strings (Hebrew sentences)
  are awkward; YAML is a superset for this use.

## References

- HLD §4 — Adapter interfaces
- ADR-014 — Schema versioning by contract test
- Biz corpus E02-F03 / S02 / Open Question
- Related: N01/F10 design.md DE-03
