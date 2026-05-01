"""F26 T-02 — YAP CoNLL response parser tests."""
from __future__ import annotations
import json
from pathlib import Path
from tirvi.adapters.alephbert.parser import parse_yap_response

_FIXTURE = Path(__file__).parent.parent / "fixtures" / "yap_lattice_sample.json"


def _load() -> dict:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


class TestYapResponseParser:
    def test_uses_dep_tree_when_present(self):
        tokens = parse_yap_response(_load())
        assert [t["surface"] for t in tokens] == ["שלום", "עולם", "הוא", "טוב", "מאוד"]

    def test_token_carries_lemma_and_pos(self):
        tokens = parse_yap_response(_load())
        first = tokens[0]
        assert first["lemma"] == "שלום"
        assert first["CPOSTag"] == "NN"
        assert first["FPOSTag"] == "NN"

    def test_feats_split_into_dict(self):
        tokens = parse_yap_response(_load())
        assert tokens[0]["feats"] == {"gen": "M", "num": "S"}
        assert tokens[1]["feats"] == {"gen": "M", "num": "S", "def": "D"}
        assert tokens[4]["feats"] == {}

    def test_dep_tree_carries_head_and_rel(self):
        tokens = parse_yap_response(_load())
        assert tokens[0]["dep_head"] == 0
        assert tokens[0]["dep_rel"] == "ROOT"
        assert tokens[1]["dep_rel"] == "dobj"

    def test_falls_back_to_md_lattice_when_no_dep_tree(self):
        response = {
            "md_lattice": "0\t1\tשלום\tשלום\tNN\tNN\tgen=M|num=S\t1\n",
            "dep_tree": "",
        }
        tokens = parse_yap_response(response)
        assert len(tokens) == 1
        assert tokens[0]["surface"] == "שלום"

    def test_empty_response_returns_empty_list(self):
        assert parse_yap_response({"ma_lattice": "", "md_lattice": "", "dep_tree": ""}) == []
