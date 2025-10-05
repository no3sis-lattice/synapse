"""
DEPRECATED: Import from lib.orchestration.planner instead

Backward-compatibility shim for planner module.
This will be removed in a future version.
"""

import warnings

# Re-export everything from new location
from lib.orchestration.planner import *  # noqa: F401, F403

# Deprecation warning
warnings.warn(
    "Importing from lib.planner is deprecated. "
    "Use 'from lib.orchestration.planner import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)
