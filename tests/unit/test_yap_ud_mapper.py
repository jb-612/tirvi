"""F26 T-03 — UD-Hebrew schema mapper tests.

Spec: N02/F26 DE-03. AC: US-02/AC-01. FT-anchors: FT-133, FT-134.
"""

from __future__ import annotations

from tirvi.results import NLPToken


class TestYapUdMapper:
    def test_cpos_maps_to_ud_pos(self) -> None:
        from tirvi.adapters.alephbert.ud_mapper import yap_token_to_nlp

        cases = {
            "VB": "VERB",
            "NN": "NOUN",
            "JJ": "ADJ",
            "RB": "ADV",
            "IN": "ADP",
            "DT": "DET",
            "CC": "CCONJ",
            "PRP": "PRON",
        }
        for cpos, ud in cases.items():
            token = yap_token_to_nlp(
                {"surface": "x", "lemma": "x", "CPOSTag": cpos, "FPOSTag": cpos, "feats": {}}
            )
            assert token.pos == ud, f"{cpos} should map to {ud}"

    def test_unknown_cpos_falls_through_to_x(self) -> None:
        from tirvi.adapters.alephbert.ud_mapper import yap_token_to_nlp

        token = yap_token_to_nlp(
            {"surface": "x", "lemma": "x", "CPOSTag": "ZZZ", "FPOSTag": "ZZZ", "feats": {}}
        )
        assert token.pos == "X"

    def test_morph_features_filled_from_yap_feats(self) -> None:
        from tirvi.adapters.alephbert.ud_mapper import yap_token_to_nlp

        token = yap_token_to_nlp(
            {
                "surface": "עולם",
                "lemma": "עולם",
                "CPOSTag": "NN",
                "FPOSTag": "NN",
                "feats": {"gen": "M", "num": "S", "def": "D"},
            }
        )
        assert isinstance(token, NLPToken)
        assert token.morph_features == {
            "Gender": "Masc",
            "Number": "Sing",
            "Definite": "Def",
        }

    def test_empty_feats_yields_none_morph_features(self) -> None:
        from tirvi.adapters.alephbert.ud_mapper import yap_token_to_nlp

        token = yap_token_to_nlp(
            {"surface": "מאוד", "lemma": "מאוד", "CPOSTag": "RB", "FPOSTag": "RB", "feats": {}}
        )
        assert token.morph_features is None

    def test_non_whitelisted_keys_dropped(self) -> None:
        from tirvi.adapters.alephbert.ud_mapper import yap_token_to_nlp

        token = yap_token_to_nlp(
            {
                "surface": "x",
                "lemma": "x",
                "CPOSTag": "NN",
                "FPOSTag": "NN",
                "feats": {"gen": "M", "ExoticKey": "Bogus"},
            }
        )
        assert token.morph_features == {"Gender": "Masc"}
