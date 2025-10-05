"""
DEPRECATED: Import from templates.file_creator.particles.file_reader instead

Backward-compatibility shim for file_reader module.
This will be removed in a future version.
"""

import warnings

# Re-export everything from new location
from templates.file_creator.particles.file_reader import *  # noqa: F401, F403

# Deprecation warning
warnings.warn(
    "Importing from lib.particles.file_reader is deprecated. "
    "Use 'from templates.file_creator.particles.file_reader import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)
