"""
DEPRECATED: Import from lib.core.agent_consumer instead

Backward-compatibility shim for agent_consumer module.
This will be removed in a future version.
"""

import warnings

# Re-export everything from new location
from lib.core.agent_consumer import *  # noqa: F401, F403

# Deprecation warning
warnings.warn(
    "Importing from lib.agent_consumer is deprecated. "
    "Use 'from lib.core.agent_consumer import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)
