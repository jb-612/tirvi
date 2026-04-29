# Dart / Flutter reference shapes for ddd-7l-scaffold

Idiomatic Dart: sealed classes for results, abstract classes for ports,
named constructors / factories, `throw UnimplementedError()` for stubs,
`flutter_test` / `test` package, Riverpod for DI in Flutter apps.
Adapt to the project's actual conventions discovered in L1 inspection.

---

## L1 — Folder layout

```
<flutter_app>/lib/<bounded_context>/
    domain/
        aggregates/
            loan_application.dart       # aggregate root
        entities/
            borrower.dart
        value_objects/
            loan_application_id.dart
            money.dart
        events/
            loan_approved.dart
        policies/
            borrower_eligibility_policy.dart
        errors.dart
    application/
        commands/
            approve_loan_command.dart
        use_cases/
            approve_loan_use_case.dart   # abstract + impl
            approve_loan_result.dart     # sealed
        ports/
            loan_application_repository.dart
            borrower_repository.dart
            domain_event_publisher.dart
    infrastructure/
        adapters/
            in_memory_loan_application_repository.dart
    presentation/
        api/                              # for backend-shelf use
            loan_routes.dart
        widgets/                          # for Flutter UI use
            approve_loan_button.dart
<flutter_app>/test/<bounded_context>/
    unit/
        loan_application_test.dart
        approve_loan_use_case_test.dart
    behavioural/
        approve_loan_behaviour_test.dart
```

For Flutter app code: `flutter_app/lib/...`. For pure Dart server code (e.g.,
shelf): `lib/...` at the package root.

---

## L2 — Contract shapes (abstract classes, sealed results, commands)

```dart
// lib/lending/application/use_cases/approve_loan_use_case.dart
import '../commands/approve_loan_command.dart';
import 'approve_loan_result.dart';

/// Use case port. AC: AC-LOAN-003.
abstract class ApproveLoanUseCase {
  Future<ApproveLoanResult> execute(ApproveLoanCommand command);
}


// lib/lending/application/commands/approve_loan_command.dart
import '../../domain/value_objects/loan_application_id.dart';
import '../../shared/user_id.dart';

/// AC: AC-LOAN-001.
class ApproveLoanCommand {
  final LoanApplicationId loanApplicationId;
  final UserId requestedBy;

  const ApproveLoanCommand({
    required this.loanApplicationId,
    required this.requestedBy,
  });
}


// lib/lending/application/use_cases/approve_loan_result.dart
import '../../domain/value_objects/loan_id.dart';
import '../../domain/value_objects/rejection_reason.dart';

/// Sealed-class result. Exhaustive pattern-matching at call sites.
sealed class ApproveLoanResult {
  const ApproveLoanResult();
}

class ApproveLoanResultApproved extends ApproveLoanResult {
  final LoanId loanId;
  const ApproveLoanResultApproved({required this.loanId});
}

class ApproveLoanResultRejected extends ApproveLoanResult {
  final List<RejectionReason> reasons;
  const ApproveLoanResultRejected({required this.reasons});
}


// lib/lending/application/ports/loan_application_repository.dart
import '../../domain/aggregates/loan_application.dart';
import '../../domain/value_objects/loan_application_id.dart';

abstract class LoanApplicationRepository {
  Future<LoanApplication?> findById(LoanApplicationId id);
  Future<void> save(LoanApplication aggregate);
}
```

---

## L3 — Domain shapes (aggregate, VO, event, errors)

```dart
// lib/lending/domain/value_objects/loan_application_id.dart

/// Value object. AC: AC-LOAN-001.
class LoanApplicationId {
  final String value;
  const LoanApplicationId._(this.value);

  factory LoanApplicationId(String value) {
    if (value.isEmpty) {
      throw ArgumentError('LoanApplicationId cannot be empty');
    }
    return LoanApplicationId._(value);
  }

  @override
  bool operator ==(Object other) =>
      other is LoanApplicationId && other.value == value;

  @override
  int get hashCode => value.hashCode;
}


// lib/lending/domain/aggregates/loan_application.dart
import '../value_objects/loan_application_id.dart';
import '../value_objects/borrower_id.dart';
import '../value_objects/money.dart';

enum LoanApplicationStatus { pending, approved, rejected }

/// LoanApplication aggregate root.
///
/// Invariants (named, not implemented — TDD fills these in):
///   - INV-LA-001 (AC-LOAN-003): only pending applications may be approved
///   - INV-LA-002 (AC-LOAN-004): rejected applications must include >= 1 reason
class LoanApplication {
  final LoanApplicationId id;
  final BorrowerId borrowerId;
  final Money requestedAmount;
  LoanApplicationStatus _status;

  LoanApplication._({
    required this.id,
    required this.borrowerId,
    required this.requestedAmount,
    required LoanApplicationStatus status,
  }) : _status = status;

  static LoanApplication submit(SubmitLoanApplicationCommand command) {
    // TODO AC-LOAN-001: enforce requested amount eligibility invariant
    // TODO AC-LOAN-002: emit LoanApplicationSubmitted event
    throw UnimplementedError();
  }

  void approve(ApprovalDecision decision) {
    // TODO AC-LOAN-003: only pending applications may be approved
    // TODO AC-LOAN-004: emit LoanApproved event
    throw UnimplementedError();
  }
}


// lib/lending/domain/events/loan_approved.dart
import '../value_objects/loan_application_id.dart';

/// Domain event — emitted by LoanApplication.approve(). AC: AC-LOAN-003.
class LoanApproved {
  final LoanApplicationId loanApplicationId;
  final DateTime decidedAt;

  const LoanApproved({
    required this.loanApplicationId,
    required this.decidedAt,
  });
}


// lib/lending/domain/errors.dart

abstract class DomainError implements Exception {
  String get message;
}

/// INV-LA-001: only pending applications may be approved (AC-LOAN-003).
class LoanNotPendingError implements DomainError {
  @override
  final String message;
  const LoanNotPendingError([this.message = 'loan application is not pending']);
}
```

---

## L4 — Test skeleton shapes (test package, skip)

```dart
// test/lending/unit/approve_loan_use_case_test.dart
import 'package:test/test.dart';

void main() {
  group('ApproveLoanUseCase', () {
    group('AC-LOAN-003: only pending applications may be approved', () {
      test(
        'rejects approval when the loan application is already rejected',
        () {
          // Given: a rejected loan application exists
          // And:   the borrower exists
          // When:  the approve loan use case is executed
          // Then:  the result is a domain error
          // And:   no LoanApproved event is emitted
          // And:   no approval audit record is written
        },
        skip: 'scaffold — implement in TDD phase',
      );

      test(
        'rejects approval when the loan application is already approved',
        () {
          // Given: an already approved loan application exists
          // When:  the approve loan use case is executed
          // Then:  the result is a domain error
        },
        skip: 'scaffold — implement in TDD phase',
      );
    });
  });
}


// test/lending/behavioural/approve_loan_behaviour_test.dart
import 'package:test/test.dart';

void main() {
  group('ApproveLoan behaviour. AC: AC-LOAN-001..AC-LOAN-007', () {
    test(
      'approves loan when eligibility passes and emits LoanApproved event',
      () {
        // Given: a pending loan application
        // And:   borrower passes eligibility policy
        // When:  the approve loan use case is invoked
        // Then:  status is approved
        // And:   LoanApproved event is published
        // And:   audit log contains LOAN_APPROVAL_DECISION
      },
      skip: 'scaffold — implement in TDD phase',
    );
  });
}
```

For Flutter widget tests, use `flutter_test` and `testWidgets` with the
same `skip:` parameter convention.

---

## L5 — TDD shell shapes (DI, fakes, fixtures)

```dart
// lib/lending/application/use_cases/approve_loan_use_case_impl.dart
import 'approve_loan_use_case.dart';
import 'approve_loan_result.dart';
import '../commands/approve_loan_command.dart';
import '../ports/loan_application_repository.dart';
import '../ports/borrower_repository.dart';
import '../ports/domain_event_publisher.dart';
import '../ports/audit_log.dart';
import '../../domain/policies/borrower_eligibility_policy.dart';

class ApproveLoanUseCaseImpl implements ApproveLoanUseCase {
  final LoanApplicationRepository _loanApplications;
  final BorrowerRepository _borrowers;
  final BorrowerEligibilityPolicy _eligibilityPolicy;
  final DomainEventPublisher _events;
  final AuditLog _audit;

  const ApproveLoanUseCaseImpl({
    required LoanApplicationRepository loanApplications,
    required BorrowerRepository borrowers,
    required BorrowerEligibilityPolicy eligibilityPolicy,
    required DomainEventPublisher events,
    required AuditLog audit,
  })  : _loanApplications = loanApplications,
        _borrowers = borrowers,
        _eligibilityPolicy = eligibilityPolicy,
        _events = events,
        _audit = audit;

  @override
  Future<ApproveLoanResult> execute(ApproveLoanCommand command) async {
    // TODO AC-LOAN-001: load loan application
    // TODO AC-LOAN-002: verify borrower exists
    // TODO AC-LOAN-003: evaluate eligibility policy
    // TODO AC-LOAN-004: approve or reject aggregate
    // TODO AC-LOAN-005: persist aggregate
    // TODO AC-LOAN-006: publish domain events
    // TODO AC-LOAN-007: write audit record
    throw UnimplementedError();
  }
}


// lib/lending/infrastructure/adapters/in_memory_loan_application_repository.dart
import '../../application/ports/loan_application_repository.dart';
import '../../domain/aggregates/loan_application.dart';
import '../../domain/value_objects/loan_application_id.dart';

class InMemoryLoanApplicationRepository implements LoanApplicationRepository {
  final Map<String, LoanApplication> _store = {};

  @override
  Future<LoanApplication?> findById(LoanApplicationId id) async => _store[id.value];

  @override
  Future<void> save(LoanApplication aggregate) {
    // NOTE: scaffold only. Real impl deferred to TDD.
    throw UnimplementedError();
  }
}


// test/fixtures/loan_application_factory.dart
import '../../lib/lending/domain/aggregates/loan_application.dart';

LoanApplication makePendingLoanApplication({
  // overrides
}) {
  throw UnimplementedError('scaffold — TDD fills this in');
}
```

For Flutter / Riverpod DI, scaffold the providers as `final
approveLoanUseCaseProvider = Provider<ApproveLoanUseCase>((ref) =>
ApproveLoanUseCaseImpl(...))` with `throw UnimplementedError()` in the
factory body until TDD.

---

## L6 — Runtime shapes (shelf for Dart server, Riverpod for Flutter UI)

```dart
// Dart server (shelf):
// lib/lending/presentation/api/loan_routes.dart
import 'package:shelf/shelf.dart';
import 'package:shelf_router/shelf_router.dart';
import '../../application/use_cases/approve_loan_use_case.dart';

Router loanRoutes(ApproveLoanUseCase useCase) {
  final router = Router();

  router.post('/loan-applications/<id>/approve', (Request request, String id) async {
    // TODO AC-LOAN-APPROVAL-API-001: check permission lending.approve
    // TODO AC-LOAN-APPROVAL-API-002: map request to ApproveLoanCommand
    // TODO AC-LOAN-APPROVAL-API-003: call ApproveLoanUseCase
    // TODO AC-LOAN-APPROVAL-API-004: map result to HTTP response
    throw UnimplementedError();
  });

  return router;
}


// Flutter UI (Riverpod widget):
// flutter_app/lib/lending/presentation/widgets/approve_loan_button.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ApproveLoanButton extends ConsumerWidget {
  final String loanApplicationId;
  const ApproveLoanButton({super.key, required this.loanApplicationId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ElevatedButton(
      onPressed: () {
        // TODO AC-LOAN-APPROVAL-UI-001: read use-case provider
        // TODO AC-LOAN-APPROVAL-UI-002: dispatch ApproveLoanCommand
        // TODO AC-LOAN-APPROVAL-UI-003: render result via state notifier
      },
      child: const Text('Approve'),
    );
  }
}
```

---

## L7 — Traceability emission (Dart projects)

```yaml
bounded_contexts:
  Lending:
    features:
      ApproveLoan:
        # ... (canonical structure from SKILL.md)
        tests:
          unit:
            - flutter_app/test/lending/unit/approve_loan_use_case_test.dart
          behavioural:
            - flutter_app/test/lending/behavioural/approve_loan_behaviour_test.dart
          contract:
            - flutter_app/test/lending/contract/loan_application_repository_contract_test.dart
        runtime:
          api_routes:
            - POST /loan-applications/{id}/approve
          ui_widgets:
            - flutter_app/lib/lending/presentation/widgets/approve_loan_button.dart
```

---

## Anti-patterns

- ❌ Real validation in factory constructors beyond truthy checks
- ❌ Implementing `approve()` body — only TODO + `throw UnimplementedError()`
- ❌ Repository `save()` that actually persists
- ❌ Use-case `execute()` calling real domain methods
- ❌ Importing `infrastructure/` from `domain/`
- ❌ Using `dynamic` where the design specifies a sealed class / VO
- ❌ Test bodies with real assertions — only GWT comments and `skip:`
- ❌ Riverpod providers with real factory bodies — only `throw UnimplementedError()`
- ❌ Widget `onPressed` callbacks with real logic
