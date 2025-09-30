#!/usr/bin/env python3
"""
Clarity Judge Agent

Specialized agent for assessing code readability and maintainability.
Provides objective clarity scores to support the 4Q.Zero compression process.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, AsyncGenerator, TypedDict

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

# Claude Code SDK imports (with fallback)
try:
    from claude_code_sdk import (
        create_sdk_mcp_server,
        tool,
        query,
        ClaudeCodeSdkMessage
    )
except ImportError:
    print("⚠️  Claude Code SDK not available, using mock implementations")
    # Use the mock SDK from Pneuma
    sys.path.insert(0, str(Path(__file__).parent.parent / "Pneuma" / "tools"))
    from mock_sdk import (
        create_sdk_mcp_server,
        tool,
        query,
        ClaudeCodeSdkMessage
    )

from tools import assess_readability, compare_clarity, generate_clarity_report

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

# Tool argument schemas
class ClarityAssessmentArgs(TypedDict):
    code: str
    language: str

class ClarityComparisonArgs(TypedDict):
    original_code: str
    transformed_code: str
    language: str

class ClarityReportArgs(TypedDict):
    code: str
    language: str
    include_suggestions: bool

# Agent tools
@tool
async def judge_clarity(args: ClarityAssessmentArgs) -> dict[str, Any]:
    """Assess the readability and maintainability of code."""
    return await assess_readability(
        args["code"],
        args.get("language", "python")
    )

@tool
async def compare_code_clarity(args: ClarityComparisonArgs) -> dict[str, Any]:
    """Compare clarity between original and transformed code."""
    return await compare_clarity(
        args["original_code"],
        args["transformed_code"],
        args.get("language", "python")
    )

@tool
async def create_clarity_report(args: ClarityReportArgs) -> dict[str, Any]:
    """Generate comprehensive clarity report with recommendations."""
    return await generate_clarity_report(
        args["code"],
        args.get("language", "python"),
        args.get("include_suggestions", True)
    )

# System prompt generator
async def generate_prompt(user_message: str) -> AsyncGenerator[ClaudeCodeSdkMessage, None]:
    """Generate prompt with clarity judge instructions."""

    # Load system prompt
    prompt_path = Path(__file__).parent / "clarity_judge_prompt.md"
    try:
        with open(prompt_path, 'r') as f:
            system_prompt = f.read()
    except FileNotFoundError:
        system_prompt = "You are the Clarity Judge, assessing code readability and maintainability."

    # Combine with user request
    full_prompt = f"""{system_prompt}

## User Request
{user_message}

Please assess the clarity of the provided code and provide a detailed analysis with:
1. Overall clarity score (0.0-1.0)
2. Breakdown by linguistic, structural, and cognitive factors
3. Specific recommendations for improvement if score < 0.8
4. Comparison analysis if both original and transformed code provided

Focus on objective readability metrics while considering the human developer perspective."""

    yield {
        "type": "user",
        "message": {
            "role": "user",
            "content": full_prompt
        }
    }

# Main agent logic
async def main():
    """Main entry point for Clarity Judge agent."""

    console.print(Panel.fit(
        "[bold blue]Clarity Judge: The Readability Arbiter[/bold blue]\n"
        "[italic]Assessing code clarity and maintainability[/italic]",
        border_style="blue"
    ))

    # Initialize MCP server with tools
    clarity_server = create_sdk_mcp_server(
        name="clarity_judge_tools",
        version="1.0.0",
        tools=[
            judge_clarity,
            compare_code_clarity,
            create_clarity_report
        ]
    )

    # Get user input
    if len(sys.argv) > 1:
        user_request = " ".join(sys.argv[1:])
    else:
        console.print("\n📋 [dim]Clarity Judge Usage Examples:[/dim]")
        console.print("  • Judge clarity: [code block]")
        console.print("  • Compare: original: [code] vs transformed: [code]")
        console.print("  • Report on: [file path or code block]")

        user_request = input("\n🔍 What code shall I judge for clarity?: ")

    if not user_request.strip():
        user_request = "Show me how to use the clarity judge for code assessment."

    console.print(Panel(user_request, title="Assessment Request", border_style="yellow"))

    # Query options
    options = {
        "mcpServers": {
            "clarity_judge_tools": clarity_server
        },
        "allowedTools": [
            "mcp__clarity_judge_tools__judge_clarity",
            "mcp__clarity_judge_tools__compare_code_clarity",
            "mcp__clarity_judge_tools__create_clarity_report"
        ]
    }

    # Process request
    console.print("\n[dim]Analyzing code clarity...[/dim]")

    try:
        async for message in query(prompt=generate_prompt(user_request), options=options):
            if message.get("type") == "result" and message.get("subtype") == "success":
                # Final result
                result_content = message.get("result", {}).get("content", [{}])
                if result_content:
                    final_text = result_content[0].get("text", "No assessment generated.")
                    console.print(Panel(final_text, title="Clarity Assessment", border_style="green"))

            elif message.get("type") == "thought":
                # Agent's internal reasoning
                thought = message.get("thought", "")
                if thought:
                    console.print(f"[dim italic]💭 {thought}[/dim italic]")

            elif message.get("type") == "tool_use":
                # Tool execution feedback
                tool_name = message.get("name", "unknown")
                console.print(f"[blue]📊 Using tool: {tool_name}[/blue]")

    except Exception as e:
        console.print(f"[red]❌ Error during assessment: {e}[/red]")
        return 1

    console.print("\n[dim]Clarity assessment complete.[/dim]")
    return 0


# CLI helper functions
def _detect_language_from_code(code: str) -> str:
    """Detect programming language from code content."""
    if 'def ' in code and ':' in code:
        return "python"
    elif 'function ' in code and '{' in code:
        return "javascript"
    elif 'fn ' in code and '-> ' in code:
        return "rust"
    elif 'func ' in code and '{' in code:
        return "go"
    else:
        return "unknown"


def _parse_comparison_request(request: str) -> tuple:
    """Parse comparison request to extract original and transformed code."""
    # Look for patterns like "original: ... vs transformed: ..." or "before: ... after: ..."
    patterns = [
        r'original:\s*(.+?)\s+(?:vs|transformed:|after:)\s*(.+)',
        r'before:\s*(.+?)\s+(?:vs|after:)\s*(.+)',
        r'(.+?)\s+vs\s+(.+)'
    ]

    for pattern in patterns:
        import re
        match = re.search(pattern, request, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip(), match.group(2).strip()

    return None, None


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n[yellow]⏹️  Clarity Judge interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]💥 Fatal error: {e}[/red]")
        sys.exit(1)