"""T-04a — Ollama HTTP adapter (LLMClientPort) + sqlite cache.

Spec: F48 DE-04. AC: F48-S03/AC-02. FT-321. BT-220.
"""

from __future__ import annotations

import json
import sqlite3

import pytest

from tirvi.correction.adapters.ollama import CAP_RESPONSE, OllamaClient


def _patched(monkeypatch, response_text: str = "ok"):
    monkeypatch.setattr(
        "tirvi.correction.adapters.ollama._http_post",
        lambda url, payload: {"response": response_text},
    )


class TestOllamaHttpRequest:
    """ADR-029: this adapter is the only file allowed to do HTTP."""

    def test_post_to_localhost_11434_api_generate(self, tmp_path, monkeypatch):
        calls: list[tuple] = []
        monkeypatch.setattr(
            "tirvi.correction.adapters.ollama._http_post",
            lambda url, payload: (calls.append((url, payload)) or {"response": "r"}),
        )
        OllamaClient(llm_cache_path=tmp_path / "c.sqlite").generate("p", "model", 0.0, 0)
        assert calls[0][0] == "http://localhost:11434/api/generate"

    def test_uses_temperature_and_seed_from_args(self, tmp_path, monkeypatch):
        calls: list[dict] = []
        monkeypatch.setattr(
            "tirvi.correction.adapters.ollama._http_post",
            lambda url, payload: (calls.append(payload) or {"response": "r"}),
        )
        OllamaClient(llm_cache_path=tmp_path / "c.sqlite").generate("p", "model", 0.0, 0)
        assert calls[0]["options"]["temperature"] == 0.0
        assert calls[0]["options"]["seed"] == 0

    def test_passes_model_id_to_ollama_payload(self, tmp_path, monkeypatch):
        calls: list[dict] = []
        monkeypatch.setattr(
            "tirvi.correction.adapters.ollama._http_post",
            lambda url, payload: (calls.append(payload) or {"response": "r"}),
        )
        OllamaClient(llm_cache_path=tmp_path / "c.sqlite").generate("p", "gemma4:31b", 0.0, 0)
        assert calls[0]["model"] == "gemma4:31b"


class TestSqliteLLMCache:
    """ADR-034: sqlite cache with sha256 cache key."""

    def test_cache_miss_writes_response(self, tmp_path, monkeypatch):
        _patched(monkeypatch, "result")
        cache = tmp_path / "c.sqlite"
        OllamaClient(llm_cache_path=cache).generate("p", "model", 0.0, 0)
        row = sqlite3.connect(str(cache)).execute("SELECT response FROM llm_calls LIMIT 1").fetchone()
        assert row is not None
        assert row[0] == "result"

    def test_cache_hit_skips_http(self, tmp_path, monkeypatch):
        calls: list[int] = []
        monkeypatch.setattr(
            "tirvi.correction.adapters.ollama._http_post",
            lambda url, payload: (calls.append(1) or {"response": "r"}),
        )
        client = OllamaClient(llm_cache_path=tmp_path / "c.sqlite")
        client.generate("prompt", "model", 0.0, 0)
        client.generate("prompt", "model", 0.0, 0)
        assert len(calls) == 1

    def test_cache_key_is_sha256_hex(self, tmp_path, monkeypatch):
        _patched(monkeypatch)
        cache = tmp_path / "c.sqlite"
        OllamaClient(llm_cache_path=cache).generate("p", "model", 0.0, 0)
        row = sqlite3.connect(str(cache)).execute("SELECT cache_key FROM llm_calls LIMIT 1").fetchone()
        assert row is not None
        assert len(row[0]) == 64  # sha256 hex digest


class TestPerPageLLMCallCap:
    """BT-F-05: per-page cap (default 10)."""

    def test_call_count_increments_per_page(self, tmp_path, monkeypatch):
        _patched(monkeypatch)
        client = OllamaClient(llm_cache_path=tmp_path / "c.sqlite", page_cap=5)
        client.generate("p1", "model", 0.0, 0)
        client.generate("p2", "model", 0.0, 0)
        assert client._page_calls == 2

    def test_cap_reached_emits_event(self, tmp_path, monkeypatch):
        _patched(monkeypatch)
        events: list[str] = []
        client = OllamaClient(
            llm_cache_path=tmp_path / "c.sqlite",
            page_cap=2,
            on_cap_reached=lambda: events.append("cap"),
        )
        for i in range(3):
            client.generate(f"p{i}", "model", 0.0, 0)
        assert events == ["cap"]

    def test_post_cap_returns_keep_original_short_circuit(self, tmp_path, monkeypatch):
        _patched(monkeypatch)
        client = OllamaClient(llm_cache_path=tmp_path / "c.sqlite", page_cap=2)
        client.generate("p1", "model", 0.0, 0)
        client.generate("p2", "model", 0.0, 0)
        result = client.generate("p3", "model", 0.0, 0)
        assert json.loads(result)["verdict"] == "keep_original"
