"""F19 — Dicta-Nakdan diacritization adapter.

Implements :class:`tirvi.ports.DiacritizerBackend` against the public
Dicta REST API at ``nakdan-2-0.loadbalancer.dicta.org.il/api`` (per
ADR-025 — supersedes the in-process loader path of ADR-021 for POC).

Vendor isolation: HTTP I/O and the Dicta endpoint URL live only in
this package (DE-06, ADR-029).

Spec: N02/F19. Bounded context: ``bc:pronunciation``.
"""

__all__: list[str] = []
