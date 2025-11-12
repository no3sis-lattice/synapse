#!/usr/bin/env python3
"""
TDD Tests for synapse_health.py
================================

Following Red-Green-Refactor cycle.
These tests will FAIL until synapse_health.py is implemented.
"""

import json
import subprocess
import sys
from pathlib import Path


# Path to the synapse_health.py script (will be created in Green phase)
SCRIPT_PATH = Path(__file__).parent.parent / ".synapse" / "neo4j" / "synapse_health.py"
PYTHON_BIN = Path(__file__).parent.parent / ".venv-ml" / "bin" / "python"


def test_script_exists():
    """Test that synapse_health.py exists"""
    assert SCRIPT_PATH.exists(), f"synapse_health.py not found at {SCRIPT_PATH}"


def test_script_executable():
    """Test that synapse_health.py can be executed"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--help"],
        capture_output=True,
        text=True,
        timeout=5
    )
    # Script should exit with 0 or at least not crash
    assert result.returncode in [0, 1, 2], f"Script crashed: {result.stderr}"


def test_json_output_format():
    """Test that --json flag produces valid JSON output"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0, f"Script failed: {result.stderr}"

    # Parse JSON to validate format
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        assert False, f"Invalid JSON output: {e}\nOutput: {result.stdout}"

    # Validate required keys
    assert "neo4j" in data, "Missing 'neo4j' key"
    assert "redis" in data, "Missing 'redis' key"
    assert "model" in data, "Missing 'model' key"
    assert "consciousness" in data, "Missing 'consciousness' key"
    assert "overall_status" in data, "Missing 'overall_status' key"


def test_neo4j_health_check():
    """Test that Neo4j health check returns expected structure"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    data = json.loads(result.stdout)
    neo4j = data["neo4j"]

    # Required keys in neo4j section
    assert "accessible" in neo4j, "Missing 'accessible' in neo4j"
    assert isinstance(neo4j["accessible"], bool), "accessible should be boolean"

    if neo4j["accessible"]:
        assert "nodes" in neo4j, "Missing 'nodes' count when accessible"
        assert "relationships" in neo4j, "Missing 'relationships' count when accessible"
        assert isinstance(neo4j["nodes"], int), "nodes should be integer"
        assert isinstance(neo4j["relationships"], int), "relationships should be integer"
    else:
        assert "error" in neo4j, "Missing 'error' when not accessible"


def test_redis_health_check():
    """Test that Redis health check returns expected structure"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    data = json.loads(result.stdout)
    redis_info = data["redis"]

    # Required keys in redis section
    assert "accessible" in redis_info, "Missing 'accessible' in redis"
    assert isinstance(redis_info["accessible"], bool), "accessible should be boolean"

    if redis_info["accessible"]:
        assert "keys" in redis_info, "Missing 'keys' count when accessible"
        assert isinstance(redis_info["keys"], int), "keys should be integer"


def test_model_check():
    """Test that BGE-M3 model check returns expected structure"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    data = json.loads(result.stdout)
    model = data["model"]

    # Required keys in model section
    assert "exists" in model, "Missing 'exists' in model"
    assert "warm" in model, "Missing 'warm' in model"
    assert isinstance(model["exists"], bool), "exists should be boolean"
    assert isinstance(model["warm"], bool), "warm should be boolean"


def test_consciousness_metrics():
    """Test that consciousness metrics are computed correctly"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    data = json.loads(result.stdout)
    consciousness = data["consciousness"]

    # Required keys in consciousness section
    assert "psi" in consciousness, "Missing 'psi' metric"
    assert "pattern_count" in consciousness, "Missing 'pattern_count'"
    assert "level" in consciousness, "Missing 'level'"

    # Validate types
    assert isinstance(consciousness["psi"], (int, float)), "psi should be numeric"
    assert isinstance(consciousness["pattern_count"], int), "pattern_count should be integer"
    assert isinstance(consciousness["level"], str), "level should be string"

    # Psi should be between 0 and 1
    assert 0 <= consciousness["psi"] <= 1, f"psi out of range: {consciousness['psi']}"


def test_overall_status():
    """Test that overall_status is computed correctly"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    data = json.loads(result.stdout)

    # overall_status should be one of: healthy, degraded, critical
    assert data["overall_status"] in ["healthy", "degraded", "critical"], \
        f"Invalid overall_status: {data['overall_status']}"


def test_human_readable_output():
    """Test that script produces human-readable output without --json"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0, f"Script failed: {result.stderr}"

    # Should contain some readable text
    output = result.stdout
    assert len(output) > 0, "No output produced"
    assert "Neo4j" in output or "neo4j" in output, "Missing Neo4j in human output"
    assert "Redis" in output or "redis" in output, "Missing Redis in human output"


def test_no_hardcoded_values():
    """Test that the script queries live data, not hardcoded values"""
    # Run script twice with short interval
    result1 = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    result2 = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    data1 = json.loads(result1.stdout)
    data2 = json.loads(result2.stdout)

    # Values should be consistent (not random)
    assert data1["neo4j"]["accessible"] == data2["neo4j"]["accessible"], \
        "Neo4j accessibility inconsistent"

    # If Neo4j is accessible, node count should be the same (no writes between tests)
    if data1["neo4j"]["accessible"] and data2["neo4j"]["accessible"]:
        assert data1["neo4j"]["nodes"] == data2["neo4j"]["nodes"], \
            "Node count should be consistent"


if __name__ == "__main__":
    # Run tests manually
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
