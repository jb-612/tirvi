---
name: sweep-analytics
description: Analyze Runtime Sweep output — correlate with ACM knowledge graph, produce behavioral specifications and characterization test templates. Use after running sweep-observ against a target application.
argument-hint: "<sweep-output-dir>"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
---

# Sweep Analytics — Runtime Behavior Correlation

Analyze sweep results at `$ARGUMENTS` and correlate with the ACM knowledge graph.

## Prerequisites

- Runtime Sweep output exists at the specified path (contains `data/sweep-result.json`)
- ACM MCP server is configured and running (FalkorDB + Redis)
- ACM has been ingested for the target project (`acm ingest`)

## Step 1: Load and Summarize Sweep Data

Read `<sweep-output-dir>/data/sweep-result.json` and extract:

1. **Pages discovered** — list all URLs with element counts
2. **API catalog** — unique (method, path, status) tuples with frequency
3. **DB mutations** — tables modified, operations per table
4. **SSE events** — event types and frequencies
5. **Interaction count** — total clicks/actions performed

Print a summary table to the user before proceeding.

## Step 2: Correlate API Endpoints with Code

For each unique API endpoint found in the sweep:

```
acm_query_router(query="what code handles {METHOD} {PATH}", persona="code")
```

Build a mapping table:

| HTTP Endpoint | Handler Function | ACM Node ID | Module |
|---------------|-----------------|-------------|--------|
| GET /api/agents | `_get_agents()` | fn:server:_get_agents | server.py |
| POST /api/chat | `_post_chat()` | fn:server:_post_chat | server.py |

If ACM returns no result for an endpoint, mark it as **unmapped** — this
indicates either missing ingestion or dead code.

## Step 3: Correlate DB Mutations with Code

For each table that was mutated during the sweep:

```
acm_search(pattern="{table_name}", layer="code")
```

Build a mapping:

| Table | Operations | Writer Functions | ACM Node IDs |
|-------|-----------|-----------------|-------------|
| heartbeats | INSERT, UPDATE | `_write_heartbeat()` | fn:server:_write_heartbeat |
| messages | INSERT | `_post_respond()` | fn:server:_post_respond |

## Step 4: Map UI Pages to Code

For each discovered page (hash route):

```
acm_query_router(query="code for {page_name} page rendering", persona="code")
```

Identify which functions render each page's data.

## Step 5: Trace Coverage Gaps

For the top-10 highest-centrality functions (from ACM graph analysis):

```
acm_trace(node_id="{function_node_id}")
```

Check if the function appeared in any sweep interaction. Functions that are
high-centrality but never triggered during the sweep are **behavioral blind
spots** — critical code that the sweep didn't exercise.

## Step 6: Generate Behavioral Specification

Write `docs/research/behavioral-spec.md` with:

```markdown
# Behavioral Specification — {Target App}

## Page: {page_name}

### Element: {role} "{name}"

**Action:** click
**Triggered API calls:**
- GET /api/summary → 200 (42ms)
- GET /api/agents → 200 (38ms)

**Database effects:**
- heartbeats: UPDATE row 3 (status: idle → active)

**SSE events:**
- change: {"tables": ["heartbeats"]}

**Code path:**
- Handler: fn:server:_get_summary (server.py:245)
- DB write: fn:server:_write_heartbeat (server.py:150)
- Called by: fn:server:do_GET (server.py:3405)
```

## Step 7: Generate Characterization Test Templates

Write test files to `tests/characterization/` — one file per page:

```python
"""Characterization tests for Board page — pins observed runtime behavior."""

import pytest

class TestBoardPage:
    """Tests pinning Board page behavior as observed by Runtime Sweep."""

    def test_refresh_button_calls_summary_api(self, client):
        """OBSERVED: clicking Refresh triggers GET /api/summary → 200."""
        response = client.get("/api/summary")
        assert response.status_code == 200

    def test_refresh_button_updates_heartbeats(self, db):
        """OBSERVED: clicking Refresh updates heartbeats table."""
        before = db.execute("SELECT * FROM heartbeats").fetchall()
        # Trigger the action (via API or direct function call)
        # ...
        after = db.execute("SELECT * FROM heartbeats").fetchall()
        assert len(after) >= len(before)
```

Mark each test with a comment indicating it was auto-generated from sweep data:
`# SWEEP-GENERATED: from sweep-output/<timestamp>`

## Step 8: Summary Report

Print to the user:

- Total API endpoints mapped: X/Y (Z unmapped)
- Total DB tables correlated: X/Y
- Behavioral blind spots: list of high-centrality functions not observed
- Characterization tests generated: N files, M test functions
- Recommended next steps (which blind spots to investigate, which tests to run first)

## Output Files

| File | Content |
|------|---------|
| `docs/research/behavioral-spec.md` | Full behavioral specification |
| `tests/characterization/test_{page}.py` | Characterization test templates per page |
| Console output | Summary table + recommendations |

## Tips

- Run with `--verbose` in the sweep to capture more interaction detail
- If ACM returns poor results, re-ingest with updated `ACM_SOURCE_DIRS`
- For large sweeps (100+ pages), focus Steps 2-4 on the top-20 most-called endpoints
- The behavioral spec is a living document — re-generate after each sweep
