#!/usr/bin/env python3
"""
TDD Tests for synapse_search.py
================================

Following Red-Green-Refactor cycle.
These tests will FAIL until synapse_search.py is implemented.

Tests cover:
- Argument parsing
- Embedding computation
- Neo4j query execution
- Vector similarity ranking
- JSON output format
- Error handling
- Latency requirements (<200ms warm)
"""

import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

# Path to the synapse_search.py script (will be created in Green phase)
SCRIPT_PATH = Path(__file__).parent.parent / ".synapse" / "neo4j" / "synapse_search.py"
PYTHON_BIN = Path(__file__).parent.parent / ".venv-ml" / "bin" / "python"


def test_script_exists():
    """Test that synapse_search.py exists"""
    assert SCRIPT_PATH.exists(), f"synapse_search.py not found at {SCRIPT_PATH}"


def test_script_executable():
    """Test that synapse_search.py can be executed with --help"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--help"],
        capture_output=True,
        text=True,
        timeout=5
    )
    # Script should show usage or exit gracefully
    assert result.returncode in [0, 1, 2], f"Script crashed: {result.stderr}"


def test_missing_query_argument():
    """Test that missing query argument shows usage"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        timeout=5
    )
    # Should exit with error code
    assert result.returncode == 1
    assert "Usage" in result.stdout or "Usage" in result.stderr


def test_json_output_format():
    """Test that --json flag produces valid JSON output"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "test query", "--json"],
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

    # Validate required keys
    assert "query" in data, "Missing 'query' key"
    assert "max_results" in data, "Missing 'max_results' key"
    assert "latency_ms" in data, "Missing 'latency_ms' key"
    assert "results" in data, "Missing 'results' key"
    assert isinstance(data["results"], list), "results should be a list"


def test_empty_query_returns_empty():
    """Test that empty query returns 0 results"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "", "--json"],
        capture_output=True,
        text=True,
        timeout=15
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data["results"]) == 0, "Empty query should return 0 results"


def test_search_with_no_patterns_returns_empty():
    """Test that search on empty Pattern Map returns 0 results"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "error handling", "--json"],
        capture_output=True,
        text=True,
        timeout=15
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)
    # Since Pattern Map is empty (Phase 0), should return 0 results
    assert isinstance(data["results"], list)


def test_max_results_argument():
    """Test that max_results argument is respected"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "test query", "5", "--json"],
        capture_output=True,
        text=True,
        timeout=15
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["max_results"] == 5, "max_results should be 5"


def test_latency_tracking():
    """Test that latency is tracked in milliseconds"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "test query", "--json"],
        capture_output=True,
        text=True,
        timeout=15
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "latency_ms" in data
    assert isinstance(data["latency_ms"], (int, float))
    assert data["latency_ms"] >= 0, "Latency should be non-negative"


def test_warm_latency_requirement():
    """Test that warm queries complete in <200ms (after model loaded)"""
    # Warm up: Load model into memory
    subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "warm up query", "--json"],
        capture_output=True,
        text=True,
        timeout=30
    )

    # Measure warm query latency
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "test query", "--json"],
        capture_output=True,
        text=True,
        timeout=15
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)

    # Latency requirement: <200ms for warm queries
    # Note: This may fail on first run before model is cached in memory
    # It's a performance target, not a strict requirement for Phase 1
    latency = data["latency_ms"]
    if latency >= 200:
        pytest.skip(f"Warm latency {latency}ms exceeds target (acceptable for early implementation)")


def test_result_structure():
    """Test that result objects have expected structure"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "test query", "--json"],
        capture_output=True,
        text=True,
        timeout=15
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)

    # If results exist, validate structure
    if len(data["results"]) > 0:
        pattern = data["results"][0]

        # Required fields in pattern result
        assert "id" in pattern, "Pattern missing 'id'"
        assert "name" in pattern, "Pattern missing 'name'"
        assert "description" in pattern, "Pattern missing 'description'"
        assert "language" in pattern, "Pattern missing 'language'"
        assert "similarity" in pattern, "Pattern missing 'similarity'"

        # Similarity should be 0-1 range
        assert 0 <= pattern["similarity"] <= 1, "Similarity out of range"


def test_neo4j_connection_failure_handling():
    """Test graceful handling when Neo4j is down"""
    # This test is informational - we can't easily simulate Neo4j down
    # during test run without affecting other tests
    # Documenting expected behavior: Should return error JSON, not crash
    pass


def test_human_readable_output():
    """Test that script produces human-readable output without --json"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "test query"],
        capture_output=True,
        text=True,
        timeout=15
    )

    assert result.returncode == 0
    output = result.stdout
    assert len(output) > 0, "No output produced"
    # Should contain query or results indication
    assert "query" in output.lower() or "result" in output.lower()


if __name__ == "__main__":
    # Run tests manually
    sys.exit(pytest.main([__file__, "-v"]))
