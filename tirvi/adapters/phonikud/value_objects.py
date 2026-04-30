"""F20 — pronunciation hints (per-token IPA + stress + shva).

Spec: N02/F20 DE-02. AC: US-01/AC-01.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PronunciationHint:
    """Per-token pronunciation hint emitted by the F20 G2P adapter.

    Invariants (named, TDD fills):
      - INV-PHON-HINT-001 (DE-02): ``ipa`` is non-empty IPA string per F20 alphabet
      - INV-PHON-HINT-002 (DE-02): ``stress`` is 1-based index when present
      - INV-PHON-HINT-003 (DE-06): IPA characters JSON-safe (escape applied)
    """

    ipa: str
    stress: int | None = None
    shva: tuple[bool, ...] = ()
