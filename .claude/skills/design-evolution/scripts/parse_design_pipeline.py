"""Parse a design-pipeline workitem into a chain-of-thought JSON model.

Walks `meeting-room/`, `review-r{1,2,3}/` and root `design.md` of a feature
workitem directory, then emits a structured `cot.json` capturing findings,
challenges, votes, rebuttal-table outcomes, and a graveyard of overruled
claims. Designed for `@design-evolution` skill consumption.

Every public function targets cyclomatic complexity ≤ 5.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

# --- regex tables ------------------------------------------------------------

FINDING_RE = re.compile(r"^### (?:Finding\s+|F)(\d+):\s*(.+?)$", re.MULTILINE)
CHALLENGE_RE = re.compile(r"^### Challenge\s+(\d+):\s*(.+?)$", re.MULTILINE)
VERDICT_RE = re.compile(r"\*\*Verdict\*\*:\s*\**\s*([A-Z]+)", re.IGNORECASE)
REBUTTAL_HEADER_RE = re.compile(
    r"\|\s*Finding\s*\|\s*R1\s*\|\s*Adversary\s*\|\s*Rebuttal\s*\|\s*Final\s*\|",
    re.IGNORECASE,
)
SEVERITY_PATTERNS = (
    re.compile(r"\[(CRITICAL|HIGH|MEDIUM|MED|LOW)\]", re.IGNORECASE),
    re.compile(r"\*\*Severity\*\*:\s*(\w+)", re.IGNORECASE),
    re.compile(r"\bSeverity:\s*(\w+)", re.IGNORECASE),
)
CITE_PATTERNS = (
    re.compile(r"\bDE-\d+\b"),
    re.compile(r"\bAC-\d+\b"),
    re.compile(r"\bUS-\d+\b"),
    re.compile(r"\bT\d{1,2}[a-z]?\b"),
    re.compile(r"\bF\d{1,2}\b"),
    re.compile(r"`([\w./-]+\.(?:dart|py|go|md|yaml|yml)(?::\d+)?)`"),
)
WRONG_MARKERS = (
    "factually wrong",
    "verified:",
    "actually makes",
    "is wrong",
    "is incorrect",
)


# --- frontmatter -------------------------------------------------------------


def parse_frontmatter(text: str) -> dict[str, Any]:
    """Extract YAML frontmatter block. Returns {} if absent or invalid."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[4:end]
    loaded = yaml.safe_load(block)
    return loaded if isinstance(loaded, dict) else {}


# --- severity ---------------------------------------------------------------


def _normalise_severity(raw: str) -> str:
    token = raw.upper()
    if token.startswith("CRIT"):
        return "CRITICAL"
    if token.startswith("HIGH"):
        return "HIGH"
    if token.startswith("MED"):
        return "MED"
    if token.startswith("LOW"):
        return "LOW"
    return "UNKNOWN"


def _detect_severity(heading: str, body: str) -> str:
    for pattern in SEVERITY_PATTERNS:
        for blob in (heading, body):
            match = pattern.search(blob)
            if match:
                return _normalise_severity(match.group(1))
    return "UNKNOWN"


# --- citations ---------------------------------------------------------------


def extract_citations(text: str) -> list[str]:
    """Find DE-/AC-/US-/T/F ids and `file.ext:line` refs in prose."""
    found: list[str] = []
    for pattern in CITE_PATTERNS:
        for match in pattern.finditer(text):
            hit = match.group(1) if match.lastindex else match.group(0)
            if hit not in found:
                found.append(hit)
    return found


# --- findings & challenges ---------------------------------------------------


def _slice_bodies(text: str, matches: list[re.Match[str]]) -> list[str]:
    bodies = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        bodies.append(text[start:end])
    return bodies


def extract_findings(text: str) -> list[dict[str, Any]]:
    """Extract `### Finding N:` or `### FN:` sections."""
    matches = list(FINDING_RE.finditer(text))
    bodies = _slice_bodies(text, matches)
    return [_make_finding(m, b) for m, b in zip(matches, bodies, strict=True)]


def _make_finding(match: re.Match[str], body: str) -> dict[str, Any]:
    title = match.group(2).strip()
    return {
        "id": f"F{match.group(1)}",
        "title": title,
        "severity": _detect_severity(title, body),
        "body": body.strip(),
        "citations": extract_citations(body),
    }


def _extract_verdict(body: str) -> str:
    match = VERDICT_RE.search(body)
    return match.group(1).upper() if match else "UNKNOWN"


def extract_challenges(text: str) -> list[dict[str, Any]]:
    """Extract `### Challenge N:` sections (R2 adversary files)."""
    matches = list(CHALLENGE_RE.finditer(text))
    bodies = _slice_bodies(text, matches)
    return [_make_challenge(m, b) for m, b in zip(matches, bodies, strict=True)]


def _make_challenge(match: re.Match[str], body: str) -> dict[str, Any]:
    return {
        "id": f"C{match.group(1)}",
        "title": match.group(2).strip(),
        "verdict": _extract_verdict(body),
        "body": body.strip(),
        "citations": extract_citations(body),
    }


# --- rebuttal table ---------------------------------------------------------


def parse_rebuttal_table(text: str) -> list[dict[str, str]]:
    """Parse the R3 synthesis `| Finding | R1 | Adversary | Rebuttal | Final |` table."""
    header = REBUTTAL_HEADER_RE.search(text)
    if not header:
        return []
    lines = text[header.end() :].lstrip().splitlines()
    if lines and lines[0].lstrip().startswith("|---"):
        lines = lines[1:]
    return _parse_table_rows(lines)


def _parse_table_rows(lines: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            break
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) >= 5:
            rows.append(_row_from_cells(cells))
    return rows


def _row_from_cells(cells: list[str]) -> dict[str, str]:
    return {
        "finding": cells[0],
        "r1": cells[1],
        "adversary": cells[2],
        "rebuttal": cells[3],
        "final": cells[4],
    }


# --- graveyard --------------------------------------------------------------


def detect_graveyard_claims(findings: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Surface findings that overrule a prior design claim."""
    graves: list[dict[str, str]] = []
    for finding in findings:
        body_lower = finding.get("body", "").lower()
        if any(marker in body_lower for marker in WRONG_MARKERS):
            graves.append(_build_grave_entry(finding))
    return graves


def _build_grave_entry(finding: dict[str, Any]) -> dict[str, str]:
    citations = finding.get("citations", [])
    verification = next(
        (c for c in citations if any(ext in c for ext in (".dart", ".py", ".go"))),
        "",
    )
    return {
        "claim": finding.get("title", ""),
        "verification": verification,
        "source_finding": finding.get("id", ""),
        "source_file": finding.get("source_file", ""),
    }


# --- workitem walk ----------------------------------------------------------


def _tag_findings(
    findings: list[dict[str, Any]],
    source: str,
    fm: dict[str, Any],
    round_num: int,
) -> list[dict[str, Any]]:
    for finding in findings:
        finding["source_file"] = source
        finding["round"] = round_num
        finding["reviewer"] = fm.get("reviewer", "")
    return findings


def _tag_challenges(
    challenges: list[dict[str, Any]],
    source: str,
    fm: dict[str, Any],
) -> list[dict[str, Any]]:
    for challenge in challenges:
        challenge["source_file"] = source
        challenge["round"] = 2
        challenge["reviewer"] = fm.get("reviewer", "adversary")
    return challenges


def _collect_meeting_room(
    relative: str,
    fm: dict[str, Any],
    meeting_room: dict[str, list[dict[str, Any]]],
) -> None:
    name = relative.split("/", 1)[1] if "/" in relative else relative
    record: dict[str, Any] = {
        "file": relative,
        "reviewer": fm.get("draft_author") or fm.get("reviewer", ""),
    }
    bucket = _meeting_room_bucket(name)
    if bucket == "votes":
        record["vote"] = fm.get("vote", "")
    if bucket:
        meeting_room[bucket].append(record)


def _meeting_room_bucket(name: str) -> str:
    if name.startswith("draft-"):
        return "drafts"
    if name.startswith("remarks-"):
        return "remarks"
    if name.startswith("vote-"):
        return "votes"
    if name.startswith("synthesis"):
        return "synthesis"
    return ""


def _dispatch_file(
    relative: str,
    text: str,
    fm: dict[str, Any],
    accum: dict[str, Any],
) -> None:
    if relative.startswith("meeting-room/"):
        _collect_meeting_room(relative, fm, accum["meeting_room"])
        return
    if relative.startswith("review-r1/"):
        accum["findings"].extend(_tag_findings(extract_findings(text), relative, fm, 1))
        return
    if relative.startswith("review-r2/"):
        accum["challenges"].extend(_tag_challenges(extract_challenges(text), relative, fm))
        return
    if relative.startswith("review-r3/"):
        accum["rebuttal_outcomes"].extend(parse_rebuttal_table(text))


def _feature_id(workitem_dir: Path) -> str:
    design = workitem_dir / "design.md"
    if not design.exists():
        return workitem_dir.name
    fm = parse_frontmatter(design.read_text(encoding="utf-8", errors="replace"))
    return str(fm["id"]) if "id" in fm else workitem_dir.name


def _empty_accumulator() -> dict[str, Any]:
    return {
        "meeting_room": {"drafts": [], "remarks": [], "votes": [], "synthesis": []},
        "findings": [],
        "challenges": [],
        "rebuttal_outcomes": [],
    }


def parse_workitem(workitem_dir: Path) -> dict[str, Any]:
    """Top-level entry point: walk a workitem directory, return cot dict."""
    workitem_dir = Path(workitem_dir)
    accum = _empty_accumulator()
    files_scanned = 0
    for md_file in sorted(workitem_dir.rglob("*.md")):
        files_scanned += 1
        text = md_file.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)
        relative = md_file.relative_to(workitem_dir).as_posix()
        _dispatch_file(relative, text, fm, accum)
    accum["graveyard"] = detect_graveyard_claims(accum["findings"])
    accum["feature_id"] = _feature_id(workitem_dir)
    accum["files_scanned"] = files_scanned
    return accum


# --- CLI --------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Parse a design-pipeline workitem into cot.json")
    ap.add_argument("workitem_dir", type=Path)
    args = ap.parse_args(argv)
    cot = parse_workitem(args.workitem_dir)
    json.dump(cot, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
