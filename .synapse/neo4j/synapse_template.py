#!/usr/bin/env python3
"""
Synapse Template Retrieval Tool
================================

Retrieve project templates and boilerplate code from Pattern Map (Neo4j).

Usage:
    python synapse_template.py <template_name> [--json] [--var key=value ...]

Examples:
    python synapse_template.py fastapi-service --json
    python synapse_template.py react-component --var component_name=Button
    python synapse_template.py fastapi-service --var project_name=myapi --var port=8080 --json
"""

import json
import sys
from typing import Dict, Any, List

# Import shared configuration (DRY principle)
from synapse_config import (
    NEO4J_URI,
    NEO4J_AUTH,
    check_neo4j_available
)


def substitute_variables(content: str, variables: Dict[str, str]) -> str:
    """Substitute {{variable_name}} placeholders with values."""
    result = content
    for key, value in variables.items():
        result = result.replace(f"{{{{{key}}}}}", value)
    return result


def build_file_tree(path: str) -> List[str]:
    """Build file tree entries from a file path (directories + file)."""
    parts = path.split("/")
    tree = []
    for i in range(len(parts)):
        if i < len(parts) - 1:  # Directory
            tree.append("/".join(parts[:i+1]) + "/")
        else:  # File
            tree.append(path)
    return tree


def get_template(template_name: str, variables: Dict[str, str]) -> Dict[str, Any]:
    """
    Retrieve template from Neo4j and apply variable substitution.

    Returns:
        {
            "template_name": str,
            "description": str,
            "variables": Dict[str, str],
            "files": List[{path, content}],
            "file_tree": List[str],
            "source": "Pattern Map"
        }
    """
    result = {
        "template_name": template_name,
        "description": "",
        "variables": variables,
        "files": [],
        "file_tree": [],
        "source": "Pattern Map"
    }

    if not check_neo4j_available():
        result["error"] = "neo4j package not available"
        return result

    from neo4j import GraphDatabase

    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
        try:
            with driver.session() as session:
                query_result = session.run("""
                    MATCH (t:Template {name: $template_name})
                    OPTIONAL MATCH (t)-[:HAS_FILE]->(f:TemplateFile)
                    RETURN t.description as description,
                           collect({path: f.path, content: f.content}) as files
                """, template_name=template_name)

                record = query_result.single()
                if not record:
                    result["error"] = f"Template '{template_name}' not found"
                    return result

                result["description"] = record.get("description", "")
                file_tree_set = set()

                for file_data in record.get("files", []):
                    path = file_data.get("path")
                    if path is None:  # Skip empty OPTIONAL MATCH results
                        continue

                    # Apply variable substitution to path and content
                    path_sub = substitute_variables(path, variables)
                    content_sub = substitute_variables(file_data.get("content", ""), variables)

                    result["files"].append({"path": path_sub, "content": content_sub})

                    # Build file tree
                    file_tree_set.update(build_file_tree(path_sub))

                result["file_tree"] = sorted(file_tree_set)
        finally:
            driver.close()
    except Exception as e:
        result["error"] = f"Neo4j query failed: {str(e)}"

    return result


def format_human_readable(result: Dict[str, Any]) -> str:
    """Format template result as human-readable text."""
    lines = [
        f"Template: {result['template_name']}",
        f"Description: {result['description']}" if result.get("description") else None,
        f"Source: {result['source']}",
        ""
    ]
    lines = [l for l in lines if l is not None]  # Remove None entries

    if "error" in result:
        lines.append(f"Error: {result['error']}")
    elif not result["files"]:
        lines.append("No files found (Template may be empty or not exist)")
    else:
        if result["variables"]:
            lines.append("Variables:")
            lines.extend(f"  {k} = {v}" for k, v in result["variables"].items())
            lines.append("")

        lines.append(f"File Tree ({len(result['file_tree'])} entries):")
        lines.extend(f"  {path}" for path in result["file_tree"])
        lines.append("")

        lines.append(f"Files ({len(result['files'])}):")
        lines.extend(f"  {f['path']} ({len(f['content'])} bytes)" for f in result["files"])

    return "\n".join(lines)


def parse_var_arguments(args: List[str]) -> Dict[str, str]:
    """Parse --var key=value arguments from command line."""
    variables = {}
    i = 0
    while i < len(args):
        if args[i] == "--var" and i + 1 < len(args):
            if "=" in args[i + 1]:
                key, value = args[i + 1].split("=", 1)
                variables[key.strip()] = value.strip()
            i += 2
        else:
            i += 1
    return variables


def print_usage():
    """Print usage information"""
    print("Usage: python synapse_template.py <template_name> [--json] [--var key=value ...]")
    print("\nArguments:")
    print("  template_name    Name of template (required)")
    print("  --json           Output JSON format")
    print("  --var key=value  Substitute variable (repeatable)")
    print("\nExamples:")
    print("  python synapse_template.py fastapi-service --json")
    print("  python synapse_template.py react-component --var component_name=Button")
    print("  python synapse_template.py fastapi-service --var project_name=myapi --var port=8080 --json")


def main():
    """Main entry point for CLI"""
    if "--help" in sys.argv or "-h" in sys.argv:
        print_usage()
        sys.exit(0)

    if len(sys.argv) < 2:
        print("Error: Missing required template_name argument", file=sys.stderr)
        print()
        print_usage()
        sys.exit(1)

    template_name = sys.argv[1]
    if template_name.startswith("-"):
        print(f"Error: Invalid template_name '{template_name}'", file=sys.stderr)
        print()
        print_usage()
        sys.exit(1)

    json_mode = "--json" in sys.argv
    variables = parse_var_arguments(sys.argv[2:])

    try:
        result = get_template(template_name, variables)

        if json_mode:
            print(json.dumps(result, indent=2))
        else:
            print(format_human_readable(result))

    except Exception as e:
        error = {"error": str(e), "template_name": template_name, "files": []}
        if json_mode:
            print(json.dumps(error, indent=2))
        else:
            print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
