"""F26 T-06 — Integration test for F17 → F26 failover chain.

Spec: N02/F26 DE-06 (verifies F17 T-06 wiring). AC: US-01/AC-01.
FT-anchors: FT-131, FT-132.

Verifies that ``DictaBERTAdapter`` falls through to
``AlephBertYapFallbackAdapter`` on ImportError, and to the degraded
provider when F26 is also unavailable.
"""

from __future__ import annotations

from unittest.mock import patch


_FAKE_YAP_RESPONSE = {
    "lattice_md": {
        "0": [
            {
                "surface": "שלום",
                "lemma": "שלום",
                "CPOSTag": "NN",
                "FPOSTag": "NN",
                "feats": "Gender=Masc|Number=Sing",
            }
        ],
    }
}


def _patch_probe():
    """Stub the F26 health probe so __init__ does not hit the network."""
    return patch("tirvi.adapters.alephbert.adapter.urllib.request.urlopen")


def test_dictabert_fails_falls_through_to_f26() -> None:
    from tirvi.adapters.dictabert.adapter import DictaBERTAdapter

    adapter = DictaBERTAdapter()
    with patch(
        "tirvi.adapters.dictabert.inference.load_model",
        side_effect=ImportError("transformers not installed"),
    ), patch(
        "tirvi.adapters.alephbert.adapter.yap_joint_via_api",
        return_value=_FAKE_YAP_RESPONSE,
    ), _patch_probe():
        result = adapter.analyze("שלום", "he")

    assert result.provider == "alephbert+yap"
    assert len(result.tokens) == 1
    assert result.tokens[0].text == "שלום"


def test_full_chain_degrades_when_f26_unavailable() -> None:
    """When F26's import fails, the chain returns ``provider="degraded"``."""
    import importlib

    from tirvi.adapters.dictabert.adapter import DictaBERTAdapter

    real_import_module = importlib.import_module

    def fake_import_module(name, *args, **kwargs):
        if name == "tirvi.adapters.alephbert":
            raise ImportError("simulated F26 absence")
        return real_import_module(name, *args, **kwargs)

    adapter = DictaBERTAdapter()
    with patch(
        "tirvi.adapters.dictabert.inference.load_model",
        side_effect=ImportError("transformers not installed"),
    ), patch(
        "tirvi.adapters.dictabert.adapter.importlib.import_module",
        side_effect=fake_import_module,
    ):
        result = adapter.analyze("שלום", "he")

    assert result.provider == "degraded"
    assert result.tokens == []
