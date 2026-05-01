"""F18 T-00/T-01/T-03 — sense disambiguation: legacy + v2.

Spec: N02/F18 DE-03. AC: US-01/AC-01, AC-02, AC-03. FT-anchors: FT-127.
BT-anchors: BT-083.

``_legacy_pick_sense`` pins the Wave-1 ``tuple[NLPToken, bool]`` API.
``pick_sense(token, candidates)`` is the Wave-2 per-token API (T-03).
"""

from __future__ import annotations

import pytest

from tirvi.nlp.disambiguate import _legacy_pick_sense, pick_sense
from tirvi.nlp.errors import DisambiguationError
from tirvi.results import NLPToken


class TestLegacyDisambiguate:
    def test_us_01_ac_01_picks_top_candidate(self) -> None:
        noun = NLPToken(text="ילד", pos="NOUN", lemma="ילד")
        verb = NLPToken(text="ילד", pos="VERB", lemma="ילד")
        chosen, _ = _legacy_pick_sense([(noun, 0.7), (verb, 0.2)])
        assert chosen.pos == "NOUN"

    def test_us_01_ac_01_marks_ambiguous_when_margin_below_threshold(self) -> None:
        noun = NLPToken(text="ספר", pos="NOUN", lemma="ספר")
        verb = NLPToken(text="ספר", pos="VERB", lemma="ספר")
        _, ambiguous = _legacy_pick_sense([(noun, 0.51), (verb, 0.49)])
        assert ambiguous is True

    def test_unambiguous_when_margin_meets_threshold(self) -> None:
        noun = NLPToken(text="בית", pos="NOUN", lemma="בית")
        adj = NLPToken(text="בית", pos="ADJ", lemma="ביתי")
        _, ambiguous = _legacy_pick_sense([(noun, 0.95), (adj, 0.05)])
        assert ambiguous is False

    def test_us_01_ac_01_env_var_tunes_margin(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        a = NLPToken(text="x", pos="NOUN")
        b = NLPToken(text="x", pos="VERB")
        candidates = [(a, 0.60), (b, 0.45)]

        monkeypatch.delenv("TIRVI_DISAMBIG_MARGIN", raising=False)
        _, default_ambiguous = _legacy_pick_sense(candidates)
        assert default_ambiguous is True

        monkeypatch.setenv("TIRVI_DISAMBIG_MARGIN", "0.05")
        _, tuned_ambiguous = _legacy_pick_sense(candidates)
        assert tuned_ambiguous is False

    def test_empty_candidates_raises(self) -> None:
        with pytest.raises(DisambiguationError):
            _legacy_pick_sense([])

    def test_single_candidate_is_unambiguous(self) -> None:
        only = NLPToken(text="only", pos="NOUN")
        chosen, ambiguous = _legacy_pick_sense([(only, 0.9)])
        assert chosen is only
        assert ambiguous is False


class TestPickSenseV2:
    """T-03: Wave-2 pick_sense(token, candidates) → NLPToken."""

    def test_unambiguous_passthrough(self) -> None:
        token = NLPToken(text="ילד", pos="NOUN", ambiguous=False)
        result = pick_sense(token)
        assert result is token

    def test_ambiguous_no_override_no_candidates_passthrough(self) -> None:
        """S-2: ambiguous token with no override and no candidates → passthrough."""
        token = NLPToken(text="ספר", pos="NOUN", ambiguous=True)
        result = pick_sense(token, candidates=None)
        assert result is token

    def test_ambiguous_morph_features_none_does_not_crash(self) -> None:
        """A-2: (morph_features or {}).items() — must not raise AttributeError."""
        token = NLPToken(text="ילד", pos="NOUN", ambiguous=True, morph_features=None)
        result = pick_sense(token, candidates=None)
        assert result is token

    def test_ambiguous_override_hit_returns_overridden_token(self) -> None:
        noun = NLPToken(text="ספר", pos="NOUN", ambiguous=True, morph_features={"Number": "Sing"})
        override = NLPToken(text="ספר", pos="VERB", ambiguous=False, lemma="לספר")
        from tirvi.nlp import overrides as _ov
        key = ("ספר", frozenset({"Number": "Sing"}.items()))
        _ov.MORPH_HOMOGRAPH_OVERRIDES[key] = override
        try:
            result = pick_sense(noun)
            assert result is override
        finally:
            del _ov.MORPH_HOMOGRAPH_OVERRIDES[key]

    def test_ambiguous_override_miss_with_candidates_returns_top1(self) -> None:
        token = NLPToken(text="בית", pos="NOUN", ambiguous=True, morph_features=None)
        top = NLPToken(text="בית", pos="NOUN", lemma="בית")
        second = NLPToken(text="בית", pos="ADJ", lemma="ביתי")
        result = pick_sense(token, candidates=[(top, 0.8), (second, 0.1)])
        assert result is top

    def test_kol_homograph_override(self) -> None:
        """AC-02 GH#20 anchor: כל can be DET or NOUN — override table resolves."""
        det = NLPToken(text="כל", pos="DET", ambiguous=True, morph_features={"Definite": "Def"})
        result = pick_sense(det, candidates=None)
        assert isinstance(result, NLPToken)

    def test_ambiguous_participle_passthrough(self) -> None:
        """AC-03 GH#20 anchor: ambiguous participle with no override passes through."""
        token = NLPToken(text="כותב", pos="VERB", ambiguous=True,
                         morph_features={"VerbForm": "Part"})
        result = pick_sense(token, candidates=None)
        assert result is token
