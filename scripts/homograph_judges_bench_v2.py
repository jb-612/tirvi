#!/usr/bin/env python
"""Homograph bench v2 — adds possessive-mappiq rule + Gemma v2 prompt.

Pipeline per sentence:
    DictaBERT NLP
        → Nakdan (REST)
        → possessive-mappiq rule (deterministic; fires on possessor patterns)
        → Gemma 4 31B with linguistic harness prompt (v2)

Sonnet / Opus are NOT called here — their picks come from v1 bench
(/tmp/homograph_bench.json). The point of v2 is to push the LOCAL stack
(Nakdan + Gemma) closer to Anthropic-grade quality without API cost.

Outputs JSON with the v2 picks; the parent agent assembles the
before/after delta table.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tirvi.adapters.dictabert.adapter import DictaBERTAdapter
from tirvi.adapters.nakdan.client import diacritize_via_api
from tirvi.homograph.possessive_mappiq import apply_rule as possessive_mappiq

OLLAMA_URL = "http://localhost:11434/api/generate"
PROMPT_TEMPLATE_PATH = Path(__file__).parent / "prompts" / "gemma_he_judge_v2.txt"

CASES = [
    {"id": "S1", "sentence": "האם הקריאה ספר לילדה",                 "focus": "האם",   "gold_meaning": "mother (הָאֵם)",        "gold_index": 1},
    {"id": "S2", "sentence": "האם כדאי להקריא ספר",                  "focus": "האם",   "gold_meaning": "whether (הַאִם)",       "gold_index": 1},
    {"id": "S3", "sentence": "האים כדאי להקריא ספר",                 "focus": "האים",  "gold_meaning": "whether plene (הַאִם)", "gold_index": 1},
    {"id": "S4", "sentence": "הוא טיפוס שלו ורגוע",                  "focus": "שלו",   "gold_meaning": "calm (שָׁלֵו)",         "gold_index": 3},
    {"id": "S5", "sentence": "זה הספר שלו",                          "focus": "שלו",   "gold_meaning": "his (שֶׁלּוֹ)",          "gold_index": 1},
    {"id": "S6", "sentence": "כל אם רוצה את הטוב ביותר לילדה",      "focus": "לילדה", "gold_meaning": "to her child (לְיַלְדָּהּ)", "gold_index": 3},
]


def _options_for_focus(focus: str, raw_entries: list[dict]) -> list[str]:
    for entry in raw_entries:
        if entry.get("word") == focus:
            return list(entry.get("options") or [])
    return []


def _ollama_call(model: str, prompt: str, timeout: int = 600) -> dict:
    payload = {
        "model": model, "prompt": prompt, "stream": False,
        "options": {"temperature": 0.0, "seed": 0},
    }
    req = urllib.request.Request(
        OLLAMA_URL, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read())
    except Exception as exc:
        return {"error": str(exc), "latency_s": round(time.time() - t0, 2)}
    raw = body.get("response", "").strip()
    return {"raw": raw, "parsed": _lenient_json(raw), "latency_s": round(time.time() - t0, 2)}


def _lenient_json(raw: str) -> dict | None:
    try:
        return json.loads(raw)
    except Exception:
        pass
    m = re.search(r'\{[^{}]*"pick_index"\s*:\s*(\d+)[^{}]*\}', raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return {"pick_index": int(m.group(1)), "reason": "(extracted)"}
    return None


def _build_prompt(template: str, sentence: str, focus: str, options: list[str]) -> str:
    options_block = "\n".join(f"{i + 1}. {opt}" for i, opt in enumerate(options))
    return template.replace("{sentence}", sentence).replace("{focus}", focus).replace("{options_block}", options_block)


def main() -> None:
    template = PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")
    nlp = DictaBERTAdapter()
    results: list[dict] = []

    for case in CASES:
        print(f"[{case['id']}] {case['sentence']}", file=sys.stderr)
        nlp_result = nlp.analyze(case["sentence"], lang="he")
        raw_nakdan = diacritize_via_api(case["sentence"])
        options = _options_for_focus(case["focus"], raw_nakdan)

        rule_pick = possessive_mappiq(case["sentence"], case["focus"], options)
        rule_fired = rule_pick is not None
        print(f"  rule: fired={rule_fired} pick={rule_pick}", file=sys.stderr)

        prompt = _build_prompt(template, case["sentence"], case["focus"], options)
        gemma = _ollama_call("gemma4:31b-nvfp4", prompt)
        print(f"  gemma: parsed={gemma.get('parsed')} latency={gemma['latency_s']}s", file=sys.stderr)

        # Cascade pick: rule wins if it fired; else gemma's pick
        cascade_pick = rule_pick if rule_fired else (gemma.get("parsed") or {}).get("pick_index")

        results.append({
            "id": case["id"],
            "sentence": case["sentence"],
            "focus": case["focus"],
            "gold_meaning": case["gold_meaning"],
            "gold_index": case["gold_index"],
            "options": options,
            "nlp_focus_pos": next(
                (t.pos for t in nlp_result.tokens if t.text == case["focus"]),
                None,
            ),
            "rule_fired": rule_fired,
            "rule_pick": rule_pick,
            "gemma_v2": gemma,
            "cascade_pick": cascade_pick,
            "correct": cascade_pick == case["gold_index"],
        })

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
