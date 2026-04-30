"""F18 T-01 — top-1 sense disambiguation (POC numbering).

Spec: N02/F18 DE-03. AC: US-01/AC-01. FT-anchors: FT-127.
BT-anchors: BT-083.
"""

from __future__ import annotations

import pytest

from tirvi.nlp.disambiguate import pick_sense
from tirvi.nlp.errors import DisambiguationError
from tirvi.results import NLPToken


class TestDisambiguate:
    def test_us_01_ac_01_picks_top_candidate(self) -> None:
        noun = NLPToken(text="ילד", pos="NOUN", lemma="ילד")
        verb = NLPToken(text="ילד", pos="VERB", lemma="ילד")
        chosen, _ = pick_sense([(noun, 0.7), (verb, 0.2)])
        assert chosen.pos == "NOUN"

    def test_us_01_ac_01_marks_ambiguous_when_margin_below_threshold(self) -> None:
        noun = NLPToken(text="ספר", pos="NOUN", lemma="ספר")
        verb = NLPToken(text="ספר", pos="VERB", lemma="ספר")
        _, ambiguous = pick_sense([(noun, 0.51), (verb, 0.49)])
        assert ambiguous is True

    def test_unambiguous_when_margin_meets_threshold(self) -> None:
        noun = NLPToken(text="בית", pos="NOUN", lemma="בית")
        adj = NLPToken(text="בית", pos="ADJ", lemma="ביתי")
        _, ambiguous = pick_sense([(noun, 0.95), (adj, 0.05)])
        assert ambiguous is False

    def test_us_01_ac_01_env_var_tunes_margin(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Default margin 0.2 → margin 0.15 is ambiguous; tuned to 0.05 → not ambiguous.
        a = NLPToken(text="x", pos="NOUN")
        b = NLPToken(text="x", pos="VERB")
        candidates = [(a, 0.60), (b, 0.45)]

        monkeypatch.delenv("TIRVI_DISAMBIG_MARGIN", raising=False)
        _, default_ambiguous = pick_sense(candidates)
        assert default_ambiguous is True

        monkeypatch.setenv("TIRVI_DISAMBIG_MARGIN", "0.05")
        _, tuned_ambiguous = pick_sense(candidates)
        assert tuned_ambiguous is False

    def test_empty_candidates_raises(self) -> None:
        with pytest.raises(DisambiguationError):
            pick_sense([])

    def test_single_candidate_is_unambiguous(self) -> None:
        only = NLPToken(text="only", pos="NOUN")
        chosen, ambiguous = pick_sense([(only, 0.9)])
        assert chosen is only
        assert ambiguous is False
