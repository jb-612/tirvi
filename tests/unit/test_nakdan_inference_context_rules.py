"""F51 T-02 — context-rules layer wired into _project_with_context.

Tests the integration of `tirvi.homograph.possessive_mappiq.apply_rule`
into `tirvi.adapters.nakdan.inference._project_with_context` via the
new `_apply_context_rules` helper.

Spec: N02/F51 DE-02. AC: F51-S01/AC-01, F51-S01/AC-02. ADR-038.
"""
from __future__ import annotations

from tirvi.adapters.nakdan.inference import _project_with_context
from tirvi.results import NLPToken


def _entry(word: str, options: list[str], sep: bool = False) -> dict:
    """Build a Dicta-shaped entry for the unit tests."""
    return {"word": word, "sep": sep, "options": options, "fpasuk": False, "fconfident": False}


def _token(text: str, pos: str | None = "NOUN") -> NLPToken:
    return NLPToken(text=text, pos=pos, lemma=text)


def test_rule_fires_picks_mappiq_for_kol_em_sentence():
    sentence = "כל אם רוצה את הטוב ביותר לילדה"
    entries = [
        _entry("כל",      ["כֹּל"]),
        _entry(" ",       [], sep=True),
        _entry("אם",      ["אֵם"]),
        _entry(" ",       [], sep=True),
        _entry("רוצה",    ["רוֹצָה"]),
        _entry(" ",       [], sep=True),
        _entry("את",      ["אֶת"]),
        _entry(" ",       [], sep=True),
        _entry("הטוב",    ["הַטּוֹב"]),
        _entry(" ",       [], sep=True),
        _entry("ביותר",   ["בְּיוֹתֵר"]),
        _entry(" ",       [], sep=True),
        _entry("לילדה",   ["לַ|יַּלְדָּה", "לְ|יַלְדָּה", "לְ|יַלְדָּהּ"]),
    ]
    tokens = [_token(e["word"]) for e in entries if not e["sep"]]
    out = _project_with_context(entries, tokens, sentence=sentence)
    assert "לְיַלְדָּהּ" in out
    assert "לַיַּלְדָּה" not in out


def test_rule_does_not_fire_on_no_possessor_sentence():
    sentence = "המשחק הזה מתאים לכל ילד או ילדה"
    entries = [
        _entry("המשחק",   ["הַמִּשְׂחָק"]),
        _entry(" ",       [], sep=True),
        _entry("הזה",     ["הַזֶּה"]),
        _entry(" ",       [], sep=True),
        _entry("מתאים",   ["מַתְאִים"]),
        _entry(" ",       [], sep=True),
        _entry("לכל",     ["לְכָל"]),
        _entry(" ",       [], sep=True),
        _entry("ילד",     ["יֶלֶד"]),
        _entry(" ",       [], sep=True),
        _entry("או",      ["אוֹ"]),
        _entry(" ",       [], sep=True),
        _entry("ילדה",    ["יַלְדָּה", "יַלְדָּהּ"]),
    ]
    tokens = [_token(e["word"]) for e in entries if not e["sep"]]
    out = _project_with_context(entries, tokens, sentence=sentence)
    # rule must NOT fire — top-1 (non-mappiq) wins
    assert out.endswith("יַלְדָּה")
    assert not out.endswith("יַלְדָּהּ")


def test_rule_falls_through_when_no_mappiq_in_options():
    sentence = "כל אם רוצה לילדה"
    # No mappiq variant in the candidate list
    entries = [
        _entry("כל",     ["כֹּל"]),
        _entry(" ",      [], sep=True),
        _entry("אם",     ["אֵם"]),
        _entry(" ",      [], sep=True),
        _entry("רוצה",   ["רוֹצָה"]),
        _entry(" ",      [], sep=True),
        _entry("לילדה",  ["לַ|יַּלְדָּה", "לְ|יַלְדָּה"]),
    ]
    tokens = [_token(e["word"]) for e in entries if not e["sep"]]
    out = _project_with_context(entries, tokens, sentence=sentence)
    # No mappiq option — falls through to top-1
    assert out.endswith("לַיַּלְדָּה")


def test_no_sentence_kwarg_means_no_rule_eval_backwards_compat():
    """When called without `sentence`, the rule layer is silently skipped.

    Preserves the existing test surface for callers that don't yet
    thread the sentence through.
    """
    entries = [
        _entry("כל",     ["כֹּל"]),
        _entry(" ",      [], sep=True),
        _entry("אם",     ["אֵם"]),
        _entry(" ",      [], sep=True),
        _entry("לילדה",  ["לַ|יַּלְדָּה", "לְ|יַלְדָּהּ"]),
    ]
    tokens = [_token(e["word"]) for e in entries if not e["sep"]]
    out = _project_with_context(entries, tokens)  # no sentence kwarg
    # Rule cannot fire without sentence → top-1 wins
    assert out.endswith("לַיַּלְדָּה")
