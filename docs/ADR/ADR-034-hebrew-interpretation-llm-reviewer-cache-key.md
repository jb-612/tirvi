# ADR-034 — LLM reviewer prompt template + cache-key strategy

**Status**: Proposed
**Bounded context**: hebrew-interpretation (N02/F48)
**Owner**: tirvi pipeline orchestrator
**Date**: 2026-05-01

## Context

ADR-033 §Decision row 3 specifies a local Gemma reviewer for ambiguous
cascade tokens. ADR-033 §Consequences calls for *deterministic* re-runs
("LLM output isn't strictly deterministic. Cache key includes prompt +
model + temperature=0; further variance acceptable.") but does not
pin the exact key shape, the prompt asset location, or the
versioning policy.

UAT-2026-05-01-tts-quality recommendation #1 ("OCR fix list will grow")
depends on engineers being able to tune the reviewer prompt without
silently invalidating thousands of cached verdicts in unpredictable ways.
A cache-key drift would also break the FT-322 determinism test — and
hide regressions for several runs before surfacing.

HLD-§5.2 §"Pronunciation hint generation" treats prompt assets as code;
HLD-§10 lists "vendor lock-in" as a managed risk. The Ollama HTTP
contract is treated as just another adapter (ADR-029).

## Decision

The LLM reviewer caches verdicts under the key:

```
cache_key = sha256(
    model_id ||
    "/" ||
    prompt_template_version ||
    "/" ||
    sentence_hash ||
    "/" ||
    sorted(candidates) joined by "|"
)
```

- **`model_id`**: the exact Ollama model identifier the user has pulled
  (e.g., `gemma4:31b-nvfp4`, `llama3.1:8b`). Bumping the model evicts
  the cache automatically.
- **`prompt_template_version`**: read from the YAML frontmatter of the
  prompt asset; never inferred from file mtime.
- **`sentence_hash`**: `sha256(sentence)` after F14 normalization.
- **`sorted(candidates)`**: deterministic ordering so the key is stable
  across MLM scoring runs that produce the same set in different order.

Prompt assets live at:

```
tirvi/correction/prompts/<lang>/<role>/<filename>.txt
```

with sibling YAML frontmatter `_meta.yaml` carrying `version`,
`language`, `description`, and the model-id allowlist. Bumping the
prompt requires a new version (e.g., `v1` → `v2`), never an in-place
edit. Old prompts are retained for cache lookups but new runs use the
current version.

The cache itself is a sqlite table at `drafts/<sha>/llm_cache.sqlite`
(per-draft, follows F43 TTL). Schema:

```
CREATE TABLE llm_cache (
    cache_key TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    prompt_template_version TEXT NOT NULL,
    sentence_hash TEXT NOT NULL,
    candidates TEXT NOT NULL,
    verdict_json TEXT NOT NULL,
    ts_iso TEXT NOT NULL
);
```

## Consequences

### Positive
- **Deterministic re-runs** (FT-322, FT-328): same input + same model +
  same prompt version → 0 LLM calls; verdicts byte-identical.
- **Safe prompt iteration**: bumping `version` invalidates cache atomically;
  no half-cached / half-fresh runs.
- **Cross-document leakage avoided**: cache is per-draft (TTL'd with the
  draft), so verdicts from one student's exam never bleed into another's.
- **Adapter-friendly**: cache key is computed in `LLMReviewer`, not in
  the HTTP client; swapping Ollama for another local LLM runtime is a
  port-level change.

### Negative
- **Cache loss on draft delete**: F43 TTL also deletes the LLM cache.
  Acceptable: privacy invariant trumps cache reuse.
- **No cross-page reuse without sentence match**: if the same sentence
  appears verbatim in two different drafts, each draft computes its
  verdict independently. Acceptable cost; cross-draft cache would
  require a global namespace and complicate retention.
- **`sorted(candidates)` requires the cascade to never feed unordered
  collections**: enforced by `tuple(sorted(...))` at the call site.

## Alternatives considered

1. **Cache key = `sha256(prompt_body + sentence)`** — rejected. Prompt
   body changes invisibly with every whitespace edit; not stable
   enough for an audit gate.
2. **Global LRU cache in `~/.tirvi/llm_cache/`** — rejected. Crosses
   draft TTL boundary; privacy invariant violated.
3. **No caching, rely on `temperature=0` only** — rejected. Cost +
   latency targets impossible; FT-322 / BT-217 explicit acceptance
   criteria require deterministic re-runs.
4. **Prompt-asset versioning via filename mtime** — rejected. Editor
   touches mtime; CI re-checkouts reset it. Frontmatter `version`
   field is the only stable signal.

## References

- ADR-033 — Hebrew correction cascade (parent)
- ADR-029 — Vendor-boundary discipline (LLM client behind a port)
- HLD-§5.2 — pronunciation hint generation (prompt assets are code)
- `.workitems/N02-hebrew-interpretation/F48-correction-cascade/functional-test-plan.md` (FT-320, FT-322, FT-328)
- `.workitems/N02-hebrew-interpretation/F48-correction-cascade/behavioural-test-plan.md` (BT-217)
