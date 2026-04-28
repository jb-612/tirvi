---
name: behavioral-testing
description: Write dual-lens characterization tests — pinning code behavior AND validating product intent. Reads reverse PRD + behavioral spec + ACM graph to produce tests that catch both regressions and intent violations. Part of the Brownfield Refactoring Toolkit.
argument-hint: "<test-scope or feature-name>"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
---

# Behavioral Testing — Dual-Lens Characterization Tests

Write tests for `$ARGUMENTS` that capture both code behavior and product intent.

## Purpose

Traditional characterization tests only pin *what the code does*. This skill
writes **dual-lens tests** that also validate *what the product should do*:

| Lens | Question | Test type | Source |
|------|----------|-----------|--------|
| **Behavior** | What does this code actually do? | Characterization test | Sweep data + ACM |
| **Intent** | What should this feature accomplish? | Intent validation test | Reverse PRD |
| **Gap** | Where do behavior and intent diverge? | Gap test | Both |

## Prerequisites

- **Reverse PRD** exists at `docs/research/reverse-prd.md` (from `reverse-prd` skill)
- **Behavioral spec** exists at `docs/research/behavioral-spec.md` (from `sweep-analytics` skill)
- **ACM graph** is ingested and queryable
- **Sweep output** exists (for observed behavior data)

## Test Categories

### 1. Behavior Tests (`[BEHAVIOR]`)

Pin the exact current behavior of the code. These tests should pass today
and break if refactoring changes behavior — that's their purpose.

```python
class TestBoardEndpointBehavior:
    """BEHAVIOR: pins current /api/board response shape."""

    def test_board_returns_agent_heartbeats(self, api_get):
        """OBSERVED in sweep: /api/board includes heartbeat data."""
        status, data = api_get("/api/board")
        assert status == 200
        # Pin the response shape we observed
        assert "heartbeats" in data or isinstance(data, list)
```

**Source:** Sweep JSON → behavioral spec → ACM code path
**When they break:** Something changed in the code — investigate before committing

### 2. Intent Tests (`[INTENT]`)

Validate that the code fulfills the product intent from the reverse PRD.
These may fail today if the feature is incomplete — that's valuable information.

```python
class TestBoardPageIntent:
    """INTENT: Board page should show real-time agent status (from reverse PRD US-003)."""

    def test_board_includes_agent_status(self, api_get):
        """PRD: 'As an operator, I want to see which agents are active.'"""
        status, data = api_get("/api/board")
        assert status == 200
        # Intent: board should contain agent activity data
        # This validates the PRD user story, not just the API contract

    def test_board_includes_pending_decisions(self, api_get):
        """PRD: 'As an operator, I want to see decisions waiting for my input.'"""
        status, data = api_get("/api/decisions")
        assert status == 200
```

**Source:** Reverse PRD user stories → code path
**When they fail:** Feature is incomplete or intent was never implemented

### 3. Gap Tests (`[GAP]`)

Document known divergences between intent and behavior. These tests are
expected to fail — they mark work that needs to be done.

```python
@pytest.mark.xfail(reason="GAP: PRD says cost per agent should be visible, no UI endpoint exists")
class TestCostTrackingGap:
    """GAP G-002: Cost tracking data exists in DB but no API serves it."""

    def test_cost_endpoint_exists(self, api_get):
        status, data = api_get("/api/costs")
        assert status == 200
```

**Source:** Gap report from reverse PRD
**When they pass:** Gap was closed — remove the xfail marker

## Workflow

### Step 1: Read Sources

```
Read docs/research/reverse-prd.md         → user stories, personas, gaps
Read docs/research/behavioral-spec.md     → endpoint→code mapping
Read sweep-result.json                    → observed interactions
Query ACM for target scope               → code structure, dependencies
```

### Step 2: Map Test Targets

For the specified scope (`$ARGUMENTS`), identify:

1. **Which user stories apply?** (from reverse PRD)
2. **Which endpoints were observed?** (from sweep)
3. **Which code functions handle them?** (from ACM + behavioral spec)
4. **Which gaps affect this scope?** (from gap report)

### Step 3: Write Behavior Tests

For each observed endpoint/interaction in scope:

- Pin the HTTP status code
- Pin the response content type
- Pin key response fields (shape, not values — values change)
- Pin DB side effects if observed in sweep
- Pin SSE events if observed

Naming convention: `test_{feature}_{behavior}_{scenario}`
File location: `tests/characterization/test_{scope}_behavior.py`

### Step 4: Write Intent Tests

For each user story in scope:

- Translate acceptance criteria into pytest assertions
- Reference the PRD story ID in the docstring
- Mark status: `[OBSERVED]` stories get normal tests, `[INFERRED]` get
  `@pytest.mark.skip(reason="Needs user validation")`, `[MISSING]` get
  `@pytest.mark.xfail`

Naming convention: `test_{feature}_{intent}_{story_id}`
File location: `tests/characterization/test_{scope}_intent.py`

### Step 5: Write Gap Tests

For each gap in scope:

- Write the test that *would* pass if the gap were closed
- Mark with `@pytest.mark.xfail(reason="GAP G-NNN: description")`
- Include the gap ID and description in the docstring

File location: `tests/characterization/test_{scope}_gaps.py`

### Step 6: Create Test Index

Write `tests/characterization/README.md` documenting:

| Test File | Category | Stories Covered | Status |
|-----------|----------|-----------------|--------|
| test_board_behavior.py | BEHAVIOR | - | 16/16 pass |
| test_board_intent.py | INTENT | US-001, US-003 | 8/10 pass |
| test_board_gaps.py | GAP | G-001, G-002 | 0/3 pass (xfail) |

### Step 7: Run and Report

```bash
# All characterization tests
python -m pytest tests/characterization/ -v

# Only behavior tests (should all pass)
python -m pytest tests/characterization/ -k "behavior" -v

# Only intent tests (may have failures)
python -m pytest tests/characterization/ -k "intent" -v

# Only gap tests (expected failures)
python -m pytest tests/characterization/ -k "gap" -v --runxfail
```

Report:
- Behavior tests: X/Y passing (regression risk if any fail)
- Intent tests: X/Y passing (incomplete features if any fail)
- Gap tests: X/Y xfail (known work items)
- Total coverage delta: before → after

## Test Infrastructure

### Shared Fixtures (`tests/characterization/conftest.py`)

```python
@pytest.fixture
def api_get():
    """GET request helper — skips if dashboard not running."""
    ...

@pytest.fixture
def api_post():
    """POST request helper with JSON body."""
    ...

@pytest.fixture
def db_snapshot(tmp_path):
    """Read-only SQLite snapshot for DB state assertions."""
    ...

@pytest.fixture
def sweep_data():
    """Load sweep result JSON for reference in tests."""
    ...
```

### Mock Infrastructure (for unit-level behavior tests)

| Mock | Interface | For testing |
|------|-----------|-------------|
| `MockMailboxDB` | SQLite in-memory with schema | DB query/write functions |
| `MockSubprocess` | Captures CLI commands | Agent dispatch logic |
| `MockSlackClient` | Records API calls | Slack integration |
| `MockConfigLoader` | Returns test YAML | Config parsing |

## Output Files

| File | Content |
|------|---------|
| `tests/characterization/test_{scope}_behavior.py` | Behavior-pinning tests |
| `tests/characterization/test_{scope}_intent.py` | Intent validation tests |
| `tests/characterization/test_{scope}_gaps.py` | Gap documentation tests |
| `tests/characterization/conftest.py` | Shared fixtures |
| `tests/characterization/README.md` | Test index with coverage |

## Integration with Refactoring

During Phase 3 refactoring:
- **Behavior tests protect against regressions** — if one fails, the refactor changed behavior
- **Intent tests guide the refactor** — if an intent test starts passing after refactoring, you fixed a gap
- **Gap tests track progress** — as gaps close, remove xfail markers
- **Re-run sweep after refactoring** — compare before/after behavioral specs
