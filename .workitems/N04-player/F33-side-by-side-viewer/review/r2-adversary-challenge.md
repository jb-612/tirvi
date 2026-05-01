# Design Review R2 — Adversary Challenge — N04/F33 Side-by-Side Debug Viewer

**Feature:** N04/F33 — Side-by-side debug viewer (MVP deferred)
**Round:** R2 adversary challenge + synthesis
**Date:** 2026-05-01
**Status:** R2 complete — approved

---

## Adversary Position

The adversary challenges the R1 "approved as deferred" verdict and probes
whether the design is genuinely complete enough to survive the gap between
now and TDD scheduling.

---

### Challenge A — The folding of N05/F47 into F33 obscures N05's scope

**Challenge:** Design D-01 folds N05/F47 (feedback-capture) into F33.
This means N05's feature list has an implicit dependency on F33's TDD
being scheduled and completed. If N05 work begins before F33's TDD cycle,
the N05 task breakdown will reference F47 as a stub or a "completed by F33"
note, creating a traceability gap. No explicit N05 plan update is documented.

**Synthesis:** The adversary identifies a legitimate traceability risk. The
design states "F47's slot in N05 is repurposed for feedback
aggregation/export, not capture," which is a scope decision but not a
traceability update. The N05 workitem for F47 should carry a note pointing
to N04/F33. This is an inter-feature coordination item, not a design revision.
**Resolution:** Design author to add a note to N05/F47 workitem (when that
exists) referencing F33 as the upstream capture surface. No F33 design
revision needed.

---

### Challenge B — `renderArtifact` dispatch by extension will reach CC > 5

**Challenge:** `renderArtifact(node, panel)` dispatches on extension:
`.json`, `.txt`, `.png`, `.mp3`, `.ssml`. That is 5 branches in a single
function, giving CC = 6 before any null-checks or error handling. The
project CC ≤ 5 rule would block this at commit time.

**Synthesis:** The adversary is correct. `renderArtifact` must be split:
extract `chooseRenderer(ext) -> RendererFn` (a lookup table, CC = 1), and
each renderer is a separate function (CC ≤ 2 each). The rAF CC pattern from
F35 R2/Challenge-B is directly applicable here. This is a design-level
refactor note that should be added to `design.md §Approach DE-preview`:
"renderArtifact dispatches via renderer lookup table to keep each path CC ≤ 2."
**Resolution:** Add architecture note to §Approach for the preview.js
dispatcher. No structural redesign needed; table dispatch is a one-line
object literal in JS.

---

### Challenge C — C2 revision is insufficient: `output/` path traversal in feedback

**Challenge:** R1 C3 notes path traversal risk in the `do_POST` handler.
But the feedback file path is constructed from `markId` in the JSON body:
`output/<N>/feedback/<markId>-<ts>.json`. If `markId` contains `../` or
an absolute path, a naive implementation writes the feedback file outside
`output/`. R1 classified this as Low and proposed a TDD task note. The
adversary argues that since the design explicitly specifies the path pattern,
the design itself must constrain `markId` to be alphanumeric+hyphen only
(no path separators).

**Synthesis:** Accepted. The `feedback/<markId>-<ts>.json` schema in
`design.md §Interfaces` should add: "markId MUST match `^[a-zA-Z0-9_-]+$`;
the server rejects any body with a non-conforming markId with HTTP 400."
This is a design-level constraint that prevents a security regression in the
TDD implementation.
**Resolution:** Add markId character constraint to §Interfaces feedback
schema. Severity of C3 upgraded from Low to Medium retroactively.

---

## Net Revisions Required After R2

| Challenge | Finding ref | Action | Owner |
|-----------|-------------|--------|-------|
| A | — | Add N05/F47 cross-reference note when N05 workitem exists | Design author (deferred) |
| B | — | Add renderer-lookup-table note to §Approach preview.js | Design author |
| C | C3 | Add markId character constraint to §Interfaces feedback schema | Design author |

---

## R2 Synthesis Verdict

**Approved** with three targeted revisions (two in `design.md`; one
deferred inter-feature note). The design is genuinely complete for a
deferred MVP feature: all DEs are specified, interfaces are defined,
the artifact filesystem contract is documented, and the F35 dependency
(highlight state subscription for feedback.js) is correctly captured.

The `renderArtifact` CC concern (Challenge B) and the `markId` path
traversal constraint (Challenge C) are the two substantive additions that
make the design implementation-safe. Both are small additions to existing
prose.

F33 is cleared to proceed to TDD when N04/F35 and F36 are fully green and
`scripts/run_demo.py` is operational.
