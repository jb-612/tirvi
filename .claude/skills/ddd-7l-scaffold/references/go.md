# Go reference shapes for ddd-7l-scaffold

Idiomatic Go: interfaces (no `I` prefix), struct types for value objects,
`panic("not implemented")` for stubs, `func TestXxx(t *testing.T)` with
table-driven subtests, typed errors implementing `error`. Adapt to the
project's actual conventions discovered in L1 inspection.

---

## L1 — Folder layout

```
<repo-root>/
    pkg/<bounded_context>/
        domain/
            aggregate.go              # aggregate root
            entity.go
            value_object.go
            event.go
            policy.go
            errors.go
        application/
            command.go
            usecase.go                # interface + impl
            ports.go                  # repository, gateway interfaces
            result.go
        infrastructure/
            inmemory_repository.go
            sqlrepository.go          # deferred to TDD
        interface/
            http_routes.go
    cmd/<binary>/
        main.go                       # composition root
    pkg/<bounded_context>/
        aggregate_test.go             # _test.go co-located
        usecase_test.go
    pkg/testutil/fakes/
        loan_application_repository_fake.go
```

Co-locate `*_test.go` with source per Go convention. Tirvi has no Go code
today — this reference is for portability to Go projects.

---

## L2 — Contract shapes (interfaces, command, result, errors)

```go
// pkg/lending/application/usecase.go
package application

import "context"

// ApproveLoanUseCase. AC: AC-LOAN-003.
type ApproveLoanUseCase interface {
    Execute(ctx context.Context, cmd ApproveLoanCommand) (ApproveLoanResult, error)
}

// pkg/lending/application/command.go
package application

import "github.com/example/lending/domain"

type ApproveLoanCommand struct {
    LoanApplicationID domain.LoanApplicationID
    RequestedBy       UserID
}

// pkg/lending/application/result.go
package application

import "github.com/example/lending/domain"

type ApproveLoanResultStatus int

const (
    StatusApproved ApproveLoanResultStatus = iota + 1
    StatusRejected
)

type ApproveLoanResult struct {
    Status   ApproveLoanResultStatus
    LoanID   domain.LoanID            // populated when Status == StatusApproved
    Reasons  []domain.RejectionReason  // populated when Status == StatusRejected
}

// pkg/lending/application/ports.go
package application

import (
    "context"
    "github.com/example/lending/domain"
)

type LoanApplicationRepository interface {
    FindByID(ctx context.Context, id domain.LoanApplicationID) (*domain.LoanApplication, error)
    Save(ctx context.Context, aggregate *domain.LoanApplication) error
}

type BorrowerRepository interface {
    FindByID(ctx context.Context, id domain.BorrowerID) (*domain.Borrower, error)
}

type DomainEventPublisher interface {
    Publish(ctx context.Context, events ...domain.DomainEvent) error
}
```

---

## L3 — Domain shapes (aggregate, VO, event, errors)

```go
// pkg/lending/domain/value_object.go
package domain

import "errors"

// LoanApplicationID value object. AC: AC-LOAN-001.
type LoanApplicationID struct {
    value string
}

func NewLoanApplicationID(value string) (LoanApplicationID, error) {
    if value == "" {
        return LoanApplicationID{}, errors.New("LoanApplicationID cannot be empty")
    }
    return LoanApplicationID{value: value}, nil
}

func (id LoanApplicationID) String() string { return id.value }


// pkg/lending/domain/aggregate.go
package domain

// LoanApplication aggregate root.
//
// Invariants (named, not implemented — TDD fills these in):
//   - INV-LA-001 (AC-LOAN-003): only pending applications may be approved
//   - INV-LA-002 (AC-LOAN-004): rejected applications must include >= 1 reason
type LoanApplication struct {
    id              LoanApplicationID
    borrowerID      BorrowerID
    requestedAmount Money
    status          LoanApplicationStatus
}

type LoanApplicationStatus int

const (
    StatusPending LoanApplicationStatus = iota + 1
    StatusApproved
    StatusRejected
)

func SubmitLoanApplication(cmd SubmitLoanApplicationCommand) (*LoanApplication, error) {
    // TODO AC-LOAN-001: enforce requested amount eligibility invariant
    // TODO AC-LOAN-002: emit LoanApplicationSubmitted event
    panic("not implemented")
}

func (a *LoanApplication) Approve(decision ApprovalDecision) error {
    // TODO AC-LOAN-003: only pending applications may be approved
    // TODO AC-LOAN-004: emit LoanApproved event
    panic("not implemented")
}


// pkg/lending/domain/event.go
package domain

import "time"

// DomainEvent base type.
type DomainEvent interface {
    OccurredAt() time.Time
}

// LoanApproved domain event. Emitted by LoanApplication.Approve(). AC: AC-LOAN-003.
type LoanApproved struct {
    LoanApplicationID LoanApplicationID
    DecidedAt         time.Time
}

func (e LoanApproved) OccurredAt() time.Time { return e.DecidedAt }


// pkg/lending/domain/errors.go
package domain

import "errors"

// ErrLoanNotPending: INV-LA-001 (AC-LOAN-003).
var ErrLoanNotPending = errors.New("loan application is not pending")
```

---

## L4 — Test skeleton shapes (table-driven, t.Skip)

```go
// pkg/lending/application/usecase_test.go
package application

import (
    "context"
    "testing"
)

func TestApproveLoanUseCase_AcLoan003_OnlyPendingApplicationsMayBeApproved(t *testing.T) {
    t.Skip("scaffold — implement in TDD phase")

    tests := []struct {
        name string
        // Given
        existingStatus LoanApplicationStatus
        // Then
        wantErr        error
        wantEvents     int
    }{
        {
            name:           "rejects approval when loan application is already rejected",
            existingStatus: StatusRejected,
            wantErr:        domain.ErrLoanNotPending,
            wantEvents:     0,
        },
        {
            name:           "rejects approval when loan application is already approved",
            existingStatus: StatusApproved,
            wantErr:        domain.ErrLoanNotPending,
            wantEvents:     0,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // Given:  ...
            // When:   ...
            // Then:   ...
            // And:    no LoanApproved event is emitted
            // And:    no approval audit record is written
        })
    }
}
```

---

## L5 — TDD shell shapes (DI, fakes, fixtures)

```go
// pkg/lending/application/usecase_impl.go
package application

import (
    "context"
    "github.com/example/lending/domain"
)

type ApproveLoanUseCaseImpl struct {
    loanApplications  LoanApplicationRepository
    borrowers         BorrowerRepository
    eligibilityPolicy domain.BorrowerEligibilityPolicy
    events            DomainEventPublisher
    audit             AuditLog
}

func NewApproveLoanUseCase(
    loanApplications LoanApplicationRepository,
    borrowers BorrowerRepository,
    eligibilityPolicy domain.BorrowerEligibilityPolicy,
    events DomainEventPublisher,
    audit AuditLog,
) ApproveLoanUseCase {
    return &ApproveLoanUseCaseImpl{
        loanApplications:  loanApplications,
        borrowers:         borrowers,
        eligibilityPolicy: eligibilityPolicy,
        events:            events,
        audit:             audit,
    }
}

func (u *ApproveLoanUseCaseImpl) Execute(ctx context.Context, cmd ApproveLoanCommand) (ApproveLoanResult, error) {
    // TODO AC-LOAN-001: load loan application
    // TODO AC-LOAN-002: verify borrower exists
    // TODO AC-LOAN-003: evaluate eligibility policy
    // TODO AC-LOAN-004: approve or reject aggregate
    // TODO AC-LOAN-005: persist aggregate
    // TODO AC-LOAN-006: publish domain events
    // TODO AC-LOAN-007: write audit record
    panic("not implemented")
}


// pkg/testutil/fakes/loan_application_repository_fake.go
package fakes

import (
    "context"
    "sync"
    "github.com/example/lending/domain"
)

type FakeLoanApplicationRepository struct {
    mu    sync.Mutex
    store map[string]*domain.LoanApplication
}

func NewFakeLoanApplicationRepository() *FakeLoanApplicationRepository {
    return &FakeLoanApplicationRepository{store: make(map[string]*domain.LoanApplication)}
}

func (f *FakeLoanApplicationRepository) FindByID(ctx context.Context, id domain.LoanApplicationID) (*domain.LoanApplication, error) {
    f.mu.Lock()
    defer f.mu.Unlock()
    return f.store[id.String()], nil
}

func (f *FakeLoanApplicationRepository) Save(ctx context.Context, aggregate *domain.LoanApplication) error {
    // NOTE: scaffold only. Real persistence behavior deferred to TDD.
    panic("not implemented")
}
```

---

## L6 — Runtime shapes (chi/echo route, DI, observability)

```go
// pkg/lending/interface/http_routes.go
package httpiface

import (
    "net/http"
    "github.com/go-chi/chi/v5"
    "github.com/example/lending/application"
    "github.com/example/auth"
)

func RegisterLoanRoutes(r chi.Router, useCase application.ApproveLoanUseCase) {
    r.With(auth.RequirePermission("lending.approve")).Post(
        "/loan-applications/{id}/approve",
        approveLoanHandler(useCase),
    )
}

func approveLoanHandler(useCase application.ApproveLoanUseCase) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        // TODO AC-LOAN-APPROVAL-API-001: map request to ApproveLoanCommand
        // TODO AC-LOAN-APPROVAL-API-002: call ApproveLoanUseCase
        // TODO AC-LOAN-APPROVAL-API-003: map result to HTTP response
        panic("not implemented")
    }
}
```

---

## L7 — Traceability emission (Go projects)

```yaml
bounded_contexts:
  Lending:
    features:
      ApproveLoan:
        # ... (canonical structure from SKILL.md)
        tests:
          unit:
            - pkg/lending/application/usecase_test.go
          behavioural:
            - pkg/lending/application/approve_loan_behaviour_test.go
          contract:
            - pkg/lending/application/loan_application_repository_contract_test.go
```

---

## Anti-patterns

- ❌ Real validation logic in constructors beyond non-empty checks
- ❌ Implementing `Approve()` body — only TODO + `panic("not implemented")`
- ❌ Repository `Save()` that actually persists
- ❌ Use-case `Execute()` calling real domain methods
- ❌ Importing `infrastructure/` from `domain/`
- ❌ Returning `interface{}` where the design specifies a typed result
- ❌ Tests with real assertions — only `t.Skip` + table structure + GWT comments
- ❌ `// TODO` without an AC ID — every TODO must trace
