#!/usr/bin/env python3
"""Migrate historic tasks.md files to the standard done-marker format.

Per `.claude/rules/task-format.md`, every `## T-NN:` task header MUST be
followed by a single `- [ ] **T-NN done**` line (or `- [x] **T-NN done**`
if the task is already implemented).

This script walks every `tasks.md` under `.workitems/`, ensures each task
header has a marker, and infers initial check-state from the
`tdd:` git commit log:

    tdd: NXX/FYY/T-NN green — <desc>

is parsed as: feature `NXX/FYY`, task `T-NN`, state checked.

Idempotent: re-running detects existing markers, updates check-state
only if the git log says the task is now done.

Usage:
    python3 .claude/scripts/migrate-task-format.py [--dry-run]
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKITEMS = ROOT / ".workitems"

TASK_HEADER = re.compile(r"^(## T-(\d+))(:.*)$", re.MULTILINE)
EXISTING_MARKER = re.compile(r"^- \[([ x])\] \*\*T-(\d+) done\*\*\s*$", re.MULTILINE)
TDD_COMMIT = re.compile(
    r"tdd:\s*([A-Z]\d+/F\d+[a-zA-Z0-9-]*)/((?:T-\d+\s*\+?\s*)+)(green|red|refactor)",
    re.IGNORECASE,
)


def collect_done_tasks() -> dict[tuple[str, str], bool]:
    """Return {(feature_path_prefix, task_id): True} for every TDD-green commit.

    feature_path_prefix is e.g. "N03/F26" — matches the path
    .workitems/N03-*/F26-*/tasks.md directory naming.

    Handles compound commits like ``tdd: N03/F26/T-02 + T-06 green`` —
    each task ID in the subject becomes its own entry.
    """
    result = subprocess.run(
        ["git", "log", "--all", "--oneline", "--grep=tdd:"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    done: dict[tuple[str, str], bool] = {}
    for line in result.stdout.splitlines():
        m = TDD_COMMIT.search(line)
        if not m:
            continue
        feat = m.group(1).upper()
        task_block = m.group(2)
        state = m.group(3).lower()
        if state != "green":
            continue
        for tid in re.findall(r"T-(\d+)", task_block):
            done[(feat, f"T-{tid}")] = True
    return done


def feature_key(tasks_md: Path) -> str:
    """Map .workitems/N03-audio-sync/F26-google-wavenet-adapter/tasks.md → 'N03/F26'."""
    parts = tasks_md.relative_to(WORKITEMS).parts
    if len(parts) < 2:
        return ""
    n = parts[0].split("-")[0].upper()  # "N03"
    f = parts[1].split("-")[0].upper()  # "F26"
    return f"{n}/{f}"


def migrate_file(path: Path, done_tasks: dict, dry_run: bool) -> tuple[int, int]:
    """Return (markers_added, markers_state_changed)."""
    text = path.read_text()
    feat = feature_key(path)
    added = 0
    changed = 0

    # Pre-collect existing markers per task id
    existing: dict[str, str] = {}
    for m in EXISTING_MARKER.finditer(text):
        state = m.group(1)
        tid = f"T-{m.group(2)}"
        existing[tid] = state

    # Walk task headers, decide insertion or state-flip
    new_lines = []
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        m = re.match(r"^(## T-(\d+))(:.*)$", line.rstrip("\n"))
        if not m:
            i += 1
            continue
        tid_short = m.group(2)
        tid = f"T-{tid_short}"
        # Determine intended state: checked if (feat, tid) in done_tasks
        intended = "x" if done_tasks.get((feat, tid)) else " "
        # Look ahead a few lines to see if a marker already exists for this task
        marker_idx = None
        for j in range(i + 1, min(i + 6, len(lines))):
            mm = re.match(r"^- \[([ x])\] \*\*T-(\d+) done\*\*\s*$", lines[j].rstrip("\n"))
            if mm and mm.group(2) == tid_short:
                marker_idx = j
                break
            # Stop if we hit another task header
            if re.match(r"^## T-\d+:", lines[j]):
                break
        if marker_idx is None:
            # Insert marker right after the header (skip a blank line if present)
            insert_at = i + 1
            # Need to preserve the blank line that usually follows the header
            if insert_at < len(lines) and lines[insert_at].strip() == "":
                # Insert *after* the blank line, then a blank line
                new_lines.append(lines[insert_at])
                new_lines.append(f"- [{intended}] **{tid} done**\n")
                new_lines.append("\n")
                i = insert_at + 1
                added += 1
                continue
            else:
                # No blank line; insert blank + marker + blank
                new_lines.append("\n")
                new_lines.append(f"- [{intended}] **{tid} done**\n")
                new_lines.append("\n")
                i += 1
                added += 1
                continue
        else:
            # Marker exists — update state if mismatched
            current = existing.get(tid, " ")
            if current != intended:
                # We don't actually need to rewrite here because we walk lines
                # one by one — but we'll let the post-pass replacement handle it
                changed += 1
            i += 1
            continue
        i += 1

    new_text = "".join(new_lines)

    # Post-pass: ensure all existing markers reflect intended state per git log
    def _replace(m):
        tid = f"T-{m.group(2)}"
        intended = "x" if done_tasks.get((feat, tid)) else " "
        return f"- [{intended}] **{tid} done**"

    new_text = EXISTING_MARKER.sub(_replace, new_text)

    if new_text == text:
        return (0, 0)

    if not dry_run:
        path.write_text(new_text)
    return (added, changed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    done_tasks = collect_done_tasks()
    print(f"git log: {len(done_tasks)} (feature, task) tuples marked green")
    sample = list(done_tasks.items())[:5]
    for (feat, tid), _ in sample:
        print(f"  green: {feat} {tid}")

    files = sorted(p for p in WORKITEMS.rglob("tasks.md") if "meeting-room" not in p.parts)
    print(f"\nfound {len(files)} tasks.md files")

    total_added = 0
    total_changed = 0
    files_touched = 0
    for f in files:
        a, c = migrate_file(f, done_tasks, args.dry_run)
        if a or c:
            files_touched += 1
            rel = f.relative_to(ROOT)
            print(f"  + {rel}: +{a} markers, {c} state-flips")
        total_added += a
        total_changed += c

    print(f"\nsummary: {files_touched} files touched, +{total_added} markers added, {total_changed} state-flips")
    if args.dry_run:
        print("(dry-run — no files written)")


if __name__ == "__main__":
    main()
