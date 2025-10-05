"""
DEPRECATED: Import from templates.file_creator.particles.batch_file_creator instead

Backward-compatibility shim for batch_file_creator module.
This will be removed in a future version.
"""

import warnings

# Re-export everything from new location
from templates.file_creator.particles.batch_file_creator import *  # noqa: F401, F403

# Deprecation warning
warnings.warn(
    "Importing from lib.particles.batch_file_creator is deprecated. "
    "Use 'from templates.file_creator.particles.batch_file_creator import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)
