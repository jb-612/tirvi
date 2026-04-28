---
paths:
  - "tests/**/*.py"
---

# Testing Rules

## Unit Tests (tests/unit/)

1. Use `@pytest.mark.asyncio` for all async test functions
2. Test daemon functions by passing config dicts and mock dependencies:
   ```python
   async def test_scheduler_dispatch():
       config = {"dispatch_order": ["cursor", "claude"]}
       mock_db = AsyncMock()
       result = await dispatch(config, mock_db)
       assert result.status == "ok"
   ```
3. Mock external services using `unittest.mock.AsyncMock` and `unittest.mock.patch`
4. NEVER call live API endpoints — use mocks for Slack SDK, aiohttp, subprocess
5. Use `@pytest.fixture` for reusable test data (configs, mock DBs)
6. Use `@pytest.mark.parametrize` for table-driven tests
7. Test error paths: what happens when API fails, config is missing, DB is locked

## Integration Tests (tests/integration/)

8. Mock HTTP calls, do not call real APIs
9. Test multi-step flows: config load → process → state update → output
10. Use temporary directories for file I/O tests (`tmp_path` fixture)
11. Use in-memory SQLite for database tests

## Characterization Tests

12. Characterization tests capture CURRENT behavior (including bugs)
13. Name them clearly: `test_<function>_current_behavior_<scenario>`
14. Add a comment if the test captures known-wrong behavior:
    ```python
    # CHARACTERIZATION: captures current behavior; known bug — truncates at 200 chars
    def test_processor_truncates_description():
        ...
    ```
15. Do NOT fix bugs in characterization tests — that's for refactoring phase

## Fixtures and Mocks

16. Shared fixtures in `tests/conftest.py`
17. Domain-specific fixtures in `tests/unit/conftest.py` or `tests/integration/conftest.py`
18. Mock infrastructure (MockSlackClient, MockMailboxDB) in `tests/mocks/`
19. Test data files in `tests/fixtures/` (JSON configs, YAML samples)

## General

20. Every test function must have a clear assertion — no test without assert
21. One concept per test — don't test multiple behaviors in one function
22. Tests must be deterministic — no reliance on time, network, or ordering
23. Fast tests: unit tests should complete in < 1 second each
