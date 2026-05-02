"""F19 T-01 (per ADR-025) — Dicta REST client.

Spec: N02/F19 DE-01 (revised), ADR-025. AC: US-01/AC-01.

Replaces the in-process loader path with a thin HTTP client against
``https://nakdan-2-0.loadbalancer.dicta.org.il/api``. Vendor boundary:
HTTP I/O lives only inside ``tirvi.adapters.nakdan.client`` (DE-06,
ADR-014).
"""

from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import MagicMock, patch


class TestDictaClient:
    def test_us_01_ac_01_posts_json_to_dicta_endpoint(self) -> None:
        from tirvi.adapters.nakdan.client import diacritize_via_api

        fake_response = MagicMock()
        fake_response.read.return_value = b"[]"
        fake_response.__enter__ = MagicMock(return_value=fake_response)
        fake_response.__exit__ = MagicMock(return_value=False)

        with patch(
            "tirvi.adapters.nakdan.client.urllib.request.urlopen",
            return_value=fake_response,
        ) as mock_urlopen:
            diacritize_via_api("שלום")

        assert mock_urlopen.call_count == 1
        request = mock_urlopen.call_args[0][0]
        assert request.full_url.endswith("/api")
        assert "dicta.org.il" in request.full_url
        assert request.get_method() == "POST"

    def test_us_01_ac_01_request_body_includes_input_text(self) -> None:
        from tirvi.adapters.nakdan.client import diacritize_via_api

        fake_response = MagicMock()
        fake_response.read.return_value = b"[]"
        fake_response.__enter__ = MagicMock(return_value=fake_response)
        fake_response.__exit__ = MagicMock(return_value=False)

        with patch(
            "tirvi.adapters.nakdan.client.urllib.request.urlopen",
            return_value=fake_response,
        ) as mock_urlopen:
            diacritize_via_api("הבחינה")

        body = json.loads(mock_urlopen.call_args[0][0].data.decode("utf-8"))
        assert body["task"] == "morph"  # ADR-039: morph variant for richer options
        assert body["data"] == "הבחינה"
        assert body["genre"] == "modern"

    def test_us_01_ac_01_returns_parsed_response_list(self) -> None:
        from tirvi.adapters.nakdan.client import diacritize_via_api

        canned = [
            {"word": "הבחינה", "sep": False, "options": ["הַ|בְּחִינָה"]},
            {"word": " ", "sep": True, "options": [" "]},
        ]
        fake_response = MagicMock()
        fake_response.read.return_value = json.dumps(canned).encode("utf-8")
        fake_response.__enter__ = MagicMock(return_value=fake_response)
        fake_response.__exit__ = MagicMock(return_value=False)

        with patch(
            "tirvi.adapters.nakdan.client.urllib.request.urlopen",
            return_value=fake_response,
        ):
            result = diacritize_via_api("הבחינה")

        assert result == canned

    def test_request_uses_configurable_timeout(self) -> None:
        from tirvi.adapters.nakdan.client import diacritize_via_api

        fake_response = MagicMock()
        fake_response.read.return_value = b"[]"
        fake_response.__enter__ = MagicMock(return_value=fake_response)
        fake_response.__exit__ = MagicMock(return_value=False)

        with patch(
            "tirvi.adapters.nakdan.client.urllib.request.urlopen",
            return_value=fake_response,
        ) as mock_urlopen:
            diacritize_via_api("שלום", timeout=12.5)

        assert mock_urlopen.call_args.kwargs.get("timeout") == 12.5
