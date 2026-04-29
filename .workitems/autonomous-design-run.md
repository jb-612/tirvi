# Autonomous Design Run — tirvi POC (14 features)

## How to launch

This prompt is designed for **claude.ai/code (web)**. The companion file
`.claude/settings.json` pre-authorises every operation this run needs, so
the web harness will not pause for permission prompts. Do NOT look for
`--dangerouslySkipPermissions` — that flag exists only in the local CLI.

**Pre-launch (one-time):**
1. Run `bash .workitems/autonomous-design-preflight.sh` — must print "READY".
2. Confirm the `.claude/settings.json` permission allowlist is committed.
3. Open the project in claude.ai/code.

**Launch:** paste this entire file as the first message. The session runs
unattended for ~3–6 hours and produces 14 git commits.

---

## Session contract

You are running in autonomous mode. Follow these rules for the entire run:

1. **Do NOT invoke any of these skills** — they contain HITL gates that
   will pause the run. Do the work directly using Read/Write/Edit/Bash:
   - `@sw-designpipeline`
   - `@design-pipeline`
   - `@design-review`
   - `@diagram-builder`
   - `@task-breakdown`
   - `/tdd`, `@tdd-go`, `@tdd-flutter`, `@tdd-workflow`
   - `@biz-functional-design`
   - `@meeting-room` agents (story-product, story-technical, story-domain)

2. **Do NOT spawn subagents.** No `Agent` tool, no `TeamCreate`. Sequential
   work only. Cloud sessions can stall under heavy subagent fan-out.

3. **Auto-decide every gate.** If you would normally ask the user, instead:
   - If the gate has options A/B/C, choose A.
   - If a check fails, fix inline; do not ask permission.
   - If you have spent 3 edit cycles on one file trying to satisfy a check,
     commit what you have and move on (see "Edit budget" below).

4. **Hooks are not active in this environment.** Do not wait for hook
   output. Do not run `bash .claude/hooks/*` manually.

5. **Do NOT push to remote.** Local commits only. The deny-list in
   `.claude/settings.json` blocks `git push`.

6. **Do NOT write production code** (`tirvi/**/*.py`, `*.html`, `*.js`),
   tests (`tests/**`), or anything outside `.workitems/`, `docs/ADR/`,
   `docs/diagrams/`, or the two writable ontology files.

7. **Do NOT modify** `ontology/business-domains.yaml`,
   `ontology/testing.yaml`, `docs/HLD.md`, `docs/PRD.md`, or any file
   under `.claude/skills/`, `.claude/hooks/`, `.claude/agents/`. The
   deny-list enforces this; do not try to override.

---

## Goal

Design 14 POC features end-to-end (biz migration → design.md →
traceability.yaml → ADRs → diagrams → tasks.md → ontology updates →
commit). One commit per feature. Stop after all 14.

**Repository:**
- Path: `/Users/jbellish/VSProjects/tirvi` (or current working dir)
- Branch: `werbeH`
- HLD: `docs/HLD.md` (sections 1–12 with sub-sections 3.1–3.4 and 5.1–5.4)
- POC plan: `.workitems/PLAN-POC.md`
- ADR index: `docs/ADR/INDEX.md` — current max is **ADR-015** → next free is **ADR-016**
- Already done: **N00/F03** at `145e820` — skip; do not re-run.

---

## Feature queue (process in this exact order)

| # | Feature | Workitem path | Biz corpus | feature_type | HLD refs |
|---|---|---|---|---|---|
| 1 | N01/F08 | `.workitems/N01-ingest-ocr/F08-tesseract-adapter/` | E02-F01 | domain | §4, §6 |
| 2 | N01/F10 | `.workitems/N01-ingest-ocr/F10-ocr-result-contract/` | E02-F03 | domain | §4 |
| 3 | N01/F11 | `.workitems/N01-ingest-ocr/F11-block-segmentation/` | E02-F04 | domain | §3.3 |
| 4 | N02/F14 | `.workitems/N02-hebrew-interpretation/F14-normalization-pass/` | E03-F01 | domain | §3.3, §5.1 |
| 5 | N02/F17 | `.workitems/N02-hebrew-interpretation/F17-dictabert-adapter/` | E04-F01 | domain | §4, §5.2 |
| 6 | N02/F18 | `.workitems/N02-hebrew-interpretation/F18-disambiguation/` | E04-F03 | domain | §4, §5.2 |
| 7 | N02/F19 | `.workitems/N02-hebrew-interpretation/F19-dicta-nakdan/` | E05-F01 | domain | §4, §5.2 |
| 8 | N02/F20 | `.workitems/N02-hebrew-interpretation/F20-phonikud-g2p/` | E05-F02 | domain | §4, §5.2 |
| 9 | N02/F22 | `.workitems/N02-hebrew-interpretation/F22-reading-plan-output/` | E06-F01 | domain | §5.2, §5.3 |
| 10 | N02/F23 | `.workitems/N02-hebrew-interpretation/F23-ssml-shaping/` | E06-F02 | domain | §5.3 |
| 11 | N03/F26 | `.workitems/N03-audio-sync/F26-google-wavenet-adapter/` | E07-F01 | domain | §4 |
| 12 | N03/F30 | `.workitems/N03-audio-sync/F30-word-timing-port/` | E08-F01 | domain | §4 |
| 13 | N04/F35 | `.workitems/N04-player/F35-word-sync-highlight/` | E09-F03 | ui | §3.1 (optional) |
| 14 | N04/F36 | `.workitems/N04-player/F36-accessibility-controls/` | E09-F04 | ui | §3.1 (optional) |

The HLD ref column above is **canonical** for this run — do not invent
new HLD section IDs. If the design needs concepts beyond these sections,
record them in the **HLD Deviations** table of `design.md`, do not invent.

---

## Locked interfaces (from N00/F03 — already committed)

Adapter features (F08, F17, F19, F20, F26, F30) MUST implement these
ports as defined. Consumer features (F10, F11, F14, F18, F22, F23, F35,
F36) consume these result types unchanged.

```
tirvi.ports.OCRBackend         → ocr_pdf(pdf_path: str) -> OCRResult
tirvi.ports.NLPBackend         → analyze(text: str) -> NLPResult
tirvi.ports.DiacritizerBackend → diacritize(text: str) -> DiacritizationResult
tirvi.ports.G2PBackend         → transliterate(text: str) -> G2PResult
tirvi.ports.TTSBackend         → synthesize(ssml: str, voice: str) -> TTSResult
tirvi.ports.WordTimingProvider → get_timings(tts_result, transcript: str) -> WordTimingResult

tirvi.results.OCRResult            → provider, text, blocks, confidence: float|None
tirvi.results.NLPResult            → provider, tokens, confidence: float|None
tirvi.results.DiacritizationResult → provider, text, confidence: float|None
tirvi.results.G2PResult            → provider, phonemes, confidence: float|None
tirvi.results.TTSResult            → provider, audio_bytes, word_marks, voice_meta
tirvi.results.WordTimingResult     → provider, timings, source: Literal["tts-marks","forced-alignment"]
```

Full spec: `.workitems/N00-foundation/F03-adapter-ports/design.md`.

---

## Per-feature process — INLINE (do not invoke skills)

Repeat for every feature in the queue. Each feature should take ~5–15 min.

### Step 1 — Read fresh state (start of every feature)

```
Read: docs/ADR/INDEX.md           # confirm next ADR number
Read: docs/HLD.md (the listed §X.Y sections only)
Read: .workitems/PLAN-POC.md      # POC scope constraints
Read: ontology/technical-implementation.yaml (last 50 lines for ID collision check)
Read: .workitems/N00-foundation/F03-adapter-ports/design.md (interface anchor)
```

### Step 2 — Biz corpus migration

```bash
scripts/migrate-feature.sh <N##/F##> <E##-F##>
```

If output contains "already migrated" or all 3 biz files exist with a
`DERIVED FROM` header, skip; otherwise re-run. Required outputs in the
workitem dir:
- `user_stories.md`
- `functional-test-plan.md`
- `behavioural-test-plan.md`

### Step 3 — Read biz corpus

Read the 3 biz files. Extract:
- All US-NN stories with their acceptance criteria
- All FT-NN functional test scenarios
- All BT-NN behavioural test scenarios
- All persona / business-object / bounded-context refs

### Step 4 — Write `design.md` (≤ 120 lines)

Frontmatter:
```yaml
---
feature_id: <N##/F##>
feature_type: <domain|ui|integration>
status: drafting
hld_refs:
  - HLD-§X.Y/<element>      # use the canonical refs from the queue table
prd_refs:
  - "PRD §<n> — <title>"    # from biz corpus user_stories.md "Source Basis"
adr_refs: [ADR-XXX]         # whatever new ADRs this feature needs
biz_corpus: true
biz_corpus_e_id: <E##-F##>
---
```

Body sections (in this order):
- `# Feature: <Title>`
- `## Overview` — 4–6 lines
- `## Dependencies` — Upstream features, ports consumed (from F03), external services, downstream consumers
- `## Interfaces` — public Python contracts (port impls or new modules); cite the locked ports from F03 for adapter features
- `## Approach` — numbered list, one bullet per Design Element (DE-NN)
- `## Design Elements` — bullet list `DE-NN: camelCaseName (ref: HLD-§X.Y/<el>)`
- `## Decisions` — `D-NN: short-name → ADR-NNN` for material decisions
- `## HLD Deviations` — table | Element | Deviation | Rationale |
- `## HLD Open Questions` — bullets; reference resolving ADR if any
- `## Risks` — table | Risk | Mitigation |
- `## Diagrams` — relative paths to your `.mmd` files
- `## Out of Scope` — bullets aligned with `PLAN-POC.md` POC scope

After writing, run:
```bash
wc -l .workitems/<path>/design.md
```
If > 120, compress Out of Scope and HLD Open Questions sections first.

### Step 5 — Author 0–2 ADRs (only when there's a material decision)

Trigger: any choice with ≥ 1 viable alternative that the implementer
shouldn't have to re-litigate. Mechanical defaults (e.g. "use the locked
F03 port") do not need an ADR.

Filename pattern:
```
docs/ADR/ADR-NNN-<bounded-context>-<short-name>.md
```

Use `ADR-016`, `ADR-017`, … sequentially across the run. Read
`docs/ADR/INDEX.md` at the start of each feature to get the current max.

Format (≤ 80 lines):
- **Status:** Proposed
- **Context:** problem framing + HLD ref
- **Decision:** one sentence
- **Consequences:** positive / negative bullets
- **Alternatives:** ≥ 1, with rejection reason
- **References:** HLD §, related ADRs, biz corpus story

After writing each ADR, append a row to `docs/ADR/INDEX.md` and a node
to `ontology/technical-implementation.yaml` under `adr_decisions:`.

### Step 6 — Write 1–2 mermaid diagrams

Path: `docs/diagrams/<N##>/<F##>/<diagram-name>.mmd`

For domain/integration features: at least one diagram showing the
component relationships (flowchart LR) or the request flow
(sequenceDiagram). For UI features: a flowchart of user actions.

**Mermaid constraints:** plain `flowchart LR/TD` or `sequenceDiagram`
only. NO `subgraph`, NO `classDef`. Quote labels with punctuation. Use
`\n` for line breaks. Never inline HTML.

### Step 7 — Run HLD ref validation (with the path fix)

```bash
HLD_PATH=docs/HLD.md .claude/scripts/validate-hld-refs.sh .workitems/<path>
```

Expected output: `All HLD references resolved.` If any FAIL line appears:
- Check that the offending HLD ref is from the canonical queue table
- If it is and the validator still fails, the HLD section heading is in
  an unexpected format — record the ref as a **HLD Deviation** in design.md
  and remove the failing ref from frontmatter `hld_refs`. Do not edit
  `docs/HLD.md`.

### Step 8 — Write `traceability.yaml`

Use the structure from `.workitems/N00-foundation/F03-adapter-ports/traceability.yaml`
as the template. Required top-level keys:

```yaml
feature_id: <N##/F##>
status: designed
hld_refs: [...]
prd_refs: [...]
adr_refs: [...]
biz_source:
  functional_test_plan_path: ./functional-test-plan.md
  behavioural_test_plan_path: ./behavioural-test-plan.md
  corpus_e_id: <E##-F##>
  imported_at: <ISO timestamp from migrate script log>
  source_sha: <git sha from biz file header>
ontology_refs: [persona:P##, bo:..., bc:..., co:..., asm:...]
acm_nodes:
  feature: feature:<N##/F##>
  specs: [spec:<N##/F##>/DE-NN, ...]
  user_stories: [story:<N##/F##>/US-NN, ...]
  acceptance_criteria: [criterion:<N##/F##>/US-NN/AC-NN, ...]
  tasks: []   # filled in Step 11
  diagrams: [diagram:<N##/F##>/<name>, ...]
acm_edges:
  # DE → HLD (TRACED_TO)
  # DE → ADR (INFLUENCED_BY) for any DE shaped by an ADR
  # Story → AC (HAS_CRITERION)
  # Story → Spec (VERIFIED_BY)
  # Feature → Spec (CONTAINS)
  # Spec → BoundedContext (BELONGS_TO)
  # Diagram → Spec (EXPLAINS)
de_to_hld: { DE-01: HLD-§X.Y/<el>, ... }
story_to_prd: { US-01: "PRD §...", ... }
ac_to_story: { US-01/AC-01: US-01, ... }    # composite-key format
task_to_de: {}                              # filled in Step 11
tests: []                                   # filled in Step 11
```

### Step 9 — Update `ontology/technical-implementation.yaml`

Append (do not overwrite) under the existing top-level keys. Read the
file's last 50 lines first to identify the highest used IDs. Common
appends per feature:

```yaml
modules:        # new packages or sub-packages
adapters:       # if this feature implements a port
classes:        # if this feature introduces value objects or services
adr_decisions:  # one node per ADR authored in Step 5
```

Each new node MUST have:
- `id:` — globally unique (no collision with existing IDs)
- `feature_refs: [<N##/F##>]`
- `status: designed`
- `bounded_context: <bc-name>`

If this feature consumes existing F03 nodes (e.g., F08 implements
PORT-01 OCRBackend), add a REALIZES edge to `ontology/dependencies.yaml`
instead of creating a duplicate node.

### Step 10 — Internal self-review (no subagents)

Run this checklist mentally and fix any failures:

- [ ] `wc -l design.md` ≤ 120
- [ ] HLD validation passed (Step 7)
- [ ] Every story AC in user_stories.md appears in traceability.yaml `ac_to_story`
- [ ] Every DE has a corresponding spec node
- [ ] Every adapter feature implements a locked F03 port (interface signature unchanged)
- [ ] Every consumer feature consumes locked F03 result types unchanged
- [ ] `provider`, `confidence: float | None` semantics preserved (biz S01)
- [ ] `WordTimingResult.source` typed as Literal where used
- [ ] No new vendor SDK referenced outside the adapter module
- [ ] POC scope constraints from PLAN-POC.md respected
- [ ] All ADR numbers sequential, no gaps, INDEX.md updated

If any item fails, fix and re-run. If you have already revised this
file 3 times, accept what you have and continue (see Edit budget).

### Step 11 — Write `tasks.md` (≤ 120 lines)

Decompose each DE into atomic tasks (≤ 2h each). Format follows
`.workitems/N00-foundation/F03-adapter-ports/tasks.md`:

```yaml
---
feature_id: <N##/F##>
status: ready
total_estimate_hours: <sum>
---

## T-NN: short-imperative-title
- design_element: DE-NN
- acceptance_criteria: [US-NN/AC-NN]
- ft_anchors: [FT-NN, ...]      # from functional-test-plan.md
- bt_anchors: [BT-NN, ...]      # from behavioural-test-plan.md
- estimate: Xh
- test_file: tests/unit/test_<topic>.py
- dependencies: [T-NN, ...]
- hints: <one-line implementation hint>

## Dependency DAG
T-01 → T-02
...
Critical path: T-NN → T-NN → T-NN (Xh)
```

Then update `traceability.yaml`:
- `acm_nodes.tasks: [task:<N##/F##>/T-NN, ...]`
- `acm_edges` — append `{from: task:<...>/T-NN, to: spec:<...>/DE-NN, type: IMPLEMENTED_BY}` for each task
- `task_to_de: { T-NN: DE-NN, ... }`
- `tests: [{ontology_id: task:<...>/T-NN, test_path: ..., status: pending}, ...]`

And append task nodes to `ontology/technical-implementation.yaml` under
the `tasks:` key (status: designed).

### Step 12 — Coverage check

```
- Every DE has ≥ 1 task
- Every AC maps to ≥ 1 task
- Every FT-NN appears in some task's ft_anchors
- Every BT-NN appears in some task's bt_anchors (or is anchored to "no production work")
- No task estimate > 2h
- Dependency DAG has no cycles
```

If anything fails, edit and re-run. Edit budget applies.

### Step 13 — Commit

```bash
git add \
  .workitems/<feature-path>/ \
  docs/ADR/ADR-0*.md \
  docs/ADR/INDEX.md \
  docs/diagrams/<N##>/<F##>/ \
  ontology/technical-implementation.yaml \
  ontology/dependencies.yaml

git commit -m "design(<N##/F##>): sw design pipeline complete — <feature-slug>

<2-3 line summary of interfaces, key decisions, ADRs authored>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

After commit, print: `COMMITTED <N##/F##> @ <sha>  Remaining: <N>` and
proceed to the next feature.

---

## POC scope constraints per feature

When writing design.md, respect these simplifications:

| Feature | POC scope |
|---|---|
| F08 | Single-page OCR; Tesseract `heb` tessdata_best; layout post-processor for column detect + RTL; no Document AI fallback |
| F10 | OCRResult structural contract (bbox, conf, lang_hint, blocks); F08 is the implementor |
| F11 | Minimum block segmentation for word-level bbox; heading/paragraph/question_stem only; no table/figure |
| F14 | Pass-through normalization + minimum OCR artifact repair; skip num2words unless trivially available |
| F17 | DictaBERT adapter only (`dicta-il/dictabert-large-joint`); prefix segmentation, morph, lemma, NER; no fallback |
| F18 | Disambiguation using DictaBERT confidence scores; no AlephBERT/YAP/HebPipe |
| F19 | Nakdan diacritization adapter; word-level; no multi-pass |
| F20 | Phonikud G2P; IPA + stress; no vocal-shva unless in Phonikud output |
| F22 | plan.json: tokens + lemma + pos + IPA hint + structural block type |
| F23 | SSML minimum: `<break>` between blocks, `<mark name="w_N">` per word; no answer-option emphasis |
| F26 | Wavenet `he-IL-Wavenet-D`; SSML v1beta1 with marks; single voice; no caching |
| F30 | WordTimingProvider with TTS-marks adapter ONLY; NO forced-alignment (WhisperX deferred to MVP) |
| F35 | Vanilla HTML + Web Audio API; single-page; moving word marker box; no framework |
| F36 | 4 controls only: play / pause / continue / reset; no speed/font/contrast |

---

## Edit budget

If you have edited the same file 3 times trying to satisfy a check
(line-count, HLD validation, coverage), do this and move on:

1. Note the failing check in the commit message footer:
   `KNOWN-DEBT: <feature> - <check> failed after 3 attempts: <one-line summary>`
2. Commit what you have.
3. Move to the next feature.

This prevents an infinite loop on edge cases that the agent cannot
resolve autonomously. The user reviews KNOWN-DEBT entries the next morning.

---

## Recovery (if the session is interrupted mid-run)

Paste this prompt again. The agent should:

1. Run:
   ```bash
   git log --oneline -30 | grep "design(N"
   ```
   This lists every feature already committed.

2. Identify the first feature in the queue NOT in that list.

3. For that feature, verify:
   ```bash
   ls .workitems/<path>/    # should contain user_stories.md, functional-test-plan.md, behavioural-test-plan.md
   head -2 .workitems/<path>/user_stories.md   # should start with `<!-- DERIVED FROM ...`
   ```
   If any of the 3 biz files is missing or lacks the `DERIVED FROM`
   header, re-run `scripts/migrate-feature.sh <N##/F##> <E##-F##>` first.

4. If the workitem has partial uncommitted work (design.md exists but no
   commit), `git status --short` will show it. Either complete the
   feature or `git restore` the partial files and start that feature
   from Step 1.

5. Resume from Step 1 of the per-feature process for that feature.

Do NOT re-run features that already have a commit.

---

## Done condition

When `git log --oneline | grep "design(N" | wc -l` returns 15 (the
existing F03 commit + 14 new), print:

```
═══════════════════════════════════════════
POC DESIGN COMPLETE — 14/14 features
═══════════════════════════════════════════
Phase A:  N01/F08, N01/F10, N01/F11
Phase B:  N02/F14, N02/F17, N02/F18, N02/F19, N02/F20
Phase C:  N02/F22, N02/F23
Phase D:  N03/F26, N03/F30
Phase E:  N04/F35, N04/F36

ADRs authored: ADR-016 .. ADR-0XX (count: N)
KNOWN-DEBT entries: <list, if any>
Total commits this session: 14

Next step: /tdd on N01/F08 T-01

Session complete. Do NOT proceed to TDD.
═══════════════════════════════════════════
```

Then stop. Do not start TDD. Do not write production code.
