"""F53 T-05 — clause-split chunker regression on the curated corpus.

Loads tests/fixtures/clause_split.yaml, runs `chunk_block_tokens` on
each case, asserts the fragment count and break-reason match
expectation. Strict floor ≥ 18/22 per F53 design.md DE-05.

Spec: N02/F53 DE-05. AC: F53-S05/AC-01. ADR-041.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tirvi.plan.value_objects import PlanToken
from tirvi.ssml.chunker import chunk_block_tokens

FIXTURE = Path(__file__).parent.parent / "fixtures" / "clause_split.yaml"


def _load() -> dict:
    return yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))


def _build_tokens(case: dict) -> list[PlanToken]:
    return [
        PlanToken(
            id=f"b1-{i}", text=t["text"], src_word_indices=(i,),
            pos=t.get("pos"),
        )
        for i, t in enumerate(case["tokens"])
    ]


def _all_cases() -> list[dict]:
    return _load()["cases"]


def _evaluate_case(case: dict) -> tuple[bool, str]:
    """Return (passed, failure_reason). passed=True with empty reason on success."""
    tokens = _build_tokens(case)
    fragments, breaks = chunk_block_tokens(tokens)
    if len(fragments) != case["expected_fragments"]:
        return (False, f"fragments {len(fragments)} != {case['expected_fragments']}")
    if len(breaks) != case["expected_breaks"]:
        return (False, f"breaks {len(breaks)} != {case['expected_breaks']}")
    if "expected_break_kind" in case and breaks:
        if breaks[0]["kind"] != case["expected_break_kind"]:
            return (False, f"kind {breaks[0]['kind']!r} != {case['expected_break_kind']!r}")
    if "expected_break_reason" in case and breaks:
        if breaks[0]["reason"] != case["expected_break_reason"]:
            return (False, f"reason {breaks[0]['reason']!r} != {case['expected_break_reason']!r}")
    if "expected_break_reason_starts_with" in case and breaks:
        if not breaks[0]["reason"].startswith(case["expected_break_reason_starts_with"]):
            prefix = case["expected_break_reason_starts_with"]
            return (False, f"reason {breaks[0]['reason']!r} does not start with {prefix!r}")
    return (True, "")


def test_fixture_has_at_least_20_cases():
    assert len(_all_cases()) >= 20


def test_fixture_covers_all_three_outcomes():
    """Under-threshold passthrough, splits, and skipped."""
    ids = {c["id"][0] for c in _all_cases()}
    # U = under-threshold, S = split, K = skipped
    assert "U" in ids and "S" in ids and "K" in ids


@pytest.mark.parametrize("case", _all_cases(), ids=lambda c: c["id"])
def test_per_case(case):
    passed, reason = _evaluate_case(case)
    assert passed, f"{case['id']}: {reason} — {case.get('description', '')}"


def test_aggregate_strict_score_threshold():
    """Per F53 design.md DE-05: strict ≥ 18/22 (≥ 81%)."""
    cases = _all_cases()
    correct = 0
    failures: list[str] = []
    for case in cases:
        passed, reason = _evaluate_case(case)
        if passed:
            correct += 1
        else:
            failures.append(f"{case['id']}: {reason}")
    threshold = 18
    assert correct >= threshold, (
        f"strict score {correct}/{len(cases)} below {threshold}; "
        f"failures:\n" + "\n".join(failures)
    )
