"""
DEPRECATED: Import from lib.orchestration.synthesizer instead

Backward-compatibility shim for synthesizer module.
This will be removed in a future version.
"""

import warnings

# Re-export everything from new location
from lib.orchestration.synthesizer import *  # noqa: F401, F403

# Deprecation warning
warnings.warn(
    "Importing from lib.synthesizer is deprecated. "
    "Use 'from lib.orchestration.synthesizer import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)
