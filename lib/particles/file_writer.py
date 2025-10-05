"""
DEPRECATED: Import from templates.file_creator.particles.file_writer instead

Backward-compatibility shim for file_writer module.
This will be removed in a future version.
"""

import warnings

# Re-export everything from new location
from templates.file_creator.particles.file_writer import *  # noqa: F401, F403

# Deprecation warning
warnings.warn(
    "Importing from lib.particles.file_writer is deprecated. "
    "Use 'from templates.file_creator.particles.file_writer import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)
