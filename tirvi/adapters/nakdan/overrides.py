"""F19/F21 hook — re-export the homograph override lexicon.

The lexicon now lives at :mod:`tirvi.homograph`, loaded from
``data/homograph-lexicon.yaml`` (F21 DE-03/DE-04). This module preserves
the import path used by ``inference._override_hit`` so that F19's
existing wiring continues to work unchanged.

Spec: N02/F21 DE-03. Issue #20.
"""

from tirvi.homograph import HOMOGRAPH_OVERRIDES

__all__ = ["HOMOGRAPH_OVERRIDES"]
