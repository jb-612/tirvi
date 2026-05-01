"""F21 T-03 — HOMOGRAPH_OVERRIDES singleton + F19 wiring.

Spec: N02/F21 DE-03. AC: US-01/AC-01. FT: FT-158. BT: BT-107.
"""


def test_singleton_loads_default_lexicon():
    from tirvi.homograph import HOMOGRAPH_OVERRIDES

    assert isinstance(HOMOGRAPH_OVERRIDES, dict)
    # POC seed (data/homograph-lexicon.yaml) maps כל → כֹּל.
    assert HOMOGRAPH_OVERRIDES["כל"] == "כֹּל"
    # POS-filtered seed entry (ספר) is skipped by the POC loader.
    assert "ספר" not in HOMOGRAPH_OVERRIDES


def test_nakdan_overrides_reexports_homograph_singleton():
    from tirvi.adapters.nakdan.overrides import HOMOGRAPH_OVERRIDES as nakdan_map
    from tirvi.homograph import HOMOGRAPH_OVERRIDES as homograph_map

    assert nakdan_map is homograph_map


def test_diacritize_in_context_uses_homograph_override(monkeypatch):
    """BT-107: F19 picks the F21 override over Nakdan's default."""
    from tirvi.adapters.nakdan import client, inference
    from tirvi.results import NLPResult

    fake_response = [
        {"word": "כל", "options": ["כָּל"], "fconfident": True},
    ]
    monkeypatch.setattr(client, "diacritize_via_api", lambda _t: fake_response)
    monkeypatch.setattr(inference, "diacritize_via_api", lambda _t: fake_response)

    result = inference.diacritize_in_context(
        "כל", NLPResult(provider="test", tokens=[])
    )
    assert "כֹּל" in result.diacritized_text
