#!/usr/bin/env python
"""
POC demo: Economy.pdf page 1 → Hebrew TTS → word-synced player.

Usage:
    uv run scripts/run_demo.py            # real pipeline → :8000
    uv run scripts/run_demo.py --stubs   # stub mode     → :8765

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
import datetime
import http.server
import json
import logging
import os
import shutil
import sys
import webbrowser
from pathlib import Path

# Make `tirvi` importable when running the script directly (no editable install)
sys.path.insert(0, str(Path(__file__).parent.parent))

import subprocess as _sp
from tirvi.pipeline import make_poc_deps, make_stub_deps, run_pipeline  # noqa: E402
from tirvi.progress import RichProgressReporter  # noqa: E402

_YAP_BIN = Path("/tmp/yap_bin")
_YAP_PORT = 8090
_YAP_DIR  = Path("/tmp/yap")   # binary must be at /tmp/yap/yap_bin; models at /tmp/yap/data/
_yap_proc = None


def _start_yap_if_available() -> None:
    global _yap_proc
    yap_bin = _YAP_DIR / "yap_bin"
    if not yap_bin.exists():
        _LOG.info("YAP binary not found at %s — alephbert+yap tab will be empty", yap_bin)
        return
    try:
        import urllib.request
        urllib.request.urlopen(f"http://127.0.0.1:{_YAP_PORT}/yap/heb/ma", timeout=1)
        _LOG.info("YAP already running on :%d", _YAP_PORT)
        return
    except Exception:
        pass
    _yap_proc = _sp.Popen(
        [str(yap_bin), "api"],
        cwd=str(_YAP_DIR),          # YAP resolves data/ relative to executable path
        stdout=_sp.DEVNULL, stderr=_sp.DEVNULL,
    )
    import time; time.sleep(5)      # YAP loads ~350MB joint model
    _LOG.info("YAP started on :%d (pid %d)", _YAP_PORT, _yap_proc.pid)

_LOG = logging.getLogger("demo")
_PDF = Path("docs/example/Economy.pdf")
_PLAYER = Path("player")
_DRAFTS = Path("drafts")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument(
        "--stubs",
        action="store_true",
        help="Use in-memory stubs instead of real ML adapters (no Docker needed)",
    )
    # Real demo owns :8000; stub runs default to :8765 so they never collide.
    p.add_argument("--port", type=int, default=None, help="HTTP server port (default: 8000 real, 8765 stubs)")
    args = p.parse_args()
    if args.port is None:
        args.port = 8765 if args.stubs else 8000
    return args


def _copy_player_assets(drafts_dir: Path) -> None:
    """Copy player/ HTML + CSS + JS into drafts_dir so it's self-contained."""
    shutil.copy(_PLAYER / "index.html", drafts_dir / "index.html")
    shutil.copy(_PLAYER / "player.css", drafts_dir / "player.css")
    js_dest = drafts_dir / "js"
    if js_dest.exists():
        shutil.rmtree(js_dest)
    shutil.copytree(_PLAYER / "js", js_dest)


def build_versions_list(drafts_dir: Path) -> list[dict]:
    """
    Return a list of version dicts for each subdirectory in drafts_dir.

    Each dict has: {"sha": str, "mtime": float, "label": str}.
    Returns [] when drafts_dir does not exist.
    Skips non-directory entries. Reads audio.json metadata when present.
    Sorts newest-first by mtime.
    """
    if not drafts_dir.exists():
        return []

    entries = []
    for child in drafts_dir.iterdir():
        if not child.is_dir() or child.name == "cascade_cache":
            continue
        mtime = child.stat().st_mtime
        label = _format_label(mtime)
        _try_enrich_from_audio_json(child, label)
        entries.append({"sha": child.name, "mtime": mtime, "label": label})

    entries.sort(key=lambda e: e["mtime"], reverse=True)
    return entries


def _format_label(mtime: float) -> str:
    """Format an mtime float into a human-readable label string."""
    dt = datetime.datetime.fromtimestamp(mtime)
    return dt.strftime("%Y-%m-%d %H:%M")


def _try_enrich_from_audio_json(sha_dir: Path, default_label: str) -> str:
    """
    Attempt to read audio.json from sha_dir for extra metadata.

    Returns default_label unchanged — enrichment is best-effort only.
    """
    audio_path = sha_dir / "audio.json"
    if not audio_path.exists():
        return default_label
    try:
        json.loads(audio_path.read_text())
    except Exception:  # noqa: BLE001
        pass
    return default_label


def _mime(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    return {"json": "application/json", "mp3": "audio/mpeg", "png": "image/png",
            "jpg": "image/jpeg", "js": "application/javascript", "css": "text/css"
            }.get(ext, "application/octet-stream")


def _build_versions_response(drafts_root: Path) -> bytes:
    """Serialize build_versions_list result to UTF-8 JSON bytes."""
    versions = build_versions_list(drafts_root)
    return json.dumps(versions).encode("utf-8")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = _parse_args()

    if not _PDF.exists():
        _LOG.error("PDF not found at %s — is the working directory the repo root?", _PDF)
        sys.exit(1)

    if not args.stubs:
        _start_yap_if_available()

    if args.stubs:
        deps = make_stub_deps()
        _LOG.info("Running pipeline in STUBS mode (no ML packages needed)")
    else:
        deps = make_poc_deps()
        _LOG.info("Running pipeline in POC mode (Tesseract OCR + Wavenet TTS)")
    _LOG.info("Running pipeline on %s …", _PDF)
    pdf_bytes = _PDF.read_bytes()
    reporter = RichProgressReporter()
    try:
        result = run_pipeline(pdf_bytes, _DRAFTS, deps, reporter=reporter)
    finally:
        reporter.summarize()
    drafts_dir: Path = result["drafts_dir"]
    _LOG.info("Artefacts written to %s (sha=%s)", drafts_dir, result["sha"])

    # Serve from repo root so player/ assets and all drafts/<sha>/ are reachable.
    # URL layout:
    #   /                      → player/index.html  (current UI)
    #   /player.css            → player/player.css
    #   /js/<file>             → player/js/<file>
    #   /api/versions          → JSON version list
    #   /api/current           → {"sha": "<current_sha>"}
    #   /<sha>/<file>          → drafts/<sha>/<file>  (page.json, audio.json, ...)

    _repo_root = Path.cwd()
    _current_sha = result["sha"]
    _repo_drafts = _repo_root / _DRAFTS
    _player_dir = _repo_root / _PLAYER

    url = f"http://localhost:{args.port}"
    _LOG.info("Starting HTTP server at %s — press Ctrl-C to stop", url)
    webbrowser.open(url)

    class _NoCacheHandler(http.server.BaseHTTPRequestHandler):
        def end_headers(self) -> None:
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            super().end_headers()

        def do_GET(self) -> None:
            path = self.path.split("?")[0]
            if path in ("/", "/index.html"):
                self._serve_file(_player_dir / "index.html", "text/html; charset=utf-8")
            elif path == "/player.css":
                self._serve_file(_player_dir / "player.css", "text/css")
            elif path.startswith("/js/"):
                self._serve_file(_player_dir / path.lstrip("/"), "application/javascript")
            elif path == "/api/versions":
                self._serve_json(_build_versions_response(_repo_drafts))
            elif path == "/api/current":
                self._serve_json(json.dumps({"sha": _current_sha}).encode())
            else:
                # /<sha>/<file> → drafts/<sha>/<file>
                parts = path.lstrip("/").split("/", 1)
                if len(parts) == 2:
                    sha, fname = parts
                    fpath = _repo_drafts / sha / fname
                    self._serve_file(fpath, _mime(fname))
                else:
                    self.send_error(404)

        def _serve_file(self, fpath: Path, ctype: str) -> None:
            if not fpath.exists():
                self.send_error(404)
                return
            body = fpath.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _serve_json(self, body: bytes) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt: str, *args: object) -> None:  # silence request log
            pass

    try:
        srv = http.server.HTTPServer(("", args.port), _NoCacheHandler)
    except OSError as exc:
        if exc.errno == 48:  # Address already in use
            _LOG.error(
                "Port %d is already in use. Kill the existing server first:\n"
                "  lsof -ti :%d | xargs kill\n"
                "Or serve on a different port: --port <n>\n"
                "Artefacts are in %s — you can reload the existing player to see them.",
                args.port, args.port, drafts_dir,
            )
            sys.exit(1)
        raise
    with srv:
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            _LOG.info("Stopped.")


if __name__ == "__main__":
    main()
