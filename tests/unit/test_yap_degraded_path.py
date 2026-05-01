"""F26 T-05 — Connection-failed degraded path tests.

Spec: N02/F26 DE-05. AC: US-01/AC-01. FT-anchors: FT-135. BT-anchors: BT-090.
"""

from __future__ import annotations

import json
import socket
from unittest.mock import patch
from urllib.error import URLError

import pytest


def _make_adapter():
    from tirvi.adapters.alephbert import AlephBertYapFallbackAdapter

    # Construct without triggering health probe network call.
    with patch("tirvi.adapters.alephbert.adapter.urllib.request.urlopen"):
        return AlephBertYapFallbackAdapter()


@pytest.mark.parametrize(
    "exc",
    [
        URLError("connection refused"),
        socket.timeout("timed out"),
        ConnectionRefusedError(),
        json.JSONDecodeError("bad", "doc", 0),
        KeyError("lattice_md"),
    ],
)
def test_each_exception_branch_returns_degraded(exc) -> None:
    adapter = _make_adapter()
    with patch(
        "tirvi.adapters.alephbert.adapter.yap_joint_via_api",
        side_effect=exc,
    ):
        result = adapter.analyze("שלום", "he")
    assert result.provider == "degraded"
    assert result.tokens == []
    assert result.confidence is None


def test_non_200_http_status_returns_degraded() -> None:
    """A non-200 HTTPError raised by urlopen flows through URLError handling."""
    from urllib.error import HTTPError

    adapter = _make_adapter()
    err = HTTPError("http://yap", 503, "Service Unavailable", {}, None)
    with patch(
        "tirvi.adapters.alephbert.adapter.yap_joint_via_api",
        side_effect=err,
    ):
        result = adapter.analyze("שלום", "he")
    assert result.provider == "degraded"


def test_empty_input_is_not_degraded() -> None:
    adapter = _make_adapter()
    with patch(
        "tirvi.adapters.alephbert.adapter.yap_joint_via_api",
        side_effect=URLError("should not be called"),
    ) as mock_call:
        result = adapter.analyze("", "he")
    assert mock_call.call_count == 0
    assert result.provider == "alephbert+yap"
    assert result.tokens == []
