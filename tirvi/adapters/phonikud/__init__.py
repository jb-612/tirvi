"""F20 — Phonikud G2P adapter.

Implements :class:`tirvi.ports.G2PBackend` via the open-source ``phonikud``
package; emits IPA per token plus stress + shva markers.

Vendor isolation: this module is the only place ``phonikud`` may be imported
(DE-06, ADR-014, ADR-022).

Spec: N02/F20. Bounded context: ``bc:pronunciation``.
"""

__all__: list[str] = []
