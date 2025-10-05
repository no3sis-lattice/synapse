"""
DEPRECATED: Import from lib.orchestration.pattern_learner instead

Backward-compatibility shim for pattern_learner module.
This will be removed in a future version.
"""

import warnings

# Re-export everything from new location
from lib.orchestration.pattern_learner import *  # noqa: F401, F403

# Deprecation warning
warnings.warn(
    "Importing from lib.pattern_learner is deprecated. "
    "Use 'from lib.orchestration.pattern_learner import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)
