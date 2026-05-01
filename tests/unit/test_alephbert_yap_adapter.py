"""F26 T-04 + T-07 — AlephBertYapFallbackAdapter tests.

Spec: N02/F26 DE-04, DE-06. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-131.
"""

from __future__ import annotations

from unittest.mock import patch

from tirvi.ports import NLPBackend
from tirvi.results import NLPResult, NLPToken


_FAKE_RESPONSE = {
    "ma_lattice": "0\t1\tשלום\tשלום\tNN\tNN\tgen=M|num=S\t1\n",
    "md_lattice": "0\t1\tשלום\tשלום\tNN\tNN\tgen=M|num=S\t1\n",
    "dep_tree":   "1\tשלום\tשלום\tNN\tNN\tgen=M|num=S\t0\tROOT\t_\t_\n",
}


class TestAlephBertYapAdapter:
    def test_provider_stamp_is_alephbert_plus_yap(self) -> None:
        from tirvi.adapters.alephbert import AlephBertYapFallbackAdapter

        with patch(
            "tirvi.adapters.alephbert.adapter.yap_joint_via_api",
            return_value=_FAKE_RESPONSE,
        ):
            result = AlephBertYapFallbackAdapter().analyze("שלום", "he")
        assert result.provider == "alephbert+yap"

    def test_returns_nlp_result_with_tokens(self) -> None:
        from tirvi.adapters.alephbert import AlephBertYapFallbackAdapter

        with patch(
            "tirvi.adapters.alephbert.adapter.yap_joint_via_api",
            return_value=_FAKE_RESPONSE,
        ):
            result = AlephBertYapFallbackAdapter().analyze("שלום", "he")
        assert isinstance(result, NLPResult)
        assert len(result.tokens) == 1
        assert isinstance(result.tokens[0], NLPToken)
        assert result.tokens[0].text == "שלום"
        assert result.tokens[0].pos == "NOUN"

    def test_empty_input_short_circuits_not_degraded(self) -> None:
        from tirvi.adapters.alephbert import AlephBertYapFallbackAdapter

        with patch(
            "tirvi.adapters.alephbert.adapter.yap_joint_via_api"
        ) as mock_call:
            result = AlephBertYapFallbackAdapter().analyze("", "he")
        assert mock_call.call_count == 0
        assert result.provider == "alephbert+yap"
        assert result.tokens == []
        assert result.confidence is None

    def test_whitespace_only_input_short_circuits(self) -> None:
        from tirvi.adapters.alephbert import AlephBertYapFallbackAdapter

        with patch(
            "tirvi.adapters.alephbert.adapter.yap_joint_via_api"
        ) as mock_call:
            result = AlephBertYapFallbackAdapter().analyze("   \t\n", "he")
        assert mock_call.call_count == 0
        assert result.provider == "alephbert+yap"
        assert result.tokens == []

    def test_implements_nlp_backend_protocol(self) -> None:
        from tirvi.adapters.alephbert import AlephBertYapFallbackAdapter

        with patch("tirvi.adapters.alephbert.adapter.yap_joint_via_api"):
            adapter = AlephBertYapFallbackAdapter()
        assert isinstance(adapter, NLPBackend)

    def test_lang_arg_accepted_but_ignored(self) -> None:
        from tirvi.adapters.alephbert import AlephBertYapFallbackAdapter

        with patch(
            "tirvi.adapters.alephbert.adapter.yap_joint_via_api",
            return_value=_FAKE_RESPONSE,
        ):
            result = AlephBertYapFallbackAdapter().analyze("שלום", "en")
        assert result.provider == "alephbert+yap"
