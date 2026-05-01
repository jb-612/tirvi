"""F48 correction-cascade scaffold fakes (T-01..T-10).

Deterministic in-memory fakes for the four ports defined in
``tirvi/correction/ports.py``. Wire-compatible with the Protocols.
TDD ``@test-mock-registry`` will harden / replace these as needed; they
exist now so test skeletons collect without import errors.

Strict scaffold rule: fakes have NO business logic. They store inputs
and return canned outputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import pytest

from tirvi.correction.ports import (
    FeedbackReadPort,
    LLMClientPort,
    NakdanWordListPort,
)
from tirvi.correction.value_objects import (
    CorrectionVerdict,
    SentenceContext,
    UserRejection,
)


# ---------------------------------------------------------------------------
# Word-list fake (CO13 / NakdanWordListPort)
# ---------------------------------------------------------------------------


@dataclass
class FakeNakdanWordList(NakdanWordListPort):
    """In-memory word-list fake.

    Behaviour: ``is_known_word(t) → t in self.known``. Used by NakdanGate
    and the LLM anti-hallucination guard. No I/O.
    """

    known: set[str] = field(default_factory=set)
    version: str = "fake-v1"

    def is_known_word(self, token: str) -> bool:
        return token in self.known


# ---------------------------------------------------------------------------
# LLM client fake (Ollama surrogate / LLMClientPort)
# ---------------------------------------------------------------------------


@dataclass
class FakeLLMClient(LLMClientPort):
    """Deterministic LLM client fake.

    Behaviour: ``generate(...) → self.canned_response`` and records the
    call args in ``self.calls`` for assertion. No HTTP.
    """

    canned_response: str = '{"verdict":"OK","chosen":null,"reason":"fake"}'
    calls: list[dict] = field(default_factory=list)

    def generate(
        self,
        prompt: str,
        model_id: str,
        temperature: float,
        seed: int,
    ) -> str:
        self.calls.append(
            {
                "prompt": prompt,
                "model_id": model_id,
                "temperature": temperature,
                "seed": seed,
            }
        )
        return self.canned_response


# ---------------------------------------------------------------------------
# Feedback fake (FeedbackReadPort)
# ---------------------------------------------------------------------------


@dataclass
class FakeFeedbackReader(FeedbackReadPort):
    """In-memory feedback fake (sqlite surrogate).

    ``rejections_by_sha[sha]`` returns a list of ``UserRejection``;
    missing key → empty.
    """

    rejections_by_sha: dict[str, list[UserRejection]] = field(default_factory=dict)

    def user_rejections(self, draft_sha: str) -> Iterable[UserRejection]:
        return list(self.rejections_by_sha.get(draft_sha, []))


# ---------------------------------------------------------------------------
# Cascade-stage fake (ICascadeStage) — shared scaffolding for service tests
# ---------------------------------------------------------------------------


@dataclass
class FakeCascadeStage:
    """Deterministic ``ICascadeStage`` fake.

    Returns a canned ``CorrectionVerdict`` for every token; records the
    call in ``self.calls``. Used by ``CorrectionCascadeService`` tests
    so the service can be exercised without DictaBERT / Ollama.
    """

    canned: CorrectionVerdict
    calls: list[tuple[str, SentenceContext]] = field(default_factory=list)

    def evaluate(
        self, token: str, context: SentenceContext
    ) -> CorrectionVerdict:
        self.calls.append((token, context))
        return self.canned


# ---------------------------------------------------------------------------
# pytest fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_word_list() -> FakeNakdanWordList:
    return FakeNakdanWordList(known={"שלום", "עולם", "סיום"})


@pytest.fixture
def fake_llm_client() -> FakeLLMClient:
    return FakeLLMClient()


@pytest.fixture
def fake_feedback() -> FakeFeedbackReader:
    return FakeFeedbackReader()


@pytest.fixture
def sample_sentence_context() -> SentenceContext:
    return SentenceContext(
        sentence_text="זה משפט לדוגמא",
        sentence_hash="sha256-deadbeef",
        page_index=0,
        token_index=0,
    )


__all__ = [
    "FakeNakdanWordList",
    "FakeLLMClient",
    "FakeFeedbackReader",
    "FakeCascadeStage",
]
