# ADR-025: Dicta-Nakdan via REST API for POC; in-process model deferred

**Status:** Proposed

**Supersedes:** ADR-021 (in-process Nakdan loader) — for the POC only;
ADR-021's deferred decision (API path is MVP work) is reversed in light
of facts discovered during the first end-to-end demo run.

## Context

ADR-021 chose an in-process Nakdan loader for the POC, mirroring
ADR-020's pattern for DictaBERT. The first end-to-end demo run on
2026-04-30 surfaced two facts that invalidate that decision:

1. **`dicta-il/dicta-nakdan` is private on HuggingFace Hub.** A direct
   request to `https://huggingface.co/dicta-il/dicta-nakdan` returns
   `401 Unauthorized`. The model card is not publicly fetchable; weights
   cannot be downloaded without a HuggingFace token tied to an account
   with explicit access to the gated repo. The POC has no such token.
2. **`dicta-il/dictabert-large-joint` (the F17 NLP model) does not
   exist** on HuggingFace at all (`404` from the search API). DictaBERT
   variants `-morph`, `-ner`, `-large`, etc. exist; the joint model
   listed in F17 does not. F19's `diacritize_in_context` design (DE-02)
   depends on F17's `NLPResult` for context tilting, so even if Nakdan
   weights were accessible, the homograph-resolution path is dead until
   F17 is rerouted.

The user-observable consequence is that the demo synthesizes Hebrew
text without nikud through Wavenet `he-IL-Wavenet-D`, which guesses
pronunciation from undecorated text. Quality is poor: wrong stress on
homographs, wrong vowel choices, and obvious mispronunciations of
common words.

Dicta runs a public REST endpoint serving the same Nakdan engine
without account or token. **Endpoint URL** (verified 2026-04-30):
`https://nakdan-2-0.loadbalancer.dicta.org.il/api`. The bare-domain
URL `https://nakdan.dicta.org.il/api` returns 404; the load-balancer
subdomain is the documented entry point. The API
requires no authentication for the diacritization endpoint, returns
JSON, and is rate-limited at the IP level. The POC is single-user and
synchronous; rate limiting is not a binding constraint for demo runs.

PRD §6.4 (Reading plan) and §10 (Success metrics) treat diacritization
quality as the central moat. Skipping it because the chosen loader path
is broken is not an option; pivoting to the REST API is the cheapest
unblock.

## Decision

POC's `DictaNakdanAdapter` calls the Dicta REST API at
`https://nakdan-2-0.loadbalancer.dicta.org.il/api` rather than loading
the model in-process. The adapter remains the same `DiacritizerBackend`
implementation; the loader file (`tirvi/adapters/nakdan/loader.py`) is
replaced by an HTTP client (`tirvi/adapters/nakdan/client.py`) that
issues `POST` requests with the Hebrew text and parses the JSON
response into `DiacritizationResult`. F19's existing inference + NFD
normalization + token-skip filter modules (DE-03, DE-04, DE-05)
continue to apply unchanged — they operate on the resulting
diacritized string, not on the model object.

The HuggingFace in-process path (ADR-021) is deferred to MVP under one
of three conditions: (a) Dicta releases the model publicly on
HuggingFace, (b) the project obtains gated access to the private repo,
or (c) a tirvi-internal Nakdan equivalent is trained. Until then the
REST API is the canonical POC + MVP path; ADR-021 is left in the index
as a deferred-alternative reference.

The DiacritizerBackend port (`tirvi.ports.DiacritizerBackend`) is
unchanged. Call sites in `pipeline.py` are unchanged. The pivot is
fully encapsulated inside `tirvi.adapters.nakdan.**`.

## Consequences

Positive:
- Unblocks demo voice quality: the largest single contributor to
  current TTS mispronunciation is the missing nikud step, and this ADR
  restores it.
- Zero credential setup: the demo runs against the public endpoint
  without HuggingFace tokens, GCS credentials beyond the existing
  Wavenet ADC, or local model weights.
- No model RAM cost. Frees the laptop budget that ADR-021 acknowledged
  as a constraint when DictaBERT is also loaded.
- Determinism is acceptable: Nakdan output for the same input is
  stable across calls in practice (verified informally; formal
  determinism contract is post-POC).

Negative:
- Demo now requires an outbound HTTPS connection at run time. Offline
  runs are no longer possible; the README runbook needs an explicit
  network-required note. Stubs mode (`make_stub_deps`) remains
  available for fully-offline development.
- Latency: each pipeline run pays one round-trip per page (Economy.pdf
  is single-page; cost is bounded). MVP block-by-block batching is
  deferred.
- Dicta's terms of service apply. The endpoint is currently free and
  has no published rate limit, but a runaway pipeline could be
  throttled. Mitigation: the POC runs the pipeline once per drafts
  SHA — content-addressed caching prevents redundant calls.
- Privacy: Hebrew exam text is sent to Dicta's servers. PRD's privacy
  posture (24-hour TTL, opt-in extension, no PII logging) does not
  cover third-party data sharing during diacritization. MVP must
  decide: in-process loader (if model becomes accessible) or
  contractual privacy guarantee from Dicta. Neither is required for
  the demo.

## Alternatives

- **Stay with `_StubDia` (passthrough).** Rejected: voice quality is
  unacceptable; the user already flagged this. The stub diacritizer
  defeats the project's stated moat.
- **Stay with in-process loader and require the user to supply a
  HuggingFace token.** Rejected: the model is gated and the project
  has no commercial relationship with Dicta. Users acquiring the model
  is not a defensible POC requirement.
- **Train a tirvi-internal Nakdan-equivalent on open Hebrew nikud
  corpora.** Rejected: outside POC scope; this is a multi-week ML
  research effort and inappropriate as the unblock for a demo.
- **License Dicta-Nakdan privately for in-process use.** Rejected for
  POC: procurement timeline and cost incompatible with demo schedule.
  Reconsidered for MVP if privacy posture demands it.
- **Use a different Hebrew diacritizer entirely (e.g., custom
  rule-based).** Rejected: lower quality than Nakdan, and the REST API
  removes the only blocker to using Nakdan.

## Migration

When the in-process path becomes viable (any of the three conditions
above), the swap is mechanical:

1. Restore `tirvi/adapters/nakdan/loader.py` from ADR-021's design
   (already TDD'd against `dicta-il/dicta-nakdan`); the existing
   `test_nakdan_loader.py` covers it.
2. Wire `loader.load_model` into `inference.py` instead of `client.py`.
3. Drop `tirvi/adapters/nakdan/client.py`.
4. The adapter call sites (`DictaNakdanAdapter.diacritize`) and the
   pipeline are unchanged because both paths produce the same
   `DiacritizationResult`.

A new ADR ("ADR-NN: Nakdan in-process restored") records the reversal
when the trigger fires.

## References

- HLD §5.2 — NLP-driven processing
- ADR-003 — Diacritization + G2P stack
- ADR-021 — In-process Nakdan loader (now deferred)
- ADR-029 — Vendor boundary discipline (REST client lives inside `tirvi.adapters.nakdan.**`)
- N02/F19 design.md DE-01 (loader topology), DE-02 (NLP-context tilt)
- PLAN-POC.md — F19 critical-path scope
- Dicta public API: `https://nakdan-2-0.loadbalancer.dicta.org.il/api`
- Discovery date: 2026-04-30 (first end-to-end demo run)
