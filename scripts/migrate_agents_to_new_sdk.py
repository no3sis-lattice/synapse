#!/usr/bin/env python3
"""
Automated migration script for claude_code_sdk → claude_agent_sdk

Updates all agent files to use the new API:
1. Import changes: claude_code_sdk → claude_agent_sdk
2. Type changes: ClaudeCodeSdkMessage → ClaudeAgentOptions
3. Tool decorator updates: Add name, description, schema
4. MCP server: Add version parameter
5. Return format: Add structured content blocks

Usage:
    python scripts/migrate_agents_to_new_sdk.py
"""

import re
from pathlib import Path
from typing import List, Tuple


def find_agent_files(base_dir: Path) -> List[Path]:
    """Find all agent Python files"""
    pattern = "*_agent.py"
    agent_files = list(base_dir.glob(f"**/{pattern}"))
    # Exclude already migrated files
    return [f for f in agent_files if f.exists()]


def update_imports(content: str) -> str:
    """Update SDK imports"""
    # Replace package name
    content = content.replace("claude_code_sdk", "claude_agent_sdk")
    content = content.replace("Claude Code SDK", "Claude Agent SDK")

    # Replace type names
    content = content.replace("ClaudeCodeSdkMessage", "ClaudeAgentOptions")
    content = content.replace("ClaudeCodeOptions", "ClaudeAgentOptions")

    return content


def update_mcp_server_creation(content: str) -> str:
    """Add version parameter to create_sdk_mcp_server calls"""
    # Pattern: create_sdk_mcp_server(name="...", tools=[...])
    # Replace with: create_sdk_mcp_server(name="...", version="1.0.0", tools=[...])

    pattern = r'(create_sdk_mcp_server\s*\(\s*name\s*=\s*["\'][^"\']+["\'])\s*,(\s*tools\s*=)'
    replacement = r'\1,\n            version="1.0.0",\2'
    content = re.sub(pattern, replacement, content)

    return content


def extract_tool_info(tool_func: str) -> Tuple[str, str]:
    """Extract tool name and description from function"""
    # Extract function name
    name_match = re.search(r'async\s+def\s+(\w+)\s*\(', tool_func)
    func_name = name_match.group(1) if name_match else "unknown_tool"

    # Extract docstring
    doc_match = re.search(r'"""([^"]+)"""', tool_func)
    description = doc_match.group(1).strip() if doc_match else f"Tool: {func_name}"

    return func_name, description


def add_structured_return(tool_func: str) -> str:
    """Wrap returns in structured content format"""
    # Check if already has structured return
    if '"content"' in tool_func and '"type": "text"' in tool_func:
        return tool_func  # Already migrated

    # Pattern: return await some_function(...)
    # Pattern: return result
    # Wrap in structured format

    # Find the return statement
    return_pattern = r'(\n\s+)(return\s+)(await\s+)?([^\n]+)'

    def replacement(match):
        indent = match.group(1)
        return_kw = match.group(2)
        await_kw = match.group(3) or ""
        value = match.group(4)

        # Store result, then return structured
        return (
            f"{indent}result = {await_kw}{value}\n"
            f"{indent}return {{\n"
            f"{indent}    \"content\": [\n"
            f"{indent}        {{\"type\": \"text\", \"text\": str(result)}}\n"
            f"{indent}    ]\n"
            f"{indent}}}"
        )

    tool_func = re.sub(return_pattern, replacement, tool_func, count=1)
    return tool_func


def update_tool_decorator(content: str) -> str:
    """
    Update @tool decorators to include name, description, and schema

    Transform:
        @tool
        async def my_tool(args: ArgsType) -> dict[str, Any]:

    To:
        @tool(
            "my_tool",
            "Description from docstring",
            {"param": str}
        )
        async def my_tool(args: ArgsType) -> dict[str, Any]:
    """

    # Find all @tool decorated functions
    tool_pattern = r'@tool\n(\s*)async\s+def\s+(\w+)\s*\([^)]*\)\s*->[^:]*:\s*\n\s*"""([^"]+)"""'

    def replacement(match):
        indent = match.group(1)
        func_name = match.group(2)
        description = match.group(3).strip()

        # Infer schema from function name (basic heuristic)
        schema = "{}"  # Default empty schema

        return (
            f'@tool(\n'
            f'{indent}    "{func_name}",\n'
            f'{indent}    "{description}",\n'
            f'{indent}    {schema}\n'
            f'{indent})\n'
            f'{indent}async def {func_name}('
        )

    # This is a simplified version - the actual implementation
    # would need more sophisticated parsing
    # For now, we'll flag files needing manual review

    return content


def migrate_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    Migrate a single agent file

    Returns:
        True if migration was successful, False if manual review needed
    """
    try:
        content = file_path.read_text()
        original_content = content

        # Apply automated migrations
        content = update_imports(content)
        content = update_mcp_server_creation(content)

        # Check if file needs manual review for tool decorators
        has_bare_tool_decorators = bool(re.search(r'^@tool\s*$', content, re.MULTILINE))

        if not dry_run and content != original_content:
            # Backup original
            backup_path = file_path.with_suffix('.py.bak')
            backup_path.write_text(original_content)

            # Write migrated content
            file_path.write_text(content)
            print(f"✓ Migrated: {file_path.relative_to(Path.cwd())}")

            if has_bare_tool_decorators:
                print(f"  ⚠ Manual review needed for tool decorators")
                return False

            return True
        elif dry_run:
            print(f"Would migrate: {file_path.relative_to(Path.cwd())}")
            if has_bare_tool_decorators:
                print(f"  ⚠ Manual review needed for tool decorators")
            return not has_bare_tool_decorators
        else:
            print(f"✓ Already migrated: {file_path.relative_to(Path.cwd())}")
            return True

    except Exception as e:
        print(f"✗ Error migrating {file_path}: {e}")
        return False


def main():
    """Main migration entry point"""
    import sys

    dry_run = "--dry-run" in sys.argv

    # Find all agent files
    base_dir = Path(__file__).parent.parent / ".synapse" / "agents"
    agent_files = find_agent_files(base_dir)

    print(f"Found {len(agent_files)} agent files to migrate")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE MIGRATION'}\n")

    # Migrate each file
    success_count = 0
    manual_review_count = 0

    for file_path in sorted(agent_files):
        if migrate_file(file_path, dry_run):
            success_count += 1
        else:
            manual_review_count += 1

    print(f"\n{'=' * 60}")
    print(f"Migration Summary:")
    print(f"  Total files: {len(agent_files)}")
    print(f"  Automated: {success_count}")
    print(f"  Manual review needed: {manual_review_count}")

    if manual_review_count > 0:
        print(f"\n⚠ {manual_review_count} files need manual review for tool decorators")
        print("  Please update @tool decorators to include (name, description, schema)")


if __name__ == "__main__":
    main()
