# Cloud-run brief — Phase A + B TDD (autonomous)

**Run mode:** unattended cloud (claude.ai/code), single long session.
**Expected duration:** 12–30 h agent time, distributed across one or
more cloud sessions at your discretion.
**Date:** 2026-04-30.
**Operator:** jbellish.
**Repo:** `https://github.com/jb-612/tirvi` branch `werbeH`.
**Branch policy:** commit on `werbeH`; **do NOT push** — report commit
SHAs at end so the operator can review and push manually.

---

## Goal

Turn the Phase A + Phase B **demo-critical** test stubs from
skip-marked into pytest-green by filling `NotImplementedError` bodies
in `tirvi/adapters/tesseract/`, `tirvi/blocks/`, `tirvi/normalize/`,
`tirvi/nlp/`, `tirvi/adapters/dictabert/`, `tirvi/adapters/nakdan/`,
`tirvi/adapters/phonikud/`. End state: `pytest -k "not skip"` runs
green for ~140 tests across the two phases; `ruff check tirvi/ tests/`
passes; cyclomatic complexity ≤ 5 per function; mypy strict on
`tirvi/` passes.

The structural scaffold (folders, ports, result types, errors,
skip-marked tests, `bounded_contexts:` traceability) is already in
place — see commits `97b34a3..b71351d`. Your job is the **business
logic only**.

---

## Scope filter — read first

Before any code is written, **read these two docs** and treat them as
authoritative:

1. `.workitems/POC-CRITICAL-PATH.md` — per-feature task allowlist.
   Skip every task marked `❌ DEFER` or `⚠️ MAYBE`. Only land
   `✅` tasks.
2. `.workitems/PLAN-POC.md` — overall POC scope; the four "DEFER"
   rows in the MAYBE table at the bottom of CRITICAL-PATH have all
   been resolved (all four defer). Confirm by reading.

After resolving deferrals, your **target task set** is approximately:

- **Phase A (ingest):** F08 T-01, T-02, T-03; F11 T-01, T-03, T-04.
  (F08 T-04/05/06 deferred. F10 deferred entirely. F11 T-02 already
  scaffold-covered.) ~6 tasks.
- **Phase B (NLP):** F14 T-01, T-02, T-05; F17 T-01, T-02, T-03, T-04,
  T-06; F18 T-01, T-02, T-03; F19 T-01, T-03, T-04, T-05, T-06; F20
  T-01, T-02, T-05, T-06. ~22 tasks.

Total: ~28 demo-critical tasks. Each task ~30–60 min of agent work.

---

## Pre-flight (cloud env, run once at start)

### System dependencies

```bash
# OCR
which tesseract || apt-get install -y tesseract-ocr tesseract-ocr-heb \
  || brew install tesseract tesseract-lang
tesseract --list-langs | grep -q heb || echo "FATAL: Hebrew tessdata missing"

# Poppler (pdf2image dep)
which pdftoppm || apt-get install -y poppler-utils || brew install poppler
```

### Python dependencies

Add a `requirements-dev.txt` if absent and `pip install` the union
of:

- `pytest`, `ruff`, `mypy` (already required by `pyproject.toml`)
- `pdf2image`, `pypdfium2`, `pytesseract`, `opencv-python`, `Pillow` (F08)
- `transformers`, `torch`, `huggingface_hub`, `tokenizers` (F17 + F19)
- `phonikud` (F20 — pip-installable; if install fails, F20-T-01's
  fallback path is exercised, which is acceptable)
- `pyyaml` (already used elsewhere in the repo)
- `unicodedata2` (NFC/NFD normalization for F19 — Python stdlib
  `unicodedata` is fine; only install `unicodedata2` if Python
  version < 3.11)

**Vendor-import boundary check (DE-06).** After installing, run
`ruff check tirvi/` once. Must pass — if a vendor name leaks into
`tirvi/` core (anything outside `tirvi/adapters/**`), the run is
broken. Stop and report.

### TDD marker setup

The marker file at `/tmp/ba-tdd-markers/<sha1(pwd)>` gates which
agent role can edit which files. For autonomous Python TDD on this
repo:

```bash
mkdir -p /tmp/ba-tdd-markers
shasum=$(echo -n "$PWD" | shasum | cut -c1-40)
echo "python" > "/tmp/ba-tdd-markers/$shasum"
```

This unlocks both `tests/unit/**/*.py` (test-writer) and
`tirvi/**/*.py` (code-writer) for the cloud agent. The
`enforce-tdd-separation.sh` hook will allow both kinds of edits.

### PLAN.md / PLAN-POC.md status update

Mark F03 as scaffold-complete so `require-workitem.sh` doesn't block
F08 production-source writes:

```bash
# .workitems/PLAN.md line 15 — F03 row
sed -i.bak 's|- \[ \] F03-adapter-ports|- [BUILT] F03-adapter-ports|' .workitems/PLAN.md
rm .workitems/PLAN.md.bak

# .workitems/PLAN-POC.md — F03 row
sed -i.bak 's|- \[ \] F03-adapter-ports|- [BUILT] F03-adapter-ports|' .workitems/PLAN-POC.md
rm .workitems/PLAN-POC.md.bak
```

Commit this once at the start: `chore(plan): mark F03 [BUILT] —
scaffold output is the POC deliverable per POC-CRITICAL-PATH.md`.

---

## Per-task TDD procedure (do NOT invoke the `/tdd` skill)

The `/tdd` skill has interactive HITL prompts that hang an
autonomous run. Inline the TDD steps below; run sequentially per task.

For each task in scope (in dependency order — see tasks.md DAGs;
roughly F08 T-01→T-02→T-03, then F11 T-01→T-03→T-04, then F14 T-01→
T-02→T-05, then F17 T-01→T-02→T-03→T-04→T-06, then F18 T-01→T-02→
T-03, then F19 T-01→T-03→T-04→T-05→T-06, then F20 T-01→T-02→T-05→
T-06):

### 1. Read inputs (4 files per task)

- `.workitems/<phase>/<feature>/tasks.md` — find the task block
  matching the T-ID; read `design_element`, `acceptance_criteria`,
  `ft_anchors`, `bt_anchors`, `dependencies`, `hints`, `test_file`.
- `.workitems/<phase>/<feature>/design.md` — read the section for
  the matching DE.
- The test file (e.g., `tests/unit/test_pdf_rasterizer.py`) — already
  exists with skip-marked test class.
- The production module path implied by the task hint (e.g.,
  `tirvi/adapters/tesseract/adapter.py`).

### 2. RED — write failing tests (bundled mode)

Convert all `@pytest.mark.skip` markers in the task's test file to
real failing tests. Each test:
- Drop the `@pytest.mark.skip` decorator.
- Replace the `pass` body with real assertions per the GWT comments
  already in the body.
- Use **inline fixtures** (small, hand-rolled — no @test-mock-registry
  dependency, no JSON fixture files unless the task hint says so).
- Run: `pytest <test_file> -v`. **Every test in the file must fail
  with a clear assertion error or `NotImplementedError`** — not pass,
  not error-on-collection.

If the test file imports symbols that don't exist yet
(`from tirvi.normalize.passthrough import normalize_text`),
**create empty stub modules** in `tirvi/<feature>/` first so imports
resolve; the function bodies remain `raise NotImplementedError`.

### 3. GREEN — write minimum production code

In the production file (the path the task hint references), implement
the minimum logic that makes every test in the file pass.

Constraints:
- **Cyclomatic complexity ≤ 5 per function.** Extract helpers
  liberally. Use `radon cc tirvi/ -nc -s` to verify before commit.
- **No business logic that isn't required by a test.** YAGNI.
- **No vendor SDK imports outside `tirvi/adapters/<vendor>/`** — the
  ruff banned-api rule will catch you; respect it.
- **Type-annotate everything.** mypy strict is enabled on `tirvi/`
  via `pyproject.toml`. Run `mypy tirvi/` to verify.
- For model-loading tasks (F17 T-01, F19 T-01, F20 T-01), use the
  module-level LRU cache pattern documented in `references/python.md`
  and the design.md DE-01 sections. Real model downloads are
  acceptable in the cloud env.
- For the F19 T-05 NFC→NFD normalization, use `unicodedata.normalize`.
- For F18 T-02 (morph dict whitelist), use a frozen set of allowed
  keys defined inline at module level.

Run `pytest <test_file> -v` — all tests must pass.

### 4. REFACTOR — clean up while green

Optional but encouraged. Constraints:
- All tests still pass.
- Cyclomatic complexity ≤ 5 per function.
- Ruff clean (`ruff check tirvi/ tests/`).
- mypy clean (`mypy tirvi/`).
- No new behavior — only structure / naming / extraction.

If refactor breaks tests, revert to the green commit; refactor is
optional.

### 5. Commit

One commit per task:

```
tdd: <feature_id>/<T-ID> green — <one-line summary>

Test file: <path>
Production code: <path(s)>
Acceptance criteria: <AC IDs>
FT/BT anchors: <anchor IDs>

<2-4 line summary of the implementation choice; reference any
ADR / DE / invariant the body satisfies>

Co-Authored-By: Claude <noreply@anthropic.com>
```

Example:

```
tdd: N01/F08/T-01 green — PDF page rasterizer at 300dpi

Test file: tests/unit/test_pdf_rasterizer.py
Production code: tirvi/adapters/tesseract/rasterizer.py (new)
Acceptance criteria: US-01/AC-01
FT-anchors: FT-061

Uses pdf2image.convert_from_bytes at dpi=300; one PIL Image per page;
raises tirvi.errors.AdapterError on corrupt input (PDFInfoNotInstalled
re-raised, otherwise wrapped). Implementation < 30 LOC; CC = 3.

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Quality gates after each task

Run all four after the task's commit:

```bash
pytest tests/unit/<task_test_file>.py -v          # 1. task tests green
pytest --collect-only tests/ 2>&1 | tail -3       # 2. no collection errors elsewhere
ruff check tirvi/ tests/                          # 3. lint clean
mypy tirvi/                                       # 4. types clean
radon cc tirvi/ -nc -s | grep -E "^\s+[A-Z] [^A-D]" | head  # 5. CC ≤ 5
```

If any of (2), (3), (4), (5) fails: fix in a follow-up commit
*before* moving to the next task. (1) failing means the task isn't
green and the commit was premature.

---

## Stop conditions — halt and report

Stop and write a report (don't retry blindly) if any of these:

1. A task's tests can't be made to pass after **two** GREEN attempts.
2. Cyclomatic complexity exceeds 5 in three different functions in a
   single task and you can't reduce it.
3. mypy strict throws errors that require disabling `strict = true`
   to pass.
4. A vendor SDK leaks into `tirvi/` core and the boundary can't be
   restored cleanly.
5. A pre-flight install fails and a workaround would compromise the
   feature (e.g., transformers fails to install — F17/F19 are blocked
   without it; report rather than fake it).
6. Phase A's first feature (F08) consumes more than **6 hours** of
   agent time — the brief or the design has a flaw; surface it.

When you stop, write a short report at
`.workitems/cloud-runs/2026-04-30-phase-A-B-status.md` containing:

- Tasks completed (with commit SHAs).
- Tasks blocked (with the specific failure).
- Recommended next action.

---

## Sign-off / verification checklist (end of run)

Before reporting completion, all of these must be true:

- [ ] `pytest tests/unit/ -v` — all in-scope tests green; deferred
      tests still skip-marked (count: ~140 green, ~115 skipped).
- [ ] `ruff check tirvi/ tests/` passes.
- [ ] `mypy tirvi/` passes.
- [ ] `radon cc tirvi/ -nc -s` reports no function above CC 5.
- [ ] No file under `tirvi/` (excluding `tirvi/adapters/**`) imports
      a vendor SDK (`google.cloud`, `transformers`, `torch`,
      `huggingface_hub`, `pdf2image`, `pypdfium2`, `pytesseract`,
      `cv2`, `phonikud`).
- [ ] Every commit on the run-branch matches the
      `tdd: <feature>/<T-ID> green` format (exception: the initial
      `chore(plan): mark F03 [BUILT]` commit and any PLAN.md status
      flips between phases).
- [ ] **No `git push`** has been issued. Operator pushes manually.

Then write a final report at
`.workitems/cloud-runs/2026-04-30-phase-A-B-completed.md` listing:

- Per-task: T-ID → commit SHA.
- Total agent wall-clock time.
- Anything surprising (e.g., F19 T-02 NLP-context-tilt was
  surprisingly easy / hard — note it for the v2 ADR).
- Suggested Phase C (F22 + F23) starting point.

---

## Resume / restart

If the cloud session is interrupted mid-run:

1. Re-read this brief.
2. Re-read `POC-CRITICAL-PATH.md`.
3. `git log --oneline werbeH | grep "^[a-f0-9]\{7,\} tdd:" | head` —
   identify the last completed task.
4. Resume from the next task in the dependency-ordered list.
5. The TDD marker file at `/tmp/ba-tdd-markers/<sha>` is per-cwd; if
   the worktree was cloned to a new path, re-create the marker.

---

## Out of scope for this run

Do NOT touch any of these — they're separate work tracks:

- F03 fakes (T-06, T-07) — deferred per POC-CRITICAL-PATH.md
- F03 contract harness (T-08) — deferred
- F03 vendor-import lint test (T-09) — already enforced by ruff config
- F22, F23 (Phase C) — operator does these interactively
- F26, F30 (Phase D) — F26 needs Google Cloud auth; operator runs
- F35, F36 (Phase E) — JS/HTML; operator runs in browser
- The skill v2 implementation per ADR-024 — separate ADR, separate work
- @test-mock-registry — deferred for POC
- Integration tests / functional tests / E2E tests — deferred

---

## Reference (do not duplicate; just read)

- `CLAUDE.md` — project conventions
- `.claude/rules/tdd-rules.md` — TDD discipline (CC ≤ 5, role
  separation; the marker file approach above is the autonomous
  variant)
- `.claude/rules/workflow.md` — 8-step trunk; this brief is Step 3
  (TDD Build) for two phases
- `.claude/skills/ddd-7l-scaffold/references/python.md` — Python L5
  shapes (use case shells, fakes, fixture builders)
- `pyproject.toml` — mypy / pytest / ruff config
- `ruff.toml` — vendor banned-api list (DE-06)
- `docs/HLD.md` — architectural baseline
- `docs/ADR/ADR-014` — result-schema versioning (contract-test-only)
- `docs/ADR/ADR-015` — WordTimingProvider fallback (deferred)
- `docs/ADR/ADR-016..023` — per-feature decisions
