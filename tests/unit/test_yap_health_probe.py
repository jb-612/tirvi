"""F26 T-08 — YAP availability health probe tests.

Spec: N02/F26 DE-07. AC: US-01/AC-01.
"""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch


def _ok_response():
    fake = MagicMock()
    fake.status = 200
    fake.read.return_value = b""
    fake.__enter__ = MagicMock(return_value=fake)
    fake.__exit__ = MagicMock(return_value=False)
    return fake


def test_health_probe_warns_on_connection_refused(caplog) -> None:
    from tirvi.adapters.alephbert import AlephBertYapFallbackAdapter

    with patch(
        "tirvi.adapters.alephbert.adapter.urllib.request.urlopen",
        side_effect=ConnectionRefusedError(),
    ):
        with caplog.at_level(logging.WARNING, logger="tirvi.adapters.alephbert"):
            AlephBertYapFallbackAdapter()

    warning_msgs = [r.message for r in caplog.records if r.levelno == logging.WARNING]
    assert any("start with `yap api`" in msg for msg in warning_msgs), warning_msgs


def test_health_probe_silent_when_yap_reachable(caplog) -> None:
    from tirvi.adapters.alephbert import AlephBertYapFallbackAdapter

    with patch(
        "tirvi.adapters.alephbert.adapter.urllib.request.urlopen",
        return_value=_ok_response(),
    ):
        with caplog.at_level(logging.WARNING, logger="tirvi.adapters.alephbert"):
            AlephBertYapFallbackAdapter()

    warns = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert warns == []


def test_health_probe_runs_once_per_instance(caplog) -> None:
    """A second `analyze` does not re-issue the probe."""
    from tirvi.adapters.alephbert import AlephBertYapFallbackAdapter

    with patch(
        "tirvi.adapters.alephbert.adapter.urllib.request.urlopen",
        side_effect=ConnectionRefusedError(),
    ) as mock_probe:
        adapter = AlephBertYapFallbackAdapter()
        # urlopen called exactly once during __init__ for the probe.
        assert mock_probe.call_count == 1

        with patch(
            "tirvi.adapters.alephbert.adapter.yap_joint_via_api",
            return_value={"lattice_md": {}},
        ):
            adapter.analyze("שלום", "he")
            adapter.analyze("עולם", "he")

        assert mock_probe.call_count == 1
