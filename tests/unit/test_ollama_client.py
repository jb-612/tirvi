"""T-04a — Ollama HTTP adapter (LLMClientPort) + sqlite cache.

Spec: F48 DE-04. AC: F48-S03/AC-02. FT-321. BT-220.

Scaffold — TDD T-04a fills bodies. The adapter file does not yet
exist; TDD will create ``tirvi/correction/adapters/ollama.py``.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="scaffold — /tdd fills")


class TestOllamaHttpRequest:
    """ADR-029: this adapter is the only file allowed to import httpx."""

    def test_post_to_localhost_11434_api_generate(self):
        # AC-F48-S03/AC-02 — privacy: localhost only (ADR-033)
        pass

    def test_uses_temperature_zero_and_seed_zero(self):
        # Determinism (BT-217)
        pass

    def test_passes_model_id_to_ollama_payload(self):
        pass


class TestSqliteLLMCache:
    """ADR-034 cache key: sha256(model_id || version || sentence_hash || sorted(candidates))."""

    def test_cache_miss_writes_response(self):
        pass

    def test_cache_hit_returns_stored_response(self):
        pass

    def test_cache_key_uses_sorted_candidates(self):
        # ADR-034 — order-independent
        pass


class TestPerPageLLMCallCap:
    """BT-F-05: per-page cap (default 10)."""

    def test_call_count_increments_per_page(self):
        pass

    def test_cap_reached_emits_event(self):
        # Emits LLMCallCapReached
        pass

    def test_post_cap_returns_keep_original_short_circuit(self):
        # BT-220
        pass
