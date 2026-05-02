"""F52 T-05 — block-kind classifier regression on the curated corpus.

Loads tests/fixtures/block_taxonomy.yaml, runs `classify_block` on
each case, asserts strict-pick == expected on ≥ 28/30 cases per
F52 design.md DE-05.

Spec: N02/F52 DE-05. AC: F52-S05/AC-01. ADR-041.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tirvi.blocks.classifier import classify_block
from tirvi.blocks.value_objects import PageStats
from tirvi.results import OCRWord

FIXTURE = Path(__file__).parent.parent / "fixtures" / "block_taxonomy.yaml"


def _load() -> dict:
    return yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))


def _build_words(case: dict, defaults: dict) -> list[OCRWord]:
    bbox_key = case.get("word_bbox", "default_bbox")
    bbox = tuple(defaults[bbox_key])
    return [
        OCRWord(text=t, bbox=bbox, confidence=1.0)
        for t in case["words"]
    ]


def _build_stats(defaults: dict) -> PageStats:
    return PageStats(
        median_word_height=defaults["median_word_height"],
        modal_x_start=defaults["modal_x_start"],
        line_spacing=defaults["line_spacing"],
    )


def _all_cases() -> list[dict]:
    return _load()["cases"]


def test_fixture_has_at_least_30_cases():
    assert len(_all_cases()) >= 30


def test_fixture_covers_all_eight_kinds():
    kinds = {c["expected_kind"] for c in _all_cases()}
    assert kinds == {
        "paragraph", "heading", "question_stem", "mixed",
        "instruction", "datum", "answer_blank", "multi_choice_options",
    }


@pytest.mark.parametrize("case", _all_cases(), ids=lambda c: c["id"])
def test_per_case_classification(case):
    fixture = _load()
    words = _build_words(case, fixture["defaults"])
    stats = _build_stats(fixture["defaults"])
    kind, _conf = classify_block(words, stats)
    assert kind == case["expected_kind"], (
        f"{case['id']}: expected {case['expected_kind']!r}, got {kind!r}"
    )


def test_aggregate_strict_score_threshold():
    """Per F52 design.md DE-05: strict score must be ≥ 28/30."""
    fixture = _load()
    cases = fixture["cases"]
    stats = _build_stats(fixture["defaults"])
    correct = 0
    failures: list[str] = []
    for case in cases:
        words = _build_words(case, fixture["defaults"])
        kind, _ = classify_block(words, stats)
        if kind == case["expected_kind"]:
            correct += 1
        else:
            failures.append(
                f"{case['id']}: expected {case['expected_kind']!r}, got {kind!r}"
            )
    threshold = 28
    assert correct >= threshold, (
        f"strict score {correct}/{len(cases)} below {threshold}; "
        f"failures:\n" + "\n".join(failures)
    )
