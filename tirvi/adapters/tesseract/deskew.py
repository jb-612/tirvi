"""F08 T-05 — optional Hough deskew preprocessor.

Spec: N01/F08 DE-05. AC: US-01/AC-01. FT-anchors: FT-059. BT-anchors: BT-041.

Disabled by default. Enable via the ``deskew=True`` constructor flag on
:class:`TesseractOCRAdapter` or by setting ``TIRVI_TESSERACT_DESKEW=on``
in the environment. Skips rotation when ``|angle| < THRESHOLD_DEG`` (5°).

Vendor isolation: ``cv2`` (OpenCV) is imported lazily here only — DE-06,
ADR-014. ``cv2`` is optional in dev; missing raises ``NotImplementedError``.
"""

from __future__ import annotations

import os
from typing import Any

from PIL import Image  # type: ignore[import-not-found]

THRESHOLD_DEG = 5.0
_ENV_FLAG = "TIRVI_TESSERACT_DESKEW"


def is_enabled(adapter_flag: bool) -> bool:
    """``True`` iff deskew should run (constructor flag OR env var ``on``)."""
    if adapter_flag:
        return _env_value() != "off"
    return _env_value() == "on"


def _env_value() -> str:
    return os.environ.get(_ENV_FLAG, "").strip().lower()


def deskew_image(image: Image.Image) -> Image.Image:
    """Detect skew angle via Hough; rotate when ``|angle| >= THRESHOLD_DEG``."""
    cv2 = _load_cv2()
    angle = _detect_angle(image, cv2)
    if abs(angle) < THRESHOLD_DEG:
        return image
    return image.rotate(angle, expand=True, fillcolor="white")


def _load_cv2() -> Any:
    try:
        import cv2  # type: ignore[import-not-found]
    except ImportError as exc:
        raise NotImplementedError("cv2 not available") from exc
    return cv2


def _detect_angle(image: Image.Image, cv2: Any) -> float:
    import numpy as np  # type: ignore[import-not-found]

    arr = np.array(image.convert("L"))
    edges = cv2.Canny(arr, 50, 150)
    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180.0, threshold=80, minLineLength=50, maxLineGap=10
    )
    if lines is None:
        return 0.0
    angles = [_line_angle(line[0], np) for line in lines]
    return float(np.median(angles)) if angles else 0.0


def _line_angle(line: Any, np_module: Any) -> float:
    x1, y1, x2, y2 = line
    return float(np_module.degrees(np_module.arctan2(y2 - y1, x2 - x1)))
