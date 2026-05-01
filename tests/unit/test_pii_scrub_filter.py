"""F46 — No-PII logging filter (deferred post-POC stub)."""

from __future__ import annotations


def test_f46_stub_module_imports() -> None:
    from tirvi.pii_logging import PiiScrubFilter

    assert PiiScrubFilter is not None
    import logging

    assert issubclass(PiiScrubFilter, logging.Filter)
