"""F26 — AlephBERT + YAP fallback NLP adapter package.

Spec: N02/F26 (per ADR-027). Vendor boundary: HTTP I/O lives only inside
this package (DE-06, ADR-029). No transformers/AlephBERT model imports
for the POC.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .adapter import AlephBertYapFallbackAdapter


def __getattr__(name: str):
    if name == "AlephBertYapFallbackAdapter":
        from .adapter import AlephBertYapFallbackAdapter

        return AlephBertYapFallbackAdapter
    raise AttributeError(name)


__all__ = ["AlephBertYapFallbackAdapter"]
