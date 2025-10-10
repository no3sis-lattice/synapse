#!/usr/bin/env python3
"""
Migrate 6 restored agents to new SDK and shared mock.

These agents were restored from backup and need:
1. SDK package rename: claude_code_sdk → claude_agent_sdk
2. Type rename: ClaudeCodeSdkMessage → ClaudeAgentOptions
3. Mock import update: tools.mock_sdk → shared mock_sdk
4. Version parameter added to create_sdk_mcp_server
"""

from pathlib import Path
import re

# The 6 agents that need migration
AGENTS = [
    "devops-engineer/devops_engineer_agent.py",
    "docs-writer/docs_writer_agent.py",
    "python-specialist/python_specialist_agent.py",
    "rust-specialist/rust_specialist_agent.py",
    "test-runner/test_runner_agent.py",
    "typescript-specialist/typescript_specialist_agent.py"
]

def migrate_agent(agent_path: Path) -> None:
    """Migrate a single agent file."""
    print(f"Migrating {agent_path.name}...")

    content = agent_path.read_text()
    original = content

    # 1. Update SDK import package name
    content = content.replace('from claude_code_sdk import', 'from claude_agent_sdk import')

    # 2. Update type name
    content = content.replace('ClaudeCodeSdkMessage', 'ClaudeAgentOptions')

    # 3. Update mock SDK import pattern
    # Find the except ImportError block and update it
    old_mock_pattern = r'''except ImportError:
    # Fallback for development/testing
    print\("⚠️  Claude Code SDK not available, using mock implementations"\)
    from tools\.mock_sdk import \('''

    new_mock_pattern = '''except ImportError:
    # Fallback for development/testing - use shared mock SDK
    print("⚠️  Claude Agent SDK not available, using shared mock SDK")
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))
    from mock_sdk import ('''

    content = re.sub(old_mock_pattern, new_mock_pattern, content)

    # 4. Add version parameter to create_sdk_mcp_server if missing
    # Pattern 1: name= with tools= on next line
    content = re.sub(
        r'create_sdk_mcp_server\(\s*name="([^"]+)"\s*,\s*tools=',
        r'create_sdk_mcp_server(\n            name="\1",\n            version="1.0.0",\n            tools=',
        content
    )

    # Pattern 2: name= with tools= on same line
    content = re.sub(
        r'create_sdk_mcp_server\(name="([^"]+)",\s*tools=',
        r'create_sdk_mcp_server(name="\1", version="1.0.0", tools=',
        content
    )

    # Pattern 3: name= only (no tools parameter)
    content = re.sub(
        r'create_sdk_mcp_server\(\s*name="([^"]+)"\s*\)',
        r'create_sdk_mcp_server(name="\1", version="1.0.0")',
        content
    )

    # Only write if changes were made
    if content != original:
        # Create backup
        backup_path = agent_path.with_suffix('.py.mig_bak')
        backup_path.write_text(original)

        # Write updated content
        agent_path.write_text(content)
        print(f"  ✓ Migrated (backup: {backup_path.name})")
    else:
        print(f"  ⚠ No changes needed")


def main():
    """Migrate all 6 agents."""
    base_dir = Path(__file__).parent.parent / ".synapse/agents"

    print("=" * 60)
    print("Migrating 6 Agents to New SDK + Shared Mock")
    print("=" * 60)

    for agent_rel_path in AGENTS:
        agent_path = base_dir / agent_rel_path
        if agent_path.exists():
            migrate_agent(agent_path)
        else:
            print(f"✗ Not found: {agent_rel_path}")

    print("\n" + "=" * 60)
    print("Migration Complete")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Test agent imports: python3 -c 'import <agent>'")
    print("2. Update tool decorators manually")
    print("3. Verify with code-hound")


if __name__ == "__main__":
    main()
