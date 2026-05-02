# ADR-041 — Red-line decision register for reading-disability accommodations

**Status**: Proposed
**Bounded context**: hebrew-interpretation / reading-accommodation
(N02 + N04, cross-cutting product policy)
**Owner**: tirvi pipeline orchestrator
**Date**: 2026-05-02
**Authoritative source**: roadmap §C —
`docs/research/reading-disability-pipeline-roadmap.md`
**Filed before**: F52 / F53 / F39 design pipeline (per PR #30 question 7
answer: red-line ADR ships *before* the Phase-0 features it bounds)

## Context

The product owner (a domain expert in reading disabilities) defined a
**red line** for tirvi:

> "לא להוריד רמת קושי קוגניטיבית, אלא להסיר חסם קריאה"
> *Do not reduce the cognitive difficulty of the exam; only remove the
> reading barrier.*

The Israeli Ministry of Education frames the same principle structurally
as a three-level accommodation matrix [1]:

- **Level 1** — `התאמות שאינן פוגעות במהות הנמדדת`. Accommodations
  that do **not** compromise what the exam measures. (e.g., extra time,
  audio reading.)
- **Level 2** — `שינויים בתנאי הבחינה אך לא בתוכנה`. Changes to test
  conditions but not content. (e.g., enlarged font, separate room.)
- **Level 3** — `שינויים הן בתנאי הבחינה והן בתוכנה`. Changes to both
  conditions AND content. Granted only by exception, with explicit
  documentation per student.

**tirvi must operate strictly within Levels 1 and 2.** Any feature that
crosses into Level 3 territory — paraphrasing, simplifying vocabulary,
removing distractors, summarising — is out of scope at any tier of the
product.

The roadmap research (PR #30) surfaced 20 candidate interventions and
mapped each to allow / disallow / defer-to-human. This ADR codifies
those decisions as the binding red-line register for design-time
scope. **Future features that propose entries marked `disallow` here
must come back through ADR review, not through feature design.**

## Decision

### The register

Each row is a binding scope decision. Adding a new row (or changing a
decision) requires this ADR's "Status: Superseded" with a successor
ADR pointing back here.

| # | Intervention | Decision | MoE level (per [1]) | Rationale |
|---|---|---|---|---|
| 1 | Acronym expansion (`צה"ל` → `צבא הגנה לישראל`) | **allow** | 1 | Rendering, not modification — the acronym and its expansion refer to the same entity; printed-text human readers expand the same way. F15 already implements; just needs pipeline wiring. |
| 2 | Number reading: `12.05` as date vs. decimal | **allow with context guard** | 1 | Reading is rendering. Risk is *wrong* context (date vs. decimal) — F14 normalisation must use surrounding text. If context is ambiguous, default to decimal AND flag in `transformations[]` provenance for human review. Never silently guess. |
| 3 | Punctuation-driven SSML breaks (`<break time="500ms"/>` after `.`, `?`, `:`, `;`) | **allow** | 1 | No word reordering, no content change. Direct comprehension benefit for dyslexic listeners on complex syntax (Wood et al. 2017 [3], Košak-Babuder 2019 [6]). F23 already emits between blocks; F53 extends intra-block. |
| 4 | Clause-splitting at known conjunctions (`כיוון ש`, `מאחר ש`, `אף על פי ש`) | **allow with guardrail** | 1 | Splitting at safe conjunction boundaries with NO word reordering preserves meaning. Guardrail: only split when conjunction is unambiguous AND each fragment parses as a clause; otherwise leave intact and emit a "complex sentence" flag. |
| 5 | Pause-after-question (auto-pause at `question` block end) | **allow** | 1 | MoE accommodation matrix explicitly recognises extra time as Level-1 [1, 4]. Auto-pause is "extra time wired into the medium" rather than an exam modification. |
| 6 | Repeat instructions on demand | **allow** | 1 | Student is consuming the same content twice. No transformation. Equivalent to a human reader re-reading on request, universally allowed [1]. |
| 7 | Slowing audio playback (0.5×–1.0×) | **allow** | 1 | Identical to Wood et al. 2017 [3] meta-analysis intervention conditions; widely accepted Level-1 accommodation. Pitch correction is a quality issue, not a red-line issue. |
| 8 | Highlighting current word during read | **allow** | 1 | Synchronisation, not modification. Wood 2017 [3] found no significant moderating effect on comprehension gain; Košak-Babuder 2019 [6] reported gains in TTS-with-highlighting vs. silent read. Net allow; measure separately as UX preference. |
| 9 | Splitting one 40-word sentence into two ≤22-word audio segments | **allow with provenance** | 1 | Safe punctuation/conjunction boundary + no reordering = pacing. Must be recorded in `PlanBlock.transformations[]` so reviewer sees what was split. Default token cap 22 (per question 3 answer). |
| 10 | Pre-highlighting the *next* sentence in faint colour | **defer-to-human** | 1 (if scaffolds attention) / 2 (if distracts focus) | Genuine empirical uncertainty. No found peer-reviewed evidence either way for ל"ל readers in Hebrew exam settings. Defer until UX study answers it. |
| 11 | Skipping figure captions or image alt text | **defer-to-human** | depends | Whether the figure is exam content (graph student must read) or decorative. Default: read everything. Allow per-block opt-out only via player UI, not automatic policy. |
| 12 | Hebrew→English code-switch for loanwords (`קומפיוטר` vs. `מחשב`) | **defer-to-human** | 1 | F24 currently a no-op gate. Whether to switch voice per loanword affects how the student hears exam vocabulary; some teachers want strict-Hebrew, others code-switch. Owner: F24 ADR when MVP work begins. |
| 13 | Paraphrasing a question into simpler vocabulary | **DISALLOW** | 3 | Changes the vocabulary the exam tests; violates Level 1. |
| 14 | Removing distractors in multiple-choice | **DISALLOW** | 3 | Defeats the assessment; would require Level 3 special permission per MoE matrix [1]. |
| 15 | Auto-summarising long passages | **DISALLOW** | 3 | Replaces tested content with a derived shorter form. Clearly content modification. |
| 16 | Surfacing answer hints / explanations | **DISALLOW** | 3 | Direct cognitive scaffolding of tested content. Out of scope at any level. |
| 17 | Auto-blanking answer fields / pre-checking options | **DISALLOW** | 3 | The student must perform the answer; the system reads the question. |
| 18 | Reading answer choices in randomised order | **DISALLOW** | 2 (changes test condition by reordering) | Some Bagrut subjects test reasoning about order; reordering is a content change. Always read answer options in printed order. |
| 19 | Reading silently (TTS off) when student requests | **allow** | 1 | The whole product is a TTS opt-in. Off is the user's choice. |
| 20 | Adding "this is a question / instruction / data" verbal marker before each block | **allow with caution** | 1 | Student gets a structural cue (e.g., "*שאלה:*") not present in printed text — but the printed exam DOES present this structurally (boxes, headings, numbering); audio is rendering that structural information. Mark in `transformations[]`; revisit if any teacher pushback. |

### Process

- **Adding a row**: file a new ADR (e.g., ADR-NNN) that supersedes
  this ADR. Both the old and new register live in the repo; the old is
  marked Superseded.
- **Changing an existing decision**: same — supersession ADR. Do not
  edit this ADR's table in place after the ADR is Accepted.
- **Implementation that crosses a `DISALLOW` row**: refused at
  design-pipeline review. The reviewer should cite this ADR row
  number.
- **A `defer-to-human` row** that becomes blocking for a feature:
  open a follow-up ADR scoped to that single decision before the
  feature can ship.

### Schema-level enforcement

`PlanBlock.transformations[]` (per F22) is the audit trail. Every
allowed-with-provenance entry (rows 2, 9, 20) MUST emit a
`transformations[]` record naming this ADR row number, the input
fragment, the output fragment, and a one-line rationale. Reviewers
verify in the F33 / F50 portal.

## Alternatives considered

### A. Don't formalise — let designers judge case-by-case

**Rejected.** The whole point of a red-line register is to take
moment-of-design discretion off the table. Without it, a future
feature spec writer who hasn't read the user-stated framing might
slide into Level 3 territory by accident. The register is binding
precisely so the line is not re-litigated per feature.

### B. Make the register a workitem-level convention rather than an ADR

**Rejected.** Workitem-level conventions can be edited without
discussion. ADRs change only by supersession with explicit rationale
— the right governance level for a product red line.

### C. Emit `disallow` decisions only; let `allow` be the default

**Rejected.** Several "tempting" interventions look benign at a
glance but are red-line violations (auto-summarising long passages,
randomising answer choices). Listing both halves prevents a future
designer from arguing "but it wasn't on the disallow list, so I
assumed it was fine."

### D. Adopt the MoE matrix verbatim

**Rejected.** The MoE matrix is structural (Level 1 / 2 / 3) but
not specific to TTS-pipeline interventions. Mapping the user's
specific intervention candidates to that framework is the value of
this ADR — direct adoption would leave every concrete design
decision unanswered.

## Consequences

### Positive

- Design pipeline (`@design-pipeline`, `@sw-designpipeline`) has a
  binding scope reference. F52 / F53 / F39 design proceeds without
  re-deriving the red line.
- Gives the F50 review portal team an explicit policy contract:
  every `transformations[]` entry maps to a numbered row in this
  ADR. Auditable end-to-end.
- Israeli MoE accommodation framework citation gives tirvi an
  external authority footing for any future regulatory review.

### Negative

- One more ADR to maintain. Worth it given the load-bearing nature
  of the policy.
- Some `defer-to-human` rows (10, 11, 12) will need follow-up ADRs
  once their evidence base matures. Tracking debt acknowledged.

### Operational

- F22 plan.json schema requires `PlanBlock.transformations[]` entries
  to carry an `adr_row` field referencing this ADR (e.g.,
  `"adr_row": "ADR-041 #9"`). Schema bump tracked under F22 next-rev.
- F33 / F50 review surfaces the row number as part of the
  transformation tooltip.
- New workitems opening from the roadmap (F52, F53, F39, F54, F40,
  F41, F55, N05/F51-bench) reference this ADR in their `adr_refs`
  frontmatter.

## References

- [1] Israeli Ministry of Education, Psychological Counselling
  Service. *חוזר התאמות 2024–2025 לתלמידים עם לקויות למידה והפרעות
  קשב*. The level matrix and Bagrut accommodation framework.
  `Hozer_Hatamot_2024-2025.pdf` (existence + structure confirmed
  in PR #30; full text deferred to reviewer per the citation chain).
- [3] Wood, S. G., Moxley, J. H., Tighe, E. L., & Wagner, R. K.
  (2017). *Does Use of Text-to-Speech and Related Read-Aloud Tools
  Improve Reading Comprehension for Students With Reading
  Disabilities? A Meta-Analysis*. Journal of Learning Disabilities.
  PMC archive.
- [4] Kol-Zchut. *הקראת השאלות בבחינות הבגרות לתלמידים עם לקויות
  למידה*. Practical guidance reflecting Israeli MoE accommodation
  policy.
- [6] Košak-Babuder, M. et al. (2019). *The effect of read-aloud
  assistance on the text comprehension of students with and without
  reading difficulties.* (Cited via abstract; journal returned 403.)
- PR #30 — `research(N02): reading-disability pipeline roadmap`,
  merged at `a89519d`. Authoritative source for §C.
- ADR-035 — `corrections.json` schema (the audit trail format).
- ADR-038, ADR-040 — adjacent reading-accommodation ADRs (homograph
  context-rules + ambiguous verdict).
