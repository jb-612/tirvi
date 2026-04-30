"""F22 — reading-plan errors."""

from tirvi.errors import AdapterError


class PlanInvariantError(AdapterError):
    """Raised when ReadingPlan invariants fail (id uniqueness, ordering, …).

    Spec: N02/F22 DE-04.
    """
