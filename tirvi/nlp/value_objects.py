"""F18 — disambiguated token VO (extends F17's NLPToken with sense fields).

Spec: N02/F18 DE-01, DE-02, DE-03. AC: US-01/AC-01.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DisambiguatedToken:
    """Token after F18 disambiguation; extends F17's NLPToken.

    Invariants (named, TDD fills):
      - INV-DISAM-T-001 (DE-01): ``pos`` is a valid UD-Hebrew POS tag
      - INV-DISAM-T-002 (DE-02): ``morph`` keys whitelisted; values are short tags
      - INV-DISAM-T-003 (DE-03): ``ambiguous=True`` when softmax margin < threshold
      - INV-DISAM-T-004 (biz S01): ``confidence`` is float|None, never 0.0 default
    """

    text: str
    pos: str
    lemma: str
    morph: dict[str, str] = field(default_factory=dict)
    confidence: float | None = None
    ambiguous: bool = False
