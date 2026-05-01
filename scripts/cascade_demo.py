#!/usr/bin/env python
"""F48 cascade smoke demo — runs the real correction cascade on a hardcoded
sentence with known ם/ס OCR errors, using llama3.1:8b via Ollama.

Usage:
    uv run scripts/cascade_demo.py

Prereqs: Ollama running at localhost:11434 with llama3.1:8b pulled.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Sentence with deliberate ם→ס OCR substitution errors
SENTENCE_WITH_ERRORS = "אנשיס רביס בעולס חושביס שלוס הוא מקוס טוב"
# Expected: אנשים רבים בעולם חושבים שלום הוא מקום טוב

def main() -> None:
    print("F48 Hebrew Correction Cascade — live demo")
    print("=" * 50)
    print(f"Input:    {SENTENCE_WITH_ERRORS}")
    print()

    from tirvi.pipeline import _build_poc_correction_cascade
    from tirvi.correction.value_objects import CascadeMode, SentenceContext
    import hashlib

    print("Initialising cascade (health probe → Ollama check) ...")
    try:
        service, mode = _build_poc_correction_cascade()
    except Exception as exc:
        print(f"ERROR wiring cascade: {exc}")
        sys.exit(1)
    print(f"Cascade mode: {mode.name}")
    print()

    tokens = SENTENCE_WITH_ERRORS.split()
    sentence_hash = hashlib.sha256(SENTENCE_WITH_ERRORS.encode()).hexdigest()[:16]
    sentences = [
        CascadeMode  # placeholder; we pass sentence context below
    ]

    from tirvi.correction.value_objects import SentenceContext
    ctx_list = [
        SentenceContext(
            sentence_text=SENTENCE_WITH_ERRORS,
            sentence_hash=sentence_hash,
            page_index=0,
            token_index=i,
        )
        for i in range(len(tokens))
    ]

    print(f"Processing {len(tokens)} tokens ...")
    result = service.run_page(
        tokens, sentences=ctx_list, page_index=0, sha="demo", mode=mode
    )

    print()
    print("Token-level results:")
    print(f"{'Original':<16} {'Corrected':<16} {'Stage':<16} {'Verdict'}")
    print("-" * 70)
    for orig, corr, dec in zip(result.original_tokens, result.corrected_tokens, result.stage_decisions):
        changed = " ← FIXED" if orig != corr else ""
        print(f"{orig:<16} {corr:<16} {dec.stage:<16} {dec.verdict}{changed}")

    print()
    print(f"Output:   {' '.join(result.corrected_tokens)}")
    print()
    if result.applied:
        print(f"Corrections applied: {len(result.applied)}")
        for ev in result.applied:
            print(f"  {ev.original!r} → {ev.corrected!r}")
    else:
        print("No corrections applied (tokens may all be known words).")

if __name__ == "__main__":
    main()
