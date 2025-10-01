"""
CLI integration tests for Synapse System

Tests the command-line interface functionality including
project initialization and manifest operations.
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add lib path for CLI imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))


def test_synapse_init(cli_runner, tmp_path):
    """
    Test synapse init command functionality.

    This test verifies that the synapse init command:
    1. Creates a .synapse.yml configuration file
    2. Creates the .claude/agents/ directory structure
    3. Creates the synapse-project-manager.md agent file

    Args:
        cli_runner: CLI runner fixture
        tmp_path: Pytest temporary directory fixture
    """
    # Execute synapse init in temporary directory
    result = cli_runner("init", ".", cwd=tmp_path)

    # Assert command succeeded
    assert result.exit_code == 0, f"Command failed: {result.stderr}"

    # Assert .synapse.yml file was created
    synapse_config = tmp_path / ".synapse.yml"
    assert synapse_config.exists(), ".synapse.yml file was not created"
    assert synapse_config.is_file(), ".synapse.yml is not a file"

    # Assert .claude/agents directory was created
    agents_dir = tmp_path / ".claude" / "agents"
    assert agents_dir.exists(), ".claude/agents directory was not created"
    assert agents_dir.is_dir(), ".claude/agents is not a directory"

    # Assert synapse-project-manager.md agent file exists
    project_manager_agent = agents_dir / "synapse-project-manager.md"
    assert project_manager_agent.exists(), "synapse-project-manager.md was not created"
    assert project_manager_agent.is_file(), "synapse-project-manager.md is not a file"

    # Verify the agent file has content
    assert project_manager_agent.stat().st_size > 0, "synapse-project-manager.md is empty"

    # Optional: Verify the .synapse.yml has expected structure
    config_content = synapse_config.read_text()
    assert len(config_content) > 0, ".synapse.yml is empty"


def test_manifest_list_snapshot(cli_runner, snapshot):
    """
    Test synapse manifest list command with snapshot testing.

    This test verifies that the manifest list command produces
    consistent output by comparing against a stored snapshot.

    Args:
        cli_runner: CLI runner fixture
        snapshot: Pytest snapshot fixture
    """
    # Execute synapse manifest list command
    result = cli_runner("manifest", "list")

    # Assert command succeeded
    assert result.exit_code == 0, f"Command failed: {result.stderr}"

    # Assert stdout is not empty
    assert result.stdout.strip(), "Command produced no output"

    # Compare output with snapshot
    snapshot.assert_match(result.stdout, "manifest_list_output.txt")


@pytest.mark.asyncio
async def test_orchestrator_async_initialization():
    """
    Test CLI orchestrator async initialization.

    This test verifies that:
    1. TaskOrchestrator can be async-initialized via CLI helper
    2. Initialization flag works correctly
    3. Multiple calls are idempotent (safe to call repeatedly)
    4. Reactive router is enabled if configured
    """
    from cli import SynapseCLI

    # Create CLI instance
    cli = SynapseCLI()

    # Initially not initialized
    assert not cli._orchestrator_initialized, "Orchestrator should not be initialized on creation"

    # Call async initialization
    await cli._ensure_orchestrator_initialized()

    # Should now be initialized
    assert cli._orchestrator_initialized, "Orchestrator should be initialized after first call"

    # Call again (idempotent check)
    await cli._ensure_orchestrator_initialized()

    # Should still be initialized (no errors)
    assert cli._orchestrator_initialized, "Orchestrator should remain initialized after second call"

    # Verify orchestrator exists
    assert cli.orchestrator is not None, "Orchestrator should exist"

    # Verify reactive router state is set (may be True or False depending on config)
    assert hasattr(cli.orchestrator, 'use_reactive'), "Orchestrator should have use_reactive attribute"

    # Clean up if needed
    if cli.orchestrator.use_reactive and cli.orchestrator.reactive_router:
        await cli.orchestrator.stop_all_agents()


def test_workflow_command_uses_async_init(cli_runner):
    """
    Test that workflow command properly initializes async components.

    This is a smoke test to ensure the workflow command can be executed
    without errors when async initialization is in place.
    """
    # Execute synapse workflow list command (should initialize orchestrator)
    result = cli_runner("workflow", "list")

    # Command should complete without errors (even if no workflows)
    # Exit code 0 or 1 is acceptable (1 means no workflows, 0 means success)
    assert result.exit_code in [0, 1], f"Command failed unexpectedly: {result.stderr}"

    # Should not have initialization errors
    assert "async_init" not in result.stderr.lower(), "Initialization error detected"

    # Reactive router messages are acceptable (disabled, not available, etc.)
    stderr_lower = result.stderr.lower()
    if "reactive" in stderr_lower:
        # Verify it's a benign message (disabled or not available), not an error
        acceptable_messages = ["disabled", "not available", "not enabled"]
        assert any(msg in stderr_lower for msg in acceptable_messages), \
            f"Unexpected reactive router error: {result.stderr}"