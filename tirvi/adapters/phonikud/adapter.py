"""PhonikudG2PAdapter — :class:`tirvi.ports.G2PBackend` implementation.

Spec: N02/F20. AC: US-01/AC-01.
"""

from tirvi.ports import G2PBackend
from tirvi.results import G2PResult

from .inference import grapheme_to_phoneme as _g2p


class PhonikudG2PAdapter(G2PBackend):
    """Phonikud-based grapheme-to-phoneme adapter.

    Invariants (named, TDD fills):
      - INV-PHON-001 (DE-01, ADR-022): lazy-import ``phonikud``; fall back to fake when missing
      - INV-PHON-002 (DE-02): emits IPA per F20 alphabet; preserves Phonikud stress index
      - INV-PHON-006 (DE-06, ADR-014): vendor SDK imports stay in this module
    """

    def __init__(self) -> None:
        pass

    def grapheme_to_phoneme(self, text: str, lang: str) -> G2PResult:
        return _g2p(text, lang=lang)
