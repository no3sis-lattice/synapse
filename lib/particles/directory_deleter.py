"""
DEPRECATED: Import from templates.file_creator.particles.directory_deleter instead

Backward-compatibility shim for directory_deleter module.
This will be removed in a future version.
"""

import warnings

# Re-export everything from new location
from templates.file_creator.particles.directory_deleter import *  # noqa: F401, F403

# Deprecation warning
warnings.warn(
    "Importing from lib.particles.directory_deleter is deprecated. "
    "Use 'from templates.file_creator.particles.directory_deleter import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)
