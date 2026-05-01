"""F26 T-01 — YAP HTTP client tests.

Spec: N02/F26 DE-01. AC: US-01/AC-01. FT-anchors: FT-131.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch


class TestYapClient:
    def _fake_response(self, body: bytes = b"{}"):
        fake = MagicMock()
        fake.read.return_value = body
        fake.status = 200
        fake.__enter__ = MagicMock(return_value=fake)
        fake.__exit__ = MagicMock(return_value=False)
        return fake

    def test_us_01_ac_01_posts_json_to_yap_endpoint(self) -> None:
        from tirvi.adapters.alephbert.client import yap_joint_via_api

        fake = self._fake_response()
        with patch(
            "tirvi.adapters.alephbert.client.urllib.request.urlopen",
            return_value=fake,
        ) as mock_urlopen:
            yap_joint_via_api("שלום")

        assert mock_urlopen.call_count == 1
        request = mock_urlopen.call_args[0][0]
        assert request.full_url.endswith("/yap/heb/joint")
        assert request.get_method() == "POST"
        assert request.get_header("Content-type") == "application/json"

    def test_us_01_ac_01_request_body_includes_input_text(self) -> None:
        from tirvi.adapters.alephbert.client import yap_joint_via_api

        fake = self._fake_response()
        with patch(
            "tirvi.adapters.alephbert.client.urllib.request.urlopen",
            return_value=fake,
        ) as mock_urlopen:
            yap_joint_via_api("הבחינה")

        body = json.loads(mock_urlopen.call_args[0][0].data.decode("utf-8"))
        assert body["Text"] == "הבחינה"

    def test_us_01_ac_01_returns_parsed_response_dict(self) -> None:
        from tirvi.adapters.alephbert.client import yap_joint_via_api

        canned = {"lattice_md": {"0": []}}
        fake = self._fake_response(json.dumps(canned).encode("utf-8"))
        with patch(
            "tirvi.adapters.alephbert.client.urllib.request.urlopen",
            return_value=fake,
        ):
            result = yap_joint_via_api("שלום")

        assert result == canned

    def test_request_uses_default_30s_timeout(self) -> None:
        from tirvi.adapters.alephbert.client import yap_joint_via_api

        fake = self._fake_response()
        with patch(
            "tirvi.adapters.alephbert.client.urllib.request.urlopen",
            return_value=fake,
        ) as mock_urlopen:
            yap_joint_via_api("שלום")

        assert mock_urlopen.call_args.kwargs.get("timeout") == 30.0

    def test_env_override_changes_base_url(self, monkeypatch) -> None:
        from tirvi.adapters.alephbert.client import yap_joint_via_api

        monkeypatch.setenv("TIRVI_YAP_URL", "http://yap.example:9000")

        fake = self._fake_response()
        with patch(
            "tirvi.adapters.alephbert.client.urllib.request.urlopen",
            return_value=fake,
        ) as mock_urlopen:
            yap_joint_via_api("שלום")

        request = mock_urlopen.call_args[0][0]
        assert request.full_url == "http://yap.example:9000/yap/heb/joint"
