#!/usr/bin/env python3
"""
Migrate remaining TypeScript Specialist tools (14 more after the 2 already done).
"""

from pathlib import Path
import re

# Tool configurations: (function_name, description, params)
TOOLS_TO_MIGRATE = [
    ("suggest_code_refactors", "Suggest refactoring opportunities for TypeScript/JavaScript code", {"file_path": "str", "focus": "str"}),
    ("type_safety_analysis", "Analyze TypeScript code for type safety and coverage", {"file_path": "str", "strict_mode": "bool"}),
    ("improve_type_annotations", "Suggest improvements to TypeScript type annotations", {"code_snippet": "str", "context": "str"}),
    ("verify_strict_mode", "Check TypeScript project strict mode configuration", {"project_path": "str"}),
    ("react_pattern_analysis", "Analyze React component patterns and best practices", {"file_path": "str", "component_type": "str"}),
    ("node_pattern_analysis", "Analyze Node.js patterns and backend best practices", {"file_path": "str", "pattern_type": "str"}),
    ("state_management_suggestions", "Suggest optimal state management patterns for the project", {"project_path": "str", "framework": "str"}),
    ("test_coverage_analysis", "Analyze test coverage for TypeScript/JavaScript project", {"directory_path": "str"}),
    ("generate_test_stubs", "Generate test stubs for TypeScript/JavaScript files", {"file_path": "str", "test_framework": "str"}),
    ("testing_pattern_suggestions", "Suggest testing patterns and best practices", {"file_path": "str", "test_type": "str"}),
    ("build_config_optimization", "Optimize build configuration for better performance", {"config_path": "str", "build_tool": "str"}),
    ("bundle_size_analysis", "Analyze and optimize bundle size for the project", {"project_path": "str"}),
    ("query_typescript_patterns", "Query TypeScript patterns from the Synapse knowledge base", {"pattern_type": "str", "context": "str"}),
    ("search_typescript_standards", "Search TypeScript standards and conventions from Synapse", {"standard_type": "str", "framework": "str"}),
]

def migrate_tool(content: str, func_name: str, description: str, params: dict) -> str:
    """Migrate a single tool."""

    # Pattern to match bare @tool decorator and function
    pattern = rf'(@tool\s*\n)(async def {func_name}\([^)]+\)[^:]*:\s*\n\s*"""[^"]+"""\s*\n\s*try:\s*\n\s*return await [^(]+\([^)]+\))'

    def replacer(match):
        # Build schema string
        schema_items = [f'"{k}": {v}' for k, v in params.items()]
        schema = "{\n        " + ",\n        ".join(schema_items) + "\n    }"

        # New decorator
        new_decorator = f'@tool(\n    "{func_name}",\n    "{description}",\n    {schema}\n)'

        # Get the function part and modify the return
        func_part = match.group(2)

        # Replace "return await" with "result = await" and add structured return
        modified_func = func_part.replace('return await', 'result = await')
        modified_func += '''\n        return {
            "content": [{
                "type": "text",
                "text": str(result)
            }]
        }'''

        return new_decorator + '\n' + modified_func

    return re.sub(pattern, replacer, content, flags=re.DOTALL)


def main():
    agent_file = Path("/home/m0xu/1-projects/synapse/.synapse/agents/typescript-specialist/typescript_specialist_agent.py")

    print("Migrating remaining 14 tools in typescript-specialist...")

    content = agent_file.read_text()
    original = content

    for func_name, description, params in TOOLS_TO_MIGRATE:
        print(f"  Migrating {func_name}...")
        content = migrate_tool(content, func_name, description, params)

    if content != original:
        # Backup
        backup_file = agent_file.with_suffix('.py.ts_mig_bak')
        backup_file.write_text(original)

        # Write updated
        agent_file.write_text(content)
        print(f"\n✓ Migration complete! Backup: {backup_file.name}")
    else:
        print("\n⚠ No changes made")


if __name__ == "__main__":
    main()
