"""tirvi.upload — Upload attestation gate (deferred post-POC).

Spec: N05/F45. Status: deferred — populated when biz-functional-design
runs for N05.
"""

from __future__ import annotations


def validate_attestation(attested_no_pii: bool | None) -> None:  # pragma: no cover - stub
    """Reject upload (HTTP 422) when ``attested_no_pii`` is missing or False."""
    raise NotImplementedError("F45 deferred post-POC")
