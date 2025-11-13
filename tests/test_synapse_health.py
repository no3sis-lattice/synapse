#!/usr/bin/env python3
"""
TDD Tests for synapse_health.py (Phase 1.4)
============================================

Following Red-Green-Refactor cycle.
Updated to match Phase 1.4 specification.

Tests cover:
- Infrastructure connectivity (Neo4j, Redis)
- BGE-M3 model availability and load time
- CLI tools executability verification
- Overall system status calculation
- JSON output format
- Human-readable output
- Verbose mode
- --help flag
- Latency tracking
- Error handling
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


# Path to the synapse_health.py script
SCRIPT_PATH = Path(__file__).parent.parent / ".synapse" / "neo4j" / "synapse_health.py"
PYTHON_BIN = Path(__file__).parent.parent / ".venv-ml" / "bin" / "python"


def test_script_exists():
    """Test that synapse_health.py exists"""
    assert SCRIPT_PATH.exists(), f"synapse_health.py not found at {SCRIPT_PATH}"


def test_script_executable():
    """Test that synapse_health.py can be executed with --help"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--help"],
        capture_output=True,
        text=True,
        timeout=5
    )
    # Should show usage and exit with 0
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    assert "usage" in result.stdout.lower() or "Usage" in result.stdout


def test_json_output_format():
    """Test that --json flag produces valid JSON output"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=15
    )

    assert result.returncode == 0, f"Script failed: {result.stderr}"

    # Parse JSON to validate format
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        assert False, f"Invalid JSON output: {e}\nOutput: {result.stdout}"

    # Validate required top-level keys (Phase 1.4 spec)
    assert "status" in data, "Missing 'status' key"
    assert "timestamp" in data, "Missing 'timestamp' key"
    assert "checks" in data, "Missing 'checks' key"
    assert "ready_for_mcp" in data, "Missing 'ready_for_mcp' key"

    # Validate checks section
    checks = data["checks"]
    assert "neo4j" in checks, "Missing 'neo4j' check"
    assert "redis" in checks, "Missing 'redis' check"
    assert "bge_m3" in checks, "Missing 'bge_m3' check"
    assert "cli_tools" in checks, "Missing 'cli_tools' check"


def test_neo4j_health_check():
    """Test that Neo4j health check returns expected structure"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=15
    )

    data = json.loads(result.stdout)
    neo4j = data["checks"]["neo4j"]

    # Required keys in neo4j section
    assert "status" in neo4j, "Missing 'status' in neo4j"
    assert neo4j["status"] in ["up", "down"], f"Invalid neo4j status: {neo4j['status']}"

    if neo4j["status"] == "up":
        assert "latency_ms" in neo4j, "Missing 'latency_ms' when up"
        assert isinstance(neo4j["latency_ms"], (int, float)), "latency_ms should be numeric"
        assert neo4j["latency_ms"] >= 0, "latency_ms should be non-negative"


def test_redis_health_check():
    """Test that Redis health check returns expected structure"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=15
    )

    data = json.loads(result.stdout)
    redis_info = data["checks"]["redis"]

    # Required keys in redis section
    assert "status" in redis_info, "Missing 'status' in redis"
    assert "optional" in redis_info, "Missing 'optional' flag in redis"
    assert redis_info["optional"] is True, "Redis should be marked as optional"

    if redis_info["status"] == "up":
        assert "latency_ms" in redis_info, "Missing 'latency_ms' when up"
        assert isinstance(redis_info["latency_ms"], (int, float)), "latency_ms should be numeric"


def test_bge_m3_model_check():
    """Test that BGE-M3 model check returns expected structure"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=15
    )

    data = json.loads(result.stdout)
    model = data["checks"]["bge_m3"]

    # Required keys in bge_m3 section
    assert "status" in model, "Missing 'status' in bge_m3"
    assert model["status"] in ["available", "unavailable"], f"Invalid bge_m3 status: {model['status']}"

    if model["status"] == "available":
        assert "model_path" in model, "Missing 'model_path' when available"
        # load_time_ms is optional (may not be measured)


def test_cli_tools_check():
    """Test that CLI tools executability check works"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=15
    )

    data = json.loads(result.stdout)
    cli_tools = data["checks"]["cli_tools"]

    # Required keys - all 3 Phase 1 CLI tools
    assert "synapse_search" in cli_tools, "Missing synapse_search check"
    assert "synapse_standard" in cli_tools, "Missing synapse_standard check"
    assert "synapse_template" in cli_tools, "Missing synapse_template check"

    # Each tool should report executable or not_found
    for tool_name, tool_status in cli_tools.items():
        assert tool_status in ["executable", "not_found", "error"], \
            f"Invalid status for {tool_name}: {tool_status}"


def test_overall_status_calculation():
    """Test that overall status is computed correctly"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=15
    )

    data = json.loads(result.stdout)

    # overall status should be one of: healthy, degraded, unhealthy
    assert data["status"] in ["healthy", "degraded", "unhealthy"], \
        f"Invalid overall status: {data['status']}"

    # If Neo4j is down, should be unhealthy
    if data["checks"]["neo4j"]["status"] == "down":
        assert data["status"] == "unhealthy", \
            "Status should be unhealthy when Neo4j is down"

    # If any CLI tool is not executable, should be unhealthy
    cli_tools = data["checks"]["cli_tools"]
    any_tool_missing = any(status != "executable" for status in cli_tools.values())
    if any_tool_missing:
        assert data["status"] in ["unhealthy", "degraded"], \
            "Status should be unhealthy/degraded when CLI tools missing"


def test_ready_for_mcp_flag():
    """Test that ready_for_mcp flag is set correctly"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=15
    )

    data = json.loads(result.stdout)

    # ready_for_mcp should be boolean
    assert isinstance(data["ready_for_mcp"], bool), "ready_for_mcp should be boolean"

    # Should be true if Neo4j up AND all CLI tools executable
    neo4j_up = data["checks"]["neo4j"]["status"] == "up"
    all_tools_ok = all(
        status == "executable"
        for status in data["checks"]["cli_tools"].values()
    )

    expected_ready = neo4j_up and all_tools_ok
    assert data["ready_for_mcp"] == expected_ready, \
        f"ready_for_mcp mismatch: expected {expected_ready}, got {data['ready_for_mcp']}"


def test_timestamp_format():
    """Test that timestamp is in ISO format"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=15
    )

    data = json.loads(result.stdout)

    # Timestamp should be ISO 8601 format
    from datetime import datetime
    try:
        datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
    except ValueError:
        assert False, f"Invalid timestamp format: {data['timestamp']}"


def test_verbose_mode():
    """Test that --verbose flag provides detailed diagnostics"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--verbose"],
        capture_output=True,
        text=True,
        timeout=15
    )

    assert result.returncode == 0, f"Script failed: {result.stderr}"

    output = result.stdout

    # Verbose mode should include more details
    assert len(output) > 0, "No output produced in verbose mode"
    # Should mention all components
    assert "neo4j" in output.lower() or "Neo4j" in output
    assert "redis" in output.lower() or "Redis" in output


def test_human_readable_output():
    """Test that script produces human-readable output without --json"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        timeout=15
    )

    assert result.returncode == 0, f"Script failed: {result.stderr}"

    output = result.stdout
    assert len(output) > 0, "No output produced"

    # Should contain readable status information
    assert "neo4j" in output.lower() or "Neo4j" in output
    assert "status" in output.lower() or "Status" in output


def test_latency_tracking():
    """Test that latency is tracked for each service"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=15
    )

    data = json.loads(result.stdout)

    # Neo4j should have latency if up
    if data["checks"]["neo4j"]["status"] == "up":
        assert "latency_ms" in data["checks"]["neo4j"], \
            "Neo4j should report latency when up"

    # Redis should have latency if up
    if data["checks"]["redis"]["status"] == "up":
        assert "latency_ms" in data["checks"]["redis"], \
            "Redis should report latency when up"


def test_error_handling_graceful():
    """Test that partial failures are handled gracefully"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=15
    )

    # Script should always exit with 0 (health checks report status, not crash)
    assert result.returncode == 0, \
        f"Script should not crash on health check failures: {result.stderr}"

    # Should produce valid JSON even if services are down
    data = json.loads(result.stdout)
    assert "status" in data
    assert "checks" in data


def test_consistency_across_runs():
    """Test that the script queries live data consistently"""
    # Run script twice with short interval
    result1 = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=15
    )

    result2 = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=15
    )

    data1 = json.loads(result1.stdout)
    data2 = json.loads(result2.stdout)

    # Infrastructure status should be consistent
    assert data1["checks"]["neo4j"]["status"] == data2["checks"]["neo4j"]["status"], \
        "Neo4j status should be consistent"

    # CLI tools should be consistent
    assert data1["checks"]["cli_tools"] == data2["checks"]["cli_tools"], \
        "CLI tools status should be consistent"


if __name__ == "__main__":
    # Run tests manually
    sys.exit(pytest.main([__file__, "-v"]))
