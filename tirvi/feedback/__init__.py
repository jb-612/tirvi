"""tirvi.feedback — User feedback capture (deferred post-POC).

Spec: N05/F47. Status: deferred — populated when biz-functional-design
runs for N05.
"""

from __future__ import annotations


def record_feedback(doc_id: str, payload: dict[str, object]) -> str:  # pragma: no cover - stub
    """Validate and persist a user feedback entry; return the GCS object key."""
    raise NotImplementedError("F47 deferred post-POC")
