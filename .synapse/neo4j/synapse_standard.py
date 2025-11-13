#!/usr/bin/env python3
"""
Synapse Coding Standards Retrieval Tool
========================================

Retrieve language-specific coding standards from Pattern Map (Neo4j).

Standards include:
- Naming conventions
- Import organization
- Error handling patterns
- Testing guidelines
- Module structure

Usage:
    python synapse_standard.py <language> [--json]

Examples:
    python synapse_standard.py python --json
    python synapse_standard.py rust
    python synapse_standard.py typescript --json
"""

import json
import sys
from typing import Dict, Any
from datetime import datetime

# Import shared configuration (DRY principle)
from synapse_config import (
    NEO4J_URI,
    NEO4J_AUTH,
    check_neo4j_available
)


def get_standards(language: str) -> Dict[str, Any]:
    """
    Retrieve coding standards for a specific language from Neo4j.

    Args:
        language: Programming language (e.g., 'python', 'rust', 'typescript')

    Returns:
        Dict containing standards data:
        {
            "language": str,
            "standards": List[Dict],
            "source": "Pattern Map",
            "last_updated": str (ISO format)
        }
    """
    # Normalize language to lowercase
    language = language.lower()

    result = {
        "language": language,
        "standards": [],
        "source": "Pattern Map",
        "last_updated": datetime.now().isoformat()
    }

    # Check Neo4j availability
    if not check_neo4j_available():
        result["error"] = "neo4j package not available"
        return result

    # Query Neo4j for standards
    from neo4j import GraphDatabase

    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
        try:
            with driver.session() as session:
                # Query for standards matching the language
                query_result = session.run("""
                    MATCH (s:Standard {language: $language})
                    RETURN s.category as category,
                           s.rule as rule,
                           s.priority as priority,
                           s.updated as updated
                    ORDER BY s.priority DESC, s.category
                """, language=language)

                for record in query_result:
                    standard = {
                        "category": record.get("category", "general"),
                        "rule": record.get("rule", "")
                    }

                    # Include optional fields if present
                    if record.get("priority"):
                        standard["priority"] = record["priority"]
                    if record.get("updated"):
                        standard["updated"] = record["updated"]

                    result["standards"].append(standard)

        finally:
            driver.close()

    except Exception as e:
        result["error"] = f"Neo4j query failed: {str(e)}"

    return result


def format_human_readable(result: Dict[str, Any]) -> str:
    """
    Format standards result as human-readable text.

    Args:
        result: Standards result dict from get_standards()

    Returns:
        Formatted string for console output
    """
    lines = []
    lines.append(f"Language: {result['language']}")
    lines.append(f"Source: {result['source']}")
    lines.append("")

    if "error" in result:
        lines.append(f"Error: {result['error']}")
    elif len(result["standards"]) == 0:
        lines.append("No standards found (Pattern Map may be empty or language not recognized)")
        lines.append("")
        lines.append("Supported languages: python, rust, typescript, go, javascript, etc.")
    else:
        lines.append(f"Standards ({len(result['standards'])}):")
        lines.append("")

        # Group by category for better readability
        by_category = {}
        for standard in result["standards"]:
            category = standard.get("category", "general")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(standard)

        # Print grouped
        for category, standards in by_category.items():
            lines.append(f"[{category.upper()}]")
            for standard in standards:
                priority = standard.get("priority", "medium")
                lines.append(f"  - {standard['rule']} (priority: {priority})")
            lines.append("")

    return "\n".join(lines)


def print_usage():
    """Print usage information"""
    print("Usage: python synapse_standard.py <language> [--json]")
    print()
    print("Arguments:")
    print("  language     Programming language (required)")
    print("               Supported: python, rust, typescript, go, etc.")
    print("  --json       Output JSON format")
    print()
    print("Examples:")
    print("  python synapse_standard.py python --json")
    print("  python synapse_standard.py rust")
    print("  python synapse_standard.py typescript --json")


def main():
    """Main entry point for CLI"""
    # Handle --help flag FIRST
    if "--help" in sys.argv or "-h" in sys.argv:
        print_usage()
        sys.exit(0)

    # Check arguments
    if len(sys.argv) < 2:
        print("Error: Missing required language argument", file=sys.stderr)
        print()
        print_usage()
        sys.exit(1)

    language = sys.argv[1]

    # Check if language looks valid (basic sanity check)
    if language.startswith("-"):
        print(f"Error: Invalid language '{language}'", file=sys.stderr)
        print()
        print_usage()
        sys.exit(1)

    # Parse --json flag
    json_mode = "--json" in sys.argv

    # Execute query
    try:
        result = get_standards(language)

        if json_mode:
            print(json.dumps(result, indent=2))
        else:
            # Human-readable output
            print(format_human_readable(result))

    except Exception as e:
        error = {
            "error": str(e),
            "language": language,
            "standards": []
        }
        if json_mode:
            print(json.dumps(error, indent=2))
        else:
            print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
