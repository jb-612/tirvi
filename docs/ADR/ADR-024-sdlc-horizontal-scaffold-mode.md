# ADR-024 — Horizontal-mode `@ddd-7l-scaffold` (lessons from the 14-feature POC prototype)

- **Status:** Proposed
- **Date:** 2026-04-30
- **Deciders:** jbellish
- **Related:** ADR-013 (biz/sw design split), ADR-016 (`@ddd-7l-scaffold` introduction), `.claude/skills/ddd-7l-scaffold/SKILL.md`, `.claude/skills/scaffold-review/SKILL.md`

## Context

ADR-016 introduced `@ddd-7l-scaffold` as a feature-scoped skill —
invoked once per feature, runs all 7 layers (L1 structural → L7
traceability), produces 4 review gates ending in a HITL gate before
TDD starts. Argument shape: `[phase/feature-id]`.

For the tirvi POC we ran the skill **vertically** on `N00/F03-adapter-
ports` (the cross-cutting ports + result-types + fakes feature), and
then explored a **horizontal** orchestration: run L1 across all 14 POC
features, then L2 across all 14, etc. The original L7 schema (one
`bounded_contexts:` block per feature, append-only) was designed with
horizontal ingest in mind; the user's note: *"this was my initial intent
when designing the L7 skill."*

The horizontal prototype landed across 4 commits (97b34a3 → b71351d) on
2026-04-30, scaffolding 14 features (F08, F10, F11, F14, F17, F18, F19,
F20, F22, F23, F26, F30, F35, F36) without modifying F03. Total:
36 Python source files, 8 JS/HTML/CSS files, 51 pytest + 4 Jest test
skeletons, 14 traceability.yaml `bounded_contexts:` appendages, 256
test stubs, ~50 named invariants, 23 `raise NotImplementedError`
bodies, 5 new bounded contexts (Extraction, HebrewNlp, Pronunciation,
SpeechSynthesis, AudioDelivery; Platform pre-existed from F03). All 5
verification checks (import, pytest collect, ruff, traceability append,
wire-contract chain) passed.

The prototype was driven by an out-of-skill orchestrator (the operating
agent acted as horizontal coordinator, applying the skill's *patterns*
but not invoking the skill itself per feature). This ADR captures what
that revealed about the skill's design assumptions and proposes a v2
mode.

## Decision

**Add a `--mode=horizontal --features <list>` mode to `@ddd-7l-scaffold`
v2** that runs each layer across the full feature list before advancing,
with `@scaffold-review` invoked once per layer-pair (Gate 1: L1+L2,
Gate 2: L3, Gate 3: L4+L5, Gate 4: L6+L7). The vertical mode (current
default) remains the right choice for boundary / foundational features;
horizontal mode is the right choice for batches of consumer features
that share contracts.

### Five lessons baked into the v2 design

#### L1 — Strict layer-at-a-time isn't strict; L1+L2+L3 cluster

Layers L1 (folders + empty modules), L2 (contracts/ports/types), and L3
(aggregates/VOs/events/errors) **share the same files**. A feature
folder's `__init__.py` typically imports its `value_objects.py`,
`errors.py`, and contract helpers; emitting an empty `__init__.py` at
L1 and then re-editing it at L2 and again at L3 produces three commits
that touch the same lines, with each later commit invalidating the
earlier review.

**v2 design.** Treat L1+L2+L3 as a *single structural pass* per feature
within the horizontal sweep. The first reviewer (Gate 1) sees all three
layers' output for all features in one diff. L4 (tests) and L5
(adapter / use-case impls) are genuinely independent and *do* benefit
from strict separation.

#### L2 — Cross-feature naming collisions need L0 detection

`tasks.md` files are written per feature, in isolation. Two features'
tasks can name the same `test_file:` path. F30's
`tests/unit/test_word_timing_provider.py` collided with F03's existing
file from the prior scaffold run; we resolved it by emitting F30's
per-task tests under distinct names and reusing F03's existing file
for the coordinator path, but only after the conflict surfaced
mid-scaffold.

**v2 design.** L0 (the layout sign-off step the prototype introduced
ad-hoc) becomes a formal first-class layer: it cross-references every
feature's `tasks.md` test paths and emits a unified test-plan table.
Conflicts surface at L0, not L4. The user signs off on the resolution
strategy (rename / share / split) before any file is written.

#### L3 — Non-Python features need a separate test-runner seam at L4

F35 and F36 are vanilla HTML/JS per ADR-023. Their `tasks.md` files
follow the project default and reference `tests/unit/test_*.py` — but
pytest can't host them. The prototype emitted JSDoc + `*.spec.js.skel`
files under `player/test/` and deferred toolchain config (Jest /
Vitest) to a pre-`/tdd` step.

**v2 design.** L0 reads a `language:` annotation per feature (or
infers it from the source-tree folder). At L4, the skill branches into
the language-appropriate test runner: pytest for Python, Jest / Vitest
for JS, `flutter test` for Dart, `go test` for Go. Each per-language
reference at `references/<lang>.md` already exists for L1–L7 code
shapes; v2 extends them with L4 test-skeleton shapes and a documented
toolchain pre-flight.

#### L4 — Skill is feature-scoped; horizontal mode must be first-class

Today's skill has `argument-hint: [phase/feature-id]`. Horizontal
orchestration was done outside the skill, with the operating agent
applying the skill's patterns. This works as a one-shot but creates
two problems: (a) the skill's HITL gates fire per feature, not per
layer, so the horizontal run accumulated 14 × 4 = 56 implicit gates
that the orchestrator collapsed manually; (b) the skill's Repository
Inspection step runs once per invocation and isn't reused across
features in the batch.

**v2 design.** Skill accepts either `<phase/feature-id>` (vertical, as
today) or `--mode=horizontal --features <comma-separated-list>`. In
horizontal mode, `@scaffold-review` runs *once per gate*, reviewing all
features at the current layer instead of one feature at all layers.
The HITL gate count drops from `4 × N` to `4`. Repository Inspection
runs once at the start and is shared across all features in the batch.

#### L5 — Pre-flight vendor list should auto-derive from design.md

`ruff.toml` was extended manually with banned-api entries for new
vendors (`pdf2image`, `pypdfium2`, `pytesseract`, `cv2`, `phonikud`)
when L1 began. Each feature's `design.md` already declares which
vendor SDKs it imports (in the "Interfaces" or "Vendor SDKs" tables).
Manual extension is mechanical and error-prone.

**v2 design.** L0 parses every feature's design.md, extracts the
declared vendor SDKs, and emits a pre-flight delta to `ruff.toml` (or
the equivalent per-language lint config). User signs off on the delta
along with the layout table; the skill applies it before L1 begins.

### Adoption path

1. Land this ADR (status: Proposed) so the design is recorded before
   the next horizontal run.
2. Treat the current 14-feature scaffold as the v2 prototype reference
   implementation. The 6 commits at `97b34a3..b71351d` are the worked
   example v2 should be able to reproduce mechanically.
3. v2 implementation:
   - Add `--mode=horizontal --features <list>` flag to
     `@ddd-7l-scaffold` SKILL.md
     (`.claude/skills/ddd-7l-scaffold/SKILL.md`).
   - Promote L0 (layout + BC routing + test-plan + vendor-list table)
     from ad-hoc step to a documented sub-stage with a sign-off gate.
   - Extend `@scaffold-review` SKILL.md to accept a
     `--horizontal-batch` flag and emit gate reports keyed by layer
     across the feature list.
   - Add L4 language-branch tables to `references/<lang>.md`.
4. Validate v2 by re-running it against the 14 POC features in a
   throwaway worktree and comparing output against the prototype
   commits. Bit-for-bit equivalence is not the goal; same review gate
   count, same file shape, same wire-contract pinning *is*.

### What stays the same

- F03 (boundary / foundational feature) was correctly scaffolded
  vertically. Vertical mode remains the default for features that:
  - define ports other features will consume,
  - or have no aggregates / VOs of their own,
  - or land before any other feature in their dependency cluster.
- Gate 4 (final HITL) remains in both modes; horizontal Gate 4 covers
  all features in the batch in one review.
- The 7 layers themselves don't change; only the orchestration around
  them does.

## Consequences

**Positive**
- One Gate 1 review across N features catches naming drift, layout
  inconsistency, and contract divergence at the cheapest possible
  stage.
- HITL gate count drops from `4 × N` to `4` for batches of consumer
  features.
- Cross-feature wire-contract pinning (e.g., the `{block_id}-{position}`
  mark format across F22→F23→F26→F30→F35) is *visible* to the Gate 1
  reviewer instead of inferred across 5 separate review reports.
- `bounded_contexts:` ontology emission is internally consistent across
  the batch because all features are in the reviewer's view at L7.
- L0 sign-off becomes a real first-class step instead of an
  out-of-skill prep.

**Negative**
- Gate 2 (deep, domain-model review) reviewing N features at once is
  cognitively heavier than reviewing one. v2 must structure the gate
  output by BC cluster to keep the load tractable.
- One bad feature stalls the layer's progress for the whole batch. v2
  needs an "advance with N − 1" affordance — Gate 2 can pass for the
  features it accepts and re-queue the rejected feature into the next
  layer's batch.
- Wall-clock latency for the first useful artefact (a commit you can
  share for partial review) is longer in horizontal mode. v2 should
  permit per-layer commits even mid-batch so reviewers don't wait for
  all 4 gates to land before seeing anything.
- Skill maintenance cost increases: two modes to keep working, two
  per-language reference variants (vertical and horizontal-batch
  versions of the L4 shapes).

## Alternatives considered

### A. Keep the skill feature-scoped; add an external orchestrator agent

Keep `@ddd-7l-scaffold` as-is. Add a new `@ddd-7l-batch-orchestrator`
skill that calls the existing skill 14 times across N features per
layer. **Rejected** because: (a) the operating agent already does this
ad-hoc and the prototype shows the skill's HITL gates collide with
batch orchestration; (b) per-feature Repository Inspection wastes
wall-clock; (c) the horizontal review-gate cadence (4 gates total, not
4 × N) requires the skill itself to know it's in batch mode.

### B. Restrict horizontal mode to "consumer feature" batches only

Allow horizontal mode only when the batch's features all *consume*
already-locked ports and don't *define* new ones. Foundational features
(like F03) stay vertical. **Provisionally accepted.** The prototype
batch is exactly this shape — F03 was scaffolded first, then the 14
consumers ran horizontally. v2 should formalize this as a precondition
check at L0: if any feature in the batch declares new ports, abort with
"split the batch — foundational features go vertical first."

### C. Strict layer-at-a-time across N features (no L1+L2+L3 clustering)

Run L1 (only folders + `__init__.py = []`) across all N, commit; then
L2 (only types) across all N, re-edit each `__init__.py` to add
exports, commit; then L3 (only aggregates / VOs) across all N, re-edit
imports, commit. **Rejected.** The prototype tried this approach and
ran into the file-sharing problem within the first cluster: the
N01 cluster's `__init__.py` files import their `value_objects.py` and
`errors.py`, so emitting empty stubs at L1 and re-editing at L2/L3
produces commits that overwrite each other's review surface.

The pragmatic compromise (L1+L2+L3 cluster, L4 strict, L5 strict, L6+L7
together) is what the prototype actually used and what v2 codifies.

### D. Keep the prototype as-is; don't refactor the skill

Treat the 14-feature horizontal scaffold as a one-off success and not
re-attempt it. **Rejected** because: (a) the design clearly works and
catches problems vertical mode wouldn't; (b) MVP will need the same
shape for the 40+ features beyond the POC; (c) the lessons captured
here decay if not committed to a skill artefact.

## References

- ADR-013 — SDLC harness biz / sw design split
- ADR-016 — `@ddd-7l-scaffold` introduction
- `.claude/skills/ddd-7l-scaffold/SKILL.md` — current skill canonical
- `.claude/skills/ddd-7l-scaffold/references/python.md` — Python L1–L7
  shapes
- `.claude/skills/scaffold-review/SKILL.md` — review skill canonical
- Prototype run: 6 commits `97b34a3..b71351d` on `werbeH`,
  `2026-04-30T22:00:53Z` to `2026-04-30T23:00:00Z`, scaffolding F03 +
  14 POC consumer features
