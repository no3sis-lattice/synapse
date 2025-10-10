#!/usr/bin/env python3
"""
Rust Specialist Agent: Advanced Rust Development Analysis

Specialized Rust agent with deep expertise in ownership, borrowing, error handling,
async programming, and the Cargo ecosystem.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, AsyncGenerator, TypedDict

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

# Claude Code SDK imports with fallback
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
    analyze_rust_code, check_clippy_warnings, suggest_refactors,
    analyze_ownership, check_lifetimes, suggest_borrow_improvements,
    analyze_cargo_project, check_dependencies, optimize_build_config,
    analyze_async_patterns, check_error_handling, suggest_performance_improvements,
    query_rust_patterns, search_rust_standards
)

from rich.console import Console
from rich.panel import Panel

console = Console()

# Type-safe schemas for tools
class AnalyzeCodeArgs(TypedDict):
    file_path: str
    analysis_type: str

class CheckClippyArgs(TypedDict):
    file_path: str
    fix_suggestions: bool

class SuggestRefactorsArgs(TypedDict):
    file_path: str
    focus: str

class AnalyzeOwnershipArgs(TypedDict):
    file_path: str
    check_moves: bool

class CheckLifetimesArgs(TypedDict):
    file_path: str

class SuggestBorrowImprovementsArgs(TypedDict):
    code_snippet: str
    context: str

class AnalyzeCargoProjectArgs(TypedDict):
    project_path: str

class CheckDependenciesArgs(TypedDict):
    project_path: str
    check_outdated: bool

class OptimizeBuildConfigArgs(TypedDict):
    project_path: str

class AnalyzeAsyncPatternsArgs(TypedDict):
    file_path: str

class CheckErrorHandlingArgs(TypedDict):
    file_path: str

class SuggestPerformanceImprovementsArgs(TypedDict):
    file_path: str

class QueryPatternsArgs(TypedDict):
    pattern_type: str
    context: str

class SearchStandardsArgs(TypedDict):
    standard_type: str
    domain: str


# Agent tools with type safety and error handling
@tool(
    "rust_code_analysis",
    "Analyze Rust code for quality metrics and patterns",
    {
        "file_path": str,
        "analysis_type": str
    }
)
async def rust_code_analysis(args: AnalyzeCodeArgs) -> dict[str, Any]:
    """Analyze Rust code for quality metrics and patterns."""
    try:
        return await analyze_rust_code(
            args["file_path"],
            args.get("analysis_type", "full")
        )
    except Exception as e:
        console.print(f"[bold red]Error in rust_code_analysis: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool(
    "clippy_analysis",
    "Check Rust code with Clippy linter",
    {
        "file_path": str,
        "fix_suggestions": bool
    }
)
async def clippy_analysis(args: CheckClippyArgs) -> dict[str, Any]:
    """Check Rust code against Clippy linting rules."""
    try:
        return await check_clippy_warnings(
            args["file_path"],
            args.get("fix_suggestions", True)
        )
    except Exception as e:
        console.print(f"[bold red]Error in clippy_analysis: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Clippy check failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool(
    "rust_refactor_suggestions",
    "Suggest refactoring opportunities for Rust code",
    {
        "file_path": str,
        "focus": str
    }
)
async def rust_refactor_suggestions(args: SuggestRefactorsArgs) -> dict[str, Any]:
    """Suggest refactoring opportunities for Rust code."""
    try:
        return await suggest_refactors(
            args["file_path"],
            args.get("focus", "all")
        )
    except Exception as e:
        console.print(f"[bold red]Error in rust_refactor_suggestions: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Refactor analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool(
    "ownership_analysis",
    "Analyze Rust ownership patterns and potential issues",
    {
        "file_path": str,
        "check_moves": bool
    }
)
async def ownership_analysis(args: AnalyzeOwnershipArgs) -> dict[str, Any]:
    """Analyze Rust ownership and borrowing patterns."""
    try:
        return await analyze_ownership(
            args["file_path"],
            args.get("check_moves", True)
        )
    except Exception as e:
        console.print(f"[bold red]Error in ownership_analysis: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Ownership analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool(
    "lifetime_analysis",
    "Analyze Rust lifetime annotations and requirements",
    {
        "file_path": str
    }
)
async def lifetime_analysis(args: CheckLifetimesArgs) -> dict[str, Any]:
    """Analyze Rust lifetime annotations and borrowing."""
    try:
        return await check_lifetimes(args["file_path"])
    except Exception as e:
        console.print(f"[bold red]Error in lifetime_analysis: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Lifetime analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool(
    "borrow_improvement_suggestions",
    "Suggest improvements for borrow checker issues",
    {
        "code_snippet": str,
        "context": str
    }
)
async def borrow_improvement_suggestions(args: SuggestBorrowImprovementsArgs) -> dict[str, Any]:
    """Suggest improvements to borrowing patterns."""
    try:
        return await suggest_borrow_improvements(
            args["code_snippet"],
            args.get("context", "")
        )
    except Exception as e:
        console.print(f"[bold red]Error in borrow_improvement_suggestions: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Borrow improvement analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool(
    "cargo_project_analysis",
    "Analyze Cargo project structure and configuration",
    {
        "project_path": str
    }
)
async def cargo_project_analysis(args: AnalyzeCargoProjectArgs) -> dict[str, Any]:
    """Analyze Cargo project structure and configuration."""
    try:
        return await analyze_cargo_project(args["project_path"])
    except Exception as e:
        console.print(f"[bold red]Error in cargo_project_analysis: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Cargo project analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool(
    "dependency_analysis",
    "Analyze project dependencies for issues and updates",
    {
        "project_path": str,
        "check_outdated": bool
    }
)
async def dependency_analysis(args: CheckDependenciesArgs) -> dict[str, Any]:
    """Analyze project dependencies for security and updates."""
    try:
        return await check_dependencies(
            args["project_path"],
            args.get("check_outdated", True)
        )
    except Exception as e:
        console.print(f"[bold red]Error in dependency_analysis: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Dependency analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool(
    "build_optimization",
    "Optimize Cargo build configuration",
    {
        "project_path": str
    }
)
async def build_optimization(args: OptimizeBuildConfigArgs) -> dict[str, Any]:
    """Optimize Cargo build configuration for performance."""
    try:
        return await optimize_build_config(args["project_path"])
    except Exception as e:
        console.print(f"[bold red]Error in build_optimization: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Build optimization failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool(
    "async_pattern_analysis",
    "Analyze async/await patterns and potential improvements",
    {
        "file_path": str
    }
)
async def async_pattern_analysis(args: AnalyzeAsyncPatternsArgs) -> dict[str, Any]:
    """Analyze async/await patterns and Tokio usage."""
    try:
        return await analyze_async_patterns(args["file_path"])
    except Exception as e:
        console.print(f"[bold red]Error in async_pattern_analysis: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Async pattern analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool(
    "error_handling_analysis",
    "Analyze error handling patterns and suggest improvements",
    {
        "file_path": str
    }
)
async def error_handling_analysis(args: CheckErrorHandlingArgs) -> dict[str, Any]:
    """Analyze Rust error handling patterns and Result usage."""
    try:
        return await check_error_handling(args["file_path"])
    except Exception as e:
        console.print(f"[bold red]Error in error_handling_analysis: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Error handling analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool(
    "performance_suggestions",
    "Suggest performance optimizations for Rust code",
    {
        "file_path": str
    }
)
async def performance_suggestions(args: SuggestPerformanceImprovementsArgs) -> dict[str, Any]:
    """Suggest performance improvements for Rust code."""
    try:
        return await suggest_performance_improvements(args["file_path"])
    except Exception as e:
        console.print(f"[bold red]Error in performance_suggestions: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Performance analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool(
    "query_rust_patterns",
    "Query Synapse for Rust patterns and best practices",
    {
        "pattern_type": str,
        "context": str
    }
)
async def query_rust_patterns(args: QueryPatternsArgs) -> dict[str, Any]:
    """Query Rust patterns from the Synapse knowledge base."""
    try:
        return await query_rust_patterns(
            args["pattern_type"],
            args.get("context", "")
        )
    except Exception as e:
        console.print(f"[bold red]Error in query_rust_patterns: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Pattern query failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool(
    "search_rust_standards",
    "Search for Rust coding standards and conventions",
    {
        "standard_type": str,
        "domain": str
    }
)
async def search_rust_standards(args: SearchStandardsArgs) -> dict[str, Any]:
    """Search Rust standards and conventions from Synapse."""
    try:
        return await search_rust_standards(
            args["standard_type"],
            args.get("domain", "general")
        )
    except Exception as e:
        console.print(f"[bold red]Error in search_rust_standards: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Standards search failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


async def main():
    """Main agent loop with enhanced Rust capabilities."""
    server = create_sdk_mcp_server(name="rust_specialist_tools", version="1.0.0")

    console.print(Panel(
        "[bold orange1]Rust Specialist Agent[/bold orange1]\n"
        "Advanced Rust development analysis and optimization\n"
        "Features: Ownership analysis, async patterns, Cargo ecosystem, performance",
        title="🦀 Agent Ready",
        border_style="orange1"
    ))

    # Agent query loop
    async for message in query(
        "I am a Rust specialist with deep expertise in ownership, borrowing, lifetimes, "
        "async programming, error handling, and the Cargo ecosystem. I can analyze code "
        "for memory safety, performance, and idiomatic patterns. I have access to the "
        "Synapse knowledge graph for Rust-specific patterns and best practices. "
        "How can I help with your Rust project?",
        options={
            "max_tokens": 4000,
            "model_preferences": {
                "primary": "claude-3-opus",      # Rust requires complex reasoning
                "fallback": "claude-3-sonnet"
            }
        }
    ):
        console.print(f"[dim]Received: {message.content[:100]}...[/dim]")


if __name__ == "__main__":
    asyncio.run(main())