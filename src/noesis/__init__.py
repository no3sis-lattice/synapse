"""
Noesis - Knowledge Engine MCP Server

MCP server exposing Synapse Pattern Map to AI agents via 4 knowledge tools:
- noesis_search: Query Pattern Map for solutions and patterns
- noesis_standard: Retrieve language-specific coding standards
- noesis_template: Access project templates
- noesis_health: Check knowledge engine infrastructure health
"""

__version__ = "0.1.0"

from .server import (
    search_pattern_map,
    get_coding_standard,
    get_project_template,
    check_system_health,
)

__all__ = [
    "search_pattern_map",
    "get_coding_standard",
    "get_project_template",
    "check_system_health",
]
