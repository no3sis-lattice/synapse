#!/usr/bin/env python3
"""
Migrate agents from local mock_sdk.py to shared mock SDK

This script:
1. Updates imports to use shared mock SDK
2. Removes local mock_sdk.py files
3. Updates tool decorators to new format (if needed)
4. Validates changes

Usage:
    python scripts/migrate_to_shared_mock_sdk.py [--dry-run] [--agent AGENT_NAME]
"""

import argparse
import re
from pathlib import Path
from typing import List, Tuple


AGENTS_DIR = Path(".synapse/agents")
SHARED_MOCK_PATH = Path(".synapse/shared/mock_sdk.py")


def find_agents_with_mock_sdk() -> List[Path]:
    """Find all agents that have local mock_sdk.py files."""
    agents = []
    for agent_dir in AGENTS_DIR.iterdir():
        if agent_dir.is_dir():
            mock_sdk = agent_dir / "tools" / "mock_sdk.py"
            if mock_sdk.exists():
                agents.append(agent_dir)
    return agents


def update_agent_imports(agent_file: Path, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Update agent imports to use shared mock SDK.

    Returns:
        (changed, new_content) tuple
    """
    if not agent_file.exists():
        return False, ""

    content = agent_file.read_text()
    original_content = content

    # Pattern 1: from tools.mock_sdk import ...
    pattern1 = r'from tools\.mock_sdk import \([^)]+\)|from tools\.mock_sdk import [^\n]+'

    # Pattern 2: sys.path.insert for tools directory
    # We need to update this to point to shared instead

    # Replace import
    new_import = """# Shared mock SDK (single source of truth)
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))
    from mock_sdk import (
        create_sdk_mcp_server,
        tool,
        query,
        ClaudeAgentOptions
    )"""

    # Find and replace the fallback import section
    fallback_pattern = r'except ImportError:.*?from tools\.mock_sdk import[^)]+\)'

    if re.search(fallback_pattern, content, re.DOTALL):
        content = re.sub(
            fallback_pattern,
            f'except ImportError:\n    # Fallback for development/testing\n{new_import}',
            content,
            flags=re.DOTALL
        )

    changed = content != original_content

    if changed and not dry_run:
        agent_file.write_text(content)

    return changed, content


def validate_agent(agent_dir: Path) -> List[str]:
    """Validate agent structure after migration."""
    issues = []

    # Check agent file exists
    agent_files = list(agent_dir.glob("*_agent.py"))
    if not agent_files:
        issues.append(f"No agent file found in {agent_dir}")
        return issues

    agent_file = agent_files[0]
    content = agent_file.read_text()

    # Check for shared mock import
    if "from mock_sdk import" not in content and "import mock_sdk" not in content:
        issues.append(f"{agent_file.name}: No shared mock SDK import found")

    # Check for old local mock import
    if "from tools.mock_sdk import" in content:
        issues.append(f"{agent_file.name}: Still using local mock SDK import")

    return issues


def main():
    parser = argparse.ArgumentParser(description="Migrate agents to shared mock SDK")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--agent", help="Migrate specific agent only")
    args = parser.parse_args()

    # Find all agents with mock SDK
    agents = find_agents_with_mock_sdk()

    if args.agent:
        agents = [a for a in agents if a.name == args.agent]
        if not agents:
            print(f"Agent {args.agent} not found or has no mock_sdk.py")
            return

    print(f"Found {len(agents)} agents with local mock_sdk.py:")
    for agent in agents:
        print(f"  - {agent.name}")

    print()

    # Migrate each agent
    for agent_dir in agents:
        print(f"Processing {agent_dir.name}...")

        # Find agent file
        agent_files = list(agent_dir.glob("*_agent.py"))
        if not agent_files:
            print(f"  ⚠️  No agent file found, skipping")
            continue

        agent_file = agent_files[0]

        # Update imports
        changed, new_content = update_agent_imports(agent_file, args.dry_run)

        if changed:
            print(f"  ✓ Updated imports in {agent_file.name}")
            if args.dry_run:
                print("    [DRY RUN - no changes written]")
        else:
            print(f"  - No import changes needed")

        # Remove local mock_sdk.py (unless dry run)
        mock_sdk = agent_dir / "tools" / "mock_sdk.py"
        if mock_sdk.exists() and not args.dry_run:
            mock_sdk.unlink()
            print(f"  ✓ Removed local mock_sdk.py")
        elif mock_sdk.exists():
            print(f"  - Would remove mock_sdk.py [DRY RUN]")

        # Validate
        issues = validate_agent(agent_dir)
        if issues:
            print(f"  ⚠️  Validation issues:")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print(f"  ✓ Validation passed")

        print()

    print("Migration complete!")

    if not args.dry_run:
        print(f"\nNext steps:")
        print(f"1. Verify agents still work: pytest tests/")
        print(f"2. Update CHANGELOG.md")
        print(f"3. Commit changes")


if __name__ == "__main__":
    main()
