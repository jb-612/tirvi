"""F26 T-02 — YAP response parser tests.

Spec: N02/F26 DE-02. AC: US-01/AC-01. FT-anchors: FT-133.
"""

from __future__ import annotations

import json
from pathlib import Path


_FIXTURE = Path(__file__).parent.parent / "fixtures" / "yap_lattice_sample.json"


def _load_fixture() -> dict:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


class TestYapResponseParser:
    def test_parses_lattice_md_into_token_list(self) -> None:
        from tirvi.adapters.alephbert.parser import parse_lattice

        tokens = parse_lattice(_load_fixture())
        assert [t["surface"] for t in tokens] == [
            "שלום",
            "עולם",
            "הוא",
            "טוב",
            "מאוד",
        ]

    def test_token_carries_lemma_and_pos_fields(self) -> None:
        from tirvi.adapters.alephbert.parser import parse_lattice

        tokens = parse_lattice(_load_fixture())
        first = tokens[0]
        assert first["lemma"] == "שלום"
        assert first["CPOSTag"] == "NN"
        assert first["FPOSTag"] == "NN"

    def test_feats_split_into_dict(self) -> None:
        from tirvi.adapters.alephbert.parser import parse_lattice

        tokens = parse_lattice(_load_fixture())
        assert tokens[0]["feats"] == {"Gender": "Masc", "Number": "Sing"}
        assert tokens[1]["feats"] == {
            "Gender": "Masc",
            "Number": "Sing",
            "Definite": "Def",
        }
        # Empty feats become an empty dict
        assert tokens[4]["feats"] == {}

    def test_collapses_multi_edge_tokens_by_surface(self) -> None:
        from tirvi.adapters.alephbert.parser import parse_lattice

        # Same word position with multiple edges (ambiguity) — keep first edge.
        response = {
            "lattice_md": {
                "0": [
                    {
                        "surface": "ספר",
                        "lemma": "ספר",
                        "CPOSTag": "NN",
                        "FPOSTag": "NN",
                        "feats": "Gender=Masc",
                    },
                    {
                        "surface": "ספר",
                        "lemma": "ספר",
                        "CPOSTag": "VB",
                        "FPOSTag": "VB",
                        "feats": "Tense=Past",
                    },
                ],
            }
        }
        tokens = parse_lattice(response)
        assert len(tokens) == 1
        assert tokens[0]["surface"] == "ספר"

    def test_ordered_by_numeric_position_keys(self) -> None:
        from tirvi.adapters.alephbert.parser import parse_lattice

        response = {
            "lattice_md": {
                "10": [{"surface": "b", "lemma": "b", "CPOSTag": "NN",
                        "FPOSTag": "NN", "feats": ""}],
                "2": [{"surface": "a", "lemma": "a", "CPOSTag": "NN",
                       "FPOSTag": "NN", "feats": ""}],
            }
        }
        tokens = parse_lattice(response)
        assert [t["surface"] for t in tokens] == ["a", "b"]
