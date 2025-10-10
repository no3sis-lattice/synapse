#!/usr/bin/env python3
"""
Complete SDK Migration: Shared Mock SDK + Tool Decorator Updates

This script performs the complete migration:
1. Updates imports to use shared mock SDK
2. Updates tool decorators to new format
3. Updates return statements to structured content
4. Removes local mock_sdk.py files

Usage:
    python scripts/full_sdk_migration.py [--dry-run] [--agent AGENT_NAME]
"""

import argparse
import re
from pathlib import Path
from typing import List, Tuple, Dict


AGENTS_DIR = Path(".synapse/agents")
SHARED_MOCK_PATH = Path(".synapse/shared/mock_sdk.py")


def find_agents() -> List[Path]:
    """Find all agent directories."""
    agents = []
    for agent_dir in AGENTS_DIR.iterdir():
        if agent_dir.is_dir() and not agent_dir.name.startswith('.'):
            agent_files = list(agent_dir.glob("*_agent.py"))
            if agent_files:
                agents.append(agent_dir)
    return agents


def update_imports(content: str) -> Tuple[str, bool]:
    """Update imports to use shared mock SDK."""
    original = content

    # Pattern for the import fallback section
    pattern = r'(except ImportError:)\s*.*?print\([^)]+\)\s*from tools\.mock_sdk import[^)]+\)'

    replacement = r'''\1
    # Fallback for development/testing
    print("⚠️  Claude Agent SDK not available, using shared mock SDK")
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))
    from mock_sdk import (
        create_sdk_mcp_server,
        tool,
        query,
        ClaudeAgentOptions
    )'''

    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    return content, content != original


def extract_tool_info(func_text: str, func_name: str) -> Dict[str, str]:
    """Extract information from a function to create tool decorator."""
    # Extract docstring
    doc_match = re.search(r'"""([^"]+)"""', func_text)
    description = doc_match.group(1).strip() if doc_match else f"Execute {func_name}"

    # Extract parameter types from TypedDict if available
    # For now, use a simple schema
    schema = "dict"  # Simplified - could be enhanced to parse TypedDict

    return {
        "name": func_name,
        "description": description,
        "schema": schema
    }


def update_tool_decorators(content: str) -> Tuple[str, bool, List[str]]:
    """Update @tool decorators to new format."""
    original = content
    changes = []

    # Find all @tool decorator uses (bare @tool without arguments)
    # Pattern: @tool followed by newline and async def
    pattern = r'@tool\s*\n\s*async def (\w+)\([^)]+\)'

    def replace_decorator(match):
        func_name = match.group(1)
        # Get the full function text for analysis
        func_start = match.end()
        # Find next function or end of file
        next_func = content.find('\n@tool', func_start)
        next_func = next_func if next_func != -1 else content.find('\nasync def main', func_start)
        func_text = content[match.start():next_func if next_func != -1 else len(content)]

        # Extract function info
        info = extract_tool_info(func_text, func_name)

        # Create new decorator
        new_decorator = f'@tool(\n    "{info["name"]}",\n    "{info["description"]}",\n    {{}}\n)\n{match.group(0).split("@tool")[1]}'

        changes.append(f"Updated @tool decorator for {func_name}")
        return new_decorator

    content = re.sub(pattern, replace_decorator, content)

    return content, content != original, changes


def update_return_statements(content: str) -> Tuple[str, bool, List[str]]:
    """Update return statements to structured content format."""
    original = content
    changes = []

    # Find return statements that don't already use structured content
    # Pattern: return await ... or return {...}
    # Skip if already has "content": [

    lines = content.split('\n')
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this is a return statement in a tool function
        if 'return await' in line or (line.strip().startswith('return {') and '"content"' not in line):
            # Check if we're in a @tool function (look backwards)
            in_tool_function = False
            for j in range(i-1, max(0, i-20), -1):
                if '@tool' in lines[j]:
                    in_tool_function = True
                    break
                if 'async def main' in lines[j] or 'def ' in lines[j] and '@tool' not in lines[j-1]:
                    break

            if in_tool_function and '"content"' not in line:
                # Get indentation
                indent = len(line) - len(line.lstrip())
                spaces = ' ' * indent

                # Extract the return value
                return_val = line.strip()[len('return '):]

                # Create structured return
                new_lines.append(f'{spaces}result = {return_val}')
                new_lines.append(f'{spaces}return {{')
                new_lines.append(f'{spaces}    "content": [')
                new_lines.append(f'{spaces}        {{"type": "text", "text": str(result)}}')
                new_lines.append(f'{spaces}    ]')
                new_lines.append(f'{spaces}}}')

                changes.append(f"Updated return statement at line {i+1}")
                i += 1
                continue

        new_lines.append(line)
        i += 1

    content = '\n'.join(new_lines)

    return content, content != original, changes


def migrate_agent(agent_dir: Path, dry_run: bool = False) -> Dict[str, any]:
    """Migrate a single agent."""
    result = {
        "agent": agent_dir.name,
        "success": False,
        "changes": [],
        "errors": []
    }

    # Find agent file
    agent_files = list(agent_dir.glob("*_agent.py"))
    if not agent_files:
        result["errors"].append("No agent file found")
        return result

    agent_file = agent_files[0]

    try:
        content = agent_file.read_text()
        original_content = content
        all_changes = []

        # Step 1: Update imports
        content, changed = update_imports(content)
        if changed:
            all_changes.append("Updated imports to shared mock SDK")

        # Step 2: Update tool decorators
        content, changed, changes = update_tool_decorators(content)
        if changed:
            all_changes.extend(changes)

        # Step 3: Update return statements
        content, changed, changes = update_return_statements(content)
        if changed:
            all_changes.extend(changes)

        # Write changes if not dry run
        if content != original_content:
            if not dry_run:
                agent_file.write_text(content)
                result["success"] = True
            else:
                result["success"] = True  # Would succeed
            result["changes"] = all_changes
        else:
            result["changes"] = ["No changes needed"]
            result["success"] = True

        # Step 4: Remove local mock_sdk.py
        mock_sdk = agent_dir / "tools" / "mock_sdk.py"
        if mock_sdk.exists():
            if not dry_run:
                mock_sdk.unlink()
                result["changes"].append("Removed local mock_sdk.py")
            else:
                result["changes"].append("Would remove local mock_sdk.py")

    except Exception as e:
        result["errors"].append(str(e))

    return result


def main():
    parser = argparse.ArgumentParser(description="Complete SDK migration")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--agent", help="Migrate specific agent only")
    args = parser.parse_args()

    # Find all agents
    agents = find_agents()

    if args.agent:
        agents = [a for a in agents if a.name == args.agent]
        if not agents:
            print(f"Agent {args.agent} not found")
            return

    print(f"{'='*60}")
    print(f"SDK MIGRATION: {'DRY RUN' if args.dry_run else 'LIVE MODE'}")
    print(f"{'='*60}\n")
    print(f"Found {len(agents)} agents to migrate\n")

    # Migrate each agent
    results = []
    for agent_dir in agents:
        print(f"{'='*60}")
        print(f"Agent: {agent_dir.name}")
        print(f"{'='*60}")

        result = migrate_agent(agent_dir, args.dry_run)
        results.append(result)

        if result["success"]:
            print("✓ SUCCESS")
            for change in result["changes"]:
                print(f"  - {change}")
        else:
            print("✗ FAILED")
            for error in result["errors"]:
                print(f"  ERROR: {error}")

        print()

    # Summary
    print(f"\n{'='*60}")
    print("MIGRATION SUMMARY")
    print(f"{'='*60}")

    success_count = sum(1 for r in results if r["success"])
    print(f"Success: {success_count}/{len(results)}")

    if args.dry_run:
        print("\n⚠️  DRY RUN - No changes were written")
        print("Run without --dry-run to apply changes")
    else:
        print("\n✓ Migration complete!")
        print("\nNext steps:")
        print("1. Verify agents work: python -m pytest tests/")
        print("2. Update CHANGELOG.md")
        print("3. Commit changes")


if __name__ == "__main__":
    main()
