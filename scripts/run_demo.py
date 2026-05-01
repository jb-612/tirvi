#!/usr/bin/env python
"""
POC demo: Economy.pdf page 1 → Hebrew TTS → word-synced player.

Usage:
    uv run scripts/run_demo.py [--port 8000]

The pipeline runs synchronously (~30–60 s with real models). Once done,
opens http://localhost:<port> in the browser and serves the player from
drafts/<sha>/ until Ctrl-C.

Prerequisites:
    - GOOGLE_APPLICATION_CREDENTIALS set (for Cloud TTS)
    - tesseract + heb tessdata installed
    - DictaBERT + Nakdan model weights accessible
"""

from __future__ import annotations

import argparse
import http.server
import logging
import os
import shutil
import sys
import webbrowser
from pathlib import Path

# Make `tirvi` importable when running the script directly (no editable install)
sys.path.insert(0, str(Path(__file__).parent.parent))

from tirvi.pipeline import make_poc_deps, make_stub_deps, run_pipeline  # noqa: E402

_LOG = logging.getLogger("demo")
_PDF = Path("docs/example/Economy.pdf")
_PLAYER = Path("player")
_DRAFTS = Path("drafts")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--port", type=int, default=8000, help="HTTP server port (default: 8000)")
    p.add_argument(
        "--stubs",
        action="store_true",
        help="Use in-memory stubs instead of real ML adapters (no Docker needed)",
    )
    return p.parse_args()


def _copy_player_assets(drafts_dir: Path) -> None:
    """Copy player/ HTML + CSS + JS into drafts_dir so it's self-contained."""
    shutil.copy(_PLAYER / "index.html", drafts_dir / "index.html")
    shutil.copy(_PLAYER / "player.css", drafts_dir / "player.css")
    js_dest = drafts_dir / "js"
    if js_dest.exists():
        shutil.rmtree(js_dest)
    shutil.copytree(_PLAYER / "js", js_dest)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = _parse_args()

    if not _PDF.exists():
        _LOG.error("PDF not found at %s — is the working directory the repo root?", _PDF)
        sys.exit(1)

    if args.stubs:
        deps = make_stub_deps()
        _LOG.info("Running pipeline in STUBS mode (no ML packages needed)")
    else:
        deps = make_poc_deps()
        _LOG.info("Running pipeline in POC mode (Tesseract OCR + Wavenet TTS)")
    _LOG.info("Running pipeline on %s …", _PDF)
    pdf_bytes = _PDF.read_bytes()
    result = run_pipeline(pdf_bytes, _DRAFTS, deps)
    drafts_dir: Path = result["drafts_dir"]
    _LOG.info("Artefacts written to %s (sha=%s)", drafts_dir, result["sha"])

    _copy_player_assets(drafts_dir)

    url = f"http://localhost:{args.port}"
    _LOG.info("Starting HTTP server at %s — press Ctrl-C to stop", url)
    webbrowser.open(url)

    os.chdir(drafts_dir)

    class _NoCacheHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self) -> None:  # type: ignore[override]
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            super().end_headers()

    with http.server.HTTPServer(("", args.port), _NoCacheHandler) as srv:
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            _LOG.info("Stopped.")


if __name__ == "__main__":
    main()
