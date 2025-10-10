#!/usr/bin/env python3
"""
Test Runner Agent: Intelligent Test Execution and Analysis

Handles test execution, failure analysis, and coverage reporting with
Synapse System integration for testing patterns and solutions.
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
    run_tests, detect_test_framework, parse_test_output,
    analyze_failures, generate_coverage, extract_test_info,
    search_test_patterns, query_failure_solutions
)

from rich.console import Console
from rich.panel import Panel

console = Console()

# Tool argument schemas
class RunTestsArgs(TypedDict):
    test_spec: str
    framework: str
    working_dir: str

class DetectFrameworkArgs(TypedDict):
    directory: str

class ParseOutputArgs(TypedDict):
    stdout: str
    stderr: str
    framework: str

class AnalyzeFailuresArgs(TypedDict):
    failures: list
    language: str

class GenerateCoverageArgs(TypedDict):
    test_output: str
    framework: str

class ExtractTestInfoArgs(TypedDict):
    directory: str

class SearchPatternsArgs(TypedDict):
    language: str
    test_type: str

class QuerySolutionsArgs(TypedDict):
    error_type: str
    language: str


# Agent tools with decorators
@tool
async def execute_tests(args: RunTestsArgs) -> dict[str, Any]:
    """Run tests based on specification."""
    return await run_tests(
        args.get("test_spec", ""),
        args.get("framework"),
        args.get("working_dir")
    )


@tool
async def detect_framework(args: DetectFrameworkArgs) -> dict[str, Any]:
    """Detect test framework in directory."""
    framework = await detect_test_framework(args["directory"])
    return {
        "content": [{
            "type": "text",
            "text": f"Detected framework: {framework or 'unknown'}"
        }],
        "success": framework is not None,
        "framework": framework
    }


@tool
async def parse_output(args: ParseOutputArgs) -> dict[str, Any]:
    """Parse test execution output."""
    parsed = await parse_test_output(
        args["stdout"],
        args["stderr"],
        args["framework"]
    )

    return {
        "content": [{
            "type": "text",
            "text": "✓ Test output parsed successfully"
        }],
        "success": True,
        "parsed_output": parsed
    }


@tool
async def analyze_test_failures(args: AnalyzeFailuresArgs) -> dict[str, Any]:
    """Analyze test failures for patterns and solutions."""
    return await analyze_failures(
        args["failures"],
        args.get("language", "python")
    )


@tool
async def get_coverage_report(args: GenerateCoverageArgs) -> dict[str, Any]:
    """Generate coverage report from test output."""
    return await generate_coverage(
        args["test_output"],
        args["framework"]
    )


@tool
async def analyze_test_structure(args: ExtractTestInfoArgs) -> dict[str, Any]:
    """Extract information about test structure."""
    return await extract_test_info(args["directory"])


@tool
async def find_test_patterns(args: SearchPatternsArgs) -> dict[str, Any]:
    """Search for testing patterns in Synapse knowledge graph."""
    return await search_test_patterns(
        args["language"],
        args.get("test_type", "unit")
    )


@tool
async def find_failure_solutions(args: QuerySolutionsArgs) -> dict[str, Any]:
    """Query solutions for test failures."""
    return await query_failure_solutions(
        args["error_type"],
        args["language"]
    )


async def main():
    """Main agent entry point."""
    try:
        # Load configuration
        agent_dir = Path(__file__).parent

        console.print(Panel(
            "[bold yellow]Test Runner Agent[/bold yellow]\n"
            "Intelligent test execution and failure analysis\n"
            "Connected to Synapse System for testing patterns",
            title="🧪 Agent Ready"
        ))

        # Create MCP server with tools
        server = create_sdk_mcp_server(
            name="test_runner_tools",
            tools=[
                execute_tests,
                detect_framework,
                parse_output,
                analyze_test_failures,
                get_coverage_report,
                analyze_test_structure,
                find_test_patterns,
                find_failure_solutions
            ]
        )

        console.print(f"[green]✓[/green] MCP Server created with {len(server.tools)} tools")

        # Load system prompt
        prompt_file = agent_dir / "test_runner_prompt.md"
        if prompt_file.exists():
            system_prompt = prompt_file.read_text()
            console.print("[green]✓[/green] System prompt loaded")
        else:
            system_prompt = "You are a test runner agent."
            console.print("[yellow]⚠[/yellow] Using default prompt")

        # Agent loop - in real implementation, this would handle incoming requests
        console.print("[cyan]Agent ready for @test-runner calls[/cyan]")

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
        "execute_tests - Run tests with framework detection",
        "detect_framework - Identify test framework in project",
        "parse_output - Parse test execution output",
        "analyze_test_failures - Analyze failure patterns",
        "get_coverage_report - Generate coverage information",
        "analyze_test_structure - Analyze test file structure",
        "find_test_patterns - Search Synapse for testing patterns",
        "find_failure_solutions - Query failure solutions"
    ]

    for tool_desc in tools_demo:
        console.print(f"  [yellow]🧪[/yellow] {tool_desc}")

    # Show supported frameworks
    console.print("\n[bold]Supported Frameworks:[/bold]")
    frameworks = [
        "pytest (Python)",
        "Jest/Vitest (JavaScript/TypeScript)",
        "cargo test (Rust)",
        "go test (Go)",
        "JUnit (Java)"
    ]

    for framework in frameworks:
        console.print(f"  [green]✓[/green] {framework}")


if __name__ == "__main__":
    asyncio.run(main())