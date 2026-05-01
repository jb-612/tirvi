"""F25 — Content reading templates (deferred MVP stub).

Spec: N02/F25 DE-01. AC: US-01/AC-01.
"""

TEMPLATES_ENABLED = False


def apply_content_template(block):
    """Return the block unchanged until TEMPLATES_ENABLED is True."""
    if TEMPLATES_ENABLED:
        raise NotImplementedError("F25 content templates deferred to MVP")
    return block


__all__ = ["TEMPLATES_ENABLED", "apply_content_template"]
