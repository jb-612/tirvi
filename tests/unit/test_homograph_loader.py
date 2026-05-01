"""F21 T-02 — YAML homograph loader + mtime cache.

Spec: N02/F21 DE-02. AC: US-01/AC-01. FT: FT-158, FT-159, FT-162.
"""

import os
import time
from pathlib import Path

import pytest

from tirvi.homograph.loader import _load_cached, load_overrides


@pytest.fixture(autouse=True)
def _clear_cache():
    _load_cached.cache_clear()
    yield
    _load_cached.cache_clear()


def _write(p: Path, body: str) -> Path:
    p.write_text(body, encoding="utf-8")
    return p


def test_load_empty_file_returns_empty_dict(tmp_path: Path):
    p = _write(tmp_path / "lex.yaml", "")
    assert load_overrides(p) == {}


def test_load_two_entries_without_pos_filter(tmp_path: Path):
    p = _write(
        tmp_path / "lex.yaml",
        """
entries:
  - {surface_form: "כל", vocalized_form: "כֹּל", pos_filter: null}
  - {surface_form: "אבא", vocalized_form: "אַבָּא", pos_filter: null}
""".strip(),
    )
    out = load_overrides(p)
    assert out == {"כל": "כֹּל", "אבא": "אַבָּא"}


def test_load_skips_pos_filtered_entries(tmp_path: Path):
    p = _write(
        tmp_path / "lex.yaml",
        """
entries:
  - {surface_form: "כל", vocalized_form: "כֹּל", pos_filter: null}
  - {surface_form: "ספר", vocalized_form: "סָפַר", pos_filter: "VERB"}
""".strip(),
    )
    out = load_overrides(p)
    assert out == {"כל": "כֹּל"}


def test_load_malformed_yaml_raises_value_error(tmp_path: Path):
    p = _write(tmp_path / "lex.yaml", "entries: [unterminated")
    with pytest.raises(ValueError):
        load_overrides(p)


def test_load_missing_required_field_raises_value_error(tmp_path: Path):
    p = _write(
        tmp_path / "lex.yaml",
        'entries:\n  - {surface_form: "כל"}\n',
    )
    with pytest.raises(ValueError):
        load_overrides(p)


def test_load_two_entry_yaml_under_200ms(tmp_path: Path):
    p = _write(
        tmp_path / "lex.yaml",
        """
entries:
  - {surface_form: "כל", vocalized_form: "כֹּל", pos_filter: null}
  - {surface_form: "אבא", vocalized_form: "אַבָּא", pos_filter: null}
""".strip(),
    )
    _load_cached.cache_clear()
    start = time.perf_counter()
    load_overrides(p)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 200


def test_load_caches_by_mtime(tmp_path: Path):
    p = _write(
        tmp_path / "lex.yaml",
        'entries:\n  - {surface_form: "כל", vocalized_form: "כֹּל", pos_filter: null}\n',
    )
    a = load_overrides(p)
    b = load_overrides(p)
    assert a is b
    st = p.stat()
    os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000_000))
    c = load_overrides(p)
    assert c is not a
