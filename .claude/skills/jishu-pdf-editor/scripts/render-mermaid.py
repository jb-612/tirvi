#!/usr/bin/env python3
"""
render-mermaid.py — pre-render Mermaid blocks in a Markdown file to SVG,
rewriting the markdown to reference the rendered images.

Usage:
  python render-mermaid.py --in source.md --out build/source-with-svg.md \
                            --asset-dir build/diagrams/

Imports / depends on:
  - mermaid-cli (`mmdc`) on PATH — install with `npm i -g @mermaid-js/mermaid-cli`

This is a thin wrapper. The full version lives in user/scripts/render-mermaid.py
and is symlinked here for the Jishu PDF Editor skill.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

MERMAID_BLOCK = re.compile(
    r"```mermaid\s*\n(?P<body>.*?)\n```",
    re.DOTALL,
)


def render_one(mmd_text: str, out_svg: Path) -> None:
    out_svg.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_svg.with_suffix(".mmd")
    tmp.write_text(mmd_text, encoding="utf-8")
    try:
        subprocess.run(
            ["mmdc", "-i", str(tmp), "-o", str(out_svg),
             "-b", "transparent", "-t", "neutral"],
            check=True,
        )
    finally:
        tmp.unlink(missing_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True, type=Path)
    ap.add_argument("--out", dest="dst", required=True, type=Path)
    ap.add_argument("--asset-dir", dest="assets", required=True, type=Path)
    args = ap.parse_args()

    text = args.src.read_text(encoding="utf-8")
    counter = 0

    def replace(match: re.Match) -> str:
        nonlocal counter
        counter += 1
        body = match.group("body")
        out = args.assets / f"diagram-{counter:02d}.svg"
        render_one(body, out)
        rel = out.relative_to(args.dst.parent) if args.dst.parent in out.parents else out
        return f'<img class="diagram" src="{rel}" alt="Diagram {counter}" />'

    rewritten = MERMAID_BLOCK.sub(replace, text)
    args.dst.parent.mkdir(parents=True, exist_ok=True)
    args.dst.write_text(rewritten, encoding="utf-8")
    print(f"Rendered {counter} diagram(s) → {args.assets}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
