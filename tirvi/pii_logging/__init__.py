"""tirvi.pii_logging — No-PII logging guard (deferred post-POC).

Spec: N05/F46. Status: deferred — populated when biz-functional-design
runs for N05.
"""

from __future__ import annotations

import logging


class PiiScrubFilter(logging.Filter):
    """``logging.Filter`` that scrubs sensitive keys from record extras."""

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - stub
        raise NotImplementedError("F46 deferred post-POC")
