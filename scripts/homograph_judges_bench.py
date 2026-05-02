#!/usr/bin/env python
"""Homograph disambiguation benchmark — one-shot research probe.

Pipeline per sentence:
    DictaBERT NLP  →  Nakdan (with NLP context)  →  judges pick from option list

Judges run inside this script: gemma4:31b-nvfp4 and llama3.1:8b via Ollama.
Sonnet / Opus judging happens outside (sub-agent + main agent) — this
script only emits the per-sentence option list + Ollama picks as JSON.

Not a production feature. Lives under scripts/ so it's clearly a probe.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tirvi.adapters.dictabert.adapter import DictaBERTAdapter
from tirvi.adapters.nakdan.client import diacritize_via_api
from tirvi.adapters.nakdan.inference import diacritize_in_context

OLLAMA_URL = "http://localhost:11434/api/generate"

CASES = [
    {
        "id": "S1",
        "sentence": "האם הקריאה ספר לילדה",
        "focus": "האם",
        "gold_meaning": "mother (הָאֵם)",
        "gold_marker": "אֵם",  # substring that must appear in correct option
    },
    {
        "id": "S2",
        "sentence": "האם כדאי להקריא ספר",
        "focus": "האם",
        "gold_meaning": "whether (הַאִם)",
        "gold_marker": "הַאִם",
    },
    {
        "id": "S3",
        "sentence": "האים כדאי להקריא ספר",
        "focus": "האים",
        "gold_meaning": "whether, plene spelling (הַאִים → הַאִם)",
        "gold_marker": "אִם",
    },
    {
        "id": "S4",
        "sentence": "הוא טיפוס שלו ורגוע",
        "focus": "שלו",
        "gold_meaning": "calm (שָׁלֵו)",
        "gold_marker": "שָׁלֵו",
    },
    {
        "id": "S5",
        "sentence": "זה הספר שלו",
        "focus": "שלו",
        "gold_meaning": "his (שֶׁלּוֹ)",
        "gold_marker": "שֶׁלּוֹ",
    },
    {
        "id": "S6",
        "sentence": "כל אם רוצה את הטוב ביותר לילדה",
        "focus": "לילדה",
        "gold_meaning": "to her child (לְיַלְדָּהּ)",
        "gold_marker": "לְיַלְדָּהּ",
    },
]

JUDGE_PROMPT = """You are a Hebrew vocalization judge.

Given a Hebrew sentence and a focus word, pick the correct nikud (vocalization) for the focus word from the numbered candidate list. Choose the option whose meaning fits the sentence's context.

Sentence: {sentence}
Focus word (no nikud): {focus}
Meaning hint (for context only — DO NOT echo): the focus word may be a noun, verb, conjunction, etc.

Candidate vocalizations (1-indexed):
{options_block}

Reply with ONLY a JSON object on a single line, no markdown, no extra text:
{{"pick_index": <integer 1..N>, "reason": "<one short clause in English>"}}
"""


def _options_for_focus(focus: str, raw_entries: list[dict]) -> list[str]:
    for entry in raw_entries:
        if entry.get("word") == focus:
            return list(entry.get("options") or [])
    return []


def _ollama_judge(model: str, prompt: str, timeout: int = 60) -> dict:
    payload = {
        "model": model,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.0, "seed": 0},
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        OLLAMA_URL, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read())
    except Exception as exc:
        return {"error": str(exc), "latency_s": round(time.time() - t0, 2)}
    raw = body.get("response", "").strip()
    parsed: dict | None = None
    try:
        parsed = json.loads(raw)
    except Exception:
        # Some models wrap their JSON; try a leniency pass
        for line in raw.splitlines():
            line = line.strip().strip("`")
            if line.startswith("{"):
                try:
                    parsed = json.loads(line)
                    break
                except Exception:
                    continue
    return {
        "raw": raw,
        "parsed": parsed,
        "latency_s": round(time.time() - t0, 2),
    }


def main() -> None:
    nlp = DictaBERTAdapter()
    results: list[dict] = []

    for case in CASES:
        print(f"[{case['id']}] {case['sentence']}", file=sys.stderr)

        # 1. NLP analysis (DictaBERT-Morph)
        t0 = time.time()
        nlp_result = nlp.analyze(case["sentence"], lang="he")
        nlp_t = round(time.time() - t0, 2)
        nlp_tokens = [
            {
                "text": t.text,
                "lemma": t.lemma,
                "pos": t.pos,
                "morph": t.morph_features,
                "ambiguous": t.ambiguous,
            }
            for t in nlp_result.tokens
        ]
        print(
            f"  NLP({nlp_result.provider}, {nlp_t}s): "
            + ", ".join(f"{tk['text']}={tk['pos']}" for tk in nlp_tokens),
            file=sys.stderr,
        )

        # 2. Nakdan: full options + with-NLP-context pick
        raw = diacritize_via_api(case["sentence"])
        focus_options = _options_for_focus(case["focus"], raw)
        t0 = time.time()
        nakdan_with_nlp = diacritize_in_context(case["sentence"], nlp_result)
        nak_t = round(time.time() - t0, 2)

        # 3. Judges (Ollama: gemma4 + llama3.1)
        options_block = "\n".join(
            f"{i + 1}. {opt}" for i, opt in enumerate(focus_options)
        )
        prompt = JUDGE_PROMPT.format(
            sentence=case["sentence"],
            focus=case["focus"],
            options_block=options_block,
        )
        gemma = _ollama_judge("gemma4:31b-nvfp4", prompt)
        llama = _ollama_judge("llama3.1:8b", prompt)
        print(
            f"  judges: gemma={gemma.get('parsed')} llama={llama.get('parsed')}",
            file=sys.stderr,
        )

        results.append({
            "id": case["id"],
            "sentence": case["sentence"],
            "focus": case["focus"],
            "gold_meaning": case["gold_meaning"],
            "gold_marker": case["gold_marker"],
            "nlp": {
                "provider": nlp_result.provider,
                "latency_s": nlp_t,
                "tokens": nlp_tokens,
            },
            "nakdan": {
                "options": focus_options,
                "with_nlp_full_sentence": nakdan_with_nlp.diacritized_text,
                "with_nlp_latency_s": nak_t,
            },
            "judges": {
                "gemma4_31b": gemma,
                "llama3_1_8b": llama,
            },
            "judge_prompt": prompt,
        })

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
