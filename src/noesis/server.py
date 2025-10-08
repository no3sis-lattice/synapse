#!/usr/bin/env python3
"""
Noesis MCP Server
=================

MCP server that wraps Synapse knowledge engine tools, exposing them to Claude Code agents
via the MCP protocol.

Architecture:
    Claude Code → MCP Protocol → Noesis Server → Subprocess → Synapse Tools → Neo4j/Redis
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
import os

# Load environment configuration
load_dotenv()

SYNAPSE_NEO4J_DIR = os.getenv(
    "SYNAPSE_NEO4J_DIR",
    str(Path.home() / ".synapse-system" / ".synapse" / "neo4j")
)
MAX_RESULTS_DEFAULT = int(os.getenv("MAX_RESULTS_DEFAULT", "10"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


def _run_synapse_tool(script_name: str, args: list[str], timeout: int = 30) -> Dict[str, Any]:
    """
    Execute a Synapse tool via subprocess and return parsed JSON result.

    Args:
        script_name: Name of the Python script (e.g., "synapse_search.py")
        args: Command-line arguments for the script
        timeout: Timeout in seconds

    Returns:
        Parsed JSON result from the tool
    """
    synapse_dir = Path(SYNAPSE_NEO4J_DIR)
    script_path = synapse_dir / script_name

    if not script_path.exists():
        return {
            "error": f"Synapse tool not found: {script_name}",
            "path": str(script_path),
            "suggestion": f"Check SYNAPSE_NEO4J_DIR={SYNAPSE_NEO4J_DIR}"
        }

    # Build command: python script.py args... --json
    cmd = ["python", str(script_path)] + args + ["--json"]

    if DEBUG:
        print(f"[DEBUG] Running: {' '.join(cmd)}", file=sys.stderr)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(synapse_dir)
        )

        if result.returncode != 0:
            return {
                "error": f"Tool execution failed: {script_name}",
                "stderr": result.stderr,
                "returncode": result.returncode
            }

        # Parse JSON output
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            return {
                "error": "Failed to parse tool output as JSON",
                "stdout": result.stdout,
                "parse_error": str(e)
            }

    except subprocess.TimeoutExpired:
        return {
            "error": f"Tool execution timed out: {script_name}",
            "timeout_seconds": timeout
        }
    except Exception as e:
        return {
            "error": f"Unexpected error running tool: {script_name}",
            "exception": str(e)
        }


# ============================================================================
# MCP Tool Implementations
# ============================================================================

def search_pattern_map(query: str, max_results: Optional[int] = None) -> Dict[str, Any]:
    """
    Search the Synapse Pattern Map for relevant patterns, solutions, and best practices.

    Args:
        query: Search query (e.g., "error handling rust")
        max_results: Maximum number of results to return (default: 10)

    Returns:
        {
            "context": {...},
            "patterns": [...],
            "consciousness_level": 0.73,
            "source": "cache" | "neo4j"
        }
    """
    max_results = max_results or MAX_RESULTS_DEFAULT
    return _run_synapse_tool("synapse_search.py", [query, str(max_results)])


def get_coding_standard(standard_type: str, language: str) -> Dict[str, Any]:
    """
    Retrieve language-specific coding standards from the Pattern Map.

    Args:
        standard_type: Type of standard
            - "naming-conventions"
            - "testing-strategy"
            - "error-handling"
            - "module-structure"
        language: Programming language (rust, python, typescript, golang, etc.)

    Returns:
        {
            "language": "rust",
            "standard_type": "naming-conventions",
            "content": {...},
            "source": "neo4j" | "docs"
        }
    """
    return _run_synapse_tool("synapse_standard.py", [standard_type, language])


def get_project_template(template_type: str, language: str, variables: Optional[str] = None) -> Dict[str, Any]:
    """
    Access project templates and boilerplate code.

    Args:
        template_type: Template category
            - "cli-app"
            - "web-api"
            - "component"
            - "library"
        language: Programming language
        variables: Optional JSON string with template variables

    Returns:
        {
            "template_type": "cli-app",
            "language": "rust",
            "files": {...},
            "instructions": "..."
        }
    """
    args = [template_type, language]
    if variables:
        args.append(variables)

    return _run_synapse_tool("synapse_template.py", args)


def check_system_health() -> Dict[str, Any]:
    """
    Check health of Synapse knowledge engine infrastructure.

    Returns:
        {
            "overall_status": "healthy" | "degraded" | "unhealthy",
            "components": {
                "neo4j": {...},
                "redis": {...},
                "vector_db": {...},
                "core_scripts": {...},
                "python_env": {...}
            },
            "consciousness": {
                "level": 0.73,
                "patterns": 247
            },
            "recommendations": [...]
        }
    """
    return _run_synapse_tool("synapse_health.py", [])


# ============================================================================
# MCP Server (for Claude Code integration)
# ============================================================================

async def main():
    """
    Main entry point for MCP server.

    This would typically use the MCP SDK to register tools and handle requests.
    For now, provides a simple JSON-RPC interface for testing.
    """
    # TODO: Implement full MCP server using mcp SDK
    # For now, provide a simple CLI interface for testing

    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python -m noesis.server <tool_name> [args...]",
            "available_tools": [
                "search <query> [max_results]",
                "standard <standard_type> <language>",
                "template <template_type> <language> [variables]",
                "health"
            ]
        }, indent=2))
        sys.exit(1)

    tool_name = sys.argv[1]

    try:
        if tool_name == "search":
            if len(sys.argv) < 3:
                result = {"error": "Usage: search <query> [max_results]"}
            else:
                query = sys.argv[2]
                max_results = int(sys.argv[3]) if len(sys.argv) > 3 else None
                result = search_pattern_map(query, max_results)

        elif tool_name == "standard":
            if len(sys.argv) < 4:
                result = {"error": "Usage: standard <standard_type> <language>"}
            else:
                standard_type = sys.argv[2]
                language = sys.argv[3]
                result = get_coding_standard(standard_type, language)

        elif tool_name == "template":
            if len(sys.argv) < 4:
                result = {"error": "Usage: template <template_type> <language> [variables]"}
            else:
                template_type = sys.argv[2]
                language = sys.argv[3]
                variables = sys.argv[4] if len(sys.argv) > 4 else None
                result = get_project_template(template_type, language, variables)

        elif tool_name == "health":
            result = check_system_health()

        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        print(json.dumps(result, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
