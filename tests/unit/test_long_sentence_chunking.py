"""F17 T-05 — long-sentence chunking (model context window).

Spec: N02/F17 DE-05. AC: US-01/AC-01.

The DictaBERT model has a 512 sub-token context window. The adapter must
chunk inputs that exceed a 448 sub-token safe limit (64-token headroom),
with a 64 sub-token overlap between adjacent chunks. Per-word labels in
the overlap region are reconciled by majority vote; original whitespace
token order is preserved in the output.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator
from unittest.mock import MagicMock, patch

from tirvi.adapters.dictabert.inference import analyze
from tirvi.results import NLPToken

MAX_SUBTOKENS = 448
OVERLAP_SUBTOKENS = 64


def _make_predict_response(tokens: list[NLPToken]) -> list[dict[str, Any]]:
    """Build the raw ``model.predict`` response from a list of NLPToken."""
    return [
        {
            "tokens": [
                {
                    "token": tok.text,
                    "lex": tok.lemma,
                    "syntax": {"pos": tok.pos},
                }
                for tok in tokens
            ]
        }
    ]


def _encode_words(s: str, sub_per_word: int = 1) -> list[int]:
    return [0] * (len(s.split()) * sub_per_word)


def _wire_fakes(
    fake_tokenizer: MagicMock,
    fake_model: MagicMock,
    *,
    sub_per_word: int,
    chunk_log: list[str] | None = None,
    pos_per_chunk: list[str] | None = None,
) -> None:
    """Wire encode + predict mocks; optionally tag each chunk with a POS."""

    fake_tokenizer.encode.side_effect = (
        lambda s, add_special_tokens=True: _encode_words(s, sub_per_word)
    )

    state = {"chunk_idx": 0}

    def predict_side_effect(
        texts: list[str], _tok: MagicMock
    ) -> list[dict[str, Any]]:
        chunk_text = texts[0]
        if chunk_log is not None:
            chunk_log.append(chunk_text)
        pos = "NOUN"
        if pos_per_chunk is not None:
            pos = pos_per_chunk[state["chunk_idx"]]
        state["chunk_idx"] += 1
        return _make_predict_response(
            [NLPToken(text=w, pos=pos) for w in chunk_text.split()]
        )

    fake_model.predict.side_effect = predict_side_effect


@contextmanager
def _patched_loader(
    fake_model: MagicMock, fake_tokenizer: MagicMock
) -> Iterator[None]:
    with patch(
        "tirvi.adapters.dictabert.inference.load_model",
        return_value=(fake_model, fake_tokenizer),
    ):
        yield


class TestLongSentenceChunking:
    def test_us_01_ac_01_short_text_no_chunking(self) -> None:
        """Texts within model context are not chunked — single predict call."""
        fake_model = MagicMock(name="model")
        fake_tokenizer = MagicMock(name="tokenizer")
        chunk_log: list[str] = []
        _wire_fakes(
            fake_tokenizer,
            fake_model,
            sub_per_word=1,
            chunk_log=chunk_log,
        )
        text = "אחד שניים שלושה"
        with _patched_loader(fake_model, fake_tokenizer):
            result = analyze(text, lang="he")
        assert fake_model.predict.call_count == 1
        assert chunk_log == [text]
        assert [t.text for t in result.tokens] == text.split()

    def test_us_01_ac_01_long_text_triggers_multiple_chunks(self) -> None:
        """When sub-token count > 448, predict is called more than once."""
        words = [f"w{i}" for i in range(600)]
        text = " ".join(words)
        fake_model = MagicMock(name="model")
        fake_tokenizer = MagicMock(name="tokenizer")
        _wire_fakes(fake_tokenizer, fake_model, sub_per_word=1)
        with _patched_loader(fake_model, fake_tokenizer):
            result = analyze(text, lang="he")
        assert fake_model.predict.call_count >= 2
        assert len(result.tokens) == 600

    def test_us_01_ac_01_no_chunk_exceeds_subtoken_limit(self) -> None:
        """Each chunk passed to predict has at most 448 sub-tokens."""
        words = [f"w{i}" for i in range(1500)]
        text = " ".join(words)
        fake_model = MagicMock(name="model")
        fake_tokenizer = MagicMock(name="tokenizer")
        chunk_log: list[str] = []
        _wire_fakes(
            fake_tokenizer,
            fake_model,
            sub_per_word=1,
            chunk_log=chunk_log,
        )
        with _patched_loader(fake_model, fake_tokenizer):
            analyze(text, lang="he")
        assert chunk_log, "predict should have been called at least once"
        for chunk in chunk_log:
            assert len(chunk.split()) <= MAX_SUBTOKENS

    def test_us_01_ac_01_preserves_whitespace_token_order(self) -> None:
        """Output token order matches input whitespace order across chunks."""
        words = [f"w{i:04d}" for i in range(1000)]
        text = " ".join(words)
        fake_model = MagicMock(name="model")
        fake_tokenizer = MagicMock(name="tokenizer")
        _wire_fakes(fake_tokenizer, fake_model, sub_per_word=1)
        with _patched_loader(fake_model, fake_tokenizer):
            result = analyze(text, lang="he")
        assert [t.text for t in result.tokens] == words

    def test_us_01_ac_01_overlap_words_appear_once(self) -> None:
        """Words in the overlap region are not duplicated in the output."""
        words = [f"w{i}" for i in range(1100)]
        text = " ".join(words)
        fake_model = MagicMock(name="model")
        fake_tokenizer = MagicMock(name="tokenizer")
        _wire_fakes(fake_tokenizer, fake_model, sub_per_word=1)
        with _patched_loader(fake_model, fake_tokenizer):
            result = analyze(text, lang="he")
        assert fake_model.predict.call_count >= 2
        assert len(result.tokens) == len(words)
        assert [t.text for t in result.tokens] == words

    def test_us_01_ac_01_overlap_majority_vote_breaks_disagreement(
        self,
    ) -> None:
        """When chunks disagree on overlap labels, majority POS wins.

        With n=1100 single-sub-token words, MAX=448, OVERLAP=64 the
        adapter forms exactly three chunks: c1=[0,448), c2=[384,832),
        c3=[768,1100). With POS labels chunk1=NOUN, chunk2=NOUN,
        chunk3=VERB the (c1,c2) overlap is unanimous NOUN; the (c2,c3)
        overlap is a NOUN/VERB tie won by chunk 2's first-inserted vote
        (Python Counter.most_common is insertion-ordered on ties). Every
        word in chunks 1 and 2's combined span resolves to NOUN; only
        the chunk-3-only tail is VERB.
        """
        n = 1100
        words = [f"w{i}" for i in range(n)]
        text = " ".join(words)
        fake_model = MagicMock(name="model")
        fake_tokenizer = MagicMock(name="tokenizer")
        _wire_fakes(
            fake_tokenizer,
            fake_model,
            sub_per_word=1,
            pos_per_chunk=["NOUN", "NOUN", "VERB"],
        )
        with _patched_loader(fake_model, fake_tokenizer):
            result = analyze(text, lang="he")
        assert fake_model.predict.call_count == 3
        second_chunk_end = MAX_SUBTOKENS + (MAX_SUBTOKENS - OVERLAP_SUBTOKENS)
        for i in range(second_chunk_end):
            assert result.tokens[i].pos == "NOUN", (
                f"word {i} expected NOUN, got {result.tokens[i].pos}"
            )
        for i in range(second_chunk_end, n):
            assert result.tokens[i].pos == "VERB"

    def test_us_01_ac_01_high_clitic_regression(self) -> None:
        """100 × `שכשהתלמידים`: each chunk stays under the 448 sub-token cap.

        Each clitic-heavy word is approximated as 6 sub-tokens, so the
        full input is ~600 sub-tokens — over the 448 limit, forcing at
        least one chunk boundary. Regression: T-05 must compute chunks
        on sub-token count, not whitespace tokens, or this 100-word
        input would mistakenly fit in one chunk.
        """
        word = "שכשהתלמידים"
        sub_per_word = 6
        words = [word] * 100
        text = " ".join(words)
        fake_model = MagicMock(name="model")
        fake_tokenizer = MagicMock(name="tokenizer")
        chunk_log: list[str] = []
        _wire_fakes(
            fake_tokenizer,
            fake_model,
            sub_per_word=sub_per_word,
            chunk_log=chunk_log,
        )
        with _patched_loader(fake_model, fake_tokenizer):
            result = analyze(text, lang="he")
        assert fake_model.predict.call_count >= 2, (
            "100 high-clitic words should overflow the 448 cap"
        )
        for chunk in chunk_log:
            assert len(chunk.split()) * sub_per_word <= MAX_SUBTOKENS
        assert len(result.tokens) == 100
        assert all(t.text == word for t in result.tokens)
