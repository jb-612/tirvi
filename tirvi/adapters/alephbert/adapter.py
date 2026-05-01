"""F26 T-04/T-05/T-08 — AlephBertYapFallbackAdapter.

Spec: N02/F26 DE-04, DE-05, DE-07. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-131, FT-135.

Implements :class:`tirvi.ports.NLPBackend`. Provider stamp
``"alephbert+yap"`` on success; ``"degraded"`` on connection /
parse failure (per ADR-027). Empty input short-circuits to the
``alephbert+yap`` provider (matches F17's empty-input contract;
not "degraded").

Vendor boundary (ADR-029): stdlib HTTP only. No transformers/
AlephBERT imports for the POC.
"""

from __future__ import annotations

import json
import logging
import os
import socket
import urllib.request
from urllib.error import URLError

from tirvi.results import NLPResult

from .client import yap_joint_via_api
from .parser import parse_lattice
from .ud_mapper import yap_token_to_nlp

PROVIDER = "alephbert+yap"
DEGRADED_PROVIDER = "degraded"
_DEGRADED = NLPResult(provider=DEGRADED_PROVIDER, tokens=[], confidence=None)
_DEGRADED_EXC = (
    URLError,
    socket.timeout,
    ConnectionRefusedError,
    json.JSONDecodeError,
    KeyError,
)
_PROBE_TIMEOUT_S = 2.0
_DEFAULT_BASE_URL = "http://127.0.0.1:8000"

_log = logging.getLogger("tirvi.adapters.alephbert")


def _yap_base_url() -> str:
    return os.environ.get("TIRVI_YAP_URL", _DEFAULT_BASE_URL).rstrip("/")


class AlephBertYapFallbackAdapter:
    """Stdlib-only YAP-backed NLP adapter (per ADR-027 + ADR-029)."""

    def __init__(self) -> None:
        self._probed = False
        self._probe()

    def analyze(self, text: str, lang: str) -> NLPResult:  # noqa: ARG002
        if not text.strip():
            return NLPResult(provider=PROVIDER, tokens=[], confidence=None)
        try:
            response = yap_joint_via_api(text)
            tokens = [yap_token_to_nlp(t) for t in parse_lattice(response)]
        except _DEGRADED_EXC:
            return _DEGRADED
        return NLPResult(provider=PROVIDER, tokens=tokens, confidence=None)

    def _probe(self) -> None:
        if self._probed:
            return
        self._probed = True
        try:
            with urllib.request.urlopen(
                _yap_base_url() + "/", timeout=_PROBE_TIMEOUT_S
            ):
                return
        except (URLError, socket.timeout, ConnectionRefusedError, OSError):
            _log.warning(
                "YAP unreachable at %s — start with `yap api` to enable the "
                "F17 → F26 fallback (running in degraded mode otherwise).",
                _yap_base_url(),
            )
