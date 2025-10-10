#!/usr/bin/env python3
"""
Tool Runner Agent: Safe Command and Process Execution

Handles command execution, process management, and tool orchestration
with comprehensive security measures and Synapse System integration.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, AsyncGenerator, TypedDict

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

# Claude Agent SDK imports
try:
    from claude_agent_sdk import (
        create_sdk_mcp_server,
        tool,
        query,
        ClaudeAgentOptions
    )
except ImportError:
    # Fallback for development/testing - use shared mock SDK
    print("⚠️  Claude Agent SDK not available, using shared mock SDK")
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))
    from mock_sdk import (
        create_sdk_mcp_server,
        tool,
        query,
        ClaudeAgentOptions
    )

from tools import (
    execute_command, execute_script, chain_commands,
    check_status, kill_process, list_processes,
    parse_output, format_results,
    query_tool_mapping, execute_synapse_tool
)

from rich.console import Console
from rich.panel import Panel

console = Console()

# Tool argument schemas
class ExecuteCommandArgs(TypedDict):
    command: str
    timeout: int
    working_dir: str

class ExecuteScriptArgs(TypedDict):
    script_path: str
    args: list
    timeout: int

class ChainCommandsArgs(TypedDict):
    command_list: list
    stop_on_error: bool

class ProcessStatusArgs(TypedDict):
    process_id: int

class KillProcessArgs(TypedDict):
    process_id: int
    force: bool

class ListProcessesArgs(TypedDict):
    filter_name: str
    limit: int

class ParseOutputArgs(TypedDict):
    output: str
    format_type: str

class FormatResultsArgs(TypedDict):
    data: dict
    output_format: str

class ToolMappingArgs(TypedDict):
    tool_name: str

class SynapseToolArgs(TypedDict):
    tool_name: str
    args: list


# Agent tools with decorators
@tool(
    "run_command",
    "Execute a shell command with timeout and validation",
    {
        "command": str,
        "timeout": int,
        "working_dir": str
    }
)
async def run_command(args: ExecuteCommandArgs) -> dict[str, Any]:
    """Execute a shell command with timeout and validation."""
    result = await execute_command(
        args["command"],
        args.get("timeout", 30),
        args.get("working_dir")
    )
    return {
        "content": [
            {"type": "text", "text": str(result)}
        ]
    }


@tool(
    "run_script",
    "Execute a script file with arguments",
    {
        "script_path": str,
        "args": list,
        "timeout": int
    }
)
async def run_script(args: ExecuteScriptArgs) -> dict[str, Any]:
    """Execute a script file with arguments."""
    result = await execute_script(
        args["script_path"],
        args.get("args", []),
        args.get("timeout", 60)
    )
    return {
        "content": [
            {"type": "text", "text": str(result)}
        ]
    }


@tool(
    "run_command_chain",
    "Execute multiple commands in sequence",
    {
        "command_list": list,
        "stop_on_error": bool
    }
)
async def run_command_chain(args: ChainCommandsArgs) -> dict[str, Any]:
    """Execute multiple commands in sequence."""
    result = await chain_commands(
        args["command_list"],
        args.get("stop_on_error", True)
    )
    return {
        "content": [
            {"type": "text", "text": str(result)}
        ]
    }


@tool(
    "get_process_status",
    "Check the status of a process by PID",
    {
        "process_id": int
    }
)
async def get_process_status(args: ProcessStatusArgs) -> dict[str, Any]:
    """Check the status of a process by PID."""
    result = await check_status(args["process_id"])
    return {
        "content": [
            {"type": "text", "text": str(result)}
        ]
    }


@tool(
    "terminate_process",
    "Terminate a process by PID",
    {
        "process_id": int,
        "force": bool
    }
)
async def terminate_process(args: KillProcessArgs) -> dict[str, Any]:
    """Terminate a process by PID."""
    result = await kill_process(
        args["process_id"],
        args.get("force", False)
    )
    return {
        "content": [
            {"type": "text", "text": str(result)}
        ]
    }


@tool(
    "get_process_list",
    "List running processes with optional filtering",
    {
        "filter_name": str,
        "limit": int
    }
)
async def get_process_list(args: ListProcessesArgs) -> dict[str, Any]:
    """List running processes with optional filtering."""
    result = await list_processes(
        args.get("filter_name"),
        args.get("limit", 20)
    )
    return {
        "content": [
            {"type": "text", "text": str(result)}
        ]
    }


@tool(
    "parse_command_output",
    "Parse command output in various formats",
    {
        "output": str,
        "format_type": str
    }
)
async def parse_command_output(args: ParseOutputArgs) -> dict[str, Any]:
    """Parse command output in various formats."""
    result = await parse_output(
        args["output"],
        args.get("format_type", "text")
    )
    return {
        "content": [
            {"type": "text", "text": str(result)}
        ]
    }


@tool(
    "format_data",
    "Format data for display in various formats",
    {
        "data": dict,
        "output_format": str
    }
)
async def format_data(args: FormatResultsArgs) -> dict[str, Any]:
    """Format data for display in various formats."""
    result = await format_results(
        args["data"],
        args.get("output_format", "pretty")
    )
    return {
        "content": [
            {"type": "text", "text": str(result)}
        ]
    }


@tool(
    "lookup_tool_mapping",
    "Query tool mapping from Synapse knowledge graph",
    {
        "tool_name": str
    }
)
async def lookup_tool_mapping(args: ToolMappingArgs) -> dict[str, Any]:
    """Query tool mapping from Synapse knowledge graph."""
    result = await query_tool_mapping(args["tool_name"])
    return {
        "content": [
            {"type": "text", "text": str(result)}
        ]
    }


@tool(
    "run_synapse_tool",
    "Execute a Synapse-defined tool",
    {
        "tool_name": str,
        "args": list
    }
)
async def run_synapse_tool(args: SynapseToolArgs) -> dict[str, Any]:
    """Execute a Synapse-defined tool."""
    result = await execute_synapse_tool(
        args["tool_name"],
        args.get("args", [])
    )
    return {
        "content": [
            {"type": "text", "text": str(result)}
        ]
    }


async def main():
    """Main agent entry point."""
    try:
        # Load configuration
        agent_dir = Path(__file__).parent

        console.print(Panel(
            "[bold blue]Tool Runner Agent[/bold blue]\n"
            "Safe command execution and process management\n"
            "Connected to Synapse System for tool discovery",
            title="⚡ Agent Ready"
        ))

        # Create MCP server with tools
        server = create_sdk_mcp_server(
            name="tool_runner_tools",
            version="1.0.0",
            tools=[
                run_command,
                run_script,
                run_command_chain,
                get_process_status,
                terminate_process,
                get_process_list,
                parse_command_output,
                format_data,
                lookup_tool_mapping,
                run_synapse_tool
            ]
        )

        console.print(f"[green]✓[/green] MCP Server created with {len(server.tools)} tools")

        # Load system prompt
        prompt_file = agent_dir / "tool_runner_prompt.md"
        if prompt_file.exists():
            system_prompt = prompt_file.read_text()
            console.print("[green]✓[/green] System prompt loaded")
        else:
            system_prompt = "You are a tool runner agent."
            console.print("[yellow]⚠[/yellow] Using default prompt")

        # Agent loop - in real implementation, this would handle incoming requests
        console.print("[cyan]Agent ready for @tool-runner calls[/cyan]")

        # For now, just demonstrate the tools are available
        await demo_tools()

    except KeyboardInterrupt:
        console.print("\n[yellow]Agent shutdown requested[/yellow]")
    except Exception as e:
        console.print(f"[red]Agent error: {e}[/red]")


async def demo_tools():
    """Demonstrate available tools."""
    console.print("\n[bold]Available Tools:[/bold]")

    tools_demo = [
        "run_command - Execute shell commands safely",
        "run_script - Execute script files with args",
        "run_command_chain - Execute multiple commands",
        "get_process_status - Check process status by PID",
        "terminate_process - Kill processes safely",
        "get_process_list - List running processes",
        "parse_command_output - Parse outputs in various formats",
        "format_data - Format data for display",
        "lookup_tool_mapping - Query Synapse tool mappings",
        "run_synapse_tool - Execute Synapse-defined tools"
    ]

    for tool_desc in tools_demo:
        console.print(f"  [blue]•[/blue] {tool_desc}")

    # Show security features
    console.print("\n[bold]Security Features:[/bold]")
    security_features = [
        "Command validation and whitelisting",
        "Timeout protection for long-running commands",
        "Path traversal protection",
        "Process monitoring and safe termination",
        "Resource usage monitoring"
    ]

    for feature in security_features:
        console.print(f"  [green]🛡️[/green] {feature}")


if __name__ == "__main__":
    asyncio.run(main())
