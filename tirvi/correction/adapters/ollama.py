"""Ollama HTTP adapter — LLMClientPort concrete implementation (DE-04).

Spec: F48 DE-04. AC: F48-S03/AC-02. ADR-029. T-04a.

This is the ONLY file in tirvi allowed to make external HTTP calls.
All requests go to localhost (ADR-033 privacy invariant).
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from tirvi.correction.ports import LLMClientPort
from tirvi.correction.value_objects import CorrectionVerdict

CAP_RESPONSE = json.dumps(
    {"verdict": "keep_original", "chosen": None, "reason": "llm_call_cap_reached"}
)


def _http_post(url: str, payload: dict) -> dict:
    """POST JSON to url and return parsed JSON response.

    Monkeypatched in unit tests — never called in test context.
    """
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


@dataclass
class OllamaClient(LLMClientPort):
    """Ollama HTTP adapter with sqlite LLM response cache (ADR-034)."""

    llm_cache_path: str | Path
    base_url: str = "http://localhost:11434"
    page_cap: int = 10
    on_cap_reached: Callable[[], None] | None = field(default=None, compare=False, repr=False)
    _page_calls: int = field(default=0, init=False, repr=False, compare=False)
    _conn: sqlite3.Connection | None = field(default=None, init=False, repr=False, compare=False)

    def generate(self, prompt: str, model_id: str, temperature: float, seed: int) -> str:
        if self._page_calls >= self.page_cap:
            return self._cap_response()
        self._page_calls += 1
        key = _sha256(f"{model_id}:{prompt}")
        cached = self._lookup(key)
        if cached is not None:
            return cached
        response = _http_post(
            f"{self.base_url}/api/generate",
            {"model": model_id, "prompt": prompt, "stream": False,
             "options": {"temperature": temperature, "seed": seed}},
        )["response"]
        self._store(key, model_id, response)
        return response

    def reset_page(self) -> None:
        self._page_calls = 0

    def _cap_response(self) -> str:
        if self.on_cap_reached:
            self.on_cap_reached()
        return CAP_RESPONSE

    def _ensure_db(self) -> sqlite3.Connection:
        if self._conn is None:
            Path(self.llm_cache_path).parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self.llm_cache_path))
            self._conn.execute(
                """CREATE TABLE IF NOT EXISTS llm_calls (
                    cache_key TEXT PRIMARY KEY,
                    model_id TEXT,
                    prompt_template_version TEXT,
                    sentence_hash TEXT,
                    response TEXT,
                    ts TEXT
                )"""
            )
            self._conn.commit()
        return self._conn

    def _lookup(self, key: str) -> str | None:
        row = self._ensure_db().execute(
            "SELECT response FROM llm_calls WHERE cache_key = ?", (key,)
        ).fetchone()
        return row[0] if row else None

    def _store(self, key: str, model_id: str, response: str) -> None:
        ts = datetime.now(tz=timezone.utc).isoformat()
        self._ensure_db().execute(
            "INSERT OR REPLACE INTO llm_calls VALUES (?, ?, ?, ?, ?, ?)",
            (key, model_id, "", "", response, ts),
        )
        self._conn.commit()  # type: ignore[union-attr]


__all__ = ["OllamaClient", "CAP_RESPONSE"]
