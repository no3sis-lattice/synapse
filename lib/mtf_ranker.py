"""
DEPRECATED: Import from lib.orchestration.mtf_ranker instead

Backward-compatibility shim for mtf_ranker module.
This will be removed in a future version.
"""

import warnings

# Re-export everything from new location
from lib.orchestration.mtf_ranker import *  # noqa: F401, F403

# Deprecation warning
warnings.warn(
    "Importing from lib.mtf_ranker is deprecated. "
    "Use 'from lib.orchestration.mtf_ranker import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)
