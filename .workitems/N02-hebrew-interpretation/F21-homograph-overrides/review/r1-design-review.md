# R1 Design Review — N02/F21 Hebrew Homograph Override Lexicon

- **Feature:** N02/F21 (YAML-backed homograph override lexicon)
- **Reviewer:** R1 multi-role (6 specialist roles synthesized)
- **Date:** 2026-05-01
- **Inputs reviewed:** design.md (authored this session), tasks.md, traceability.yaml,
  ontology-delta.yaml, user_stories.md, functional-test-plan.md,
  behavioural-test-plan.md, docs/diagrams/N02/F21/homograph-lexicon.mmd,
  HLD §5.2/Processing, F19 design.md (consumer)

---

## Role 1 — Contract Alignment

### Finding 1: T-03 edits tirvi/adapters/nakdan/overrides.py — cross-feature file coordination required
- **Area:** contract / coordination
- **Issue:** tasks.md T-03 notes the need to update F19's `tirvi/adapters/nakdan/overrides.py`
  to import HOMOGRAPH_OVERRIDES from F21's module instead of defining the inline dict.
  This file lives in the F19 adapter module — editing it from the F21 design session
  requires coordination with the TDD session (werbeH branch) per the session contract.
- **Severity:** High (process)
- **Recommendation:** T-03 correctly notes "Send coordination mailbox msg before editing
  nakdan/overrides.py." Confirm this coordination happens before T-03 TDD starts. The
  TDD session must be informed that nakdan/overrides.py will be modified by F21 work.

### Finding 2: POC scope vs. MVP scope boundary is clear and documented
- **Area:** contract
- **Issue:** design.md correctly marks POS-filtered lookup as MVP scope. The ספר entry
  in the YAML (pos_filter: VERB) is included as a schema exemplar but will be silently
  skipped by the loader in POC. This is correctly documented.
- **Severity:** Low (confirmation)
- **Recommendation:** None — the design is clear about what POC delivers vs. what's deferred.

---

## Role 2 — Architecture & Pattern

### Finding 3: Module-level constant HOMOGRAPH_OVERRIDES loaded at import time — startup failure risk
- **Area:** architecture
- **Issue:** DE-03 specifies `HOMOGRAPH_OVERRIDES = load_overrides(default_path)` at
  module import time. If `data/homograph-lexicon.yaml` is missing at startup (e.g., in
  a Docker container where the data directory was not copied), the `load_overrides()`
  call will raise FileNotFoundError at import time, crashing the entire application.
- **Severity:** Medium
- **Recommendation:** Either (a) make `load_overrides()` return an empty dict on
  FileNotFoundError (logged as a warning), or (b) lazy-load on first access via a
  cached property pattern. Option (a) is simpler for POC; option (b) matches F19's
  lazy-import ADR-029 pattern. Document the chosen behavior in DE-02.

### Finding 4: YAML loading uses yaml.safe_load() — correct (no full yaml.load())
- **Area:** security / architecture
- **Issue:** None — tasks.md T-02 correctly specifies `yaml.safe_load()`. This prevents
  arbitrary code execution from malformed YAML. Using `yaml.load()` would be unsafe.
- **Severity:** Low (confirmation)
- **Recommendation:** None — the choice is correct and safe.

---

## Role 3 — Test Coverage

### Finding 5: FT-162 (load ≤ 200ms) is tested in T-02 but load time varies by environment
- **Area:** test coverage
- **Issue:** FT-162 asserts load time ≤ 200ms. With a 2-entry YAML this will trivially
  pass in all environments. The FT becomes meaningful only with a 500-entry production
  lexicon. For POC, this test adds noise without catching real performance issues.
- **Severity:** Low
- **Recommendation:** Mark the FT-162 test with a comment: "performance gate meaningful
  at MVP scale (500 entries); POC 2-entry load is trivially fast." Do not skip it —
  it establishes the threshold — but add a comment to the test.

### Finding 6: BT-107 (dev asks about priority) is a documentation test, not a code test
- **Area:** test coverage
- **Issue:** BT-107 tests that "lexicon wins on POS match" is documented. This is a
  documentation/policy test, not a code behavior test. T-03 anchors BT-107, but the
  test file `test_homograph_overrides.py` should test code, not read docs.
- **Severity:** Low
- **Recommendation:** Implement BT-107 as an assertion: given a word in HOMOGRAPH_OVERRIDES,
  assert `HOMOGRAPH_OVERRIDES["כל"] == "כֹּל"`. This proves the policy by exercise,
  not by doc inspection.

---

## Role 4 — HLD Compliance

### Finding 7: HLD §5.2 lexicon reference is brief — design.md correctly scoped
- **Area:** HLD compliance
- **Issue:** HLD §5.2.3 says "Maintain a curated Hebrew lexicon of high-frequency homographs
  mapped to partial ניקוד / phoneme strings." design.md implements this faithfully with
  YAML-backed lexicon and loader. No HLD deviation.
- **Severity:** Low (confirmation)
- **Recommendation:** None.

---

## Role 5 — Security & Privacy

### Finding 8: YAML data file in repo — no secrets, correct
- **Area:** security
- **Issue:** `data/homograph-lexicon.yaml` contains only Hebrew word pairs (surface →
  vocalized). No user data, no credentials. Safe to commit.
- **Severity:** Low (confirmation)

---

## Role 6 — Complexity & Correctness

### Finding 9: load_overrides() CC is trivially low (CC ≤ 2)
- **Area:** complexity
- **Issue:** The loader has: iterate list → check pos_filter → add to dict. CC ≤ 2.
  The only complexity risk is if malformed-YAML validation adds too many error-path branches.
- **Severity:** Low (confirmation)

### Finding 10: diagram mmd uses "dict-str-str" in node label — not valid Mermaid label text
- **Area:** correctness
- **Issue:** `docs/diagrams/N02/F21/homograph-lexicon.mmd` has a node labeled
  `"HOMOGRAPH_OVERRIDES\ndict-str-str"`. The hyphenated `dict-str-str` may render
  oddly but won't break Mermaid parsing (it's inside a quoted label). However,
  `\n` escape is not valid in most Mermaid renderers — use `<br/>` for line breaks
  in node labels.
- **Severity:** Low
- **Recommendation:** Use `["HOMOGRAPH_OVERRIDES<br/>dict[str, str]"]` in the mmd file.

---

## Summary

| Finding | Severity | Area | Action |
|---------|----------|------|--------|
| F1: T-03 coordination required | **High** | Contract | Confirm mailbox coordination before T-03 TDD |
| F2: POC/MVP boundary clear | Low | Contract | None |
| F3: import-time load failure risk | Medium | Architecture | Handle FileNotFoundError gracefully |
| F4: yaml.safe_load() correct | Low | Security | None |
| F5: FT-162 trivial at POC scale | Low | Test | Add comment to test |
| F6: BT-107 as code assertion | Low | Test | Assert dict value, not docs |
| F7: HLD compliance confirmed | Low | HLD | None |
| F8: YAML safe to commit | Low | Security | None |
| F9: CC trivially low | Low | Complexity | None |
| F10: diagram \n vs br | Low | Correctness | Fix mmd label |

**No Critical issues. One High (process):** F1 is a coordination requirement, not
a design defect. Design is ready for TDD after mailbox coordination.
