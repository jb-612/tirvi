"""F15 T-08 — lint CLI for the acronym lexicon YAML.

Spec: N02/F15 DE-08. AC: US-01/AC-01. FT: FT-111. BT: BT-072.
"""

from pathlib import Path

import pytest

from tirvi.acronym.lint import main
from tirvi.acronym.loader import _load_cached, from_yaml


@pytest.fixture(autouse=True)
def _clear_cache():
    _load_cached.cache_clear()
    yield
    _load_cached.cache_clear()


def _w(p: Path, body: str) -> str:
    p.write_text(body, encoding="utf-8")
    return str(p)


def test_lint_returns_zero_on_valid_yaml(tmp_path: Path, capsys):
    p = _w(
        tmp_path / "ok.yaml",
        'version: "v1"\n'
        'entries:\n'
        '  - {form: "ד״ר", expansion: "דוקטור", source: "manual"}\n',
    )
    assert main([p]) == 0


def test_lint_nonzero_on_missing_version(tmp_path: Path, capsys):
    p = _w(
        tmp_path / "noversion.yaml",
        'entries:\n  - {form: "א", expansion: "alef", source: "manual"}\n',
    )
    rc = main([p])
    assert rc != 0
    err = capsys.readouterr().err
    assert "version" in err


def test_lint_nonzero_on_missing_form(tmp_path: Path, capsys):
    p = _w(
        tmp_path / "nofield.yaml",
        'version: "v1"\n'
        'entries:\n  - {expansion: "x", source: "manual"}\n',
    )
    rc = main([p])
    assert rc != 0
    assert "form" in capsys.readouterr().err


def test_lint_nonzero_on_missing_expansion(tmp_path: Path, capsys):
    p = _w(
        tmp_path / "noexp.yaml",
        'version: "v1"\n'
        'entries:\n  - {form: "א", source: "manual"}\n',
    )
    rc = main([p])
    assert rc != 0
    assert "expansion" in capsys.readouterr().err


def test_lint_nonzero_on_duplicate_form(tmp_path: Path, capsys):
    p = _w(
        tmp_path / "dup.yaml",
        'version: "v1"\n'
        'entries:\n'
        '  - {form: "א", expansion: "x", source: "m"}\n'
        '  - {form: "א", expansion: "y", source: "m"}\n',
    )
    rc = main([p])
    assert rc != 0
    assert "duplicate" in capsys.readouterr().err.lower()


def test_repo_fixture_lints_clean():
    """The shipped data/acronym-lexicon.yaml must pass lint."""
    repo_root = Path(__file__).resolve().parents[2]
    fixture = repo_root / "data" / "acronym-lexicon.yaml"
    assert fixture.exists()
    assert main([str(fixture)]) == 0


def test_expanded_text_lexicon_version_matches_loaded_lexicon(tmp_path: Path):
    p = _w(
        tmp_path / "v.yaml",
        'version: "2099-01-01"\n'
        'entries:\n  - {form: "ד״ר", expansion: "דוקטור", source: "manual"}\n',
    )
    lex = from_yaml(p)
    from tirvi.acronym.expand import tag_and_expand
    from tirvi.normalize.value_objects import NormalizedText, Span

    nt = NormalizedText(
        text="ד״ר",
        spans=(Span(text="ד״ר", start_char=0, end_char=3, src_word_indices=(0,)),),
    )
    et = tag_and_expand(nt, lex)
    assert et.lexicon_version == "2099-01-01"
