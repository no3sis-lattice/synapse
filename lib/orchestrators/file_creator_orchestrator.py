"""
DEPRECATED: Import from templates.file_creator.orchestrator instead

Backward-compatibility shim for file_creator_orchestrator module.
This will be removed in a future version.
"""

import warnings

# Re-export everything from new location
from templates.file_creator.orchestrator import *  # noqa: F401, F403

# Deprecation warning
warnings.warn(
    "Importing from lib.orchestrators.file_creator_orchestrator is deprecated. "
    "Use 'from templates.file_creator.orchestrator import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)
