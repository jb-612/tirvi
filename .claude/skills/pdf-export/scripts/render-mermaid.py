#!/usr/bin/env python3
"""Pre-render Mermaid code blocks to inline SVG images for PDF generation."""

import base64
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def render_mermaid_to_svg(mermaid_code: str, index: int, out_dir: Path) -> str:
    """Render a Mermaid diagram to SVG and return the file path."""
    mmd_file = out_dir / f"diagram-{index}.mmd"
    svg_file = out_dir / f"diagram-{index}.svg"

    mmd_file.write_text(mermaid_code, encoding="utf-8")

    result = subprocess.run(
        [
            "mmdc",
            "-i",
            str(mmd_file),
            "-o",
            str(svg_file),
            "-t",
            "default",
            "-b",
            "transparent",
            "--quiet",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode != 0:
        print(f"WARNING: mmdc failed for diagram {index}: {result.stderr}", file=sys.stderr)
        return ""

    if not svg_file.exists():
        print(f"WARNING: SVG not created for diagram {index}", file=sys.stderr)
        return ""

    return str(svg_file)


def svg_to_data_uri(svg_path: str) -> str:
    """Convert SVG file to a base64 data URI."""
    svg_content = Path(svg_path).read_bytes()
    b64 = base64.b64encode(svg_content).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def process_markdown(input_path: str, output_path: str) -> None:
    """Replace mermaid code blocks with rendered SVG images."""
    content = Path(input_path).read_text(encoding="utf-8")

    pattern = re.compile(r"```mermaid\n(.*?)```", re.DOTALL)
    matches = list(pattern.finditer(content))

    if not matches:
        print("No mermaid blocks found.", file=sys.stderr)
        Path(output_path).write_text(content, encoding="utf-8")
        return

    print(f"Found {len(matches)} Mermaid diagrams to render...", file=sys.stderr)

    with tempfile.TemporaryDirectory(prefix="mermaid-") as tmp_dir:
        tmp_path = Path(tmp_dir)
        replacements = []

        for i, match in enumerate(matches):
            mermaid_code = match.group(1).strip()
            print(f"  Rendering diagram {i + 1}/{len(matches)}...", file=sys.stderr)

            svg_path = render_mermaid_to_svg(mermaid_code, i, tmp_path)

            if svg_path:
                data_uri = svg_to_data_uri(svg_path)
                img_tag = (
                    f'<div style="text-align:center; margin:1.5em 0; page-break-inside:avoid;">'
                    f'<img src="{data_uri}" style="max-width:100%; max-height:500px; height:auto; object-fit:contain;" />'
                    f"</div>"
                )
                replacements.append((match.start(), match.end(), img_tag))
            else:
                replacements.append((match.start(), match.end(), match.group(0)))

        for start, end, replacement in reversed(replacements):
            content = content[:start] + replacement + content[end:]

    Path(output_path).write_text(content, encoding="utf-8")

    success = sum(1 for _, _, r in replacements if r.startswith("<div"))
    print(f"Done: {success}/{len(matches)} diagrams rendered successfully.", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.md> <output.md>", file=sys.stderr)
        sys.exit(1)

    process_markdown(sys.argv[1], sys.argv[2])
