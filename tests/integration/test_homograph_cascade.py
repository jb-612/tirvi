"""F51 T-04 — homograph regression fixture, rule-layer integration.

Drives `tirvi.adapters.nakdan.inference._project_with_context` against
the curated fixture at `tests/fixtures/homographs.yaml`. Each case has
pre-baked Dicta-shape options for its focus word, so the test runs
deterministically without hitting Nakdan REST or Ollama.

Asserts strict ≥ 28/30 (≥ 93%) per ADR-038 §Round-2 follow-ups #6.

Spec: N02/F51 DE-04. AC: F51-S03/AC-01. ADR-038.
"""
from __future__ import annotations

import unicodedata
from pathlib import Path

import pytest
import yaml

from tirvi.adapters.nakdan.inference import _project_with_context
from tirvi.results import NLPToken

FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "homographs.yaml"


def _nfd(text: str) -> str:
    return unicodedata.normalize("NFD", text)


def _build_entries(case: dict) -> tuple[list[dict], list[NLPToken]]:
    """Build minimal Dicta-shape entries from the fixture case.

    Non-focus words get a single-option entry (their surface form);
    only the focus word receives the full Nakdan candidate list. This
    keeps the test focused on rule-layer behaviour for the focus word
    without polluting the resolved string with diacritics on other
    words.
    """
    sentence = case["sentence"]
    focus = case["focus"]
    focus_options = case["focus_options"]
    entries: list[dict] = []
    tokens: list[NLPToken] = []
    parts = sentence.split(" ")
    for i, word in enumerate(parts):
        if i > 0:
            entries.append({"word": " ", "sep": True, "options": []})
        if word == focus:
            opts = focus_options
        else:
            opts = [word]
        entries.append({
            "word": word, "sep": False, "options": opts,
            "fpasuk": False, "fconfident": False,
        })
        tokens.append(NLPToken(text=word, pos="NOUN", lemma=word))
    return entries, tokens


def _resolved_focus(out: str, focus: str, sentence: str) -> str:
    """Best-effort extraction of the focus word's resolved form from
    the full diacritized output. We split on whitespace and pick the
    token at the same position as the focus in the original sentence.
    """
    out_words = out.split(" ")
    in_words = sentence.split(" ")
    for i, w in enumerate(in_words):
        if w == focus and i < len(out_words):
            return out_words[i]
    return out


def _assert_case(case: dict, resolved: str) -> None:
    resolved_nfd = _nfd(resolved)
    must_any = [_nfd(s) for s in case["must_contain_any"]]
    if not any(s in resolved_nfd for s in must_any):
        raise AssertionError(
            f"{case['id']} missing any of {case['must_contain_any']!r} "
            f"in {resolved!r}"
        )
    forbidden = [_nfd(s) for s in case.get("must_not_contain_any", [])]
    for f in forbidden:
        if f in resolved_nfd:
            raise AssertionError(
                f"{case['id']} contains forbidden {f!r} in {resolved!r}"
            )


def _load_fixture() -> list[dict]:
    return yaml.safe_load(FIXTURE_PATH.read_text(encoding="utf-8"))["cases"]


def test_fixture_has_at_least_30_cases():
    assert len(_load_fixture()) >= 30


def test_fixture_covers_all_required_categories():
    cats = {c["category"] for c in _load_fixture()}
    expected = {
        "mappiq_possessive_rule_rescue",
        "mappiq_negative_no_trigger",
        "mother_or_whether_ambiguous",
        "whether_interrogative",
        "shalu_calm",
        "shalu_his",
        "control_simple",
    }
    missing = expected - cats
    assert not missing, f"fixture missing categories: {missing}"


@pytest.mark.parametrize("case", _load_fixture(), ids=lambda c: c["id"])
def test_per_case_resolution(case):
    if case.get("expected_failure"):
        pytest.xfail(f"{case['id']} expected to fail without LLM judge or T-05")
    entries, tokens = _build_entries(case)
    out = _project_with_context(entries, tokens, sentence=case["sentence"])
    resolved = _resolved_focus(out, case["focus"], case["sentence"])
    _assert_case(case, resolved)


def test_aggregate_strict_score_threshold():
    """Per ADR-038: cascade strict score must be >= 28/30 on the
    fixture. xfail-marked cases count as misses (they're known gaps
    awaiting T-05 / future work)."""
    cases = _load_fixture()
    correct = 0
    failures: list[str] = []
    for case in cases:
        try:
            entries, tokens = _build_entries(case)
            out = _project_with_context(entries, tokens, sentence=case["sentence"])
            resolved = _resolved_focus(out, case["focus"], case["sentence"])
            _assert_case(case, resolved)
        except AssertionError as exc:
            failures.append(str(exc))
            continue
        correct += 1
    threshold = 28
    assert correct >= threshold, (
        f"strict score {correct}/{len(cases)} below threshold {threshold}; "
        f"failures:\n" + "\n".join(failures)
    )
