"""Render a cot.json model into Mermaid + summary views.

Reads the JSON produced by `parse_design_pipeline.py` and emits six files
to a target directory: a markdown summary, a meeting-room convergence
flowchart, the R1→R2→R3 review DAG, per-finding severity timelines, a
graveyard of overruled claims, and a finding↔citation traceability web.

Mermaid `flowchart` is used throughout (not `mindmap` — it lacks edge
labels, subgraphs, and classDef styling). Every public function targets
cyclomatic complexity ≤ 5.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# --- shared helpers ---------------------------------------------------------

CLASSDEF_LINES = (
    "classDef crit fill:#ffcccc,stroke:#900,color:#000",
    "classDef high fill:#ffe0b3,stroke:#a60,color:#000",
    "classDef med fill:#ffffcc,stroke:#aa0,color:#000",
    "classDef low fill:#eeeeee,stroke:#666,color:#000",
    "classDef unknown fill:#f8f8f8,stroke:#999,color:#000",
)

_LABEL_TRANS = str.maketrans({'"': "'", "\n": " ", "[": "(", "]": ")", "`": ""})


def _escape_label(text: str) -> str:
    return text.translate(_LABEL_TRANS)[:90]


def _node_id(prefix: str, identifier: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9]", "_", identifier or "x")
    return f"{prefix}_{safe}"


_SEVERITY_TOKENS = (
    ("CRITICAL", "crit"),
    ("HIGH", "high"),
    ("MEDIUM", "med"),
    ("MED", "med"),
    ("LOW", "low"),
)


def _severity_class(severity: str) -> str:
    upper = (severity or "").upper()
    for token, klass in _SEVERITY_TOKENS:
        if token in upper:
            return klass
    return "unknown"


def _classdef_block() -> list[str]:
    return [f"    {line}" for line in CLASSDEF_LINES]


# --- review DAG --------------------------------------------------------------


def _finding_node_id(finding: dict[str, Any]) -> str:
    reviewer = (finding.get("reviewer") or "x").split("-")[0]
    return _node_id(f"R1_{reviewer}", finding.get("id", "F"))


def _finding_label(finding: dict[str, Any]) -> str:
    fid = finding.get("id", "?")
    title = _escape_label(finding.get("title", ""))
    sev = finding.get("severity", "?")
    return f"{fid} — {title}<br/>{sev}"


def _round1_subgraph(findings: list[dict[str, Any]]) -> list[str]:
    lines = ['    subgraph R1["R1 — Specialists"]']
    for finding in findings:
        nid = _finding_node_id(finding)
        klass = _severity_class(finding.get("severity", ""))
        lines.append(f'      {nid}["{_finding_label(finding)}"]:::{klass}')
    lines.append("    end")
    return lines


def _round2_subgraph(challenges: list[dict[str, Any]]) -> list[str]:
    lines = ['    subgraph R2["R2 — Adversary"]']
    for challenge in challenges:
        nid = _node_id("R2", challenge.get("id", "C"))
        title = _escape_label(challenge.get("title", ""))
        verdict = challenge.get("verdict", "?")
        lines.append(f'      {nid}["{challenge.get("id", "?")} — {title}<br/>{verdict}"]')
    lines.append("    end")
    return lines


def _round3_subgraph(outcomes: list[dict[str, Any]]) -> list[str]:
    lines = ['    subgraph R3["R3 — Final"]']
    for i, row in enumerate(outcomes):
        nid = f"R3_{i}"
        finding = _escape_label(row.get("finding", "?"))
        klass = _severity_class(row.get("final", ""))
        lines.append(f'      {nid}["{finding}<br/>FINAL: {row.get("final", "?")}"]:::{klass}')
    lines.append("    end")
    return lines


def render_review_dag(cot: dict[str, Any]) -> str:
    lines = ["flowchart LR", *_classdef_block(), ""]
    lines.extend(_round1_subgraph(cot.get("findings", [])))
    lines.append("")
    lines.extend(_round2_subgraph(cot.get("challenges", [])))
    lines.append("")
    lines.extend(_round3_subgraph(cot.get("rebuttal_outcomes", [])))
    return "\n".join(lines) + "\n"


# --- meeting room ------------------------------------------------------------


def _role_drafts(key: str, mr: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for draft in mr.get("drafts", []):
        if key in (draft.get("reviewer") or ""):
            out.append(f'      draft_{key}_{len(out)}["draft"]')
    return out


def _role_votes(key: str, mr: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for vote in mr.get("votes", []):
        if key in (vote.get("reviewer") or ""):
            out.append(f'      vote_{key}_{len(out)}["vote: {vote.get("vote", "?")}"]')
    return out


def _role_subgraph(role: str, mr: dict[str, Any]) -> list[str]:
    key = role.lower()
    lines = [f'    subgraph {key}["{role}"]']
    lines.extend(_role_drafts(key, mr))
    lines.extend(_role_votes(key, mr))
    lines.append("    end")
    return lines


def _synthesis_block(mr: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    if mr.get("remarks"):
        lines.append(f'    remarks["{len(mr["remarks"])} remarks"]')
    if mr.get("synthesis"):
        lines.append('    synth["synthesis"]')
    return lines


def render_meeting_room(cot: dict[str, Any]) -> str:
    mr = cot.get("meeting_room", {})
    lines = ["flowchart LR", ""]
    for role in ("Product", "Technical", "Domain"):
        lines.extend(_role_subgraph(role, mr))
        lines.append("")
    lines.extend(_synthesis_block(mr))
    return "\n".join(lines) + "\n"


# --- finding timelines -------------------------------------------------------


def _timeline_for_row(index: int, row: dict[str, Any]) -> list[str]:
    finding = _escape_label(row.get("finding", "?"))
    n1 = f"t{index}_r1"
    n2 = f"t{index}_adv"
    n3 = f"t{index}_fin"
    return [
        f'    {n1}["R1: {row.get("r1", "?")}<br/>{finding}"]',
        f'    {n2}["R2: {row.get("adversary", "?")}"]',
        f'    {n3}["R3: {row.get("final", "?")}"]:::{_severity_class(row.get("final", ""))}',
        f"    {n1} --> {n2} --> {n3}",
    ]


def render_finding_timelines(cot: dict[str, Any]) -> str:
    lines = ["flowchart LR", *_classdef_block(), ""]
    rows = cot.get("rebuttal_outcomes", [])
    if not rows:
        lines.append('    empty["no rebuttal-table entries"]')
    for index, row in enumerate(rows):
        lines.extend(_timeline_for_row(index, row))
        lines.append("")
    return "\n".join(lines) + "\n"


# --- graveyard ---------------------------------------------------------------


def _grave_node(index: int, grave: dict[str, Any]) -> str:
    claim = _escape_label(grave.get("claim", "?"))
    verification = _escape_label(grave.get("verification", "")) or "no source cited"
    return f'    g{index}["{claim}<br/>X — killed by {verification}"]:::killed'


def render_graveyard(cot: dict[str, Any]) -> str:
    lines = [
        "flowchart TD",
        "    classDef killed fill:#eee,stroke:#900,stroke-dasharray:5 5,color:#000",
        "",
    ]
    graves = cot.get("graveyard", [])
    if not graves:
        lines.append('    empty["no overruled claims found"]')
    for index, grave in enumerate(graves):
        lines.append(_grave_node(index, grave))
    return "\n".join(lines) + "\n"


# --- traceability ------------------------------------------------------------


def _collect_traceability_edges(findings: list[dict[str, Any]]) -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []
    for finding in findings:
        fid = finding.get("id", "?")
        for cite in finding.get("citations", []):
            edges.append((fid, cite))
    return edges


def _ensure_node(node_id: str, label: str, seen: set[str]) -> list[str]:
    if node_id in seen:
        return []
    seen.add(node_id)
    return [f'    {node_id}["{_escape_label(label)}"]']


def _render_edges(edges: list[tuple[str, str]]) -> list[str]:
    lines: list[str] = []
    seen: set[str] = set()
    for src, dst in edges:
        sn = _node_id("f", src)
        dn = _node_id("c", dst)
        lines.extend(_ensure_node(sn, src, seen))
        lines.extend(_ensure_node(dn, dst, seen))
        lines.append(f"    {sn} --> {dn}")
    return lines


def render_traceability(cot: dict[str, Any]) -> str:
    lines = ["flowchart LR", ""]
    edges = _collect_traceability_edges(cot.get("findings", []))
    if not edges:
        lines.append('    empty["no citations"]')
    lines.extend(_render_edges(edges))
    return "\n".join(lines) + "\n"


# --- summary ----------------------------------------------------------------


def _count_severities(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for finding in findings:
        sev = finding.get("severity", "UNKNOWN")
        counts[sev] = counts.get(sev, 0) + 1
    return counts


def _summary_views_links() -> list[str]:
    return [
        "",
        "## Views",
        "",
        "- [Meeting room](01-meeting-room.mmd)",
        "- [Review DAG](02-review-dag.mmd)",
        "- [Finding timelines](03-finding-timelines.mmd)",
        "- [Graveyard](04-graveyard.mmd)",
        "- [Traceability](05-traceability.mmd)",
        "- [Ideation mindmap](06-ideation-mindmap.mmd)  — native Mermaid mindmap, "
        "bubbles from root → stages → categories → leaves",
    ]


def _summary_header(cot: dict[str, Any]) -> list[str]:
    return [
        f"# Design Chain-of-Thought — {cot.get('feature_id', 'unknown')}",
        "",
        f"- Files scanned: {cot.get('files_scanned', 0)}",
        f"- Findings: {len(cot.get('findings', []))}",
        f"- Challenges: {len(cot.get('challenges', []))}",
        f"- Rebuttal outcomes: {len(cot.get('rebuttal_outcomes', []))}",
        f"- Graveyard entries: {len(cot.get('graveyard', []))}",
        "",
        "## Severity distribution",
        "",
        "| Severity | Count |",
        "|---|---|",
    ]


def render_summary(cot: dict[str, Any]) -> str:
    lines = _summary_header(cot)
    counts = _count_severities(cot.get("findings", []))
    for sev in ("CRITICAL", "HIGH", "MED", "LOW", "UNKNOWN"):
        lines.append(f"| {sev} | {counts.get(sev, 0)} |")
    lines.extend(_summary_views_links())
    return "\n".join(lines) + "\n"


# --- ideation mindmap (native Mermaid mindmap syntax) ----------------------
#
# Mermaid `mindmap` gives real bubble-and-line ideation trees: hierarchy by
# indentation, rounded shape via `(text)`. It does NOT support classDef or
# edge labels — that's the tradeoff vs. the flowchart views above. Here we
# use it to show how the discussion matured from meeting-room ideas down
# into specialist findings, adversary challenges, final synthesis, and the
# graveyard of overruled claims.

_MINDMAP_STRIP = re.compile(r'[()\[\]{}"`]+')


def _mindmap_safe(text: str) -> str:
    return _MINDMAP_STRIP.sub("", text or "")[:60].strip()


def _mindmap_meeting_room(mr: dict[str, Any]) -> list[str]:
    lines = ["    Meeting Room"]
    for draft in mr.get("drafts", []):
        reviewer = _mindmap_safe(draft.get("reviewer", "?"))
        lines.append(f"      ({reviewer} draft)")
    for vote in mr.get("votes", []):
        reviewer = _mindmap_safe(vote.get("reviewer", "?"))
        verdict = _mindmap_safe(vote.get("vote", "?"))
        lines.append(f"      ({reviewer}: {verdict})")
    return lines


def _group_findings_by_reviewer(
    findings: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    by_reviewer: dict[str, list[dict[str, Any]]] = {}
    for finding in findings:
        key = (finding.get("reviewer") or "unknown").split("-")[0]
        by_reviewer.setdefault(key, []).append(finding)
    return by_reviewer


def _mindmap_reviewer_group(reviewer: str, findings: list[dict[str, Any]]) -> list[str]:
    lines = [f"      {reviewer}"]
    for finding in findings:
        fid = finding.get("id", "F?")
        sev = finding.get("severity", "?")
        title = _mindmap_safe(finding.get("title", "?"))
        lines.append(f"        ({fid} {sev}: {title})")
    return lines


def _mindmap_r1(findings: list[dict[str, Any]]) -> list[str]:
    lines = ["    R1 Specialists"]
    grouped = _group_findings_by_reviewer(findings)
    for reviewer, group in grouped.items():
        lines.extend(_mindmap_reviewer_group(reviewer, group))
    return lines


def _mindmap_r2(challenges: list[dict[str, Any]]) -> list[str]:
    lines = ["    R2 Adversary"]
    for challenge in challenges:
        cid = challenge.get("id", "C?")
        verdict = challenge.get("verdict", "?")
        title = _mindmap_safe(challenge.get("title", "?"))
        lines.append(f"      ({cid} {verdict}: {title})")
    return lines


def _mindmap_r3(outcomes: list[dict[str, Any]]) -> list[str]:
    lines = ["    R3 Synthesis"]
    for row in outcomes:
        finding = _mindmap_safe(row.get("finding", "?"))
        final = _mindmap_safe(row.get("final", "?"))
        lines.append(f"      (FINAL {final}: {finding})")
    return lines


def _mindmap_graveyard_branch(graves: list[dict[str, Any]]) -> list[str]:
    lines = ["    Graveyard overruled"]
    for grave in graves:
        claim = _mindmap_safe(grave.get("claim", "?"))
        verification = _mindmap_safe(grave.get("verification", ""))
        label = f"X {claim}" if not verification else f"X {claim} by {verification}"
        lines.append(f"      ({label})")
    return lines


def render_ideation_mindmap(cot: dict[str, Any]) -> str:
    """Native Mermaid mindmap: root bubble → branches → leaves."""
    root = _mindmap_safe(cot.get("feature_id", "feature"))
    lines = ["mindmap", f"  root(({root}))"]
    lines.extend(_mindmap_meeting_room(cot.get("meeting_room", {})))
    lines.extend(_mindmap_r1(cot.get("findings", [])))
    lines.extend(_mindmap_r2(cot.get("challenges", [])))
    lines.extend(_mindmap_r3(cot.get("rebuttal_outcomes", [])))
    lines.extend(_mindmap_graveyard_branch(cot.get("graveyard", [])))
    return "\n".join(lines) + "\n"


# --- dispatcher --------------------------------------------------------------


def render_all(cot: dict[str, Any], out_dir: Path) -> dict[str, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    plan = (
        ("00-summary.md", "summary", render_summary),
        ("01-meeting-room.mmd", "meeting_room", render_meeting_room),
        ("02-review-dag.mmd", "review_dag", render_review_dag),
        ("03-finding-timelines.mmd", "finding_timelines", render_finding_timelines),
        ("04-graveyard.mmd", "graveyard", render_graveyard),
        ("05-traceability.mmd", "traceability", render_traceability),
        ("06-ideation-mindmap.mmd", "ideation_mindmap", render_ideation_mindmap),
    )
    paths: dict[str, Path] = {}
    for filename, key, fn in plan:
        target = out_dir / filename
        target.write_text(fn(cot), encoding="utf-8")
        paths[key] = target
    return paths


# --- CLI --------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Render cot.json into Mermaid views")
    ap.add_argument("cot_json", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    cot = json.loads(args.cot_json.read_text(encoding="utf-8"))
    render_all(cot, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
