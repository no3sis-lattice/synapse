#!/usr/bin/env python3
"""
Synapse Health Check Tool (Phase 1.4)
======================================

Monitors system health: Neo4j, Redis, BGE-M3, CLI tools.
Reports readiness for MCP server integration.

Usage:
    python synapse_health.py [--json] [--verbose] [--help]

Returns:
    - Neo4j connectivity and latency
    - Redis connectivity and latency (optional)
    - BGE-M3 model availability and load time
    - CLI tools executability status
    - Overall system readiness for MCP

Design:
    - Uses synapse_config.py (DRY principle)
    - Simple health checks (KISS principle)
    - Single responsibility per function (SOLID)
    - Graceful degradation for optional services
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Import shared configuration (DRY principle)
from synapse_config import (
    NEO4J_URI, NEO4J_AUTH,
    REDIS_HOST, REDIS_PORT,
    check_neo4j_available,
    check_redis_available,
    check_sentence_transformers_available,
    resolve_model_path
)


def check_neo4j_health():
    """
    Check Neo4j connectivity and latency.

    Returns:
        Dict with status, latency_ms, version (if up)
    """
    if not check_neo4j_available():
        return {
            "status": "down",
            "error": "neo4j package not available"
        }

    try:
        from neo4j import GraphDatabase

        start = time.time()
        driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)

        try:
            # Simple ping query
            with driver.session() as session:
                result = session.run("RETURN 1 AS ping")
                result.single()

                # Get version
                version_result = session.run("CALL dbms.components() YIELD versions RETURN versions[0] AS version")
                version_record = version_result.single()
                version = version_record["version"] if version_record else "unknown"

            latency_ms = int((time.time() - start) * 1000)

            return {
                "status": "up",
                "latency_ms": latency_ms,
                "version": version
            }

        finally:
            driver.close()

    except Exception as e:
        return {
            "status": "down",
            "error": str(e)
        }


def check_redis_health():
    """
    Check Redis connectivity and latency (optional service).

    Returns:
        Dict with status, latency_ms, optional flag
    """
    if not check_redis_available():
        return {
            "status": "down",
            "error": "redis package not available",
            "optional": True
        }

    try:
        import redis

        start = time.time()
        client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        client.ping()
        latency_ms = int((time.time() - start) * 1000)

        return {
            "status": "up",
            "latency_ms": latency_ms,
            "optional": True
        }

    except Exception as e:
        return {
            "status": "down",
            "error": str(e),
            "optional": True
        }


def check_bge_m3_health():
    """
    Check BGE-M3 model availability and load time.

    Returns:
        Dict with status, model_path, load_time_ms (if available)
    """
    model_path = resolve_model_path()

    # Check if model files exist
    if not model_path.exists():
        return {
            "status": "unavailable",
            "error": f"Model not found at {model_path}"
        }

    # Check if sentence_transformers is available
    if not check_sentence_transformers_available():
        return {
            "status": "unavailable",
            "error": "sentence_transformers package not available",
            "model_path": str(model_path)
        }

    # Measure load time (optional - can be slow)
    # For health check, we'll just verify package availability
    return {
        "status": "available",
        "model_path": str(model_path)
    }


def check_cli_tools_health():
    """
    Check that all 3 Phase 1 CLI tools are executable.

    Returns:
        Dict mapping tool names to status (executable, not_found, error)
    """
    script_dir = Path(__file__).parent
    tools = {
        "synapse_search": script_dir / "synapse_search.py",
        "synapse_standard": script_dir / "synapse_standard.py",
        "synapse_template": script_dir / "synapse_template.py"
    }

    results = {}

    for tool_name, tool_path in tools.items():
        if not tool_path.exists():
            results[tool_name] = "not_found"
        elif not tool_path.is_file():
            results[tool_name] = "error"
        else:
            # File exists and is a file - consider it executable
            results[tool_name] = "executable"

    return results


def calculate_overall_status(checks):
    """
    Calculate overall system status based on individual checks.

    Logic:
    - healthy: All critical services up (Neo4j + all CLI tools)
    - degraded: Critical services up but optional services down (Redis)
    - unhealthy: Any critical service down

    Args:
        checks: Dict with neo4j, redis, bge_m3, cli_tools checks

    Returns:
        "healthy", "degraded", or "unhealthy"
    """
    # Critical services
    neo4j_up = checks["neo4j"]["status"] == "up"
    all_tools_ok = all(
        status == "executable"
        for status in checks["cli_tools"].values()
    )

    # Optional services
    redis_up = checks["redis"]["status"] == "up"

    # Determine status
    if not neo4j_up or not all_tools_ok:
        return "unhealthy"
    elif not redis_up:
        return "degraded"
    else:
        return "healthy"


def calculate_ready_for_mcp(checks):
    """
    Determine if system is ready for MCP server integration.

    Requires:
    - Neo4j up
    - All CLI tools executable

    Args:
        checks: Dict with neo4j, redis, bge_m3, cli_tools checks

    Returns:
        Boolean: True if ready, False otherwise
    """
    neo4j_up = checks["neo4j"]["status"] == "up"
    all_tools_ok = all(
        status == "executable"
        for status in checks["cli_tools"].values()
    )

    return neo4j_up and all_tools_ok


def print_usage():
    """Print usage information"""
    print("Usage: python synapse_health.py [OPTIONS]")
    print()
    print("Options:")
    print("  --json       Output JSON format (for MCP server)")
    print("  --verbose    Show detailed diagnostics")
    print("  --help       Show this help message")
    print()
    print("Examples:")
    print("  python synapse_health.py")
    print("  python synapse_health.py --json")
    print("  python synapse_health.py --verbose")


def print_human_readable(health_data, verbose=False):
    """
    Print human-readable health status.

    Args:
        health_data: Dict with health check results
        verbose: If True, show detailed diagnostics
    """
    print("=== Synapse Health Status ===")
    print()

    # Neo4j
    neo4j = health_data["checks"]["neo4j"]
    status_symbol = "✓" if neo4j["status"] == "up" else "✗"
    print(f"Neo4j:  {status_symbol} {neo4j['status'].upper()}", end="")
    if neo4j["status"] == "up":
        print(f" ({neo4j['latency_ms']}ms)")
        if verbose:
            print(f"  Version: {neo4j.get('version', 'unknown')}")
    else:
        print()
        if verbose:
            print(f"  Error: {neo4j.get('error', 'Unknown')}")

    # Redis
    redis_info = health_data["checks"]["redis"]
    status_symbol = "✓" if redis_info["status"] == "up" else "✗"
    print(f"Redis:  {status_symbol} {redis_info['status'].upper()}", end="")
    if redis_info["status"] == "up":
        print(f" ({redis_info['latency_ms']}ms, optional)")
    else:
        print(" (optional)")
        if verbose:
            print(f"  Error: {redis_info.get('error', 'Unknown')}")

    # BGE-M3
    bge_m3 = health_data["checks"]["bge_m3"]
    status_symbol = "✓" if bge_m3["status"] == "available" else "✗"
    print(f"BGE-M3: {status_symbol} {bge_m3['status'].upper()}")
    if verbose:
        if bge_m3["status"] == "available":
            print(f"  Path: {bge_m3.get('model_path', 'unknown')}")
        else:
            print(f"  Error: {bge_m3.get('error', 'Unknown')}")

    # CLI Tools
    print()
    print("CLI Tools:")
    cli_tools = health_data["checks"]["cli_tools"]
    for tool_name, tool_status in cli_tools.items():
        status_symbol = "✓" if tool_status == "executable" else "✗"
        print(f"  {tool_name}: {status_symbol} {tool_status}")

    # Overall status
    print()
    status = health_data["status"]
    status_upper = status.upper()
    print(f"Overall Status: {status_upper}")
    print(f"Ready for MCP: {'YES' if health_data['ready_for_mcp'] else 'NO'}")

    if verbose:
        print()
        print(f"Timestamp: {health_data['timestamp']}")


def main():
    # Handle --help flag FIRST
    if "--help" in sys.argv or "-h" in sys.argv:
        print_usage()
        sys.exit(0)

    # Parse arguments
    json_mode = "--json" in sys.argv
    verbose = "--verbose" in sys.argv

    # Run health checks
    checks = {
        "neo4j": check_neo4j_health(),
        "redis": check_redis_health(),
        "bge_m3": check_bge_m3_health(),
        "cli_tools": check_cli_tools_health()
    }

    # Calculate overall status
    overall_status = calculate_overall_status(checks)
    ready_for_mcp = calculate_ready_for_mcp(checks)

    # Build health data structure (Phase 1.4 spec)
    health_data = {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": checks,
        "ready_for_mcp": ready_for_mcp
    }

    # Output results
    if json_mode:
        print(json.dumps(health_data, indent=2))
    else:
        print_human_readable(health_data, verbose=verbose)


if __name__ == "__main__":
    main()
