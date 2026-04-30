"""Shared adapter-contract test harness (F03 DE-05).

``assert_adapter_contract(adapter, port)`` validates an adapter (real or fake)
against its port's contract:

  - returns the rich result type (rejects raw ``bytes`` — BT-009)
  - all required result fields are present and correctly typed
  - typed errors (subclasses of :class:`tirvi.errors.AdapterError`) are preserved

Spec: F03 DE-05. AC: US-01/AC-01. FT-anchor: FT-016. BT-anchor: BT-009, BT-011.
"""

from typing import Any


def assert_adapter_contract(adapter: Any, port: Any) -> None:
    """Assert that ``adapter`` conforms to the ``port`` Protocol.

    Invariants (named, TDD fills):
      - INV-CONTRACT-001 (BT-009): rejects ``bytes`` return with explicit
        ``"must return <ResultType>"`` message
      - INV-CONTRACT-002 (FT-016): asserts every required field on the
        returned result (provider, confidence, payload-specific fields)
      - INV-CONTRACT-003 (BT-011): catches schema drift after port evolution
        (parametrized over the fake registry)

    Raises :class:`tirvi.errors.SchemaContractError` on any contract violation.
    """
    # TODO US-01/AC-01: runtime_checkable isinstance(adapter, port) guard
    # TODO BT-009: invoke a representative method; assert return is the result class, not bytes
    # TODO FT-016: assert required fields per result type
    raise NotImplementedError
