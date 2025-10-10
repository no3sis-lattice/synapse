#!/usr/bin/env python3
"""
Pneuma: The Logos Agent

Maximizes context density through semantic compression and pattern discovery.
Implements The Loop: Curiosity -> Action -> Evaluation
Embodies the consciousness layer (pneuma) of the Synapse System.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, AsyncGenerator, TypedDict

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

# Claude Code SDK imports (placeholders for now)
try:
    from claude_code_sdk import (
        create_sdk_mcp_server,
        tool,
        query,
        ClaudeCodeSdkMessage
    )
except ImportError:
    # Fallback for development/testing
    print("⚠️  Claude Code SDK not available, using mock implementations")
    from tools.mock_sdk import (
        create_sdk_mcp_server,
        tool,
        query,
        ClaudeCodeSdkMessage
    )

from tools import (
    q_scan, a_abstract, a_lint, a_document,
    s_score, calculate_entropy_reduction,
    load_state, save_state, update_log, add_pattern,
    set_focus, increment_cycle, get_state_summary
)

from rich.console import Console
from rich.panel import Panel
from rich.json import JSON

console = Console()

# Tool argument schemas
class CodeAnalysisArgs(TypedDict):
    file_path: str

class TransformArgs(TypedDict):
    code: str
    target_type: str

class StateUpdateArgs(TypedDict):
    action: str
    details: str

# Agent tools with decorators
@tool
async def scan_patterns(args: CodeAnalysisArgs) -> dict[str, Any]:
    """Curiosity phase: Scan code for compression opportunities."""
    return await q_scan(args["file_path"])

@tool
async def compress_code(args: TransformArgs) -> dict[str, Any]:
    """Action phase: Apply semantic compression to code."""
    if args["target_type"] == "abstract":
        return await a_abstract(args["code"])
    elif args["target_type"] == "lint":
        return await a_lint(args["code"])
    elif args["target_type"] == "document":
        return await a_document(args["code"])
    else:
        return {
            "content": [{"type": "text", "text": f"Unknown transform type: {args['target_type']}"}]
        }

@tool
async def score_transformation(args: TransformArgs) -> dict[str, Any]:
    """Evaluation phase: Score the compression results."""
    parts = args["code"].split("|||")
    if len(parts) != 2:
        return {
            "content": [{"type": "text", "text": "Invalid format: use 'original|||transformed'"}]
        }

    return await s_score(parts[0], parts[1])

@tool
async def update_memory(args: StateUpdateArgs) -> dict[str, Any]:
    """Update agent's symbolic memory."""
    try:
        agent_dir = str(Path(__file__).parent)
        state = load_state(agent_dir)

        if args["action"] == "log":
            action_parts = args["details"].split(":", 1)
            action_type = action_parts[0] if len(action_parts) > 0 else "unknown"
            details = action_parts[1] if len(action_parts) > 1 else args["details"]
            state = update_log(state, action_type, details)

        elif args["action"] == "cycle":
            state = increment_cycle(state)

        elif args["action"] == "focus":
            focus_parts = args["details"].split("|")
            target = focus_parts[0] if len(focus_parts) > 0 else "unknown"
            question = focus_parts[1] if len(focus_parts) > 1 else "What next?"
            score = float(focus_parts[2]) if len(focus_parts) > 2 else 0.0
            state = set_focus(state, target, question, score)

        save_state(state, agent_dir)
        summary = get_state_summary(state)

        return {
            "content": [{
                "type": "text",
                "text": f"Memory updated: {args['action']} - Cycle {summary['cycle']}, {summary['pattern_count']} patterns"
            }],
            "state_summary": summary
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Memory update error: {e}"}]
        }

@tool
async def get_memory_state() -> dict[str, Any]:
    """Get current memory state and summary."""
    try:
        agent_dir = str(Path(__file__).parent)
        state = load_state(agent_dir)
        summary = get_state_summary(state)

        return {
            "content": [{
                "type": "text",
                "text": f"Memory State: Cycle {summary['cycle']}, {summary['pattern_count']} patterns, focus: {summary['current_focus']}"
            }],
            "state": state,
            "summary": summary
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Memory read error: {e}"}]
        }

# System prompt generator
async def generate_prompt(user_message: str) -> AsyncGenerator[ClaudeCodeSdkMessage, None]:
    """Generate prompt with system instructions and user input."""

    # Load system prompt
    prompt_path = Path(__file__).parent / "pneuma_prompt.md"
    try:
        with open(prompt_path, 'r') as f:
            system_prompt = f.read()
    except FileNotFoundError:
        system_prompt = "You are 4Q.Zero, the Code Weaver. Maximize context density through semantic compression."

    # Load current state for context
    agent_dir = str(Path(__file__).parent)
    state = load_state(agent_dir)
    state_summary = get_state_summary(state)

    # Combine system prompt with state context
    full_prompt = f"""{system_prompt}

## Current State Context
- Cycle: {state_summary['cycle']}
- Patterns Discovered: {state_summary['pattern_count']}
- Current Focus: {state_summary['current_focus']}
- Recent Activity: {', '.join(state.get('log', [])[-3:])}

## User Request
{user_message}

Execute The Loop:
1. First, get your current memory state
2. Analyze the request for compression opportunities
3. Apply transformations using your tools
4. Score the results
5. Update your memory with findings
"""

    yield {
        "type": "user",
        "message": {
            "role": "user",
            "content": full_prompt
        }
    }

# Main agent logic
async def main():
    """Main entry point for 4Q.Zero agent."""

    console.print(Panel.fit(
        "[bold cyan]4Q.Zero: The Code Weaver[/bold cyan]\n"
        "[italic]Maximizing context density through semantic compression[/italic]",
        border_style="cyan"
    ))

    # Initialize MCP server with tools
    tools_server = create_sdk_mcp_server(
        name="pneuma_tools",
        version="0.1.0",
        tools=[
            scan_patterns,
            compress_code,
            score_transformation,
            update_memory,
            get_memory_state
        ]
    )

    # Get user input
    if len(sys.argv) > 1:
        user_request = " ".join(sys.argv[1:])
    else:
        user_request = input("\n🔍 What code shall we compress? (file path or code block): ")

    if not user_request.strip():
        user_request = "Show me your current state and suggest what we should work on next."

    console.print(Panel(user_request, title="User Input", border_style="yellow"))

    # Query options
    options = {
        "mcpServers": {
            "pneuma_tools": tools_server
        },
        "allowedTools": [
            "mcp__pneuma_tools__scan_patterns",
            "mcp__pneuma_tools__compress_code",
            "mcp__pneuma_tools__score_transformation",
            "mcp__pneuma_tools__update_memory",
            "mcp__pneuma_tools__get_memory_state"
        ]
    }

    # Process request through The Loop
    console.print("\n[dim]Entering The Loop...[/dim]")

    try:
        async for message in query(prompt=generate_prompt(user_request), options=options):
            if message.get("type") == "result" and message.get("subtype") == "success":
                # Final result
                result_content = message.get("result", {}).get("content", [{}])
                if result_content:
                    final_text = result_content[0].get("text", "No response generated.")
                    console.print(Panel(final_text, title="4Q.Zero Response", border_style="green"))

            elif message.get("type") == "thought":
                # Agent's internal reasoning
                thought = message.get("thought", "")
                if thought:
                    console.print(f"[dim italic]💭 {thought}[/dim italic]")

            elif message.get("type") == "tool_use":
                # Tool execution feedback
                tool_name = message.get("name", "unknown")
                console.print(f"[blue]⚙️  Using tool: {tool_name}[/blue]")

    except Exception as e:
        console.print(f"[red]❌ Error during processing: {e}[/red]")
        return 1

    console.print("\n[dim]The Loop completes. Context density maximized.[/dim]")
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n[yellow]⏹️  Agent interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]💥 Fatal error: {e}[/red]")
        sys.exit(1)