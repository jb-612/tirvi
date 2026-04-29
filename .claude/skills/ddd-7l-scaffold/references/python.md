# Python reference shapes for ddd-7l-scaffold

Idiomatic Python: dataclasses (or Pydantic) for value objects, `typing.Protocol`
for ports, `raise NotImplementedError` for stubs, `pytest` for tests. Adapt to
the project's actual conventions discovered in L1 inspection.

---

## L1 — Folder layout

```
<project>/<bounded_context>/
    domain/
        __init__.py
        aggregates/
            __init__.py
            loan_application.py        # aggregate root
        entities/
            __init__.py
            borrower.py
        value_objects/
            __init__.py
            loan_application_id.py
            money.py
        events/
            __init__.py
            loan_approved.py
        policies/
            __init__.py
            borrower_eligibility_policy.py
        errors.py                       # domain errors
    application/
        __init__.py
        commands/
            __init__.py
            approve_loan_command.py
        use_cases/
            __init__.py
            approve_loan_use_case.py    # protocol + impl
        ports/
            __init__.py
            loan_application_repository.py
            borrower_repository.py
            credit_score_gateway.py
            domain_event_publisher.py
    infrastructure/
        __init__.py
        adapters/
            __init__.py
            in_memory_loan_application_repository.py
        persistence/
            __init__.py
            sqlalchemy_models.py
    interface/
        __init__.py
        api/
            __init__.py
            loan_routes.py
tests/
    unit/<bounded_context>/
        test_loan_application.py
        test_approve_loan_use_case.py
    behavioural/<bounded_context>/
        test_approve_loan_behaviour.py
    contract/<bounded_context>/
        test_loan_application_repository_contract.py
```

In tirvi specifically: production code under `tirvi/`, tests under `tests/`.

---

## L2 — Contract shapes (interfaces, ports, commands, results)

```python
# application/use_cases/approve_loan_use_case.py
from typing import Protocol
from dataclasses import dataclass
from ..commands.approve_loan_command import ApproveLoanCommand
from .approve_loan_result import ApproveLoanResult


class ApproveLoanUseCase(Protocol):
    """Use case port. AC: AC-LOAN-003."""
    async def execute(self, command: ApproveLoanCommand) -> ApproveLoanResult: ...


# application/commands/approve_loan_command.py
from dataclasses import dataclass
from ...domain.value_objects.loan_application_id import LoanApplicationId
from ...shared.user_id import UserId

@dataclass(frozen=True)
class ApproveLoanCommand:
    """AC: AC-LOAN-001."""
    loan_application_id: LoanApplicationId
    requested_by: UserId


# application/use_cases/approve_loan_result.py
from dataclasses import dataclass
from typing import Union, Literal
from ...domain.value_objects.loan_id import LoanId
from ...domain.value_objects.rejection_reason import RejectionReason

@dataclass(frozen=True)
class ApproveLoanResultApproved:
    status: Literal["approved"] = "approved"
    loan_id: LoanId

@dataclass(frozen=True)
class ApproveLoanResultRejected:
    status: Literal["rejected"] = "rejected"
    reasons: list[RejectionReason]

ApproveLoanResult = Union[ApproveLoanResultApproved, ApproveLoanResultRejected]


# application/ports/loan_application_repository.py
from typing import Protocol
from ...domain.aggregates.loan_application import LoanApplication
from ...domain.value_objects.loan_application_id import LoanApplicationId

class LoanApplicationRepository(Protocol):
    async def find_by_id(self, id: LoanApplicationId) -> LoanApplication | None: ...
    async def save(self, aggregate: LoanApplication) -> None: ...
```

---

## L3 — Domain shapes (aggregates, VOs, events, errors)

```python
# domain/value_objects/loan_application_id.py
from dataclasses import dataclass

@dataclass(frozen=True)
class LoanApplicationId:
    """Value object — AC: AC-LOAN-001."""
    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("LoanApplicationId cannot be empty")


# domain/aggregates/loan_application.py
from dataclasses import dataclass, field
from ..value_objects.loan_application_id import LoanApplicationId
from ..value_objects.borrower_id import BorrowerId
from ..value_objects.money import Money
from ..events.loan_approved import LoanApproved

class LoanApplicationStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class LoanApplication:
    """Aggregate root.

    Invariants (named, not implemented — TDD fills these in):
      - INV-LA-001 (AC-LOAN-003): only pending applications may be approved
      - INV-LA-002 (AC-LOAN-004): rejected applications must include >= 1 reason
    """

    def __init__(
        self,
        id: LoanApplicationId,
        borrower_id: BorrowerId,
        requested_amount: Money,
        status: str,
    ):
        self._id = id
        self._borrower_id = borrower_id
        self._requested_amount = requested_amount
        self._status = status

    @classmethod
    def submit(cls, command) -> "LoanApplication":
        # TODO AC-LOAN-001: enforce requested amount eligibility invariant
        # TODO AC-LOAN-002: emit LoanApplicationSubmitted event
        raise NotImplementedError

    def approve(self, decision) -> None:
        # TODO AC-LOAN-003: only pending applications may be approved
        # TODO AC-LOAN-004: emit LoanApproved event
        raise NotImplementedError


# domain/events/loan_approved.py
from dataclasses import dataclass
from datetime import datetime
from ..value_objects.loan_application_id import LoanApplicationId

@dataclass(frozen=True)
class LoanApproved:
    """Domain event — emitted by LoanApplication.approve(). AC: AC-LOAN-003."""
    loan_application_id: LoanApplicationId
    decided_at: datetime


# domain/errors.py
class DomainError(Exception):
    """Base domain error."""

class LoanNotPendingError(DomainError):
    """INV-LA-001: only pending applications may be approved (AC-LOAN-003)."""
```

---

## L4 — Test skeleton shapes (pytest)

```python
# tests/unit/lending/test_approve_loan_use_case.py
import pytest

@pytest.mark.skip(reason="scaffold — implement in TDD phase")
class TestApproveLoanUseCase:

    class TestAcLoan003OnlyPendingApplicationsMayBeApproved:
        """AC-LOAN-003: only pending applications may be approved."""

        async def test_rejects_approval_when_application_is_already_rejected(self):
            # Given: a rejected loan application exists
            # And:   the borrower exists
            # When:  the approve loan use case is executed
            # Then:  the result is a domain error
            # And:   no LoanApproved event is emitted
            # And:   no approval audit record is written
            pass

        async def test_rejects_approval_when_application_is_already_approved(self):
            # Given: an already approved loan application exists
            # When:  the approve loan use case is executed
            # Then:  the result is a domain error
            pass


# tests/behavioural/lending/test_approve_loan_behaviour.py
import pytest

@pytest.mark.skip(reason="scaffold — implement in TDD phase")
class TestApproveLoanBehaviour:
    """Behavioural slice. AC: AC-LOAN-001..AC-LOAN-007."""

    async def test_approves_loan_when_eligibility_passes_and_emits_loan_approved_event(self):
        # Given: a pending loan application
        # And:   borrower passes eligibility policy
        # When:  the approve loan use case is invoked
        # Then:  status is approved
        # And:   LoanApproved event is published
        # And:   audit log contains LOAN_APPROVAL_DECISION
        pass
```

---

## L5 — TDD shell shapes (DI wiring, fakes, fixtures)

```python
# application/use_cases/approve_loan_use_case_impl.py
from .approve_loan_use_case import ApproveLoanUseCase
from .approve_loan_result import ApproveLoanResult
from ..commands.approve_loan_command import ApproveLoanCommand
from ..ports.loan_application_repository import LoanApplicationRepository
from ..ports.borrower_repository import BorrowerRepository
from ...domain.policies.borrower_eligibility_policy import BorrowerEligibilityPolicy
from ..ports.domain_event_publisher import DomainEventPublisher
from ..ports.audit_log import AuditLog


class ApproveLoanUseCaseImpl(ApproveLoanUseCase):
    def __init__(
        self,
        loan_applications: LoanApplicationRepository,
        borrowers: BorrowerRepository,
        eligibility_policy: BorrowerEligibilityPolicy,
        events: DomainEventPublisher,
        audit: AuditLog,
    ):
        self._loan_applications = loan_applications
        self._borrowers = borrowers
        self._eligibility_policy = eligibility_policy
        self._events = events
        self._audit = audit

    async def execute(self, command: ApproveLoanCommand) -> ApproveLoanResult:
        # TODO AC-LOAN-001: load loan application
        # TODO AC-LOAN-002: verify borrower exists
        # TODO AC-LOAN-003: evaluate eligibility policy
        # TODO AC-LOAN-004: approve or reject aggregate
        # TODO AC-LOAN-005: persist aggregate
        # TODO AC-LOAN-006: publish domain events
        # TODO AC-LOAN-007: write audit record
        raise NotImplementedError


# infrastructure/adapters/in_memory_loan_application_repository.py
from ...application.ports.loan_application_repository import LoanApplicationRepository
from ...domain.aggregates.loan_application import LoanApplication
from ...domain.value_objects.loan_application_id import LoanApplicationId

class InMemoryLoanApplicationRepository(LoanApplicationRepository):
    def __init__(self):
        self._store: dict[str, LoanApplication] = {}

    async def find_by_id(self, id: LoanApplicationId) -> LoanApplication | None:
        return self._store.get(id.value)

    async def save(self, aggregate: LoanApplication) -> None:
        # NOTE: scaffold only. Real impl deferred to TDD.
        raise NotImplementedError


# tests/fixtures/loan_application_factory.py
from ..domain.aggregates.loan_application import LoanApplication

def make_pending_loan_application(**overrides) -> LoanApplication:
    """Fixture builder — minimal valid pending loan application."""
    raise NotImplementedError("scaffold — TDD fills this in")
```

---

## L6 — Runtime shapes (FastAPI route, DI, observability)

```python
# interface/api/loan_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from ..auth import require_permission
from ...application.use_cases.approve_loan_use_case import ApproveLoanUseCase
from ...application.commands.approve_loan_command import ApproveLoanCommand

router = APIRouter()


@router.post("/loan-applications/{loan_application_id}/approve")
async def approve_loan(
    loan_application_id: str,
    use_case: ApproveLoanUseCase = Depends(),
    user=Depends(require_permission("lending.approve")),
):
    # TODO AC-LOAN-APPROVAL-API-001: map request to ApproveLoanCommand
    # TODO AC-LOAN-APPROVAL-API-002: call ApproveLoanUseCase
    # TODO AC-LOAN-APPROVAL-API-003: map result to HTTP response
    raise NotImplementedError
```

---

## L7 — Traceability emission (Python projects)

The agent emits the canonical `bounded_contexts:` block to
`.workitems/$ARGUMENTS/traceability.yaml` regardless of source language.
File names in `tests:` use Python conventions (`test_*.py`):

```yaml
bounded_contexts:
  Lending:
    features:
      ApproveLoan:
        # ... (canonical structure from SKILL.md)
        tests:
          unit:
            - tests/unit/lending/test_approve_loan_use_case.py
          behavioural:
            - tests/behavioural/lending/test_approve_loan_behaviour.py
          contract:
            - tests/contract/lending/test_loan_application_repository_contract.py
```

---

## Anti-patterns (what NOT to write during scaffold)

- ❌ Real validation in `__post_init__` beyond truthy checks
- ❌ Implementing `approve()` body — only TODO + `raise NotImplementedError`
- ❌ Repository `save()` that actually persists — fakes are TDD-phase
- ❌ Use-case `execute()` that calls real domain methods
- ❌ Importing `infrastructure/` from `domain/` (dependency direction)
- ❌ Using `dict[str, Any]` where the design specifies a dataclass / VO
- ❌ Test bodies with real assertions — only GWT comments and `pass` / `pytest.mark.skip`
