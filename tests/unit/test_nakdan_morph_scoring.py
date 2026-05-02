"""Tests for the dict-shape option scoring path (ADR-039).

Covers: `task: "morph"` returns options as dicts. The inference layer
scores them using lex + prefix_len + DictaBERT POS, NOT the
undocumented Dicta morph bitfield.

Spec: N02/F19. AC: closes #27. ADR-039.
"""
from __future__ import annotations

from tirvi.adapters.nakdan.inference import (
    _project_with_context,
    _score_option,
)
from tirvi.results import NLPToken


def _opt(w: str, lex: str, prefix_len: int = 0, level: int = 1, **extra) -> dict:
    base = {
        "w": w, "lex": lex, "prefix_len": prefix_len, "levelChoice": level,
        "Acc": "Acc0", "stdW": w,
    }
    base.update(extra)
    return base


def _entry(word: str, options: list, sep: bool = False) -> dict:
    return {"word": word, "sep": sep, "options": options, "fpasuk": False, "fconfident": False}


def _token(text: str, pos: str | None) -> NLPToken:
    return NLPToken(text=text, pos=pos, lemma=text)


# --- _score_option unit tests ---


def test_score_option_adj_canonical_form_no_prefix_scores_high():
    # שָׁלֵו = "calm" — adjective; lex==w, no prefix
    opt = _opt("שָׁלֵו", "שָׁלֵו", prefix_len=0)
    token = _token("שלו", pos="ADJ")
    assert _score_option(opt, token) >= 3


def test_score_option_adp_canonical_form_loses_to_function_word_lookup():
    # שֶׁלּוֹ = "his" — preposition; lex==שֶׁל is in function word lex
    opt_his = _opt("שֶׁלּוֹ", "שֶׁל", prefix_len=0)
    token = _token("שלו", pos="ADP")
    assert _score_option(opt_his, token) >= 3


def test_score_option_sconj_function_word_scores_high():
    # הַאִם = "whether" — SCONJ; lex=אִם is in function word lex
    opt = _opt("הַאִם", "אִם", prefix_len=0)
    token = _token("האם", pos="SCONJ")
    assert _score_option(opt, token) >= 3


def test_score_option_pos_mismatch_scores_zero():
    opt = _opt("שָׁלֵו", "שָׁלֵו", prefix_len=0)
    token = _token("שלו", pos="VERB")  # mismatched POS
    assert _score_option(opt, token) == 0


def test_score_option_no_pos_scores_zero():
    opt = _opt("שָׁלֵו", "שָׁלֵו", prefix_len=0)
    token = _token("שלו", pos=None)
    assert _score_option(opt, token) == 0


# --- _project_with_context integration with dict options ---


def test_dict_options_adj_pos_picks_adjective_not_possessive():
    """ADJ-tagged token should resolve to שָׁלֵו (calm), not שֶׁלּוֹ (his)."""
    entries = [
        _entry("הוא",   [_opt("הוּא",     "הוּא")]),
        _entry(" ",     [], sep=True),
        _entry("טיפוס", [_opt("טִפּוּס", "טִפּוּס")]),
        _entry(" ",     [], sep=True),
        _entry("שלו",   [
            _opt("שֶׁלּוֹ", "שֶׁל",     prefix_len=0, level=1),
            _opt("שָׁלֵו",  "שָׁלֵו",    prefix_len=0, level=2),
        ]),
        _entry(" ",     [], sep=True),
        _entry("ורגוע", [_opt("וְרָגוּעַ", "רָגוּעַ", prefix_len=1)]),
    ]
    tokens = [
        _token("הוא",   "PRON"),
        _token("טיפוס", "NOUN"),
        _token("שלו",   "ADJ"),     # DictaBERT correctly says ADJ here
        _token("ורגוע", "ADJ"),
    ]
    out = _project_with_context(entries, tokens, sentence="הוא טיפוס שלו ורגוע")
    assert "שָׁלֵו" in out
    assert "שֶׁלּוֹ" not in out


def test_dict_options_adp_pos_keeps_possessive():
    """ADP-tagged token (correctly) keeps שֶׁלּוֹ via top-1 + scoring."""
    entries = [
        _entry("זה",    [_opt("זֶה", "זֶה")]),
        _entry(" ",     [], sep=True),
        _entry("הספר",  [_opt("הַסֵּפֶר", "סֵפֶר", prefix_len=1)]),
        _entry(" ",     [], sep=True),
        _entry("שלו",   [
            _opt("שֶׁלּוֹ", "שֶׁל",  prefix_len=0, level=1),
            _opt("שָׁלֵו",  "שָׁלֵו", prefix_len=0, level=2),
        ]),
    ]
    tokens = [
        _token("זה",   "PRON"),
        _token("הספר", "NOUN"),
        _token("שלו",  "ADP"),
    ]
    out = _project_with_context(entries, tokens, sentence="זה הספר שלו")
    assert "שֶׁלּוֹ" in out
    assert "שָׁלֵו" not in out


def test_dict_options_sconj_picks_whether_over_mother():
    """SCONJ-tagged `האם` resolves to הַאִם (whether), not הָאֵם (mother)."""
    entries = [
        _entry("האם",  [
            _opt("הָאֵם",  "אֵם", prefix_len=1, level=1),  # mother is Dicta top-1
            _opt("הַאִם",  "אִם", prefix_len=0, level=2),  # whether is fallback
        ]),
        _entry(" ",     [], sep=True),
        _entry("כדאי",  [_opt("כְּדַאי", "כְּדַאי")]),
    ]
    tokens = [
        _token("האם",  "SCONJ"),  # DictaBERT signal: this is interrogative
        _token("כדאי", "ADV"),
    ]
    out = _project_with_context(entries, tokens, sentence="האם כדאי")
    assert "הַאִם" in out
    assert "הָאֵם" not in out


def test_dict_options_unknown_pos_falls_back_to_top_1():
    """When DictaBERT POS doesn't match the lexicon, top-1 wins."""
    entries = [
        _entry("ספר", [
            _opt("סֵפֶר",  "סֵפֶר",  level=1),
            _opt("סָפַר",  "ספר_פעל", level=2),
        ]),
    ]
    tokens = [_token("ספר", pos="NOUN")]
    out = _project_with_context(entries, tokens, sentence="ספר")
    # NOUN's score for both is similar; top-1 (סֵפֶר) wins
    assert "סֵפֶר" in out


def test_dict_options_with_pos_none_falls_back_to_top_1():
    """When DictaBERT returns POS=None, no scoring lift, top-1 wins."""
    entries = [
        _entry("שלו", [
            _opt("שֶׁלּוֹ", "שֶׁל",   prefix_len=0, level=1),
            _opt("שָׁלֵו",  "שָׁלֵו", prefix_len=0, level=2),
        ]),
    ]
    tokens = [_token("שלו", pos=None)]
    out = _project_with_context(entries, tokens, sentence="שלו")
    assert "שֶׁלּוֹ" in out


# --- backwards compat: bare-string options still work for tests ---


def test_bare_string_options_still_resolve():
    """Existing tests using bare-string options must still work."""
    entries = [
        _entry("שלום", ["שָׁלוֹם"]),
    ]
    tokens = [_token("שלום", pos="NOUN")]
    out = _project_with_context(entries, tokens, sentence="שלום")
    assert out == "שָׁלוֹם"
