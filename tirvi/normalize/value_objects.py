"""F14 — normalization value objects.

Spec: N02/F14 DE-01. AC: US-01/AC-01.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Span:
    """One normalized span tracing back to source word indices.

    Invariants (named, TDD fills):
      - INV-NORM-SPAN-001 (DE-02): ``src_word_indices`` non-empty
      - INV-NORM-SPAN-002 (DE-02): char range ``(start_char, end_char)`` valid
    """

    text: str
    start_char: int
    end_char: int
    src_word_indices: tuple[int, ...]


@dataclass(frozen=True)
class RepairLogEntry:
    """Audit-trail entry for one repair applied during normalization.

    Invariants (named, TDD fills):
      - INV-NORM-LOG-001 (DE-04): ``rule_id`` matches a documented repair rule
      - INV-NORM-LOG-002 (DE-04): ``before`` and ``after`` are both non-empty
    """

    rule_id: str
    before: str
    after: str
    position: int


@dataclass(frozen=True)
class NormalizedText:
    """Output of the F14 normalization pass.

    Invariants (named, TDD fills):
      - INV-NORM-001 (DE-01): ``text`` is the cleaned-up source text
      - INV-NORM-002 (DE-02): union of ``span.src_word_indices`` covers every input word
      - INV-NORM-003 (DE-04): ``repair_log`` records every applied transformation
    """

    text: str
    spans: tuple[Span, ...]
    repair_log: tuple[RepairLogEntry, ...] = field(default_factory=tuple)
