"""F27 T-01 — HebPipe coref no-op stub (deferred MVP). FT-144."""

from tirvi.coref import COREF_ENABLED, CorefResult, enrich_with_coref


def test_us_01_ac_01_ft_144_disabled_returns_empty_chains() -> None:
    assert COREF_ENABLED is False
    result = enrich_with_coref(object())
    assert isinstance(result, CorefResult)
    assert result.chains == []
