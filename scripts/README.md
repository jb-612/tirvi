# scripts/

## run_demo.py — POC pipeline runner + local server

Runs the full OCR → NLP → TTS pipeline on `docs/example/Economy.pdf` and
serves the result in the tirvi player.

### Port convention

| Mode | Default port | Command |
|------|-------------|---------|
| **Real** (Tesseract + Wavenet TTS) | **:8000** | `uv run scripts/run_demo.py` |
| **Stubs** (no ML deps, offline) | **:8765** | `uv run scripts/run_demo.py --stubs` |

Real and stub servers can run simultaneously without port conflicts.
Override with `--port <n>` if needed.

### Prerequisites (real mode)

- `GOOGLE_APPLICATION_CREDENTIALS` set (Cloud TTS)
- Tesseract + Hebrew tessdata installed (`brew install tesseract tesseract-lang`)
- YAP binary at `/tmp/yap/yap_bin` (optional — enables F17→F26 NLP; degraded mode otherwise)

### Stub mode

Uses hardcoded 6-word OCR output and a silent WAV instead of real models.
Useful for testing the player UI without any cloud credentials or ML setup.
Stub runs are served on `:8765` so they don't block a real run on `:8000`.

## cascade_demo.py — F48 correction cascade smoke test

Runs the Hebrew OCR correction cascade on a hardcoded sentence with known
ם/ס substitution errors and prints per-token stage/verdict/correction results.

```bash
uv run scripts/cascade_demo.py
```

Prereqs: Ollama running at `localhost:11434` with `llama3.1:8b` pulled.
