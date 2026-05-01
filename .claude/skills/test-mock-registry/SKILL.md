---
name: test-mock-registry
description: Generate canonical fake implementations (working in-memory test doubles) from port interfaces in the hexagonal architecture. Maintains a shared fake registry in pkg/testutil/fakes/ that all test-writing skills import from.
user-invocable: true
argument-hint: "[port-name | all]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Role

You are a test infrastructure engineer who generates canonical fake
implementations from port interfaces in the hexagonal architecture. You produce
working in-memory implementations — not mocks that record calls, not stubs that
return fixed values. Fakes have real (simplified) logic that exercises actual
behavior paths.

# Fake vs Mock vs Stub (Critical Distinction)

| Type | Behavior | Example | This Skill? |
|------|----------|---------|-------------|
| **Fake** | Working implementation with simplified internals | In-memory map instead of SQLite | YES |
| **Mock** | Records calls, asserts on call sequence | `mock.AssertCalled(t, "Get", id)` | NO |
| **Stub** | Returns hardcoded values, no logic | `return nil, nil` always | NO |

This skill generates **fakes only**. Fakes are preferred per the project's
Chicago-school testing philosophy. They allow tests to exercise real behavior
paths without coupling to call sequences.

# When to Use

- After port interfaces are defined in `internal/core/port/`
- When a new port is added or an existing port's method signature changes
- Before running `@tdd-go`, `@test-functional`, or `@integration-test` on
  features that depend on ports
- When a test file imports from `pkg/testutil/fakes/` and the fake is missing
- To regenerate the entire fake registry: `/test-mock-registry all`
- To generate or update a single fake: `/test-mock-registry repository`

# When NOT to Use

- Writing test logic or assertions (use `@tdd-go`, `@test-functional`)
- Designing which tests to write (use `@test-design`)
- Creating one-off test helpers specific to a single test file (put those
  in the test file itself or a `_test.go` helper in the same package)
- Building adapter implementations (those go in `internal/adapter/`)
- Generating mocks that record call sequences (use `gomock` or `testify/mock`
  directly in the rare cases London-school mocks are needed)

# Relationship to Other Skills

```
test-mock-registry (THIS SKILL)   -- produces pkg/testutil/fakes/*.go
    |
    |-- consumed-by --> tdd-go              -- imports fakes for unit tests
    |-- consumed-by --> tdd-workflow        -- language-agnostic TDD engine
    |-- consumed-by --> integration-test    -- imports fakes for boundary tests
    |-- consumed-by --> test-functional     -- imports fakes for functional tests
    |
    |-- reads-from --> internal/core/port/  -- source of truth for interfaces
    |-- validates-with --> testing          -- go build + go vet verification
```

# Instructions

## Step 1: Scan Port Interfaces

Use the Glob tool with pattern `internal/core/port/**/*.go` to find all port
files. Exclude any `*_test.go` matches.

For each file, extract every `type ... interface` definition. Record:
- Interface name (e.g., `Repository`, `EventBus`, `Dispatcher`)
- Method signatures (name, params, return types)
- Any embedded interfaces
- Import paths needed by method signatures

If `$ARGUMENTS` specifies a single port name, filter to only that interface.
If `$ARGUMENTS` is `all` or empty, process every port interface found.

## Step 2: Check Existing Fakes

Use the Glob tool with pattern `pkg/testutil/fakes/*.go` to find existing fakes.

For each existing fake, compare its method set against the current port
interface. Identify:
- **Missing fakes**: Port exists but no corresponding fake file
- **Stale fakes**: Fake exists but methods don't match current interface
- **Current fakes**: Fake matches interface exactly (skip these)

Report the delta before generating.

## Step 3: Generate Fakes

For each port that needs a new or updated fake, generate a file following
the canonical pattern below.

### Output Location

```
pkg/testutil/fakes/fake_{port_name_snake}.go
```

One file per port interface. Package name: `fakes`.

### Canonical Fake Structure

Every generated fake follows this structure:

```go
package fakes

import (
    "sync"

    "github.com/<org>/<project>/internal/core/domain"
    "github.com/<org>/<project>/internal/core/port"
)

// Compile-time interface check.
var _ port.Repository = (*FakeRepository)(nil)

// FakeRepository is a working in-memory implementation of port.Repository
// for use in tests. It stores data in maps, supports error injection via
// SetError, and is safe for concurrent use in parallel tests.
type FakeRepository struct {
    mu     sync.RWMutex
    errors map[string]error // method name -> error to return

    // State — one field per logical collection
    items map[string]domain.Item
}

// NewFakeRepository creates a FakeRepository with initialized internal state.
func NewFakeRepository() *FakeRepository {
    return &FakeRepository{
        errors: make(map[string]error),
        items:  make(map[string]domain.Item),
    }
}

// ---------------------------------------------------------------------------
// Error injection
// ---------------------------------------------------------------------------

// SetError configures the fake to return err when methodName is called.
// Pass nil to clear a previously set error. Thread-safe.
func (f *FakeRepository) SetError(methodName string, err error) {
    f.mu.Lock()
    defer f.mu.Unlock()
    if err == nil {
        delete(f.errors, methodName)
    } else {
        f.errors[methodName] = err
    }
}

// getError returns the injected error for methodName, or nil.
func (f *FakeRepository) getError(methodName string) error {
    f.mu.RLock()
    defer f.mu.RUnlock()
    return f.errors[methodName]
}

// ---------------------------------------------------------------------------
// Port interface methods
// ---------------------------------------------------------------------------

func (f *FakeRepository) GetItem(id string) (domain.Item, error) {
    if err := f.getError("GetItem"); err != nil {
        return domain.Item{}, err
    }
    f.mu.RLock()
    defer f.mu.RUnlock()
    item, ok := f.items[id]
    if !ok {
        return domain.Item{}, port.ErrNotFound
    }
    return item, nil
}

func (f *FakeRepository) SaveItem(item domain.Item) error {
    if err := f.getError("SaveItem"); err != nil {
        return err
    }
    f.mu.Lock()
    defer f.mu.Unlock()
    f.items[item.ID] = item
    return nil
}

func (f *FakeRepository) DeleteItem(id string) error {
    if err := f.getError("DeleteItem"); err != nil {
        return err
    }
    f.mu.Lock()
    defer f.mu.Unlock()
    delete(f.items, id)
    return nil
}

func (f *FakeRepository) ListItems() ([]domain.Item, error) {
    if err := f.getError("ListItems"); err != nil {
        return nil, err
    }
    f.mu.RLock()
    defer f.mu.RUnlock()
    result := make([]domain.Item, 0, len(f.items))
    for _, item := range f.items {
        result = append(result, item)
    }
    return result, nil
}

// ---------------------------------------------------------------------------
// Test helpers (not part of the port interface)
// ---------------------------------------------------------------------------

// Reset clears all stored state and injected errors. Call between test cases
// or in t.Cleanup to prevent state leakage.
func (f *FakeRepository) Reset() {
    f.mu.Lock()
    defer f.mu.Unlock()
    f.items = make(map[string]domain.Item)
    f.errors = make(map[string]error)
}

// SeedItems populates the fake with the given items for test setup.
func (f *FakeRepository) SeedItems(items ...domain.Item) {
    f.mu.Lock()
    defer f.mu.Unlock()
    for _, item := range items {
        f.items[item.ID] = item
    }
}

// Count returns the number of stored items (useful for assertions).
func (f *FakeRepository) Count() int {
    f.mu.RLock()
    defer f.mu.RUnlock()
    return len(f.items)
}
```

### Fake Pattern: Event Bus Port

For event/message-passing ports, use a channel-based approach:

```go
package fakes

import (
    "context"
    "sync"

    "github.com/<org>/<project>/internal/core/domain"
    "github.com/<org>/<project>/internal/core/port"
)

var _ port.EventBus = (*FakeEventBus)(nil)

// FakeEventBus is a working in-memory event bus that captures published
// events and delivers them to subscribers. Uses channels for delivery.
type FakeEventBus struct {
    mu          sync.RWMutex
    errors      map[string]error
    published   []domain.Event
    subscribers map[string][]chan domain.Event // topic -> channels
}

func NewFakeEventBus() *FakeEventBus {
    return &FakeEventBus{
        errors:      make(map[string]error),
        published:   make([]domain.Event, 0),
        subscribers: make(map[string][]chan domain.Event),
    }
}

func (f *FakeEventBus) SetError(methodName string, err error) {
    f.mu.Lock()
    defer f.mu.Unlock()
    if err == nil {
        delete(f.errors, methodName)
    } else {
        f.errors[methodName] = err
    }
}

func (f *FakeEventBus) getError(methodName string) error {
    f.mu.RLock()
    defer f.mu.RUnlock()
    return f.errors[methodName]
}

func (f *FakeEventBus) Publish(ctx context.Context, event domain.Event) error {
    if err := f.getError("Publish"); err != nil {
        return err
    }
    f.mu.Lock()
    f.published = append(f.published, event)
    // Copy subscriber slice to avoid race with concurrent Subscribe calls
    subs := make([]chan domain.Event, len(f.subscribers[event.Topic]))
    copy(subs, f.subscribers[event.Topic])
    f.mu.Unlock()

    for _, ch := range subs {
        select {
        case ch <- event:
        case <-ctx.Done():
            return ctx.Err()
        }
    }
    return nil
}

func (f *FakeEventBus) Subscribe(topic string) (<-chan domain.Event, error) {
    if err := f.getError("Subscribe"); err != nil {
        return nil, err
    }
    ch := make(chan domain.Event, 100)
    f.mu.Lock()
    defer f.mu.Unlock()
    f.subscribers[topic] = append(f.subscribers[topic], ch)
    return ch, nil
}

// --- Test helpers ---

func (f *FakeEventBus) Reset() {
    f.mu.Lock()
    defer f.mu.Unlock()
    f.published = make([]domain.Event, 0)
    for topic, chs := range f.subscribers {
        for _, ch := range chs {
            close(ch)
        }
        delete(f.subscribers, topic)
    }
    f.errors = make(map[string]error)
}

// Published returns a copy of all published events for assertions.
func (f *FakeEventBus) Published() []domain.Event {
    f.mu.RLock()
    defer f.mu.RUnlock()
    out := make([]domain.Event, len(f.published))
    copy(out, f.published)
    return out
}

// Drain reads all pending events from a subscription channel with no blocking.
// Handles closed channels gracefully.
func (f *FakeEventBus) Drain(ch <-chan domain.Event) []domain.Event {
    var events []domain.Event
    for {
        select {
        case e, ok := <-ch:
            if !ok {
                return events
            }
            events = append(events, e)
        default:
            return events
        }
    }
}
```

### Fake Pattern: Dispatcher Port

For ports that dispatch commands or actions. Note: the `dispatched` slice
captures commands for test assertions — this is for verifying the system's
observable behavior, not for mock-style call-sequence verification.

```go
package fakes

import (
    "context"
    "sync"

    "github.com/<org>/<project>/internal/core/domain"
    "github.com/<org>/<project>/internal/core/port"
)

var _ port.Dispatcher = (*FakeDispatcher)(nil)

// FakeDispatcher is a working in-memory dispatcher that records dispatched
// commands and returns configurable results.
type FakeDispatcher struct {
    mu         sync.RWMutex
    errors     map[string]error
    dispatched []domain.Command
    results    map[string]domain.DispatchResult // command type -> result
}

func NewFakeDispatcher() *FakeDispatcher {
    return &FakeDispatcher{
        errors:     make(map[string]error),
        dispatched: make([]domain.Command, 0),
        results:    make(map[string]domain.DispatchResult),
    }
}

func (f *FakeDispatcher) SetError(methodName string, err error) {
    f.mu.Lock()
    defer f.mu.Unlock()
    if err == nil {
        delete(f.errors, methodName)
    } else {
        f.errors[methodName] = err
    }
}

func (f *FakeDispatcher) getError(methodName string) error {
    f.mu.RLock()
    defer f.mu.RUnlock()
    return f.errors[methodName]
}

func (f *FakeDispatcher) Dispatch(ctx context.Context, cmd domain.Command) (domain.DispatchResult, error) {
    if err := f.getError("Dispatch"); err != nil {
        return domain.DispatchResult{}, err
    }
    f.mu.Lock()
    f.dispatched = append(f.dispatched, cmd)
    result, ok := f.results[cmd.Type]
    f.mu.Unlock()

    if !ok {
        return domain.DispatchResult{Status: "completed"}, nil
    }
    return result, nil
}

// --- Test helpers ---

func (f *FakeDispatcher) Reset() {
    f.mu.Lock()
    defer f.mu.Unlock()
    f.dispatched = make([]domain.Command, 0)
    f.results = make(map[string]domain.DispatchResult)
    f.errors = make(map[string]error)
}

// SetResult configures the result returned when a command of the given type
// is dispatched. Useful for testing success/failure handling paths.
func (f *FakeDispatcher) SetResult(cmdType string, result domain.DispatchResult) {
    f.mu.Lock()
    defer f.mu.Unlock()
    f.results[cmdType] = result
}

// Dispatched returns a copy of all dispatched commands for assertions.
func (f *FakeDispatcher) Dispatched() []domain.Command {
    f.mu.RLock()
    defer f.mu.RUnlock()
    out := make([]domain.Command, len(f.dispatched))
    copy(out, f.dispatched)
    return out
}
```

### Fake Pattern: Config Port

For configuration/settings ports:

```go
package fakes

import (
    "sync"

    "github.com/<org>/<project>/internal/core/port"
)

var _ port.ConfigProvider = (*FakeConfigProvider)(nil)

// FakeConfigProvider is a working in-memory config store backed by a
// map[string]string. Supports error injection and dynamic value changes.
type FakeConfigProvider struct {
    mu     sync.RWMutex
    errors map[string]error
    values map[string]string
}

func NewFakeConfigProvider() *FakeConfigProvider {
    return &FakeConfigProvider{
        errors: make(map[string]error),
        values: make(map[string]string),
    }
}

func (f *FakeConfigProvider) SetError(methodName string, err error) {
    f.mu.Lock()
    defer f.mu.Unlock()
    if err == nil {
        delete(f.errors, methodName)
    } else {
        f.errors[methodName] = err
    }
}

func (f *FakeConfigProvider) getError(methodName string) error {
    f.mu.RLock()
    defer f.mu.RUnlock()
    return f.errors[methodName]
}

func (f *FakeConfigProvider) Get(key string) (string, error) {
    if err := f.getError("Get"); err != nil {
        return "", err
    }
    f.mu.RLock()
    defer f.mu.RUnlock()
    val, ok := f.values[key]
    if !ok {
        return "", port.ErrConfigKeyNotFound
    }
    return val, nil
}

func (f *FakeConfigProvider) GetAll() (map[string]string, error) {
    if err := f.getError("GetAll"); err != nil {
        return nil, err
    }
    f.mu.RLock()
    defer f.mu.RUnlock()
    out := make(map[string]string, len(f.values))
    for k, v := range f.values {
        out[k] = v
    }
    return out, nil
}

// --- Test helpers ---

func (f *FakeConfigProvider) Reset() {
    f.mu.Lock()
    defer f.mu.Unlock()
    f.values = make(map[string]string)
    f.errors = make(map[string]error)
}

// Seed populates config values for test setup.
func (f *FakeConfigProvider) Seed(pairs map[string]string) {
    f.mu.Lock()
    defer f.mu.Unlock()
    for k, v := range pairs {
        f.values[k] = v
    }
}
```

### Mandatory Elements Checklist

Every generated fake MUST include:

1. **Compile-time check**: `var _ port.X = (*FakeX)(nil)`
2. **sync.RWMutex**: field named `mu`
3. **errors map**: `errors map[string]error` for injection
4. **Constructor**: `NewFakeX() *FakeX` that initializes all maps/slices
5. **SetError method**: `SetError(methodName string, err error)`
6. **getError method**: `getError(methodName string) error` (unexported)
7. **Every interface method**: with error injection check as first line
8. **Reset method**: clears all state and errors
9. **Seed/helper methods**: at least one method to populate test data
10. **GoDoc comments**: on the type, constructor, and public helpers

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| File name | `fake_{port_name_snake}.go` | `fake_repository.go` |
| Struct | `Fake{PortName}` | `FakeRepository` |
| Constructor | `NewFake{PortName}()` | `NewFakeRepository()` |
| Error injector | `SetError(methodName, err)` | universal |
| State reset | `Reset()` | universal |
| Seed helper | `Seed{Collection}(items...)` | `SeedItems(items...)` |
| Count helper | `Count()` or `{Collection}Count()` | `Count()` |
| Snapshot helper | `{Collection}()` (returns copy) | `Published()` |

### Concurrency Safety Rules

All fakes MUST be safe for `t.Parallel()`:

1. Use `sync.RWMutex` — read lock for reads, write lock for mutations
2. `getError` uses `RLock` (read path)
3. `SetError`, `Reset`, `Seed*` use `Lock` (write path)
4. Interface methods that only read use `RLock`
5. Interface methods that mutate use `Lock`
6. Return copies of slices/maps from snapshot helpers, never internal state
7. Channel operations in event bus fakes must not hold the mutex during
   blocking sends — copy subscriber list under lock, release, then send

### Cyclomatic Complexity

Every function in generated fakes must have CC <= 5. The patterns above
naturally stay within this limit. If a port method requires branching logic
that would exceed CC 5, split into helper functions.

## Step 4: Verify Compilation

After generating or updating fakes, verify they compile:

```bash
go build ./pkg/testutil/fakes/
go vet ./pkg/testutil/fakes/
```

If compilation fails, read the error output, fix import paths or type
mismatches, and re-verify until clean.

## Step 5: Report

Print a summary after generation:

```
Fake Registry Update
====================
Scanned ports:      {count} interfaces in internal/core/port/
Existing fakes:     {count} in pkg/testutil/fakes/
Generated (new):    {count} fakes
Updated (changed):  {count} fakes
Skipped (current):  {count} fakes
Compilation:        PASS / FAIL

Details:
  fake_repository.go       NEW     5 methods   port.Repository
  fake_event_bus.go        UPDATED 3 methods   port.EventBus (+Subscribe)
  fake_config_provider.go  CURRENT 2 methods   port.ConfigProvider

Consumers can import:
  import "github.com/<org>/<project>/pkg/testutil/fakes"
```

# Update Protocol

When a port interface changes (method added, removed, or signature changed):

1. Run `/test-mock-registry {port-name}` to regenerate just that fake
2. The skill diffs the old fake against the new interface:
   - **Added method**: Generate the method body following the pattern above
   - **Removed method**: Delete the method from the fake
   - **Changed signature**: Update the method signature and adjust internal logic
3. Preserve custom seed/helper methods that were manually added (anything
   below the `// --- Test helpers ---` separator that isn't part of the
   standard Reset/Seed pattern)
4. Re-verify compilation: `go build ./pkg/testutil/fakes/`
5. Run all tests that import the fake to catch breakage:
   Use the Grep tool to find files importing `testutil/fakes`, then run
   `go test` on the containing packages.

# Error Injection Pattern (Detailed)

The `SetError` / `getError` pattern enables testing error-handling paths
without creating separate error-returning fake types:

```go
// In test setup — simulate a database failure on GetItem:
repo := fakes.NewFakeRepository()
repo.SeedItems(domain.Item{ID: "1", Name: "test"})
repo.SetError("GetItem", errors.New("connection lost"))

// Now any call to repo.GetItem will return the injected error:
_, err := service.GetItem(ctx, "1")
require.ErrorContains(t, err, "connection lost")

// Clear the error to resume normal behavior:
repo.SetError("GetItem", nil)
item, err := service.GetItem(ctx, "1")
require.NoError(t, err)
assert.Equal(t, "test", item.Name)
```

Every interface method checks for an injected error as its first operation,
before touching any internal state. This ensures error injection is:
- **Atomic**: Uses the mutex, safe for parallel tests
- **Selective**: Only the named method returns the error
- **Reversible**: Pass `nil` to clear
- **Non-destructive**: Internal state is unchanged when an error is injected

# Cross-References

- `@tdd-go` — Consumes fakes for unit tests
- `@tdd-workflow` — Language-agnostic TDD engine, consumes fakes
- `@test-design` — Designs tests that specify which ports need fakes
- `@integration-test` — Consumes fakes for cross-boundary tests
- `@testing` — Runs `go build` / `go vet` verification on fake package
- `@test-functional` — Consumes fakes for functional/smoke/regression tests
- `internal/core/port/` — Source of truth for all port interfaces
- `pkg/testutil/fakes/` — Output directory for all generated fakes
