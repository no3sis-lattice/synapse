"""
DEPRECATED: Import from lib.core.atomic_particle instead

Backward-compatibility shim for atomic_particle module.
This will be removed in a future version.
"""

import warnings

# Re-export everything from new location
from lib.core.atomic_particle import *  # noqa: F401, F403

# Deprecation warning
warnings.warn(
    "Importing from lib.atomic_particle is deprecated. "
    "Use 'from lib.core.atomic_particle import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)
