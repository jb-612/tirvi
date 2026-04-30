# ADR-027: F26 fallback uses YAP HTTP-server mode; AlephBERT integration deferred to MVP

**Status:** Proposed

## Context

F26 (per the biz corpus E04-F02) is the AlephBERT + YAP fallback path
that activates when F17 DictaBERT-morph is unavailable (model load
failure, network issue with HF, or a future model deprecation). HLD §4
specifies "local AlephBERT + YAP" as the fallback row, anticipating
both a neural embeddings model (AlephBERT) and the rule-based
morphological parser (YAP).

Two integration questions surface for POC:

1. **YAP integration mode.** YAP (github.com/OnlpLab/yap) is a Go binary
   developed at Bar-Ilan ONLP Lab. It has no first-party Python bindings.
   Options: (a) run as a long-lived HTTP server via `yap api`, clients
   POST text and get JSON — server starts once, low per-call overhead;
   (b) subprocess-per-call (`yap hebma -in -`), pay ~1-2 sec startup
   cost on every analyze() call; (c) wrap inside HebPipe (F27) which
   bundles YAP + other tools — but couples F26 to F27's scope.

2. **AlephBERT role.** AlephBERT is a foundational Hebrew BERT model
   (`onlplab/alephbert-base`, `imvladikon/alephbertgimmel-base-512`).
   It is NOT pre-fine-tuned for POS/morph token classification — it
   provides embeddings, not labels. Using it for the fallback path
   requires either fine-tuning a head ourselves (out of POC scope) or
   using it solely for ambiguity tie-breaking when YAP returns multiple
   parses with similar weights. The added value over YAP-alone is
   marginal for POC scope (single-page demo, single-pass pipeline).

The user's framing for the F17 reroute (issue #20) emphasized using
Bar-Ilan / Hebrew University libraries that "give context to words."
YAP delivers that context (POS, morph, lemma, dependency parse).
AlephBERT alone does not — it delivers embeddings that downstream
classifiers must consume. The minimal POC fallback that satisfies the
"Bar-Ilan tool" requirement is YAP.

## Decision

F26 ships with **YAP in HTTP-server mode** as the only fallback
mechanism for POC. The user (or developer machine setup script) starts
`yap api` as a separate process listening on `127.0.0.1:8000`. F26's
adapter POSTs each `analyze()` call to the YAP API endpoint and parses
the JSON lattice into the canonical `NLPResult` shape.

AlephBERT-Gimmel embeddings for ambiguity tie-breaking are **deferred
to MVP**. POC scope is single-page; ambiguity is rare enough that
YAP's top-1 parse plus F19's homograph override lexicon (issue #20
follow-up) cover the demo.

When YAP is not running (HTTP connection refused / timeout), F26
returns `NLPResult(provider="degraded", tokens=[], confidence=None)`.
The pipeline continues without NLP context — matching the current
`_StubNLP()` baseline behaviour, so the fallback failure mode is "no
worse than today."

The vendor boundary (ADR-029) extends to the YAP HTTP URL: only
`tirvi.adapters.alephbert.client` constructs requests to YAP. The
adapter package may grow to include AlephBERT in MVP without breaking
the boundary.

## Consequences

Positive:

- **Lowest-friction Bar-Ilan integration that delivers real morph context.**
  YAP API mode requires one external setup step (build/start the binary)
  but no Python-side Go FFI or subprocess management.
- **Reuses stdlib HTTP client.** Same approach as F19 Nakdan REST per
  ADR-025 — `urllib.request`, no new vendor SDK. F19's tests demonstrate
  the mocking pattern (mock `urlopen` with a context manager).
- **Per-call overhead is negligible.** Long-lived YAP server amortizes
  startup cost across the whole pipeline run.
- **Honest "degraded" failure mode.** When YAP isn't running, the
  fallback explicitly returns empty tokens — F22 reading-plan and F19
  Nakdan-context already tolerate this case.

Negative:

- **Out-of-band dependency on YAP binary.** Developers must
  `git clone github.com/OnlpLab/yap`, build the Go binary, and run
  `yap api` before the demo will use the fallback path. Documented in
  the demo runbook; tirvi does not bundle the binary.
- **AlephBERT not used in POC.** The biz corpus story explicitly named
  "AlephBERT + YAP"; POC ships only the YAP half. Documented in this
  ADR's Out of Scope and in F26 design.md HLD Deviations.
- **YAP server is not auto-managed.** A future ADR may add `yap api`
  spawn-on-demand once we know whether the binary will ship in tirvi's
  Docker image; that decision is out of POC scope.

## Alternatives

- **Subprocess-per-call YAP invocation.** Rejected. ~1-2 sec startup
  cost per analyze() is unacceptable for any pipeline that processes
  more than a handful of pages. Multi-page MVP would have to switch
  modes anyway.
- **HebPipe wrapping YAP.** Rejected for F26 scope. HebPipe (Amir Zeldes,
  Georgetown — incorporates Bar-Ilan tooling) is a Python package that
  bundles YAP + Stanza + AlephBERT; its richer API (coreference,
  discourse) belongs in F27. Coupling F26 to F27 inverts the
  dependency direction (fallback simpler than primary).
- **Train an AlephBERT POS head ourselves.** Rejected for POC: multi-week
  ML effort; AlephBERT-base + a custom head is a project, not a
  fallback adapter.
- **Skip the fallback path entirely.** Rejected. F17's design explicitly
  references F26 in DE-06; without F26, F17 has no graceful failure
  mode and the demo crashes on `ImportError` instead of degrading.

## Migration

When AlephBERT integration becomes worth the cost (multi-page MVP with
high homograph rates), F26 grows a second adapter mode:

1. Add `tirvi/adapters/alephbert/embeddings.py` — loads
   `imvladikon/alephbertgimmel-base-512` via the existing
   `transformers` lazy-import pattern (mirrors F17 and F19 loaders).
2. Extend `mapper.py` to consume embeddings: when YAP's
   `lattice_md.weight` margin is below a threshold, query AlephBERT
   for sentence-level embeddings and use a small classifier (or
   nearest-neighbour over a labeled corpus) to pick among the YAP
   alternatives.
3. New ADR ("ADR-NN: F26 AlephBERT-Gimmel embedding integration")
   records the trigger and the classifier choice.

YAP-only adapter remains the default; AlephBERT augmentation is
opt-in via env flag.

## References

- HLD §3.3 — Worker NLP stage; HLD §4 — Adapter table fallback row;
  HLD §5.2 — NLP-driven processing
- ADR-002 — DictaBERT primary NLP (F17 unchanged)
- ADR-029 — Vendor-boundary discipline
- ADR-025 — Nakdan REST API (precedent for HTTP-server fallback)
- ADR-026 — F17 DictaBERT-morph pivot (the model F26 falls back from)
- N02/F17 design.md DE-06 — load-failure routing to F26
- N02/F26 design.md (this feature)
- YAP source: https://github.com/OnlpLab/yap
- AlephBERT-Gimmel: https://huggingface.co/imvladikon/alephbertgimmel-base-512
- Biz corpus origin: E04-F02-alephbert-yap-fallback (sha 2af7279d…)
