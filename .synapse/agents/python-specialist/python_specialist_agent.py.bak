#!/usr/bin/env python3
"""
Python Specialist Agent: Advanced Python Development Analysis

Specialized Python agent with deep expertise in modern Python patterns,
type safety, performance optimization, and testing strategies.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, AsyncGenerator, TypedDict

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

# Claude Code SDK imports with fallback
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
    analyze_code, check_pep8, suggest_refactors, profile_performance,
    add_type_hints, check_mypy_compatibility, suggest_types,
    analyze_test_coverage, suggest_test_patterns, generate_test_stubs,
    query_python_patterns, search_python_standards
)

from rich.console import Console
from rich.panel import Panel

console = Console()

# Type-safe schemas for tools
class AnalyzeCodeArgs(TypedDict):
    file_path: str
    analysis_type: str

class CheckPep8Args(TypedDict):
    file_path: str
    fix_suggestions: bool

class SuggestRefactorsArgs(TypedDict):
    file_path: str
    focus: str

class ProfilePerformanceArgs(TypedDict):
    file_path: str
    function_name: str

class AddTypeHintsArgs(TypedDict):
    file_path: str
    function_name: str

class CheckMypyArgs(TypedDict):
    file_path: str

class SuggestTypesArgs(TypedDict):
    code_snippet: str
    context: str

class AnalyzeCoverageArgs(TypedDict):
    directory_path: str

class SuggestTestPatternsArgs(TypedDict):
    file_path: str
    test_type: str

class GenerateTestStubsArgs(TypedDict):
    file_path: str
    test_framework: str

class QueryPatternsArgs(TypedDict):
    pattern_type: str
    context: str

class SearchStandardsArgs(TypedDict):
    standard_type: str
    language_version: str


# Agent tools with type safety and error handling
@tool
async def python_code_analysis(args: AnalyzeCodeArgs) -> dict[str, Any]:
    """Analyze Python code for quality metrics and patterns."""
    try:
        return await analyze_code(
            args["file_path"],
            args.get("analysis_type", "full")
        )
    except Exception as e:
        console.print(f"[bold red]Error in python_code_analysis: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def check_pep8_compliance(args: CheckPep8Args) -> dict[str, Any]:
    """Check Python code against PEP 8 standards."""
    try:
        return await check_pep8(
            args["file_path"],
            args.get("fix_suggestions", True)
        )
    except Exception as e:
        console.print(f"[bold red]Error in check_pep8_compliance: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"PEP 8 check failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def suggest_code_refactors(args: SuggestRefactorsArgs) -> dict[str, Any]:
    """Suggest refactoring opportunities for Python code."""
    try:
        return await suggest_refactors(
            args["file_path"],
            args.get("focus", "all")
        )
    except Exception as e:
        console.print(f"[bold red]Error in suggest_code_refactors: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Refactor analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def analyze_performance(args: ProfilePerformanceArgs) -> dict[str, Any]:
    """Analyze Python code for performance bottlenecks."""
    try:
        return await profile_performance(
            args["file_path"],
            args.get("function_name")
        )
    except Exception as e:
        console.print(f"[bold red]Error in analyze_performance: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Performance analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def suggest_type_hints(args: AddTypeHintsArgs) -> dict[str, Any]:
    """Suggest type hints for Python functions."""
    try:
        return await add_type_hints(
            args["file_path"],
            args.get("function_name")
        )
    except Exception as e:
        console.print(f"[bold red]Error in suggest_type_hints: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Type hint analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def check_type_safety(args: CheckMypyArgs) -> dict[str, Any]:
    """Check Python file for mypy type checking compatibility."""
    try:
        return await check_mypy_compatibility(args["file_path"])
    except Exception as e:
        console.print(f"[bold red]Error in check_type_safety: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Type safety check failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def suggest_inline_types(args: SuggestTypesArgs) -> dict[str, Any]:
    """Suggest appropriate types for code snippets."""
    try:
        return await suggest_types(
            args["code_snippet"],
            args.get("context", "function")
        )
    except Exception as e:
        console.print(f"[bold red]Error in suggest_inline_types: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Type suggestion failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def analyze_testing_coverage(args: AnalyzeCoverageArgs) -> dict[str, Any]:
    """Analyze test coverage for Python project."""
    try:
        return await analyze_test_coverage(args["directory_path"])
    except Exception as e:
        console.print(f"[bold red]Error in analyze_testing_coverage: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Coverage analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def suggest_testing_patterns(args: SuggestTestPatternsArgs) -> dict[str, Any]:
    """Suggest testing patterns for Python code."""
    try:
        return await suggest_test_patterns(
            args["file_path"],
            args.get("test_type", "unit")
        )
    except Exception as e:
        console.print(f"[bold red]Error in suggest_testing_patterns: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Test pattern analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def generate_test_templates(args: GenerateTestStubsArgs) -> dict[str, Any]:
    """Generate test stubs for Python code."""
    try:
        return await generate_test_stubs(
            args["file_path"],
            args.get("test_framework", "pytest")
        )
    except Exception as e:
        console.print(f"[bold red]Error in generate_test_templates: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Test stub generation failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def find_python_patterns(args: QueryPatternsArgs) -> dict[str, Any]:
    """Query Synapse for Python patterns and best practices."""
    try:
        return await query_python_patterns(
            args["pattern_type"],
            args.get("context", "")
        )
    except Exception as e:
        console.print(f"[bold red]Error in find_python_patterns: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Pattern search failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def find_python_standards(args: SearchStandardsArgs) -> dict[str, Any]:
    """Search for Python coding standards and conventions."""
    try:
        return await search_python_standards(
            args["standard_type"],
            args.get("language_version", "3.10+")
        )
    except Exception as e:
        console.print(f"[bold red]Error in find_python_standards: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Standards search failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


async def generate_prompt(user_message: str) -> AsyncGenerator[ClaudeCodeSdkMessage, None]:
    """Generate prompt in streaming format for MCP servers."""
    yield {
        "type": "user",
        "message": {
            "role": "user",
            "content": user_message
        }
    }


async def main():
    """Main agent entry point."""
    try:
        # Load configuration
        agent_dir = Path(__file__).parent

        console.print(Panel(
            "[bold green]Python Specialist Agent[/bold green]\n"
            "Advanced Python development analysis and optimization\n"
            "Connected to Synapse System for patterns and standards",
            title="🐍 Agent Ready"
        ))

        # Create MCP server with tools
        python_server = create_sdk_mcp_server(
            name="python_specialist_tools",
            tools=[
                python_code_analysis,
                check_pep8_compliance,
                suggest_code_refactors,
                analyze_performance,
                suggest_type_hints,
                check_type_safety,
                suggest_inline_types,
                analyze_testing_coverage,
                suggest_testing_patterns,
                generate_test_templates,
                find_python_patterns,
                find_python_standards
            ]
        )

        console.print(f"[green]✓[/green] MCP Server created with {len(python_server.tools)} tools")

        # Load system prompt
        prompt_file = agent_dir / "python_specialist_prompt.md"
        if prompt_file.exists():
            system_prompt = prompt_file.read_text()
            console.print("[green]✓[/green] System prompt loaded")
        else:
            system_prompt = "You are a Python specialist agent."
            console.print("[yellow]⚠[/yellow] Using default prompt")

        console.print("[cyan]Agent ready for @python-specialist calls[/cyan]")

        # Demonstrate tools
        await demo_tools()

    except KeyboardInterrupt:
        console.print("\n[yellow]Agent shutdown requested[/yellow]")
    except Exception as e:
        console.print(f"[red]Agent error: {e}[/red]")


async def demo_tools():
    """Demonstrate available tools."""
    console.print("\n[bold]Available Tools:[/bold]")

    tools_demo = [
        "python_code_analysis - Comprehensive code quality analysis",
        "check_pep8_compliance - PEP 8 standard compliance checking",
        "suggest_code_refactors - Refactoring opportunities identification",
        "analyze_performance - Performance bottleneck analysis",
        "suggest_type_hints - Type annotation recommendations",
        "check_type_safety - MyPy compatibility checking",
        "suggest_inline_types - Inline type suggestions",
        "analyze_testing_coverage - Test coverage analysis",
        "suggest_testing_patterns - Testing strategy recommendations",
        "generate_test_templates - Test stub generation",
        "find_python_patterns - Synapse pattern discovery",
        "find_python_standards - Python standards search"
    ]

    for tool_desc in tools_demo:
        console.print(f"  [green]🐍[/green] {tool_desc}")

    # Show expertise areas
    console.print("\n[bold]Expertise Areas:[/bold]")
    expertise = [
        "Modern Python (3.10+) - Pattern matching, type unions, dataclasses",
        "Async Programming - asyncio, aiohttp, concurrent patterns",
        "Type Safety - Type hints, mypy, protocols",
        "Testing - pytest, coverage, mocking strategies",
        "Performance - Profiling, optimization, memory management",
        "Code Quality - PEP 8, linting, refactoring patterns"
    ]

    for area in expertise:
        console.print(f"  [yellow]⚡[/yellow] {area}")


if __name__ == "__main__":
    asyncio.run(main())