"""
Pneuma Agent Tools Package

Tools for semantic code compression and pattern discovery.
"""

from .abstraction_tools import q_scan, a_abstract, a_lint, a_document
from .analysis_tools import s_score, calculate_entropy_reduction
from .memory_tools import load_state, save_state, update_log, add_pattern
from .synapse_integration import (
    query_global_patterns, publish_pattern_to_graph,
    get_pattern_usage_stats, discover_complementary_patterns
)
from .agent_communication import get_communicator
from .config_manager import get_config

__all__ = [
    "q_scan",
    "a_abstract",
    "a_lint",
    "a_document",
    "s_score",
    "calculate_entropy_reduction",
    "load_state",
    "save_state",
    "update_log",
    "add_pattern",
    "query_global_patterns",
    "publish_pattern_to_graph",
    "get_pattern_usage_stats",
    "discover_complementary_patterns",
    "get_communicator",
    "get_config"
]