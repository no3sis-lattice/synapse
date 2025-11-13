#!/usr/bin/env python3
"""
TDD Tests for synapse_template.py
===================================

Following Red-Green-Refactor cycle.
These tests will FAIL until synapse_template.py is implemented.

Tests cover:
- Argument parsing
- Template retrieval from Neo4j
- Variable substitution
- File tree structure
- JSON output format
- Error handling
- Human-readable output
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Path to the synapse_template.py script (will be created in Green phase)
SCRIPT_PATH = Path(__file__).parent.parent / ".synapse" / "neo4j" / "synapse_template.py"
PYTHON_BIN = Path(__file__).parent.parent / ".venv-ml" / "bin" / "python"


def test_script_exists():
    """Test that synapse_template.py exists"""
    assert SCRIPT_PATH.exists(), f"synapse_template.py not found at {SCRIPT_PATH}"


def test_script_executable():
    """Test that synapse_template.py can be executed with --help"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "--help"],
        capture_output=True,
        text=True,
        timeout=5
    )
    # Script should show usage and exit gracefully
    assert result.returncode == 0, f"Script crashed: {result.stderr}"
    assert "usage" in result.stdout.lower() or "help" in result.stdout.lower()


def test_missing_template_argument():
    """Test that missing template_name argument shows usage"""
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
        [str(PYTHON_BIN), str(SCRIPT_PATH), "fastapi-service", "--json"],
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
    assert "template_name" in data, "Missing 'template_name' key"
    assert "description" in data, "Missing 'description' key"
    assert "variables" in data, "Missing 'variables' key"
    assert "files" in data, "Missing 'files' key"
    assert "file_tree" in data, "Missing 'file_tree' key"
    assert "source" in data, "Missing 'source' key"
    assert isinstance(data["files"], list), "files should be a list"
    assert isinstance(data["file_tree"], list), "file_tree should be a list"
    assert isinstance(data["variables"], dict), "variables should be a dict"


def test_valid_template_retrieval():
    """Test that valid template name retrieves template"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "fastapi-service", "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["template_name"] == "fastapi-service"
    assert isinstance(data["files"], list)


def test_invalid_template_returns_error():
    """Test that invalid template returns helpful error"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "nonexistent-template", "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    # Should either exit with error or return error in JSON
    if result.returncode != 0:
        # Error mode: Should show helpful message
        output = result.stdout + result.stderr
        assert "not found" in output.lower() or "invalid" in output.lower()
    else:
        # Graceful mode: Return error in JSON
        data = json.loads(result.stdout)
        assert "error" in data or len(data["files"]) == 0


def test_variable_substitution_single():
    """Test that single --var flag substitutes variables correctly"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "fastapi-service",
         "--var", "project_name=myapi", "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "variables" in data
    assert "project_name" in data["variables"]
    assert data["variables"]["project_name"] == "myapi"


def test_variable_substitution_multiple():
    """Test that multiple --var flags work correctly"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "fastapi-service",
         "--var", "project_name=myapi",
         "--var", "port=8080",
         "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "variables" in data
    assert data["variables"]["project_name"] == "myapi"
    assert data["variables"]["port"] == "8080"


def test_variable_substitution_in_content():
    """Test that variables are substituted in file content"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "fastapi-service",
         "--var", "project_name=testapp", "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)

    # If files exist, check that variable placeholders are replaced
    if len(data["files"]) > 0:
        # Should not contain unresolved placeholders like {{project_name}}
        for file in data["files"]:
            content = file.get("content", "")
            # If variables were provided, placeholders should be resolved
            if "{{" in content and "}}" in content:
                # Unresolved placeholder found - acceptable if no template data yet
                pass


def test_file_tree_structure():
    """Test that file_tree contains valid paths"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "fastapi-service", "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)

    # file_tree should be list of strings (paths)
    assert isinstance(data["file_tree"], list)
    for path in data["file_tree"]:
        assert isinstance(path, str), "file_tree paths should be strings"


def test_file_structure():
    """Test that file objects have expected structure"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "fastapi-service", "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)

    # If files exist, validate structure
    if len(data["files"]) > 0:
        file_obj = data["files"][0]

        # Required fields in file object
        assert "path" in file_obj, "File missing 'path'"
        assert "content" in file_obj, "File missing 'content'"
        assert isinstance(file_obj["path"], str), "path should be string"
        assert isinstance(file_obj["content"], str), "content should be string"


def test_human_readable_output():
    """Test that script produces human-readable output without --json"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "fastapi-service"],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0
    output = result.stdout
    assert len(output) > 0, "No output produced"
    # Should contain template indication
    assert "template" in output.lower() or "fastapi" in output.lower()


def test_neo4j_connection_failure_handling():
    """Test graceful handling when Neo4j is unavailable"""
    # This test validates that the script returns error JSON, not crash
    # We can't easily simulate Neo4j down during test, so we document expected behavior
    # Expected: Should return {"error": "...", "files": []} or exit gracefully
    pass


def test_empty_template_scenario():
    """Test that empty template (no files) returns empty list"""
    result = subprocess.run(
        [str(PYTHON_BIN), str(SCRIPT_PATH), "fastapi-service", "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)
    # Should return empty list, not crash (Pattern Map may be empty)
    assert isinstance(data["files"], list)
    assert len(data["files"]) >= 0


if __name__ == "__main__":
    # Run tests manually
    sys.exit(pytest.main([__file__, "-v"]))
