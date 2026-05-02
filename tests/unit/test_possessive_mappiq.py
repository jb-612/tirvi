"""Tests for the possessive-mappiq rule.

Covers the homograph case where Nakdan ranks the non-mappiq form above
the mappiq form (e.g. `לְיַלְדָּה` "to-a-girl" vs `לְיַלְדָּהּ` "to-her-child")
even though the surrounding sentence has a possessor pattern that makes
the mappiq reading correct.

Spec: research probe driven by UAT-2026-05-02 §S6 finding.
Note: this rule lives under tirvi/homograph/ and is consumed by
scripts/homograph_judges_bench_v2.py — not yet wired into the production
inference path.
"""
from __future__ import annotations

from tirvi.homograph.possessive_mappiq import apply_rule


def test_fires_on_kol_em_pattern_picks_mappiq_option():
    sentence = "כל אם רוצה את הטוב ביותר לילדה"
    options = [
        "לַ|יַּלְדָּה",
        "לְ|יַלְדָּה",
        "לְ|יַלְדָּהּ",  # mappiq variant — gold
        "לְיַלְּדָהּ",
    ]
    assert apply_rule(sentence, "לילדה", options) == 3


def test_fires_on_kol_av_pattern():
    sentence = "כל אב יקרא לבתו"
    options = [
        "לְ|בִתּוֹ",        # no mappiq on ה (waw-suffix instead)
        "לְ|בִתָּהּ",        # mappiq variant
    ]
    assert apply_rule(sentence, "לבתו", options) == 2


def test_no_fire_when_no_possessor_trigger():
    sentence = "המשחק הזה מתאים לכל ילד או ילדה"
    options = ["יַלְדָּה", "יַלְדָּהּ"]
    assert apply_rule(sentence, "ילדה", options) is None


def test_no_fire_when_no_mappiq_in_options():
    sentence = "כל אם רוצה את הטוב ביותר לילדה"
    options = ["לַ|יַּלְדָּה", "לְ|יַלְדָּה"]
    assert apply_rule(sentence, "לילדה", options) is None


def test_handles_pipe_prefix_when_picking_mappiq():
    sentence = "כל אם רוצה לילדה"
    options = ["לְ|יַלְדָּהּ"]
    assert apply_rule(sentence, "לילדה", options) == 1


def test_returns_first_mappiq_option_when_multiple():
    sentence = "כל אם רוצה לילדה"
    options = [
        "לַ|יַּלְדָּה",
        "לְ|יַלְדָּהּ",   # first mappiq — should be picked
        "לְ|יֹלְדָהּ",     # second mappiq
    ]
    assert apply_rule(sentence, "לילדה", options) == 2


def test_empty_options_returns_none():
    sentence = "כל אם רוצה לילדה"
    assert apply_rule(sentence, "לילדה", []) is None


def test_does_not_fire_on_unrelated_kol():
    sentence = "אני אוהב לרוץ בכל בוקר עם הילדה"
    options = ["יַלְדָּה", "יַלְדָּהּ"]
    assert apply_rule(sentence, "הילדה", options) is None
