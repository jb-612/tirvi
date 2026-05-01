"""T-10 — Privacy invariant: no non-localhost outbound during cascade.

Spec: F48 DE-04. AC: F48-S03/AC-01.
ADR-033 (privacy hard rule). FT-AUD-03. BT-216. INV-CCS-004.

This is a HARD CI gate (per the F48 design.md). Failure must freeze
feature ship.

Scaffold — TDD T-10 fills bodies.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="scaffold — /tdd fills")


class TestOutboundDnsRestriction:
    """INV-CCS-004 — outbound DNS resolves only to 127.0.0.1 / ::1."""

    def test_socket_create_connection_only_to_localhost(self, monkeypatch):
        # Given: monkeypatched socket.create_connection recorder
        # When:  full cascade run is executed
        # Then:  every recorded host resolves to 127.0.0.1 or ::1
        pass

    def test_getaddrinfo_only_resolves_localhost(self, monkeypatch):
        # AUD-03 — DNS lookup audit
        pass

    def test_external_url_blocked_during_cascade(self, monkeypatch):
        # BT-216 — privacy invariant freeze test
        pass


class TestNoVendorLeakAcrossPorts:
    """ADR-029: vendor types do not appear in port signatures."""

    def test_llm_client_port_signature_uses_str_only(self):
        pass

    def test_no_httpx_import_outside_adapters(self):
        # Audit: tirvi/correction/{ports,value_objects,domain/**}.py
        # must not import httpx / requests.
        pass
