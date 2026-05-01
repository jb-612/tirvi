"""F21 — Hebrew homograph override lexicon.

Spec: PRD §6.4. N02/F21. Issue #20.

Module-level ``HOMOGRAPH_OVERRIDES`` is a flat ``dict[str, str]`` mapping
undecorated Hebrew surface forms to preferred diacritized forms; loaded
from ``data/homograph-lexicon.yaml`` at import time and consumed by
F19's :func:`tirvi.adapters.nakdan.inference.diacritize_in_context`.
"""

from pathlib import Path

from tirvi.homograph.loader import load_overrides

_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEXICON_PATH = _REPO_ROOT / "data" / "homograph-lexicon.yaml"

HOMOGRAPH_OVERRIDES: dict[str, str] = load_overrides(DEFAULT_LEXICON_PATH)
