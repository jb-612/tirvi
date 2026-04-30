"""F10 — fixture builders for deterministic adapter test setup.

Per ADR-014 (contract-test-only versioning): fixture builders ship as part
of the platform layer so adapters/tests can construct canonical result
instances without raw dataclass calls.
"""

__all__: list[str] = []
