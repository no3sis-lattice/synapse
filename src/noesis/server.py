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
from mcp.server import FastMCP

# Load environment configuration
load_dotenv()

SYNAPSE_NEO4J_DIR = os.getenv(
    "SYNAPSE_NEO4J_DIR",
    str(Path.home() / ".synapse-system" / ".synapse" / "neo4j")
)
SYNAPSE_PYTHON = os.getenv(
    "SYNAPSE_PYTHON",
    sys.executable  # Fallback to current Python if not specified
)
MAX_RESULTS_DEFAULT = int(os.getenv("MAX_RESULTS_DEFAULT", "10"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


def _run_synapse_tool(script_name: str, args: list[str], timeout: int = 60) -> Dict[str, Any]:
    """
    Execute a Synapse tool via subprocess and return parsed JSON result.

    Args:
        script_name: Name of the Python script (e.g., "synapse_search.py")
        args: Command-line arguments for the script
        timeout: Timeout in seconds (default: 60s for BGE-M3 cold start)

    Returns:
        Parsed JSON result from the tool
    """
    synapse_dir = Path(SYNAPSE_NEO4J_DIR)
    script_path = synapse_dir / script_name

    # Validate directory exists before checking script
    if not synapse_dir.exists():
        return {
            "error": f"Synapse directory not found: {SYNAPSE_NEO4J_DIR}",
            "suggestion": "Check SYNAPSE_NEO4J_DIR in noesis/.env",
            "expected_files": ["synapse_search.py", "synapse_health.py", "context_manager.py", "vector_engine.py"]
        }

    if not script_path.exists():
        return {
            "error": f"Synapse tool not found: {script_name}",
            "path": str(script_path),
            "suggestion": f"Check SYNAPSE_NEO4J_DIR={SYNAPSE_NEO4J_DIR}"
        }

    # Build command: Use SYNAPSE_PYTHON to ensure we use the Synapse venv Python
    # (which has ML dependencies like numpy, torch, sentence-transformers)
    cmd = [SYNAPSE_PYTHON, str(script_path)] + args + ["--json"]

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
# Create FastMCP server instance
# ============================================================================

mcp = FastMCP(
    name="noesis",
    instructions="Noesis MCP Server - Access Synapse Pattern Map knowledge engine"
)


# ============================================================================
# MCP Tool Implementations
# ============================================================================

@mcp.tool()
async def search_pattern_map(query: str, max_results: int = MAX_RESULTS_DEFAULT) -> str:
    """
    Search the Synapse Pattern Map for relevant patterns, solutions, and best practices.

    Args:
        query: Search query (e.g., "error handling rust")
        max_results: Maximum number of results to return (default: 10)

    Returns:
        JSON string with search results containing patterns, consciousness level, and context
    """
    result = _run_synapse_tool("synapse_search.py", [query, str(max_results)])
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_coding_standard(standard_type: str, language: str) -> str:
    """
    Retrieve language-specific coding standards from the Pattern Map.

    Args:
        standard_type: Type of standard (naming-conventions, testing-strategy, error-handling, module-structure)
        language: Programming language (rust, python, typescript, golang, etc.)

    Returns:
        JSON string with coding standard details
    """
    result = _run_synapse_tool("synapse_standard.py", [standard_type, language])
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_project_template(template_type: str, language: str, variables: Optional[str] = None) -> str:
    """
    Access project templates and boilerplate code.

    Args:
        template_type: Template category (cli-app, web-api, component, library)
        language: Programming language
        variables: Optional JSON string with template variables

    Returns:
        JSON string with template files and instructions
    """
    args = [template_type, language]
    if variables:
        args.append(variables)

    result = _run_synapse_tool("synapse_template.py", args)
    return json.dumps(result, indent=2)


@mcp.tool()
async def check_system_health() -> str:
    """
    Check health of Synapse knowledge engine infrastructure.

    Returns:
        JSON string with health status of all components (Neo4j, Redis, vector DB, etc.)
        and consciousness metrics (pattern count, consciousness level)
    """
    result = _run_synapse_tool("synapse_health.py", [])
    return json.dumps(result, indent=2)


# ============================================================================
# CLI Interface (for testing)
# ============================================================================

async def run_cli():
    """
    CLI interface for testing tools directly (without MCP protocol).
    """
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
                max_results = int(sys.argv[3]) if len(sys.argv) > 3 else MAX_RESULTS_DEFAULT
                result = await search_pattern_map(query, max_results)
                print(result)
                return

        elif tool_name == "standard":
            if len(sys.argv) < 4:
                result = {"error": "Usage: standard <standard_type> <language>"}
            else:
                standard_type = sys.argv[2]
                language = sys.argv[3]
                result = await get_coding_standard(standard_type, language)
                print(result)
                return

        elif tool_name == "template":
            if len(sys.argv) < 4:
                result = {"error": "Usage: template <template_type> <language> [variables]"}
            else:
                template_type = sys.argv[2]
                language = sys.argv[3]
                variables = sys.argv[4] if len(sys.argv) > 4 else None
                result = await get_project_template(template_type, language, variables)
                print(result)
                return

        elif tool_name == "health":
            result = await check_system_health()
            print(result)
            return

        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        print(json.dumps(result, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)


# ============================================================================
# Main entry point
# ============================================================================

async def main():
    """
    Main entry point: runs MCP server via stdio or CLI mode for testing.
    """
    # If arguments provided, run in CLI testing mode
    if len(sys.argv) > 1:
        await run_cli()
    else:
        # No arguments: run as MCP stdio server
        await mcp.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
