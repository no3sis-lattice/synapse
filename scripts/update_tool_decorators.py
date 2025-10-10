#!/usr/bin/env python3
"""
Update bare @tool decorators to include name, description, and schema

This script finds all functions with bare @tool decorators and updates them
to include proper metadata for claude-agent-sdk v0.1.0+
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple


def extract_function_schema(args_type_def: str) -> Dict:
    """Extract schema from TypedDict definition"""
    # This is a simplified approach - just return empty dict
    # Real implementation would parse the TypedDict
    return {}


def update_tool_decorators_in_file(file_path: Path) -> bool:
    """Update all tool decorators in a file"""
    content = file_path.read_text()
    original_content = content

    # Pattern to match bare @tool decorator followed by async function
    pattern = r'@tool\n(\s*)async\s+def\s+(\w+)\s*\([^)]*\)\s*->[^:]*:\s*\n\s*"""([^"]+)"""'

    def replacement(match):
        indent = match.group(1)
        func_name = match.group(2)
        description = match.group(3).strip()

        # Build new decorator
        new_decorator = (
            f'@tool(\n'
            f'{indent}    "{func_name}",\n'
            f'{indent}    "{description}",\n'
            f'{indent}    {{}}\n'  # Empty schema for now
            f'{indent})\n'
            f'{indent}async def {func_name}('
        )
        return new_decorator

    # Apply replacement
    content = re.sub(pattern, replacement, content)

    # Also need to wrap returns in structured format
    # Pattern for simple returns
    return_pattern = r'(\n\s+)(return\s+await\s+)([a-z_]+\([^)]*\))'

    def return_replacement(match):
        indent = match.group(1)
        return_kw = match.group(2)
        func_call = match.group(3)

        return (
            f"{indent}result = await {func_call}\n"
            f"{indent}return {{\n"
            f"{indent}    \"content\": [\n"
            f"{indent}        {{\"type\": \"text\", \"text\": str(result)}}\n"
            f"{indent}    ]\n"
            f"{indent}}}"
        )

    content = re.sub(return_pattern, return_replacement, content)

    if content != original_content:
        # Backup
        backup_path = file_path.with_suffix('.py.bak2')
        if not backup_path.exists():
            backup_path.write_text(original_content)

        # Write updated content
        file_path.write_text(content)
        print(f"✓ Updated: {file_path.relative_to(Path.cwd())}")
        return True
    else:
        print(f"  No changes: {file_path.relative_to(Path.cwd())}")
        return False


def main():
    """Update all agent files"""
    base_dir = Path(__file__).parent.parent / ".synapse" / "agents"

    # List of agent files needing updates (from migration script output)
    agents_needing_update = [
        "tool-runner/tool_runner_agent.py",
        "test-runner/test_runner_agent.py",
        "docs-writer/docs_writer_agent.py",
        "architect/architect_agent.py",
        "devops-engineer/devops_engineer_agent.py",
        "ux-designer/ux_designer_agent.py",
        "security-specialist/security_specialist_agent.py",
        "git-workflow/git_workflow_agent.py",
        "code-hound/code_hound_agent.py",
        "python-specialist/python_specialist_agent.py",
        "typescript-specialist/typescript_specialist_agent.py",
        "rust-specialist/rust_specialist_agent.py",
        "pneuma/pneuma_agent.py",
        "pneuma/pneuma_enhanced_agent.py",
        "clarity-judge/clarity_judge_agent.py",
    ]

    updated_count = 0
    for agent_file in agents_needing_update:
        file_path = base_dir / agent_file
        if file_path.exists():
            if update_tool_decorators_in_file(file_path):
                updated_count += 1
        else:
            print(f"⚠ Not found: {agent_file}")

    print(f"\n{'=' * 60}")
    print(f"Updated {updated_count} agent files")


if __name__ == "__main__":
    main()
