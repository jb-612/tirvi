"""tirvi — Hebrew exam PDF → audio reading accommodation.

This package exposes the hexagonal port boundary defined by feature N00/F03.
Domain code never imports vendor SDKs; vendor adapters live in
:mod:`tirvi.adapters` and are gated by the ruff vendor-import lint
(see ``ruff.toml``, F03 DE-06, ADR-014).
"""

__version__ = "0.0.0"

__all__: list[str] = []
