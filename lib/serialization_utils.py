"""
DEPRECATED: Import from lib.orchestration.serialization_utils instead

Backward-compatibility shim for serialization_utils module.
This will be removed in a future version.
"""

import warnings

# Re-export everything from new location
from lib.orchestration.serialization_utils import *  # noqa: F401, F403

# Deprecation warning
warnings.warn(
    "Importing from lib.serialization_utils is deprecated. "
    "Use 'from lib.orchestration.serialization_utils import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)
