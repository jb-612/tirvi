"""N05/F43 DE-01/DE-02 — GCS bucket TTL/lifecycle automation (deferred post-POC stub).

Applies a 7-day TTL lifecycle rule to ``pdfs/``, ``pages/``, ``plans/``,
and ``manifests/`` prefixes; ``audio/`` is excluded because it is
content-addressed and shareable across users (HLD-§3.4). Deferred per
PLAN-POC.md §Deferred.
"""

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TTLReport:
    """TTL apply / verify result. Spec: N05/F43 DE-02."""

    applied_prefixes: list[str] = field(default_factory=list)
    excluded_prefixes: list[str] = field(default_factory=list)
    rule_active: bool = False
    findings: list[dict[str, Any]] = field(default_factory=list)


def apply_ttl(
    resource_paths: Iterable[str],
    policy: dict[str, Any],
) -> TTLReport:
    """Apply TTL lifecycle rule to the given GCS prefixes per policy.

    Deferred post-POC: raises ``NotImplementedError``. TDD will fill the
    GCS lifecycle_rule application + cleanup-verification queries.
    """
    raise NotImplementedError("F43 ttl-automation — deferred post-POC")
