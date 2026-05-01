# ADR-035 — `corrections.json` schema and chunking policy

**Status**: Proposed
**Bounded context**: hebrew-interpretation (N02/F48)
**Owner**: tirvi pipeline orchestrator
**Date**: 2026-05-01

## Context

ADR-033 §Consequences declares: *"every correction has a Gemma
reasoning trail saved to `corrections.log`. User can review and amend."*
The biz functional test plan (FT-323, FT-330) hardens this to "100% of
corrections have reasoning trail" as an auditability target measured in
CI. F50 inspector (under design) is the consumer; F48 is the producer.
The biz design-review (F48-R1-8) makes F48 the schema owner so F50 can
read without circular dependency.

The biz user_stories.correction-log.md notes two open questions:
"ndjson vs JSON object — sw-pipeline decides (performance trade-off
for 1000-page docs)" and "Multi-MB log on 1000-page documents — chunk
per page (`drafts/<sha>/corrections.<page>.json`)". Both are answered
here.

A schema change is a contract break with F50; bumping `corrections_schema_version`
must be co-ordinated. Locking the v1 shape now lets F50 begin its
inspector work in parallel.

## Decision

`drafts/<sha>/corrections.json` is a **single JSON object** (not ndjson)
with the shape:

```jsonc
{
  "corrections_schema_version": 1,
  "draft_sha": "<hex>",
  "page_index": 3,                    // -1 in the index file (see chunking)
  "ts_iso": "2026-05-01T12:00:00Z",
  "mode": "full" | "no_llm" | "no_mlm" | "emergency_fixes" | "bypass",
  "model_versions": {
    "nakdan_word_list": "<sha-or-tag>",
    "dictabert_mlm": "dicta-il/dictabert@<rev>",
    "ollama_llm": "gemma4:31b-nvfp4"  // omit when mode=no_llm
  },
  "prompt_template_version": "v1",     // omit when mode=no_llm
  "audit_quality": "ok" | "audit-incomplete" | "degraded:<mode>",
  "entries": [
    {
      "token_id": 142,                 // matches F22 reading-plan word index
      "sentence_hash": "<hex>",
      "original": "תגרוס",
      "corrected": "תגרום",            // null when verdict not in {auto_apply, apply}
      "stages": [
        { "stage": "nakdan_gate",  "verdict": "suspect", "cache_hit": false },
        { "stage": "mlm_scorer",   "verdict": "auto_apply", "scores": {...},
          "candidates": ["תגרום","תגרוס"], "cache_hit": false },
        { "stage": "llm_reviewer", "verdict": "apply", "reason": "...",
          "cache_hit": true }
      ],
      "cache_hit_chain": [false, false, true]
    }
  ]
}
```

### Chunking

- Documents ≤ 50 pages: one file per page,
  `drafts/<sha>/corrections.<page-index>.json`. Plus an index file
  `drafts/<sha>/corrections.json` listing
  `{schema_version, page_count, chunks: ["corrections.0.json", ...]}`.
- Documents > 50 pages: same per-page chunking, plus the index file
  `drafts/<sha>/corrections.json` with `chunks: [...]` only — no
  page-level `entries[]` denormalised.
- Always emitted, even when the page has zero corrections — the index
  is itself evidence of a successful run (BT-F-01). Empty pages have
  `entries: []`.

### Audit-gap behaviour

- Disk full / IO error during write → write a sibling
  `drafts/<sha>/audit_gaps.json` with `[{page_index, sha, ts_iso,
  error_kind}]` rows; the run-level summary marks
  `audit_quality: "audit-incomplete"` for that page (FT-324).
- Pipeline does NOT abort on log failure. The student's audio still
  ships.

### Pass-through tokens

Not logged by default. `--log-passthrough` (engineer flag) enables for
debugging. Rationale: a 1000-page document × 5 KB/passthrough × 200
tokens/page = 1 GB of audit noise.

## Consequences

### Positive
- **F50 contract is stable**: F50 can pin `corrections_schema_version: 1`
  and ship inspector code in parallel.
- **Audit invariant holds at any document size**: chunking keeps
  per-file size bounded.
- **Random-access friendly**: F50 lazy-loads only the visible page's
  chunk file.
- **Schema versioned**: future bump (v2) handled by inspector
  `version_gate`; v1 retained.

### Negative
- **Two read modes for F50** (single file ≤ 50 pages, index + chunks
  > 50 pages). Mitigation: index file is *always* present, so F50 can
  uniformly read the index first, then resolve chunks.
- **No live streaming view** — file is written once per page, then
  closed. Streaming inspector defer per biz behavioural plan §"Open
  Questions".

## Alternatives considered

1. **Newline-delimited JSON (ndjson) for `entries[]`** — rejected.
   Inspector wants a single load; pipeline wants atomicity. Single
   JSON object wins.
2. **Single corrections.json for the whole document** — rejected.
   1000-page docs would produce 50+ MB files; F50 lazy-load impossible.
3. **`corrections_schema_version` as a string ("1.0")** — rejected.
   Integer minor bumps don't earn a major; if a future ADR breaks
   compat we bump to 2 and gate.
4. **Pass-through always logged** — rejected. Volume blows the budget;
   no one needs them by default.

## References

- ADR-033 — Hebrew correction cascade (parent)
- ADR-014 — Result-object schema versioning (precedent for contract-tested versioned shapes)
- `.workitems/N02-hebrew-interpretation/F48-correction-cascade/user_stories.correction-log.md`
- `.workitems/N02-hebrew-interpretation/F48-correction-cascade/functional-test-plan.md` (FT-323, FT-324, FT-330)
- F50 inspector workitem (under design) — schema consumer
