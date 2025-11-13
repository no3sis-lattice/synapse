#!/usr/bin/env python3
"""
TDD Tests for synapse_standard.py
===================================

Following Red-Green-Refactor cycle.
These tests will FAIL until synapse_standard.py is implemented.

Tests cover:
- Argument parsing
- Language validation
- Neo4j query execution
- JSON output format
- Standard retrieval
- Error handling
- Human-readable output
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Path to the synapse_standard.py script (will be created in Green phase)
SCRIPT_PATH = Path(__file__).parent.parent / ".synapse" / "neo4j" / "synapse_standard.py"
PYTHON_BIN = Path(__file__).parent.parent / ".venv-ml" / "bin" / "python"


def test_script_exists():
    """Test that synapse_standard.py exists"""
    assert SCRIPT_PATH.exists(), f"synapse_standard.py not found at {SCRIPT_PATH}"


def test_script_executable():
    """Test that synapse_standard.py can be executed with --help"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--help"],
        capture_output=True,
        text=True,
        timeout=5
    )
    # Script should show usage and exit gracefully
    assert result.returncode == 0, f"Script crashed: {result.stderr}"
    assert "usage" in result.stdout.lower() or "help" in result.stdout.lower()


def test_missing_language_argument():
    """Test that missing language argument shows usage"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        timeout=5
    )
    # Should exit with error code
    assert result.returncode == 1
    assert "usage" in result.stdout.lower() or "usage" in result.stderr.lower()


def test_json_output_format():
    """Test that --json flag produces valid JSON output"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "python", "--json"],
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
    assert "language" in data, "Missing 'language' key"
    assert "standards" in data, "Missing 'standards' key"
    assert "source" in data, "Missing 'source' key"
    assert isinstance(data["standards"], list), "standards should be a list"


def test_valid_language_python():
    """Test that valid language 'python' is accepted"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "python", "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["language"] == "python"
    assert isinstance(data["standards"], list)


def test_valid_language_rust():
    """Test that valid language 'rust' is accepted"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "rust", "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["language"] == "rust"
    assert isinstance(data["standards"], list)


def test_valid_language_typescript():
    """Test that valid language 'typescript' is accepted"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "typescript", "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["language"] == "typescript"
    assert isinstance(data["standards"], list)


def test_invalid_language_returns_error():
    """Test that invalid language returns helpful error"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "invalid_language", "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    # Should either exit with error or return error in JSON
    if result.returncode != 0:
        # Error mode: Should show helpful message
        output = result.stdout + result.stderr
        assert "invalid" in output.lower() or "unknown" in output.lower()
    else:
        # Graceful mode: Return error in JSON
        data = json.loads(result.stdout)
        assert "error" in data or len(data["standards"]) == 0


def test_empty_standards_graceful_handling():
    """Test that empty standards (no data in Neo4j) returns empty list"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "python", "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)
    # Should return empty list, not crash
    assert isinstance(data["standards"], list)
    # Pattern Map is empty in Phase 0, so this is expected
    assert len(data["standards"]) >= 0


def test_standard_structure():
    """Test that standard objects have expected structure"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "python", "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)

    # If standards exist, validate structure
    if len(data["standards"]) > 0:
        standard = data["standards"][0]

        # Required fields in standard
        assert "category" in standard, "Standard missing 'category'"
        assert "rule" in standard, "Standard missing 'rule'"

        # Optional fields
        # priority and updated are optional but good to have


def test_human_readable_output():
    """Test that script produces human-readable output without --json"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "python"],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0
    output = result.stdout
    assert len(output) > 0, "No output produced"
    # Should contain language indication
    assert "python" in output.lower() or "standard" in output.lower()


def test_neo4j_connection_failure_handling():
    """Test graceful handling when Neo4j is unavailable"""
    # This test validates that the script returns error JSON, not crash
    # We can't easily simulate Neo4j down during test, so we document expected behavior
    # Expected: Should return {"error": "...", "standards": []} or exit gracefully
    pass


def test_case_insensitive_language():
    """Test that language argument is case-insensitive"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "Python", "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)
    # Should normalize to lowercase
    assert data["language"].lower() == "python"


if __name__ == "__main__":
    # Run tests manually
    sys.exit(pytest.main([__file__, "-v"]))
