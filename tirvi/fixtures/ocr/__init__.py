"""F10 — OCRResult fixture builder (YAML-backed).

Per ADR-017: ``OCRResultBuilder.from_yaml(path)`` reads a canonical YAML
fixture and constructs a fully-populated :class:`tirvi.results.OCRResult`.
The YAML format is the authoritative test fixture surface; bypasses raw
dataclass construction.

Public API filled at L5.

Spec: N01/F10. Bounded contexts: ``bc:platform`` (DE-01,03,04), ``bc:extraction`` (DE-02,05).
"""

__all__: list[str] = []
