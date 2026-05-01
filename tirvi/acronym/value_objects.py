"""F15 — Acronym value objects.

Spec: N02/F15 DE-01. AC: US-01/AC-01, US-02/AC-01.
"""

from dataclasses import dataclass, field

from tirvi.normalize.value_objects import RepairLogEntry, Span


@dataclass(frozen=True)
class AcronymEntry:
    """One acronym lexicon entry.

    Invariants:
      - INV-ACR-ENTRY-001 (DE-01): ``form`` is the surface acronym
      - INV-ACR-ENTRY-002 (DE-01): ``expansion`` is the spoken expansion
    """

    form: str
    expansion: str
    source: str
    context_tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class Lexicon:
    """Acronym lexicon with derived form→entry index.

    Invariants:
      - INV-ACR-LEX-001 (DE-01): ``_index`` maps every entry's form to itself
    """

    version: str
    entries: tuple[AcronymEntry, ...]
    _index: dict[str, AcronymEntry] = field(
        init=False, repr=False, compare=False
    )

    def __post_init__(self) -> None:
        index: dict[str, AcronymEntry] = {}
        for entry in self.entries:
            index.setdefault(entry.form, entry)
        object.__setattr__(self, "_index", index)


@dataclass(frozen=True)
class ExpansionLogEntry:
    """One expansion (or spell-out) audit-log entry.

    Invariants:
      - INV-ACR-LOG-001 (DE-04): ``src_word_indices`` non-empty for matches
      - INV-ACR-LOG-002 (DE-06): ``spell_out=True`` iff fallback path
    """

    original_form: str
    expansion: str
    src_word_indices: tuple[int, ...]
    spell_out: bool


@dataclass(frozen=True)
class ExpandedText:
    """Output of the F15 acronym expansion pass.

    Invariants:
      - INV-ACR-001 (DE-04): ``text`` is the expanded surface text
      - INV-ACR-002 (DE-04): multi-word expansions form one logical span
      - INV-ACR-003 (DE-08): ``lexicon_version`` matches lexicon used
    """

    text: str
    spans: tuple[Span, ...]
    repair_log: tuple[RepairLogEntry, ...]
    expansion_log: tuple[ExpansionLogEntry, ...]
    lexicon_version: str
