"""Unit tests for run_demo.py review and feedback endpoints (N04/F33 T-05).

Tests cover the extracted helper functions:
  - _serve_review(handler)    — GET /review serves player/index.html
  - _handle_feedback_post(handler, output_base)  — POST /feedback validates + writes

Design element: DE-06
Acceptance criteria: US-02/AC-09
FT-anchors: FT-317, FT-318
"""

from __future__ import annotations

import io
import json
import re
import unittest.mock as mock
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers to build a minimal fake handler object
# ---------------------------------------------------------------------------


def _make_handler(
    *,
    path: str = "/review",
    body: bytes = b"",
    headers: dict[str, str] | None = None,
    player_dir: Path | None = None,
) -> mock.MagicMock:
    """Return a MagicMock that quacks like BaseHTTPRequestHandler."""
    handler = mock.MagicMock()
    handler.path = path
    handler.rfile = io.BytesIO(body)
    hdr = headers or {}
    hdr.setdefault("Content-Length", str(len(body)))
    handler.headers = hdr
    # wfile accumulates response bytes
    handler.wfile = io.BytesIO()
    # Record calls to send_response/send_header/end_headers
    handler.send_response = mock.Mock()
    handler.send_header = mock.Mock()
    handler.end_headers = mock.Mock()
    handler.send_error = mock.Mock()
    # Attach player_dir attribute so helpers can find index.html
    handler._player_dir = player_dir
    return handler


# ---------------------------------------------------------------------------
# Import the helpers under test
# ---------------------------------------------------------------------------
# We import lazily to avoid triggering run_demo.py's module-level sys.path
# manipulation or pipeline imports prematurely.


def _import_helpers():
    """Import _serve_review and _handle_feedback_post from scripts.run_demo."""
    import importlib, sys

    # run_demo.py does sys.path.insert(0, …) which may fail in test env;
    # we patch the tirvi import so we can import the module.
    with mock.patch.dict(
        sys.modules,
        {
            "tirvi": mock.MagicMock(),
            "tirvi.pipeline": mock.MagicMock(),
        },
    ):
        # Force reimport in case a prior test already patched it differently.
        mod_name = "scripts.run_demo"
        if mod_name in sys.modules:
            del sys.modules[mod_name]
        import scripts.run_demo as mod  # noqa: PLC0415
    return mod._serve_review, mod._handle_feedback_post


@pytest.fixture(scope="module")
def helpers():
    return _import_helpers()


@pytest.fixture()
def serve_review(helpers):
    return helpers[0]


@pytest.fixture()
def handle_feedback_post(helpers):
    return helpers[1]


# ---------------------------------------------------------------------------
# TestReviewEndpoints
# ---------------------------------------------------------------------------


class TestReviewEndpoints:
    """Tests for GET /review and POST /feedback extracted helpers."""

    # ------------------------------------------------------------------
    # GET /review
    # ------------------------------------------------------------------

    def test_get_review_serves_index_html(self, serve_review, tmp_path):
        """GET /review → status 200 and Content-Type text/html."""
        html = b"<html>hello</html>"
        (tmp_path / "index.html").write_bytes(html)
        handler = _make_handler(path="/review", player_dir=tmp_path)

        serve_review(handler)

        handler.send_response.assert_called_once_with(200)
        ct_calls = [
            call_args
            for call_args in handler.send_header.call_args_list
            if call_args.args[0] == "Content-Type"
        ]
        assert ct_calls, "Content-Type header must be set"
        assert "text/html" in ct_calls[0].args[1]

    def test_get_review_with_query_string(self, serve_review, tmp_path):
        """GET /review?run=001 → status 200 (query string ignored)."""
        (tmp_path / "index.html").write_bytes(b"<html/>")
        handler = _make_handler(path="/review?run=001", player_dir=tmp_path)

        serve_review(handler)

        handler.send_response.assert_called_once_with(200)

    # ------------------------------------------------------------------
    # POST /feedback — success cases
    # ------------------------------------------------------------------

    def test_post_feedback_returns_201(self, handle_feedback_post, tmp_path):
        """Valid POST /feedback body → 201 response."""
        body = json.dumps({"run": "001", "markId": "w-0-1", "note": "wrong"}).encode()
        handler = _make_handler(path="/feedback", body=body)

        handle_feedback_post(handler, tmp_path)

        handler.send_response.assert_called_once_with(201)

    def test_post_feedback_writes_file(self, handle_feedback_post, tmp_path):
        """After valid POST, a JSON file exists in output/<run>/feedback/."""
        run = "001"
        mark_id = "w-0-1"
        body = json.dumps({"run": run, "markId": mark_id}).encode()
        handler = _make_handler(path="/feedback", body=body)

        handle_feedback_post(handler, tmp_path)

        feedback_dir = tmp_path / run / "feedback"
        files = list(feedback_dir.glob(f"{mark_id}-*.json"))
        assert len(files) == 1, f"Expected 1 feedback file, found {files}"

    def test_post_feedback_file_contains_body(self, handle_feedback_post, tmp_path):
        """Feedback file contents match the posted JSON body exactly."""
        payload = {"run": "002", "markId": "w-3-7", "note": "stress error"}
        body = json.dumps(payload).encode()
        handler = _make_handler(path="/feedback", body=body)

        handle_feedback_post(handler, tmp_path)

        feedback_dir = tmp_path / "002" / "feedback"
        files = list(feedback_dir.glob("w-3-7-*.json"))
        assert files
        saved = json.loads(files[0].read_bytes())
        assert saved == payload

    # ------------------------------------------------------------------
    # POST /feedback — validation failures
    # ------------------------------------------------------------------

    def test_post_feedback_invalid_json_returns_400(self, handle_feedback_post, tmp_path):
        """Body that is not valid JSON → 400 with error key."""
        body = b"not json at all"
        handler = _make_handler(path="/feedback", body=body)

        handle_feedback_post(handler, tmp_path)

        handler.send_response.assert_called_once_with(400)
        # Response body written to wfile should contain {"error": "invalid JSON"}
        handler.wfile.seek(0)
        raw = handler.wfile.read()
        assert b"invalid JSON" in raw

    def test_post_feedback_invalid_mark_id_returns_400(self, handle_feedback_post, tmp_path):
        """markId with path-traversal characters (../) → 400."""
        body = json.dumps({"run": "001", "markId": "../evil"}).encode()
        handler = _make_handler(path="/feedback", body=body)

        handle_feedback_post(handler, tmp_path)

        handler.send_response.assert_called_once_with(400)
        handler.wfile.seek(0)
        raw = handler.wfile.read()
        assert b"invalid markId" in raw

    def test_post_feedback_invalid_run_returns_400(self, handle_feedback_post, tmp_path):
        """run field that is not 1-3 digits (e.g., '../output') → 400."""
        body = json.dumps({"run": "../output", "markId": "w-0-1"}).encode()
        handler = _make_handler(path="/feedback", body=body)

        handle_feedback_post(handler, tmp_path)

        handler.send_response.assert_called_once_with(400)
        handler.wfile.seek(0)
        raw = handler.wfile.read()
        assert b"invalid run" in raw

    def test_post_feedback_missing_mark_id_returns_400(self, handle_feedback_post, tmp_path):
        """Body without markId field → 400."""
        body = json.dumps({"run": "001", "note": "oops"}).encode()
        handler = _make_handler(path="/feedback", body=body)

        handle_feedback_post(handler, tmp_path)

        handler.send_response.assert_called_once_with(400)

    def test_post_feedback_missing_run_returns_400(self, handle_feedback_post, tmp_path):
        """Body without run field → 400."""
        body = json.dumps({"markId": "w-0-1", "note": "oops"}).encode()
        handler = _make_handler(path="/feedback", body=body)

        handle_feedback_post(handler, tmp_path)

        handler.send_response.assert_called_once_with(400)

    def test_post_unknown_path_returns_404(self, handle_feedback_post, tmp_path):
        """POST to any path other than /feedback → 404."""
        body = json.dumps({"run": "001", "markId": "w-0-1"}).encode()
        handler = _make_handler(path="/other", body=body)

        handle_feedback_post(handler, tmp_path)

        handler.send_error.assert_called_once_with(404)

    # ------------------------------------------------------------------
    # Atomic write
    # ------------------------------------------------------------------

    def test_feedback_file_written_atomically(self, handle_feedback_post, tmp_path):
        """No .tmp file remains after successful POST (atomic write via os.replace)."""
        body = json.dumps({"run": "003", "markId": "w-1-2"}).encode()
        handler = _make_handler(path="/feedback", body=body)

        handle_feedback_post(handler, tmp_path)

        tmp_files = list((tmp_path / "003" / "feedback").glob("*.tmp"))
        assert tmp_files == [], f"Leftover .tmp files: {tmp_files}"
