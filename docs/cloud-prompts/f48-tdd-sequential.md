# Cloud Agent Prompt — F48 Sequential TDD (unattended)

**Branch:** `werbeH`  
**Estimated runtime:** 2–3 hours  
**Mode:** fully autonomous — no HITL, no mode-selection prompts, no skill invocations that pause

Paste everything below the `---` separator into a new Claude Code web session.

---

## SESSION INSTRUCTIONS: F48 Hebrew Correction Cascade — Full Sequential TDD

You are a TDD engineer completing **feature N02/F48** (`tirvi/correction/`) on branch
`werbeH`. The DDD 7L scaffold is committed; all 10 tasks are unchecked.
Your job: activate every test skeleton, implement every production stub, keep all tests
green, commit after each task, and never stop to ask the user a question.

---

### STARTUP CHECKLIST (run these first, before any TDD work)

```bash
git rev-parse --abbrev-ref HEAD        # must print: werbeH
git log --oneline -3                   # must show scaffold commit as most recent
git status --short                     # must be clean (no untracked or modified files)
uv run pytest tests/unit/ -q --co 2>&1 | tail -5   # must show ~850 tests collected
```

If `HEAD` is not `werbeH`, run `git checkout werbeH` before proceeding.
If `git status` is not clean, investigate before editing any file.
If test collection fails, check that `uv` and `pytest` are available in the environment.

Only proceed to T-01 once all four checks pass.

---

### 0. MANDATORY RULES — READ FIRST

#### 0a. Never pause or invoke these skills (they have HITL gates)
Do NOT call: `@design-pipeline`, `@sw-designpipeline`, `@design-review`, `@test-design`,
`@test-mock-registry`, `@code-review`, `@feature-completion`, `@verify`, `@testing`,
`@commit`, `@hotfix`. Work inline throughout.

#### 0b. TDD mode: BUNDLED for all tasks (pre-approved)
For every task: write ALL tests first, run (expect RED), fill ALL production code,
run (expect GREEN), refactor, commit. No strict one-test-at-a-time cycle.

#### 0c. Never push
`git push` is deny-listed. Commit locally; the user reviews and pushes after.

#### 0d. Cyclomatic complexity ≤ 5 per function
After each GREEN, check CC. If any function exceeds 5, refactor before committing.
Check with: `uv run python -c "import ast, sys; ..."` or count branches manually.

#### 0e. No real model loads or HTTP in unit tests
All tests under `tests/unit/` must complete in < 1 s per test with no network.
Use `monkeypatch`, the fakes in `tests/unit/conftest.py`, or `tmp_path` for I/O.

#### 0f. sw-dispute.md — log every unresolvable question
File: `.workitems/N02-hebrew-interpretation/F48-correction-cascade/sw-dispute.md`
Whenever you reach a design ambiguity you cannot resolve from the existing documents
(design.md, tasks.md, ADRs, task hints), write an entry, apply a reasonable workaround,
and continue. NEVER stop working to wait for an answer. Format:

```
## [DISPUTE-NN] <short title>
- **Task:** T-NN
- **Question:** <what you needed to know>
- **Workaround:** <what you assumed / how you proceeded>
- **Impact if wrong:** <low / medium / high>
```

#### 0g. Inline code review after each task
After each task reaches GREEN + CC passes, do a self-review:
- **Critical / High** (security, data loss, privacy breach, broken invariant): fix
  immediately, add a commit `fix(N02/F48): T-NN post-review <issue>`.
- **Medium / Low** (non-blocking quality, nice-to-have): append to
  `sw-dispute.md` under a `## [REVIEW-NN]` entry tagged `[GH-ISSUE-NEEDED]`.
  The user will open GitHub issues from these after the run.

---

### 1. REPO STATE

```
Branch:       werbeH
Last commit:  scaffold(N02/F48): DDD 7L correction cascade — tirvi/correction + test skeletons
Tasks file:   .workitems/N02-hebrew-interpretation/F48-correction-cascade/tasks.md
```

Key directories already on disk:
```
tirvi/correction/
  ports.py              ← COMPLETE (Protocols, all @runtime_checkable)
  value_objects.py      ← COMPLETE (CorrectionVerdict, SentenceContext, etc.)
  nakdan_gate.py        ← STUB (NotImplementedError — TDD T-02 fills)
  mlm_scorer.py         ← STUB (NotImplementedError — TDD T-03 fills)
  adapters/ollama.py    ← STUB (NotImplementedError — TDD T-04a fills)
  llm_reviewer.py       ← STUB (NotImplementedError — TDD T-04b fills)
  service.py            ← STUB (NotImplementedError — TDD T-05 fills)
  log.py                ← STUB (NotImplementedError — TDD T-06 fills)
  health.py             ← STUB (NotImplementedError — TDD T-07 fills)
  feedback_aggregator.py← STUB (NotImplementedError — TDD T-08 fills)
  domain/cascade.py     ← STUB aggregate shell
  domain/events.py      ← STUB domain events shell
  domain/policies.py    ← STUB policies shell
  prompts/he_reviewer/v1.txt ← prompt template (read, do not overwrite)

tests/unit/conftest.py  ← COMPLETE fakes: FakeNakdanWordList, FakeLLMClient,
                           FakeFeedbackReader, FakeCascadeStage + pytest fixtures

tests/unit/
  test_correction_ports.py    ← SKELETON (T-01)
  test_nakdan_gate.py         ← SKELETON (T-02)
  test_mlm_scorer.py          ← SKELETON (T-03)
  test_ollama_client.py       ← SKELETON (T-04a)
  test_llm_reviewer.py        ← SKELETON (T-04b)
  test_cascade_service.py     ← SKELETON (T-05)
  test_correction_log.py      ← SKELETON (T-06)
  test_health_probe.py        ← SKELETON (T-07)
  test_feedback_aggregator.py ← SKELETON (T-08)
  test_pipeline.py            ← SKELETON (T-09, extend existing)
  test_privacy_invariant.py   ← SKELETON (T-10)
```

All skeletons have `pytestmark = pytest.mark.skip(reason="scaffold — /tdd fills")`.
**Your first action on each task file is to remove that skip marker.**

---

### 2. FAKES REFERENCE (tests/unit/conftest.py)

These fixtures are available in every test file automatically:

| Fixture | Type | What it does |
|---------|------|--------------|
| `fake_word_list` | `FakeNakdanWordList` | `is_known_word(t) → t in {"שלום","עולם","סיום"}` |
| `fake_llm_client` | `FakeLLMClient` | returns `canned_response`; records calls in `.calls` |
| `fake_feedback` | `FakeFeedbackReader` | returns `rejections_by_sha.get(sha, [])` |
| `sample_sentence_context` | `SentenceContext` | pre-built context for sentence "זה משפט לדוגמא" |

You can also instantiate them directly: `FakeNakdanWordList(known={"word"})`.

---

### 3. TASK SEQUENCE

Work strictly in this order. Do not start the next task until the current one is green,
CC-checked, self-reviewed, and committed.

---

#### T-01 — ICascadeStage port + CorrectionVerdict value object
- **Test file:** `tests/unit/test_correction_ports.py`
- **Source:** `tirvi/correction/ports.py`, `tirvi/correction/value_objects.py`
- **Status of source:** COMPLETE in scaffold — no production code to write.
- **Your job:** remove the skip marker; fill all test bodies; run; all should be GREEN.

Tests to write (fill existing skeletons):
1. `test_icascadestage_is_runtime_checkable` — create an object with an `evaluate` method,
   assert `isinstance(obj, ICascadeStage)` is True.
2. `test_nakdan_word_list_port_is_runtime_checkable` — duck-type fake, isinstance check.
3. `test_llm_client_port_is_runtime_checkable` — duck-type fake, isinstance check.
4. `test_feedback_read_port_is_runtime_checkable` — duck-type fake, isinstance check.
5. `test_verdict_is_frozen_dataclass` — build a `CorrectionVerdict`, try `v.stage = "x"`,
   assert `FrozenInstanceError` is raised.
6. `test_verdict_carries_all_bo52_fields` — assert `CorrectionVerdict` has fields:
   `stage`, `verdict`, `original`, `corrected_or_none`, `score`, `candidates`,
   `mode`, `cache_hit`, `reason`, `model_versions`, `prompt_template_version`.
7. `test_verdict_default_factory_for_model_versions` — build two verdicts, assert
   `v1.model_versions is not v2.model_versions` (no shared mutable default).
8. `test_sentence_context_is_frozen` — mutate attempt raises `FrozenInstanceError`.
9. `test_sentence_context_has_sentence_hash` — assert field present and is a str.

Run: `uv run pytest tests/unit/test_correction_ports.py -v`

Commit on GREEN: `tdd(N02/F48): T-01 green — port contracts + CorrectionVerdict shape`

---

#### T-02 — NakdanGate first-stage word-list filter
- **Test file:** `tests/unit/test_nakdan_gate.py`
- **Source:** `tirvi/correction/nakdan_gate.py`
- **Implements:** `ICascadeStage.evaluate` with skip rules + word-list verdict

Tests to write (fill skeletons — add more if needed):
1. `skip_empty` — `evaluate("", ctx)` → `verdict="skip_empty"`.
2. `skip_short` — `evaluate("א", ctx)` (len=1) → `verdict="skip_short"`.
3. `skip_non_hebrew` — `evaluate("123", ctx)` or `evaluate("abc", ctx)` → `verdict="skip_non_hebrew"`.
4. `known_word_returns_pass` — word in `fake_word_list.known` → `verdict="pass"`.
5. `unknown_word_returns_suspect` — word not in list → `verdict="suspect"`.
6. `lru_cache_hit` — call twice with same token; assert `word_list.is_known_word` called once
   (monkeypatch or use a counting fake).
7. Performance (mark `@pytest.mark.slow`): 1000-token loop with warm list; assert p95 ≤ 5 ms
   (use `time.perf_counter`; skip in CI with `-m "not slow"`).

Implementation notes:
- Use `functools.lru_cache` on a module-level helper or wrap the method.
- Cache key: `(token, self.word_list_version)`.
- Skip rules checked before the cache lookup.
- Return `CorrectionVerdict(stage="nakdan_gate", verdict=..., original=token)`.
- CC must be ≤ 5. Split helpers if the skip-rule block would exceed 5 branches.

Run: `uv run pytest tests/unit/test_nakdan_gate.py -v -m "not slow"`

Commit on GREEN: `tdd(N02/F48): T-02 green — NakdanGate skip rules + word-list verdicts`

---

#### T-03 — DictaBertMLMScorer confusion-table + decision tree
- **Test file:** `tests/unit/test_mlm_scorer.py`
- **Source:** `tirvi/correction/mlm_scorer.py`
- **Key design:** single-site token swap; scores via MLM head; decision tree with
  `(threshold_low=1.0, threshold_high=3.0, margin=0.5)`.
- **Never load the real DictaBERT model in tests** — monkeypatch the scorer function.

Tests to write:
1. `low_delta_returns_keep_original` — patched delta < 1.0 → `verdict="keep_original"`.
2. `mid_delta_returns_ambiguous` — 1.0 ≤ delta < 3.0 → `verdict="ambiguous"`.
3. `high_delta_known_word_returns_auto_apply` — delta ≥ 3.0, candidate in word list,
   margin satisfied → `verdict="auto_apply"`, `corrected_or_none=candidate`.
4. `high_delta_unknown_word_returns_ambiguous` — delta ≥ 3.0, candidate NOT in word list
   → `verdict="ambiguous"` (anti-hallucination).
5. `cache_hit_skips_model_call` — second call same (token, ctx, model_id, table_ver) →
   `cache_hit=True`, model not called again.
6. `confusion_table_missing_raises` — missing `confusion_pairs.yaml` →
   `ConfusionTableMissing` error at init.
7. `candidates_from_confusion_table` — assert candidates come from the loaded table only.

For the confusion table, create a minimal in-memory `confusion_pairs.yaml` in `tmp_path`
and pass its path to the scorer at init.

Monkeypatching pattern (pin MLM scores deterministically):
```python
def test_low_delta(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "tirvi.correction.mlm_scorer.score_token_in_context",
        lambda token, ctx, model_id: {"original": 2.0, "candidate": 2.5},
    )
    scorer = DictaBertMLMScorer(
        confusion_table_path=_write_table(tmp_path, {"שלום": ["שָׁלוֹם"]}),
        word_list=FakeNakdanWordList(known={"שָׁלוֹם"}),
    )
    verdict = scorer.evaluate("שלום", sample_sentence_context)
    assert verdict.verdict == "keep_original"
```

Run: `uv run pytest tests/unit/test_mlm_scorer.py -v`

Commit on GREEN: `tdd(N02/F48): T-03 green — MLMScorer decision tree + confusion-table init`

---

#### T-04a — Ollama HTTP adapter (LLMClientPort) + sqlite cache
- **Test file:** `tests/unit/test_ollama_client.py`
- **Source:** `tirvi/correction/adapters/ollama.py`
- **ADR-029:** this is the ONLY file allowed to import `httpx`. No real HTTP in tests.

Tests to write:
1. `generate_posts_to_ollama_endpoint` — monkeypatch `httpx.post`; assert called with
   `http://localhost:11434/api/generate`, correct `model` and `prompt` fields.
2. `generate_returns_response_text` — mocked response JSON → returns `response` field.
3. `cache_hit_skips_http` — call twice with same params; assert `httpx.post` called once.
4. `cache_key_is_sha256` — assert cache key = `sha256(model_id + version + sentence_hash)`.
5. `per_page_cap_reached_returns_keep_original` — make N+1 calls where N is the cap;
   last call returns response indicating `keep_original` / emits cap event.
6. `sqlite_schema_matches_adr034` — after a `generate()`, open the sqlite file and assert
   columns: `cache_key`, `model_id`, `prompt_template_version`, `sentence_hash`,
   `response`, `ts`.

sqlite path: `drafts/<draft_sha>/llm_cache.sqlite` (use `tmp_path` for tests).

Run: `uv run pytest tests/unit/test_ollama_client.py -v`

Commit on GREEN: `tdd(N02/F48): T-04a green — OllamaClient HTTP adapter + sqlite cache`

---

#### T-04b — OllamaLLMReviewer domain wrapper + anti-hallucination guards
- **Test file:** `tests/unit/test_llm_reviewer.py`
- **Source:** `tirvi/correction/llm_reviewer.py`
- **Uses:** `FakeLLMClient` from conftest; loads prompt from `prompts/he_reviewer/v1.txt`.

Tests to write:
1. `chosen_in_candidates_and_known_returns_apply` — LLM response `{"verdict":"OK","chosen":"שלום"}`
   with `"שלום"` in candidates and word list → `verdict="apply"`.
2. `chosen_not_in_candidates_rejects` — `chosen` not in candidates list →
   emit `anti_hallucination_reject`, return `verdict="keep_original"`.
3. `chosen_not_in_word_list_rejects` — `chosen` not in `NakdanWordListPort` →
   `verdict="keep_original"`.
4. `parse_failure_triggers_reprompt` — first LLM response is invalid JSON; assert
   `fake_llm_client.generate` called twice (re-prompt with stricter template).
5. `parse_failure_twice_returns_keep_original` — both calls fail → `verdict="keep_original"`.
6. `cache_hit_flag_propagated` — if `LLMClientPort` marks response as cache hit,
   `CorrectionVerdict.cache_hit` is True.
7. `prompt_template_version_in_verdict` — `prompt_template_version` from `_meta.yaml`
   ends up in the returned `CorrectionVerdict`.

Load `prompts/he_reviewer/v1.txt` relative to `tirvi/correction/`. Read `_meta.yaml`
sibling for the version string.

Run: `uv run pytest tests/unit/test_llm_reviewer.py -v`

Commit on GREEN: `tdd(N02/F48): T-04b green — LLMReviewer anti-hallucination guards + reprompt`

---

#### T-05 — CorrectionCascadeService orchestrator + domain events
- **Test file:** `tests/unit/test_cascade_service.py`
- **Source:** `tirvi/correction/service.py`, `tirvi/correction/domain/events.py`,
  `tirvi/correction/domain/cascade.py`
- **Uses:** `FakeCascadeStage`, `FakeFeedbackReader` from conftest.

Tests to write:
1. `run_page_calls_stages_in_order` — NakdanGate → MLM → LLM; use three FakeCascadeStages
   wired into the service; assert each called.
2. `nakdan_pass_skips_mlm_and_llm` — NakdanGate returns `verdict="pass"`; assert MLM stage
   not called.
3. `nakdan_suspect_calls_mlm` — NakdanGate returns `suspect`; assert MLM called.
4. `mlm_ambiguous_calls_llm` — MLM returns `ambiguous`; assert LLM called.
5. `mlm_auto_apply_skips_llm` — MLM returns `auto_apply`; assert LLM NOT called.
6. `feedback_rejection_forces_keep_original` — `FakeFeedbackReader` has a rejection for
   `("ocr_word", draft_sha)`; cascade service forces `keep_original` for that token.
7. `correction_applied_event_emitted` — when `auto_apply` or `apply` verdict, listener
   receives `CorrectionApplied` event.
8. `correction_rejected_event_emitted` — `keep_original` with a prior candidate →
   `CorrectionRejected` event emitted.
9. `no_cascade_mode_degraded_in_full_mode` — `CascadeMode(name="full")` → no degraded event.
10. `degraded_mode_no_mlm_emits_event` — `CascadeMode(name="no_mlm")` → `CascadeModeDegraded`
    event emitted at service init.

Token-in / token-out invariant: the returned page must have the same token count as input.
Assert this as a property-style test (parametrize over small token lists).

Run: `uv run pytest tests/unit/test_cascade_service.py -v`

Commit on GREEN: `tdd(N02/F48): T-05 green — CascadeService orchestration + domain events`

---

#### T-06 — CorrectionLog writer + audit-gap path
- **Test file:** `tests/unit/test_correction_log.py`
- **Source:** `tirvi/correction/log.py`
- **Uses:** `tmp_path` for all file I/O.

Tests to write:
1. `write_creates_json_file` — after `log.write_page(...)`, assert `corrections.json` exists.
2. `write_is_atomic` — mock `os.replace` to succeed; assert no `.tmp` left after write.
3. `disk_full_appends_to_audit_gaps` — mock `os.replace` to raise `OSError`; assert entry
   in `audit_gaps.json`.
4. `disk_full_marks_page_header` — page header `audit_quality` field = `"audit-incomplete"`.
5. `schema_version_constant_present` — `corrections.json` has `schema_version` key.
6. `index_file_has_chunks_list` — `corrections.json` top-level has `chunks` list.
7. `large_page_uses_index_only` — single entry for a page; schema stays uniform
   (no duplicate denormalization that breaks the schema).

Run: `uv run pytest tests/unit/test_correction_log.py -v`

Commit on GREEN: `tdd(N02/F48): T-06 green — CorrectionLog atomic write + audit-gap path`

---

#### T-07 — HealthProbe + degraded-mode policy
- **Test file:** `tests/unit/test_health_probe.py`
- **Source:** `tirvi/correction/health.py`
- **Never make real HTTP calls** — monkeypatch `httpx.get`.

Tests to write:
1. `ollama_reachable_dictabert_loaded_returns_full` — both OK → `CascadeMode(name="full")`.
2. `ollama_unreachable_returns_no_llm` — httpx raises `ConnectError` → `no_llm`.
3. `dictabert_not_loaded_returns_no_mlm` — DictaBERT loader raises → `no_mlm`.
4. `both_failed_returns_emergency_fixes` — both fail → `emergency_fixes`.
5. `timeout_respected` — assert httpx called with `timeout=1`.
6. `mode_is_immutable` — `CascadeMode` is frozen; assert mutate attempt raises.
7. `deprecated_lookup_path_in_no_mlm` — `no_mlm` mode triggers
   `_deprecated_known_fixes_lookup()` annotated helper (assert callable exists and
   marked as deprecated).

Run: `uv run pytest tests/unit/test_health_probe.py -v`

Commit on GREEN: `tdd(N02/F48): T-07 green — HealthProbe degraded-mode policy`

---

#### T-08 — FeedbackAggregator + FeedbackReadPort sqlite adapter
- **Test file:** `tests/unit/test_feedback_aggregator.py`
- **Source:** `tirvi/correction/feedback_aggregator.py`,
  `tirvi/correction/adapters/feedback_sqlite.py`
- **Uses:** `tmp_path` for sqlite.

Tests to write:
1. `suggestion_emitted_when_distinct_shas_gte_3` — 3 rows with same `(ocr_word, expected)`,
   3 distinct `draft_sha` values → suggestion in `rule_suggestions.json`.
2. `suggestion_not_emitted_when_shas_lt_3` — same pair but only 2 distinct shas → no suggestion.
3. `per_sha_contribution_capped_at_1` — 5 rows same pair, same sha → counts as 1.
4. `output_written_to_rule_suggestions_json` — file exists after aggregator run.
5. `confusion_table_missing_raises_typed_error` — missing `confusion_pairs.yaml` →
   `ConfusionTableMissing` (typed, not bare Exception).
6. `feedback_read_port_adapter_reads_by_sha` — insert a `UserRejection` row; assert
   `FeedbackSqliteAdapter.user_rejections(sha)` returns it.
7. `adapter_returns_empty_for_unknown_sha` — no rows for sha → empty iterable.

Run: `uv run pytest tests/unit/test_feedback_aggregator.py -v`

Commit on GREEN: `tdd(N02/F48): T-08 green — FeedbackAggregator rule promotion + sqlite adapter`

---

#### T-09 — Wire cascade into tirvi/pipeline.py
- **Test file:** `tests/unit/test_pipeline.py` (extend existing; do not break existing tests)
- **Source:** `tirvi/pipeline.py`
- **Config knob:** `enable_correction_cascade: bool` (default `True`).

Tests to add (extend test_pipeline.py, do NOT remove existing tests):
1. `cascade_called_between_normalize_and_nakdan` — patch `CorrectionCascadeService.run_page`;
   assert it's called between the normalize step and the Nakdan NLP step.
2. `cascade_disabled_by_config` — `enable_correction_cascade=False` → service not called.
3. `cascade_disabled_does_not_break_pipeline` — existing pipeline tests still pass.
4. `pipeline_returns_correct_token_count` — output token count equals input (token-in/out
   invariant is maintained end-to-end).

Run: `uv run pytest tests/unit/test_pipeline.py -v`

Commit on GREEN: `tdd(N02/F48): T-09 green — cascade wired into pipeline between F14 and F19`

---

#### T-10 — Privacy invariant: no non-localhost outbound during cascade
- **Test file:** `tests/unit/test_privacy_invariant.py`
- **Source:** no new production code; pure invariant test.
- **This is a hard CI gate** (ADR-033). It must pass before the run ends.

Tests to write (the skeleton file is new; write the whole file):
```python
"""T-10 — privacy invariant: cascade must only contact localhost.

AC: F48-S03/AC-01. FT-AUD-03. BT-216. ADR-033.
Hard gate: failure freezes feature ship.
"""
import socket
import pytest
from tirvi.correction.service import CorrectionCascadeService
from tests.unit.conftest import (
    FakeNakdanWordList, FakeLLMClient, FakeFeedbackReader
)

class TestPrivacyInvariant:
    def test_no_non_localhost_outbound(self, monkeypatch, tmp_path):
        outbound_hosts = []

        original_getaddrinfo = socket.getaddrinfo
        def tracking_getaddrinfo(host, *args, **kwargs):
            outbound_hosts.append(host)
            return original_getaddrinfo(host, *args, **kwargs)

        monkeypatch.setattr(socket, "getaddrinfo", tracking_getaddrinfo)

        # run a full cascade page with fakes
        svc = CorrectionCascadeService(
            word_list=FakeNakdanWordList(known={"שלום"}),
            llm_client=FakeLLMClient(),
            feedback_reader=FakeFeedbackReader(),
            draft_sha="test-sha",
            llm_cache_path=tmp_path / "llm_cache.sqlite",
        )
        svc.run_page(tokens=["שלום", "unknown_word"], page_index=0)

        non_local = [h for h in outbound_hosts
                     if h not in ("localhost", "127.0.0.1", "::1", "0.0.0.0")]
        assert non_local == [], f"Non-localhost outbound detected: {non_local}"
```

Run: `uv run pytest tests/unit/test_privacy_invariant.py -v`

Commit on GREEN: `tdd(N02/F48): T-10 green — privacy invariant no non-localhost outbound`

---

### 4. COMMIT FORMAT

```
tdd(N02/F48): T-NN green — <one-line summary>
```

After each GREEN commit, flip the done marker in tasks.md:

```
- [ ] **T-NN done**   →   - [x] **T-NN done**
```

Then add to the commit (use `git add -p` to stage selectively or just `git add tasks.md`).

Commit the done-marker update in the same commit as the green tests and implementation.

---

### 5. TEST COMMANDS

```bash
# Single task
uv run pytest tests/unit/test_correction_ports.py -v
uv run pytest tests/unit/test_nakdan_gate.py -v -m "not slow"
uv run pytest tests/unit/test_mlm_scorer.py -v
uv run pytest tests/unit/test_ollama_client.py -v
uv run pytest tests/unit/test_llm_reviewer.py -v
uv run pytest tests/unit/test_cascade_service.py -v
uv run pytest tests/unit/test_correction_log.py -v
uv run pytest tests/unit/test_health_probe.py -v
uv run pytest tests/unit/test_feedback_aggregator.py -v
uv run pytest tests/unit/test_pipeline.py -v
uv run pytest tests/unit/test_privacy_invariant.py -v

# All F48 tasks together (run after T-10 to verify nothing regressed)
uv run pytest tests/unit/test_correction_ports.py \
              tests/unit/test_nakdan_gate.py \
              tests/unit/test_mlm_scorer.py \
              tests/unit/test_ollama_client.py \
              tests/unit/test_llm_reviewer.py \
              tests/unit/test_cascade_service.py \
              tests/unit/test_correction_log.py \
              tests/unit/test_health_probe.py \
              tests/unit/test_feedback_aggregator.py \
              tests/unit/test_pipeline.py \
              tests/unit/test_privacy_invariant.py \
              -v -m "not slow" 2>&1 | tail -30

# Regression check (full suite, skip slow)
uv run pytest tests/unit/ -v -m "not slow" -q 2>&1 | tail -30
```

---

### 6. sw-dispute.md BOOTSTRAP

Create `.workitems/N02-hebrew-interpretation/F48-correction-cascade/sw-dispute.md`
with this header before you start T-01:

```markdown
# sw-dispute.md — F48 open questions and workarounds

Cloud TDD run. Any design question that required a workaround is logged here
for user review. Medium/Low code-review findings are tagged [GH-ISSUE-NEEDED].

---
```

---

### 7. DONE CRITERIA

The session is complete when:
- [ ] T-01 through T-10 all show `- [x] **T-NN done**` in tasks.md
- [ ] `uv run pytest tests/unit/ -m "not slow" -q` exits green with no skips in the F48 files
- [ ] `sw-dispute.md` exists (even if empty of disputes)
- [ ] All commits follow `tdd(N02/F48): T-NN green — ...` format
- [ ] No `git push` was executed

After the last commit, write a brief session summary to
`.workitems/N02-hebrew-interpretation/F48-correction-cascade/tdd-session-notes.md`:
list every task completed, any disputes logged, any GH issues needed.

---

**Start now with T-01. Do not ask questions. If in doubt, log to sw-dispute.md and continue.**
