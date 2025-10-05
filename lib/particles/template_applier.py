"""
DEPRECATED: Import from templates.file_creator.particles.template_applier instead

Backward-compatibility shim for template_applier module.
This will be removed in a future version.
"""

import warnings

# Re-export everything from new location
from templates.file_creator.particles.template_applier import *  # noqa: F401, F403

# Deprecation warning
warnings.warn(
    "Importing from lib.particles.template_applier is deprecated. "
    "Use 'from templates.file_creator.particles.template_applier import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)
