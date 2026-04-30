"""F22 T-07 — page.json projection (post-review C4).

Spec: N02/F22 DE-07. AC: US-01/AC-01.

``ReadingPlan.to_page_json(ocr_result)`` produces the F35-consumed
projection conforming to ``docs/schemas/page.schema.json``:
``{page_image_url, words[], marks_to_word_index}``. Bboxes are
converted from OCRWord's ``(x0, y0, x1, y1)`` to schema's
``[x, y, w, h]``. ``marks_to_word_index`` maps each ``PlanToken.id``
to the first word index from its ``src_word_indices``.
"""

from tirvi.plan import PlanBlock, PlanToken, ReadingPlan
from tirvi.results import OCRPage, OCRResult, OCRWord


def _ocr_result() -> OCRResult:
    return OCRResult(
        provider="tesseract-fake",
        pages=[
            OCRPage(
                words=[
                    OCRWord(text="שלום", bbox=(10, 20, 50, 40), conf=0.9, lang_hint="he"),
                    OCRWord(text="עולם", bbox=(60, 20, 100, 40), conf=0.85, lang_hint="he"),
                    OCRWord(text="פרק", bbox=(10, 60, 40, 80), conf=0.95, lang_hint="he"),
                ],
                lang_hints=["he"],
            ),
        ],
        confidence=None,
    )


def _plan() -> ReadingPlan:
    return ReadingPlan(
        page_id="page-1",
        blocks=(
            PlanBlock(
                block_id="b1",
                block_type="heading",
                tokens=(
                    PlanToken(id="b1-0", text="שלום", src_word_indices=(0,)),
                    PlanToken(id="b1-1", text="עולם", src_word_indices=(1,)),
                ),
            ),
            PlanBlock(
                block_id="b2",
                block_type="paragraph",
                tokens=(
                    PlanToken(id="b2-0", text="פרק", src_word_indices=(2,)),
                ),
            ),
        ),
    )


class TestPageJsonProjection:
    def test_us_01_ac_01_to_page_json_returns_dict(self) -> None:
        out = _plan().to_page_json(_ocr_result())
        assert isinstance(out, dict)
        # Required keys per docs/schemas/page.schema.json
        assert {"page_image_url", "words", "marks_to_word_index"} <= out.keys()

    def test_us_01_ac_01_default_page_image_url_is_page_1_png(self) -> None:
        out = _plan().to_page_json(_ocr_result())
        assert out["page_image_url"] == "page-1.png"

    def test_us_01_ac_01_caller_supplied_page_image_url_overrides_default(self) -> None:
        out = _plan().to_page_json(_ocr_result(), page_image_url="custom.png")
        assert out["page_image_url"] == "custom.png"

    def test_us_01_ac_01_words_bbox_converted_to_xywh(self) -> None:
        out = _plan().to_page_json(_ocr_result())
        words = out["words"]
        assert len(words) == 3
        assert words[0]["text"] == "שלום"
        # bbox converted from (x0, y0, x1, y1) to [x, y, w, h]
        # OCRWord.bbox = (10, 20, 50, 40) → [10, 20, 40, 20]
        assert words[0]["bbox"] == [10, 20, 40, 20]
        assert words[0]["lang_hint"] == "he"

    def test_us_01_ac_01_marks_to_word_index_from_first_src_word(self) -> None:
        out = _plan().to_page_json(_ocr_result())
        m = out["marks_to_word_index"]
        # Per schema: PlanToken.id → first(src_word_indices)
        assert m == {"b1-0": 0, "b1-1": 1, "b2-0": 2}

    def test_us_01_ac_01_empty_block_contributes_no_marks(self) -> None:
        plan_with_empty = ReadingPlan(
            page_id="page-1",
            blocks=(
                PlanBlock(block_id="b1", block_type="heading", tokens=()),
                PlanBlock(
                    block_id="b2",
                    block_type="paragraph",
                    tokens=(PlanToken(id="b2-0", text="א", src_word_indices=(0,)),),
                ),
            ),
        )
        out = plan_with_empty.to_page_json(_ocr_result())
        assert out["marks_to_word_index"] == {"b2-0": 0}
