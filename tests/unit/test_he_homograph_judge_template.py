"""F51 T-03 — homograph judge prompt template + meta sanity.

Asserts the production-grade prompt artifact is in place, has the
right placeholders, and that the cache-key scheme will isolate
homograph-judge entries from OCR-reviewer entries (per ADR-034).

Spec: N02/F51 DE-03. AC: F51-S02/AC-01. ADR-038, ADR-034.
"""
from __future__ import annotations

from pathlib import Path

import yaml

PROMPT_DIR = Path("tirvi/correction/prompts/he_homograph_judge")


def test_v1_template_exists_with_required_placeholders():
    template = (PROMPT_DIR / "v1.txt").read_text(encoding="utf-8")
    assert "{sentence}" in template
    assert "{focus}" in template
    assert "{options_block}" in template


def test_meta_yaml_declares_v1_homograph_version():
    meta = yaml.safe_load((PROMPT_DIR / "_meta.yaml").read_text(encoding="utf-8"))
    assert meta["prompt_template_version"] == "v1-homograph"
    assert meta["status"] == "active"


def test_meta_lists_the_four_homograph_categories():
    meta = yaml.safe_load((PROMPT_DIR / "_meta.yaml").read_text(encoding="utf-8"))
    cats = " ".join(meta["reasoning_categories"]).lower()
    assert "mappiq" in cats
    assert "prefix" in cats
    assert "possessive" in cats or "his" in cats
    assert "interrogative" in cats or "whether" in cats


def test_homograph_judge_version_is_distinct_from_ocr_reviewer():
    """Cache-key isolation per ADR-034 — two different version strings."""
    homograph_meta = yaml.safe_load(
        (PROMPT_DIR / "_meta.yaml").read_text(encoding="utf-8")
    )
    reviewer_meta = yaml.safe_load(
        Path("tirvi/correction/prompts/he_reviewer/_meta.yaml").read_text(encoding="utf-8")
    )
    assert (
        homograph_meta["prompt_template_version"]
        != reviewer_meta["prompt_template_version"]
    )
