# ADR-032 — Reviewer Notes: localStorage over Server-Side POST

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-05-01 |
| Feature | N04/F50 Review UI |
| Deciders | Design (N04/F50) |
| Supersedes | — |
| Superseded by | — |

---

## Context

The F50 Review UI adds per-tab reviewer notes to the artifact inspector sidebar.
Notes must survive page reloads and version switches within a single browser session.

The POC server (`run_demo.py`) uses Python's `http.server.SimpleHTTPRequestHandler`
extended with a minimal `_NoCacheHandler` subclass. This handler serves static files
and (after F50 T-09) a single read-only `GET /api/versions` JSON endpoint. It has
no POST handler, no request body parsing, and no write path.

---

## Decision

Reviewer notes are persisted to the **browser's localStorage** using the key
`tirvi:notes:{sha}:{tab}`, where `{sha}` is the 7-character commit hash of the
active draft version and `{tab}` is one of `ocr | nlp | nakdan | voice`.

Notes are:
- Written on every `input` event (auto-save, no manual save button).
- Read and restored by `loadInspector(pageJson, audioJson)` on page load and on
  every `switchVersion(sha)` call.
- Cleared (textarea left empty) when no key exists for a sha+tab combination,
  preventing stale data from a prior version bleeding into a new one.
- Exported on demand via an "Export notes" button that assembles all four tab
  notes for the active sha into `{ sha, tabs: { ocr, nlp, nakdan, voice } }` and
  triggers a Blob download as `notes-{sha}.json`.

---

## Rationale

| Option | Assessment |
|--------|------------|
| **localStorage** | Zero server changes; persists across reloads within same origin; export button provides portability; CC = 0 additional server logic. **Selected.** |
| Server-side POST to run_demo.py | Requires non-trivial `BaseHTTPRequestHandler` refactor: body parsing, MIME handling, file-write path, CORS. Out of scope for a POC review tool. |
| sessionStorage | Does not survive tab close or page reload — insufficient durability for reviewer sessions that may span hours. |
| IndexedDB | Heavier API for text blobs that fit comfortably in localStorage values (<5 KB per tab). Overcomplicated. |

localStorage is appropriate here because:
1. The POC runs locally (same origin, single user) — no cross-origin or multi-user conflicts.
2. Notes per version are bounded in size (free-text annotation, not binary data).
3. Export button satisfies the portability requirement without server involvement.

---

## Consequences

**Positive:**
- No server changes beyond the read-only `GET /api/versions` endpoint (T-09).
- Notes survive browser restarts on most platforms (localStorage is persistent, not session-scoped).
- Implementation is entirely in `inspector.js` — no new Python code for notes.

**Negative / Risks:**
- Notes are browser-local: switching browsers or clearing browser data loses notes not yet exported.
- localStorage is not encrypted at rest — acceptable for a local POC review tool; not acceptable for production deployment with sensitive exam content.
- `localStorage` capacity is typically 5–10 MB per origin. At typical annotation lengths this is not a constraint, but a very large number of versions with verbose notes could approach it.

---

## Revisit Trigger

When `run_demo.py` is replaced by or extended with a proper HTTP API (FastAPI or similar),
implement a `POST /api/notes/{sha}` endpoint and migrate localStorage notes to server-side
persistence on first export. Update this ADR to "Superseded" at that point.
