"""RED phase tests for T-05: RichProgressReporter with TTY detection and summary table.

All tests exercise the NON-TTY path — the CI-safe path — by monkeypatching
sys.stdout.isatty to return False before the constructor runs.

F49-ARCH-02: rich import is guarded with try/except ImportError; falls back
             to plain-log path automatically.
F49-ARCH-03: constructor checks sys.stdout.isatty() BEFORE creating any rich
             objects.
F49-ADV-02:  RichProgressReporter is documented as non-thread-safe.

Acceptance criteria covered: FT-325, FT-326, FT-327, FT-328,
US-F49-01/AC-01..AC-03, US-F49-05/AC-01..AC-04.
"""

from __future__ import annotations

import logging
import sys


# ---------------------------------------------------------------------------
# T-05 / AC-01 — protocol conformance
# ---------------------------------------------------------------------------


def test_rich_reporter_satisfies_protocol(monkeypatch) -> None:
    """isinstance(RichProgressReporter(), ProgressReporter) must be True (FT-325)."""
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    # Import after monkeypatch so constructor sees non-TTY environment.
    from tirvi.progress import ProgressReporter, RichProgressReporter  # noqa: PLC0415

    reporter = RichProgressReporter()
    assert isinstance(reporter, ProgressReporter)


# ---------------------------------------------------------------------------
# T-05 / AC-02 — all five protocol methods exist and can be called (non-TTY)
# ---------------------------------------------------------------------------


def test_rich_reporter_nontty_stage_started_no_error(monkeypatch) -> None:
    """In non-TTY mode, stage_started('OCR') must not raise (FT-326)."""
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    from tirvi.progress import RichProgressReporter  # noqa: PLC0415

    reporter = RichProgressReporter()
    reporter.stage_started("OCR")  # must not raise


def test_rich_reporter_nontty_stage_completed_no_error(monkeypatch) -> None:
    """In non-TTY mode, stage_completed must not raise (FT-326)."""
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    from tirvi.progress import RichProgressReporter  # noqa: PLC0415

    reporter = RichProgressReporter()
    reporter.stage_completed("OCR", 1.2, "5 words")  # must not raise


def test_rich_reporter_nontty_stage_error_no_error(monkeypatch) -> None:
    """In non-TTY mode, stage_error must not raise (FT-326)."""
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    from tirvi.progress import RichProgressReporter  # noqa: PLC0415

    reporter = RichProgressReporter()
    reporter.stage_error("OCR", "tesseract crashed")  # must not raise


def test_rich_reporter_nontty_token_tick_no_error(monkeypatch) -> None:
    """In non-TTY mode, token_tick must not raise (FT-326)."""
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    from tirvi.progress import RichProgressReporter  # noqa: PLC0415

    reporter = RichProgressReporter()
    reporter.token_tick()  # must not raise


def test_rich_reporter_nontty_summarize_no_error(monkeypatch) -> None:
    """In non-TTY mode, summarize with no stages must not raise (FT-326)."""
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    from tirvi.progress import RichProgressReporter  # noqa: PLC0415

    reporter = RichProgressReporter()
    reporter.summarize()  # must not raise even with no stages recorded


# ---------------------------------------------------------------------------
# T-05 / AC-03 — non-TTY summarize output content
# ---------------------------------------------------------------------------


def test_rich_reporter_nontty_summarize_contains_stage_name(monkeypatch, caplog) -> None:
    """After stage_completed('OCR', ...), summarize() must log 'OCR' (FT-327)."""
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    from tirvi.progress import RichProgressReporter  # noqa: PLC0415

    reporter = RichProgressReporter()
    reporter.stage_completed("OCR", 1.2, "5 words")
    with caplog.at_level(logging.INFO):
        reporter.summarize()
    assert "OCR" in caplog.text, (
        "summarize() log output must contain the stage name 'OCR'"
    )


def test_rich_reporter_nontty_summarize_contains_elapsed(monkeypatch, caplog) -> None:
    """After stage_completed('TTS', 2.5, ...), summarize() must log 'TTS' and '2.5' (FT-327)."""
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    from tirvi.progress import RichProgressReporter  # noqa: PLC0415

    reporter = RichProgressReporter()
    reporter.stage_completed("TTS", 2.5, "512 KB")
    with caplog.at_level(logging.INFO):
        reporter.summarize()
    assert "TTS" in caplog.text, (
        "summarize() log output must contain the stage name 'TTS'"
    )
    assert "2.5" in caplog.text, (
        "summarize() log output must contain the elapsed time '2.5'"
    )


def test_rich_reporter_nontty_summarize_contains_total(monkeypatch, caplog) -> None:
    """Non-TTY summarize() must include a 'Total' footer line (FT-328, US-F49-05/AC-04)."""
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    from tirvi.progress import RichProgressReporter  # noqa: PLC0415

    reporter = RichProgressReporter()
    reporter.stage_completed("OCR", 1.0, "10 words")
    reporter.stage_completed("TTS", 3.0, "256 KB")
    with caplog.at_level(logging.INFO):
        reporter.summarize()
    assert "Total" in caplog.text, (
        "summarize() non-TTY output must include a 'Total' footer"
    )


def test_rich_reporter_nontty_summarize_sorted_by_elapsed_desc(monkeypatch, caplog) -> None:
    """Non-TTY summarize() must emit stages sorted descending by elapsed_s (US-F49-05/AC-03).

    After completing OCR (elapsed=1.0) then TTS (elapsed=3.0), the TTS row
    must appear BEFORE the OCR row in the logged output.
    """
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    from tirvi.progress import RichProgressReporter  # noqa: PLC0415

    reporter = RichProgressReporter()
    reporter.stage_completed("OCR", 1.0, "10 words")
    reporter.stage_completed("TTS", 3.0, "256 KB")
    with caplog.at_level(logging.INFO):
        reporter.summarize()
    ocr_pos = caplog.text.find("OCR")
    tts_pos = caplog.text.find("TTS")
    assert tts_pos != -1 and ocr_pos != -1, (
        "Both stage names must appear in summarize() output"
    )
    assert tts_pos < ocr_pos, (
        "TTS (elapsed=3.0) must appear before OCR (elapsed=1.0) — sorted descending"
    )


# ---------------------------------------------------------------------------
# T-05 / AC-01 — construction in a non-TTY environment
# ---------------------------------------------------------------------------


def test_rich_reporter_does_not_require_tty_for_construction(monkeypatch) -> None:
    """RichProgressReporter() must construct without error in a non-TTY env (FT-325)."""
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    from tirvi.progress import RichProgressReporter  # noqa: PLC0415

    # Should not raise, even without a real terminal or rich installed.
    reporter = RichProgressReporter()
    assert reporter is not None


# ---------------------------------------------------------------------------
# T-05 / F49-ARCH-02 — graceful fallback when rich is not importable
# ---------------------------------------------------------------------------


def test_rich_reporter_graceful_fallback_without_rich(monkeypatch) -> None:
    """RichProgressReporter must work even if rich is not installed (F49-ARCH-02).

    We simulate rich being absent by temporarily hiding it from sys.modules,
    then force a re-import of tirvi.progress so the try/except ImportError
    guard fires on the module-level rich import.

    If this test is too fragile due to import caching, it is annotated with a
    TODO rather than removed — the behaviour must still be declared.

    TODO: if sys.modules manipulation proves flaky under parallel test
    collection, replace with a subprocess-based test that sets PYTHONPATH to
    exclude rich and imports tirvi.progress from scratch.
    """
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)

    # Evict rich and tirvi.progress from sys.modules so the re-import
    # exercises the try/except ImportError guard.
    rich_keys = [k for k in sys.modules if k == "rich" or k.startswith("rich.")]
    for key in rich_keys:
        monkeypatch.delitem(sys.modules, key, raising=False)
    monkeypatch.delitem(sys.modules, "tirvi.progress", raising=False)

    # Patch builtins.__import__ to raise ImportError for 'rich'.
    import builtins  # noqa: PLC0415
    original_import = builtins.__import__

    def patched_import(name, *args, **kwargs):  # type: ignore[return]
        if name == "rich" or name.startswith("rich."):
            raise ImportError(f"Simulated missing rich: {name}")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", patched_import)

    # Now re-import the module under the patched import system.
    import importlib  # noqa: PLC0415
    import tirvi.progress as _prog_mod  # noqa: PLC0415

    importlib.reload(_prog_mod)

    from tirvi.progress import RichProgressReporter  # noqa: PLC0415  # type: ignore[attr-defined]

    reporter = RichProgressReporter()
    # Should still be callable — falls back to plain-log path.
    reporter.stage_started("OCR")
    reporter.stage_completed("OCR", 1.0, "3 words")
    reporter.summarize()
