#!/usr/bin/env python3
"""
Batch migrate all agents to shared mock SDK with updated tool decorators.

This script applies the proven migration pattern to all remaining agents.
"""

import re
from pathlib import Path
from typing import Dict, List

AGENTS_DIR = Path(".synapse/agents")

# Agents to migrate (excluding file-creator and tool-runner which are done)
AGENTS_TO_MIGRATE = [
    "test-runner",
    "typescript-specialist",
    "rust-specialist",
    "python-specialist",
    "golang-specialist",
    "ux-designer",
    "docs-writer",
    "architect",
    "devops-engineer",
    "security-specialist",
    "git-workflow",
    "code-hound",
    "boss",
    "pneuma"
]

def update_imports_section(content: str) -> str:
    """Update the imports section to use shared mock SDK."""

    # Pattern to match the entire import fallback section
    pattern = r'(except ImportError:)\s*#.*?\n\s*print\([^)]+\)\s*from tools\.mock_sdk import[^)]+\)'

    replacement = r'''\1
    # Fallback for development/testing - use shared mock SDK
    print("⚠️  Claude Agent SDK not available, using shared mock SDK")
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))
    from mock_sdk import (
        create_sdk_mcp_server,
        tool,
        query,
        ClaudeAgentOptions
    )'''

    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    return content


def update_bare_tool_decorators(content: str) -> str:
    """Update bare @tool decorators to new format with name, description, and schema."""

    lines = content.split('\n')
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this is a bare @tool decorator
        if line.strip() == '@tool':
            # Look ahead for the function definition
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                func_match = re.match(r'\s*async def (\w+)\(args: (\w+)\)', next_line)

                if func_match:
                    func_name = func_match.group(1)
                    args_type = func_match.group(2)

                    # Look ahead for docstring
                    description = f"Execute {func_name.replace('_', ' ')}"
                    if i + 2 < len(lines) and '"""' in lines[i + 2]:
                        doc_line = lines[i + 2].strip().strip('"""')
                        if doc_line:
                            description = doc_line

                    # Get indentation
                    indent = ' ' * (len(line) - len(line.lstrip()))

                    # Create new decorator
                    new_lines.append(f'{indent}@tool(')
                    new_lines.append(f'{indent}    "{func_name}",')
                    new_lines.append(f'{indent}    "{description}",')
                    new_lines.append(f'{indent}    {{}}')
                    new_lines.append(f'{indent})')
                    i += 1
                    continue

        new_lines.append(line)
        i += 1

    return '\n'.join(new_lines)


def update_return_statements(content: str) -> str:
    """Update return statements to use structured content format."""

    lines = content.split('\n')
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check for return await pattern in tool functions
        if 'return await' in line:
            # Check if we're in a tool function
            in_tool_func = False
            for j in range(max(0, i-15), i):
                if '@tool(' in lines[j]:
                    in_tool_func = True
                    break

            if in_tool_func and '"content"' not in line:
                # Get indentation and extract the return value
                indent = len(line) - len(line.lstrip())
                spaces = ' ' * indent
                return_val = line.strip()[len('return '):]

                # Check if next lines already have structured return
                if i + 1 < len(lines) and 'content' in lines[i + 1]:
                    new_lines.append(line)
                    i += 1
                    continue

                # Create structured return
                new_lines.append(f'{spaces}result = {return_val}')
                new_lines.append(f'{spaces}return {{')
                new_lines.append(f'{spaces}    "content": [')
                new_lines.append(f'{spaces}        {{"type": "text", "text": str(result)}}')
                new_lines.append(f'{spaces}    ]')
                new_lines.append(f'{spaces}}}')
                i += 1
                continue

        new_lines.append(line)
        i += 1

    return '\n'.join(new_lines)


def migrate_agent(agent_name: str) -> Dict[str, any]:
    """Migrate a single agent."""
    result = {
        "agent": agent_name,
        "success": False,
        "changes": [],
        "errors": []
    }

    agent_dir = AGENTS_DIR / agent_name
    if not agent_dir.exists():
        result["errors"].append(f"Agent directory not found: {agent_dir}")
        return result

    # Find agent file
    agent_files = list(agent_dir.glob("*_agent.py"))
    if not agent_files:
        result["errors"].append("No agent file found")
        return result

    agent_file = agent_files[0]

    try:
        content = agent_file.read_text()
        original_content = content

        # Apply migrations
        content = update_imports_section(content)
        if content != original_content:
            result["changes"].append("✓ Updated imports to shared mock SDK")
            original_content = content

        content = update_bare_tool_decorators(content)
        if content != original_content:
            # Count how many decorators were updated
            count = content.count('@tool(') - original_content.count('@tool(')
            if count > 0:
                result["changes"].append(f"✓ Updated {count} tool decorators")
            original_content = content

        content = update_return_statements(content)
        if content != original_content:
            # Count structured returns
            count = content.count('"content": [') - original_content.count('"content": [')
            if count > 0:
                result["changes"].append(f"✓ Updated {count} return statements")

        # Write back if changed
        if content != agent_file.read_text():
            agent_file.write_text(content)
            result["success"] = True
        else:
            result["changes"].append("No changes needed")
            result["success"] = True

        # Remove local mock_sdk.py
        mock_sdk = agent_dir / "tools" / "mock_sdk.py"
        if mock_sdk.exists():
            mock_sdk.unlink()
            result["changes"].append("✓ Removed local mock_sdk.py")

    except Exception as e:
        result["errors"].append(str(e))

    return result


def main():
    print("=" * 70)
    print("BATCH AGENT MIGRATION")
    print("=" * 70)
    print()

    results = []

    for agent_name in AGENTS_TO_MIGRATE:
        print(f"\nMigrating: {agent_name}")
        print("-" * 70)

        result = migrate_agent(agent_name)
        results.append(result)

        if result["success"]:
            print("✓ SUCCESS")
            for change in result["changes"]:
                print(f"  {change}")
        else:
            print("✗ FAILED")
            for error in result["errors"]:
                print(f"  ERROR: {error}")

    # Summary
    print()
    print("=" * 70)
    print("MIGRATION SUMMARY")
    print("=" * 70)

    success_count = sum(1 for r in results if r["success"])
    total_count = len(results)

    print(f"\nSuccess: {success_count}/{total_count} agents")

    if success_count == total_count:
        print("\n✓ ALL AGENTS MIGRATED SUCCESSFULLY!")
        print("\nNext steps:")
        print("1. Verify: find .synapse/agents -name 'mock_sdk.py' (should be empty)")
        print("2. Update CHANGELOG.md")
        print("3. Commit changes")
    else:
        print("\n⚠️  Some agents failed - review errors above")
        failed = [r["agent"] for r in results if not r["success"]]
        print(f"Failed agents: {', '.join(failed)}")


if __name__ == "__main__":
    main()
