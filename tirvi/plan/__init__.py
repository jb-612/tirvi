"""F22 — reading-plan aggregate (page-level orchestration).

Assembles a :class:`ReadingPlan` from F11 blocks + F14 spans + F18 tokens +
F19 diacritization + F20 G2P. Emits deterministic JSON serialization
(``plan.json``) and the F35-consumed projection (``page.json`` per DE-07).

Spec: N02/F22. Bounded contexts: ``bc:hebrew_nlp`` (DE-01..06),
``bc:audio_delivery`` (DE-07).
"""

from .aggregates import ReadingPlan
from .contracts import assert_plan_v1
from .errors import PlanInvariantError
from .value_objects import PlanBlock, PlanToken

__all__ = [
    "PlanBlock",
    "PlanInvariantError",
    "PlanToken",
    "ReadingPlan",
    "assert_plan_v1",
]
