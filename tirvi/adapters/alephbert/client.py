"""F26 T-01 — YAP HTTP client.

Spec: N02/F26 DE-01. AC: US-01/AC-01. FT-anchors: FT-131. BT-anchors: BT-087.

Stdlib-only HTTP per ADR-029 vendor boundary. POST JSON to YAP's
``/api/v0/joint`` endpoint. Base URL configurable via ``TIRVI_YAP_URL``.
"""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any

_DEFAULT_BASE_URL = "http://127.0.0.1:8000"
_JOINT_PATH = "/api/v0/joint"
_DEFAULT_TIMEOUT_S = 30.0


def _base_url() -> str:
    return os.environ.get("TIRVI_YAP_URL", _DEFAULT_BASE_URL).rstrip("/")


def yap_joint_via_api(text: str, timeout: float = _DEFAULT_TIMEOUT_S) -> dict[str, Any]:
    """POST ``text`` to YAP's joint morpho-syntactic endpoint."""
    payload = json.dumps({"text": text}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        _base_url() + _JOINT_PATH,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))
