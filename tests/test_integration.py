"""
Integration tests for No3sis MCP server.

Tests the wrapper functions against actual Synapse tools.
"""

import pytest
from no3sis.server import (
    search_pattern_map,
    get_coding_standard,
    get_project_template,
    check_system_health,
)


def test_health_check():
    """Test that health check returns valid structure."""
    result = check_system_health()

    # Should have these keys
    assert "overall_status" in result
    assert result["overall_status"] in ["healthy", "degraded", "unhealthy", "error"]

    # If successful, should have components
    if result["overall_status"] != "error":
        assert "components" in result
        assert "recommendations" in result


def test_search_pattern_map():
    """Test pattern map search."""
    result = search_pattern_map("error handling", max_results=3)

    # Should return either results or error
    if "error" not in result:
        # Successful search
        assert "context" in result or "patterns" in result
    else:
        # Error case - should have helpful info
        assert "suggestion" in result or "details" in result


def test_get_coding_standard():
    """Test coding standard retrieval."""
    result = get_coding_standard("naming-conventions", "rust")

    # Should return either standard or error
    if "error" not in result:
        assert "language" in result
        assert "standard_type" in result
        assert "content" in result
    else:
        assert "suggestion" in result or "details" in result


def test_get_project_template():
    """Test template retrieval."""
    result = get_project_template("cli-app", "rust")

    # Should return either template or error
    if "error" not in result:
        assert "template_type" in result
        assert "language" in result
    else:
        assert "suggestion" in result or "details" in result


@pytest.mark.parametrize("query,expected_type", [
    ("async patterns", "search"),
    ("rust error handling", "search"),
    ("testing best practices", "search"),
])
def test_search_variations(query, expected_type):
    """Test various search queries."""
    result = search_pattern_map(query, max_results=5)

    # Should always return a dict
    assert isinstance(result, dict)


if __name__ == "__main__":
    # Run tests manually
    print("Testing health check...")
    health = check_system_health()
    print(f"Health: {health.get('overall_status')}")

    print("\nTesting pattern search...")
    search = search_pattern_map("error handling", 3)
    print(f"Search: {'success' if 'error' not in search else 'error'}")

    print("\nAll manual tests complete!")
