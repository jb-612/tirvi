"""T-10 — Privacy invariant: no non-localhost outbound during cascade.

Spec: F48 DE-04. AC: F48-S03/AC-01.
ADR-033 (privacy hard rule). FT-AUD-03. BT-216. INV-CCS-004.

This is a HARD CI gate. Failure must freeze feature ship.
"""

from __future__ import annotations

import inspect
import socket
from pathlib import Path

import pytest

from tests.unit.conftest import FakeCascadeStage, FakeFeedbackReader
from tirvi.correction.service import CorrectionCascadeService
from tirvi.correction.value_objects import CascadeMode, CorrectionVerdict


def _passthrough_verdict() -> CorrectionVerdict:
    return CorrectionVerdict(stage="nakdan_gate", verdict="pass", original="")


def _make_cascade_service() -> CorrectionCascadeService:
    """Build a cascade wired entirely from in-process fakes (no network I/O)."""
    stage = FakeCascadeStage(canned=_passthrough_verdict())
    return CorrectionCascadeService(
        nakdan_gate=stage,
        mlm_scorer=stage,
        llm_reviewer=stage,
        feedback=FakeFeedbackReader(),
    )


_LOCALHOST_NAMES = frozenset({"localhost", "127.0.0.1", "::1"})


class TestOutboundDnsRestriction:
    """INV-CCS-004 — outbound DNS resolves only to 127.0.0.1 / ::1."""

    def test_socket_create_connection_only_to_localhost(self, monkeypatch: pytest.MonkeyPatch) -> None:
        violations: list[str] = []

        def recording_create_connection(address, *args, **kwargs):
            host, _port = address
            if host not in _LOCALHOST_NAMES:
                violations.append(host)
            raise OSError("Blocked by privacy invariant test")

        monkeypatch.setattr(socket, "create_connection", recording_create_connection)

        svc = _make_cascade_service()
        svc.run_page(["שלום", "עולם"], mode=CascadeMode(name="full"))

        assert violations == [], f"Non-localhost create_connection attempts: {violations}"

    def test_getaddrinfo_only_resolves_localhost(self, monkeypatch: pytest.MonkeyPatch) -> None:
        non_localhost_lookups: list[str] = []

        def recording_getaddrinfo(host, *args, **kwargs):
            if host not in _LOCALHOST_NAMES:
                non_localhost_lookups.append(host)
            return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 0))]

        monkeypatch.setattr(socket, "getaddrinfo", recording_getaddrinfo)

        svc = _make_cascade_service()
        svc.run_page(["שלום"], mode=CascadeMode(name="full"))

        assert non_localhost_lookups == [], f"Non-localhost DNS lookups: {non_localhost_lookups}"

    def test_external_url_blocked_during_cascade(self, monkeypatch: pytest.MonkeyPatch) -> None:
        violations: list[str] = []

        def blocking_create_connection(address, *args, **kwargs):
            host, _port = address
            if host not in _LOCALHOST_NAMES:
                violations.append(host)
                raise OSError(f"INV-CCS-004 privacy violation: outbound to {host!r}")
            raise OSError("Blocked by privacy invariant test (localhost path)")

        monkeypatch.setattr(socket, "create_connection", blocking_create_connection)

        svc = _make_cascade_service()
        svc.run_page(["שלום"], mode=CascadeMode(name="full"))

        assert violations == [], f"External connection attempts detected: {violations}"


class TestNoVendorLeakAcrossPorts:
    """ADR-029: vendor types do not appear in port signatures."""

    def test_llm_client_port_signature_uses_str_only(self) -> None:
        import typing
        from tirvi.correction.ports import LLMClientPort

        # get_type_hints evaluates forward-ref strings (from __future__ annotations)
        hints = typing.get_type_hints(LLMClientPort.generate)
        allowed_types = {str, float, int}
        for name, ann in hints.items():
            if name == "return":
                continue
            assert ann in allowed_types, (
                f"LLMClientPort.generate param {name!r} has non-primitive annotation {ann!r} "
                f"(ADR-029: no vendor types in port signatures)"
            )

    def test_no_httpx_import_outside_adapters(self) -> None:
        correction_root = Path("tirvi/correction")
        vendor_modules = ("httpx", "requests")

        for py_file in sorted(correction_root.rglob("*.py")):
            rel = py_file.parts
            if "adapters" in rel:
                continue
            source = py_file.read_text(encoding="utf-8")
            for vendor in vendor_modules:
                assert f"import {vendor}" not in source, (
                    f"{py_file} imports {vendor!r} — ADR-029 violation: "
                    f"vendor imports restricted to tirvi/correction/adapters/"
                )
