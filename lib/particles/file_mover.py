"""
DEPRECATED: Import from templates.file_creator.particles.file_mover instead

Backward-compatibility shim for file_mover module.
This will be removed in a future version.
"""

import warnings

# Re-export everything from new location
from templates.file_creator.particles.file_mover import *  # noqa: F401, F403

# Deprecation warning
warnings.warn(
    "Importing from lib.particles.file_mover is deprecated. "
    "Use 'from templates.file_creator.particles.file_mover import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)
