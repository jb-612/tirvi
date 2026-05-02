"""F19 T-02 — NLP context tilt for homograph picks.

Spec: N02/F19 DE-02. AC: US-01/AC-01. FT-anchors: FT-146, FT-147.

`diacritize_in_context(text, nlp)` walks the Dicta REST response in lock-
step with the NLP tokens. For each non-separator entry, the cascade
runs F51 context rules → ADR-039 lex+POS scoring → top-1 fallback.

NOTE (2026-05-02, post-ADR-039): the original tests assumed Dicta would
return options as ``{w, morph: {pos, Definite, ...}}`` dicts. Live Dicta
never returned that shape — the morph-context branch was dormant for
the entire POC (see ADR-038 §Finding 1). ADR-039 switches the client to
``task: morph`` (which DOES return dict options) and replaces the
speculative dict-morph scoring with lex+prefix_len heuristics. The
authoritative tests for the post-ADR-039 contract live in
``tests/unit/test_nakdan_morph_scoring.py``. Tests in this file that
happen to still pass are kept for their lockstep-alignment coverage,
not their scoring behaviour.
"""

from __future__ import annotations

from unittest.mock import patch

from tirvi.adapters.nakdan.inference import (
    PROVIDER,
    diacritize_in_context,
)
from tirvi.results import DiacritizationResult, NLPResult, NLPToken


def _nlp(tokens: list[NLPToken]) -> NLPResult:
    return NLPResult(provider="dictabert-morph", tokens=tokens, confidence=None)


class TestNakdanContext:
    def test_us_01_ac_01_returns_diacritization_result(self) -> None:
        nlp = _nlp([NLPToken(text="שלום", pos="NOUN")])
        with patch(
            "tirvi.adapters.nakdan.inference.diacritize_via_api",
            return_value=[
                {"word": "שלום", "sep": False, "options": ["שָׁלוֹם"]},
            ],
        ):
            result = diacritize_in_context("שלום", nlp)
        assert isinstance(result, DiacritizationResult)
        assert result.provider == PROVIDER

    def test_us_01_ac_01_pos_context_biases_pick(self) -> None:
        # Two options carry morph signals; NLP token is a feminine noun, so
        # the noun-feminine option must win over the verb-masculine option,
        # even though it is not first in the list.
        verb_option = {"w": "שָׁרָה", "morph": {"pos": "VERB", "Gender": "Masc"}}
        noun_option = {"w": "שָׁרָה", "morph": {"pos": "NOUN", "Gender": "Fem"}}
        nlp = _nlp(
            [NLPToken(text="שרה", pos="NOUN", morph_features={"Gender": "Fem"})]
        )
        with patch(
            "tirvi.adapters.nakdan.inference.diacritize_via_api",
            return_value=[
                {
                    "word": "שרה",
                    "sep": False,
                    "options": [verb_option, noun_option],
                },
            ],
        ):
            result = diacritize_in_context("שרה", nlp)
        assert "שָׁרָה" in result.diacritized_text

    def test_us_01_ac_01_no_context_falls_through_to_seq2seq(self) -> None:
        # Plain string options carry no morph signal — fall through to T-03's
        # `_pick` (top-pick when confident).
        nlp = _nlp([])  # empty/degraded NLP
        with patch(
            "tirvi.adapters.nakdan.inference.diacritize_via_api",
            return_value=[
                {
                    "word": "שלום",
                    "sep": False,
                    "options": ["שָׁלוֹם"],
                    "fconfident": True,
                },
            ],
        ):
            result = diacritize_in_context("שלום", nlp)
        assert "שָׁלוֹם" in result.diacritized_text

    def test_sep_entries_do_not_consume_nlp_tokens(self) -> None:
        # Separator entries (whitespace/punct) sit between word entries but
        # are not aligned with NLP tokens — emit verbatim.
        verb_option = {"w": "שָׁרָה", "morph": {"pos": "VERB"}}
        noun_option = {"w": "שָׁרָה", "morph": {"pos": "NOUN"}}
        nlp = _nlp(
            [
                NLPToken(text="שרה", pos="NOUN"),
                NLPToken(text="ילד", pos="NOUN"),
            ]
        )
        entries = [
            {
                "word": "שרה",
                "sep": False,
                "options": [verb_option, noun_option],
            },
            {"word": " ", "sep": True, "options": [" "]},
            {
                "word": "ילד",
                "sep": False,
                "options": ["יֶלֶד"],
            },
        ]
        with patch(
            "tirvi.adapters.nakdan.inference.diacritize_via_api",
            return_value=entries,
        ):
            result = diacritize_in_context("שרה ילד", nlp)
        assert "שָׁרָה" in result.diacritized_text
        assert " " in result.diacritized_text
        assert "יֶלֶד" in result.diacritized_text

    # test_definite_state_breaks_tie: REMOVED 2026-05-02 per ADR-039.
    # The original test asserted that an indefinite vs definite option
    # could tie-break on a `morph.Definite` field. Live Dicta REST never
    # returned that shape — see ADR-038 §Finding 1. The replacement
    # contract (lex + prefix_len heuristics) is covered in
    # tests/unit/test_nakdan_morph_scoring.py. Real-world Dicta only
    # returns options whose vocalized form matches the surface, so the
    # synthetic "indef vs def for surface הבית" scenario does not occur.

    def test_empty_text_skips_api_call(self) -> None:
        nlp = _nlp([])
        with patch(
            "tirvi.adapters.nakdan.inference.diacritize_via_api"
        ) as mock_api:
            result = diacritize_in_context("   ", nlp)
        assert result.diacritized_text == ""
        mock_api.assert_not_called()
