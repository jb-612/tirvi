# ADR-019: Normalization uses deterministic rules for POC; ML repair deferred

**Status:** Proposed

## Context

Biz corpus E03-F01 surfaces an open question: should OCR artifact
repair be deterministic rules or an ML-based model? POC must produce
clean enough Hebrew text on a single demo PDF page to feed DictaBERT
(F17) — no labelled artifact corpus exists, no GPU budget for inference,
no nightly bench. HLD §3.3 specifies the `normalize` stage but does not
constrain the implementation.

## Decision

Adopt a **deterministic** rule registry for POC. `tirvi.normalize.rules`
ships exactly two rules: line-break rejoin and stray-punctuation drop.
Each rule has a stable `rule_id`, an applies-to predicate, and an
audit-logged transformation. ML-based repair (e.g., a small seq2seq
denoiser fine-tuned on tirvi-bench) is deferred to MVP and gated on the
N05 quality bench showing residual error worth modeling.

## Consequences

Positive:
- Zero training data + zero inference cost for POC.
- Rules are inspectable, testable per-input, and reversible.
- Audit log (DE-06) makes regressions traceable to a specific rule.

Negative:
- Limited recall — patterns the rules don't cover survive into the NLP
  step (which DictaBERT is generally robust enough to handle for clean
  digital-born PDFs like the demo).
- Adding rules per publisher does not scale beyond a handful before a
  learned approach becomes more cost-effective.

## Alternatives

- **Small fine-tuned seq2seq.** Rejected for POC: training data + GPU
  cost + inference latency without measured benefit.
- **Skip normalization entirely (pure pass-through).** Rejected: the
  demo PDF likely has at least one mid-word line-break that would
  poison downstream tokenization.

## References

- HLD §3.3 — Worker pipeline `normalize` stage
- HLD §5.1 — Cleaned input contract
- Biz corpus E03-F01 / S02 / Open Question
- Related: N02/F14 design.md DE-03/DE-04/DE-06
