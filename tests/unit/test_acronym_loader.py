"""F15 T-02 — YAML lexicon loader + mtime cache.

Spec: N02/F15 DE-02. AC: US-01/AC-01. FT: FT-111.
"""

from pathlib import Path

import pytest

from tirvi.acronym.loader import _load_cached
from tirvi.acronym.value_objects import Lexicon


@pytest.fixture(autouse=True)
def _clear_cache():
    _load_cached.cache_clear()
    yield
    _load_cached.cache_clear()


def _write(p: Path, body: str) -> Path:
    p.write_text(body, encoding="utf-8")
    return p


def test_from_yaml_parses_version_and_entries(tmp_path: Path):
    p = _write(
        tmp_path / "lex.yaml",
        """
version: "2026-05-01"
entries:
  - {form: "ד״ר", expansion: "דוקטור", source: "manual"}
  - {form: "ת״א", expansion: "תל אביב", source: "manual", context_tags: ["geo"]}
""".strip(),
    )

    lex = Lexicon.from_yaml(p)

    assert lex.version == "2026-05-01"
    assert len(lex.entries) == 2
    assert lex.entries[0].form == "ד״ר"
    assert lex.entries[0].expansion == "דוקטור"
    assert lex.entries[1].context_tags == ("geo",)
    assert lex._index["ת״א"].expansion == "תל אביב"


def test_from_yaml_preserves_yaml_source_order(tmp_path: Path):
    p = _write(
        tmp_path / "lex.yaml",
        """
version: "v1"
entries:
  - {form: "ב", expansion: "ב-exp", source: "manual"}
  - {form: "א", expansion: "א-exp", source: "manual"}
""".strip(),
    )

    lex = Lexicon.from_yaml(p)
    assert [e.form for e in lex.entries] == ["ב", "א"]


def test_from_yaml_caches_by_mtime(tmp_path: Path, monkeypatch):
    p = tmp_path / "lex.yaml"
    body = (
        'version: "v1"\n'
        'entries:\n'
        '  - {form: "א", expansion: "alef", source: "manual"}\n'
    )
    p.write_text(body, encoding="utf-8")

    lex1 = Lexicon.from_yaml(p)
    lex2 = Lexicon.from_yaml(p)
    # Same mtime + path → cache hit; same instance
    assert lex1 is lex2

    # Touch the file (new mtime) → cache miss → new instance
    import os
    st = p.stat()
    os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000_000))
    lex3 = Lexicon.from_yaml(p)
    assert lex3 is not lex1
    assert lex3.version == "v1"
