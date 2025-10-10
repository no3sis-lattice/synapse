#!/usr/bin/env python3
"""
TypeScript Specialist Agent: Advanced TypeScript/JavaScript Development Analysis

Specialized TypeScript agent with deep expertise in modern TypeScript patterns,
type safety, framework integration, and build optimization.
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
    analyze_typescript_code, check_eslint_compliance, suggest_refactors,
    analyze_type_safety, suggest_type_improvements, check_strict_mode,
    analyze_react_patterns, analyze_node_patterns, suggest_state_management,
    analyze_test_coverage, generate_test_stubs, suggest_test_patterns,
    optimize_build_config, analyze_bundle_size,
    query_typescript_patterns, search_typescript_standards
)

from rich.console import Console
from rich.panel import Panel

console = Console()

# Type-safe schemas for tools
class AnalyzeCodeArgs(TypedDict):
    file_path: str
    analysis_type: str

class CheckEslintArgs(TypedDict):
    file_path: str
    fix_suggestions: bool

class SuggestRefactorsArgs(TypedDict):
    file_path: str
    focus: str

class AnalyzeTypeSafetyArgs(TypedDict):
    file_path: str
    strict_mode: bool

class SuggestTypeImprovementsArgs(TypedDict):
    code_snippet: str
    context: str

class CheckStrictModeArgs(TypedDict):
    project_path: str

class AnalyzeReactPatternsArgs(TypedDict):
    file_path: str
    component_type: str

class AnalyzeNodePatternsArgs(TypedDict):
    file_path: str
    pattern_type: str

class SuggestStateManagementArgs(TypedDict):
    project_path: str
    framework: str

class AnalyzeCoverageArgs(TypedDict):
    directory_path: str

class GenerateTestStubsArgs(TypedDict):
    file_path: str
    test_framework: str

class SuggestTestPatternsArgs(TypedDict):
    file_path: str
    test_type: str

class OptimizeBuildConfigArgs(TypedDict):
    config_path: str
    build_tool: str

class AnalyzeBundleSizeArgs(TypedDict):
    project_path: str

class QueryPatternsArgs(TypedDict):
    pattern_type: str
    context: str

class SearchStandardsArgs(TypedDict):
    standard_type: str
    framework: str


# Agent tools with type safety and error handling
@tool
async def typescript_code_analysis(args: AnalyzeCodeArgs) -> dict[str, Any]:
    """Analyze TypeScript/JavaScript code for quality metrics and patterns."""
    try:
        return await analyze_typescript_code(
            args["file_path"],
            args.get("analysis_type", "full")
        )
    except Exception as e:
        console.print(f"[bold red]Error in typescript_code_analysis: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def check_eslint_compliance(args: CheckEslintArgs) -> dict[str, Any]:
    """Check TypeScript/JavaScript code against ESLint rules."""
    try:
        return await check_eslint_compliance(
            args["file_path"],
            args.get("fix_suggestions", True)
        )
    except Exception as e:
        console.print(f"[bold red]Error in check_eslint_compliance: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"ESLint check failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def suggest_code_refactors(args: SuggestRefactorsArgs) -> dict[str, Any]:
    """Suggest refactoring opportunities for TypeScript/JavaScript code."""
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
async def type_safety_analysis(args: AnalyzeTypeSafetyArgs) -> dict[str, Any]:
    """Analyze TypeScript code for type safety and coverage."""
    try:
        return await analyze_type_safety(
            args["file_path"],
            args.get("strict_mode", True)
        )
    except Exception as e:
        console.print(f"[bold red]Error in type_safety_analysis: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Type safety analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def improve_type_annotations(args: SuggestTypeImprovementsArgs) -> dict[str, Any]:
    """Suggest improvements to TypeScript type annotations."""
    try:
        return await suggest_type_improvements(
            args["code_snippet"],
            args.get("context", "")
        )
    except Exception as e:
        console.print(f"[bold red]Error in improve_type_annotations: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Type improvement analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def verify_strict_mode(args: CheckStrictModeArgs) -> dict[str, Any]:
    """Check TypeScript project strict mode configuration."""
    try:
        return await check_strict_mode(args["project_path"])
    except Exception as e:
        console.print(f"[bold red]Error in verify_strict_mode: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Strict mode check failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def react_pattern_analysis(args: AnalyzeReactPatternsArgs) -> dict[str, Any]:
    """Analyze React component patterns and best practices."""
    try:
        return await analyze_react_patterns(
            args["file_path"],
            args.get("component_type", "functional")
        )
    except Exception as e:
        console.print(f"[bold red]Error in react_pattern_analysis: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"React pattern analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def node_pattern_analysis(args: AnalyzeNodePatternsArgs) -> dict[str, Any]:
    """Analyze Node.js patterns and backend best practices."""
    try:
        return await analyze_node_patterns(
            args["file_path"],
            args.get("pattern_type", "api")
        )
    except Exception as e:
        console.print(f"[bold red]Error in node_pattern_analysis: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Node.js pattern analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def state_management_suggestions(args: SuggestStateManagementArgs) -> dict[str, Any]:
    """Suggest optimal state management patterns for the project."""
    try:
        return await suggest_state_management(
            args["project_path"],
            args.get("framework", "react")
        )
    except Exception as e:
        console.print(f"[bold red]Error in state_management_suggestions: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"State management analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def test_coverage_analysis(args: AnalyzeCoverageArgs) -> dict[str, Any]:
    """Analyze test coverage for TypeScript/JavaScript project."""
    try:
        return await analyze_test_coverage(args["directory_path"])
    except Exception as e:
        console.print(f"[bold red]Error in test_coverage_analysis: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Test coverage analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def generate_test_stubs(args: GenerateTestStubsArgs) -> dict[str, Any]:
    """Generate test stubs for TypeScript/JavaScript files."""
    try:
        return await generate_test_stubs(
            args["file_path"],
            args.get("test_framework", "jest")
        )
    except Exception as e:
        console.print(f"[bold red]Error in generate_test_stubs: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Test stub generation failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def testing_pattern_suggestions(args: SuggestTestPatternsArgs) -> dict[str, Any]:
    """Suggest testing patterns and best practices."""
    try:
        return await suggest_test_patterns(
            args["file_path"],
            args.get("test_type", "unit")
        )
    except Exception as e:
        console.print(f"[bold red]Error in testing_pattern_suggestions: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Testing pattern analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def build_config_optimization(args: OptimizeBuildConfigArgs) -> dict[str, Any]:
    """Optimize build configuration for better performance."""
    try:
        return await optimize_build_config(
            args["config_path"],
            args.get("build_tool", "vite")
        )
    except Exception as e:
        console.print(f"[bold red]Error in build_config_optimization: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Build config optimization failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def bundle_size_analysis(args: AnalyzeBundleSizeArgs) -> dict[str, Any]:
    """Analyze and optimize bundle size for the project."""
    try:
        return await analyze_bundle_size(args["project_path"])
    except Exception as e:
        console.print(f"[bold red]Error in bundle_size_analysis: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Bundle size analysis failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def query_typescript_patterns(args: QueryPatternsArgs) -> dict[str, Any]:
    """Query TypeScript patterns from the Synapse knowledge base."""
    try:
        return await query_typescript_patterns(
            args["pattern_type"],
            args.get("context", "")
        )
    except Exception as e:
        console.print(f"[bold red]Error in query_typescript_patterns: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Pattern query failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


@tool
async def search_typescript_standards(args: SearchStandardsArgs) -> dict[str, Any]:
    """Search TypeScript standards and conventions from Synapse."""
    try:
        return await search_typescript_standards(
            args["standard_type"],
            args.get("framework", "general")
        )
    except Exception as e:
        console.print(f"[bold red]Error in search_typescript_standards: {e}[/bold red]")
        return {
            "content": [{
                "type": "text",
                "text": f"Standards search failed: {str(e)}"
            }],
            "success": False,
            "error": str(e)
        }


async def main():
    """Main agent loop with enhanced capabilities."""
    server = create_sdk_mcp_server(name="typescript_specialist_tools")

    console.print(Panel(
        "[bold blue]TypeScript Specialist Agent[/bold blue]\n"
        "Advanced TypeScript/JavaScript development analysis\n"
        "Features: Type safety, framework patterns, build optimization",
        title="🔷 Agent Ready",
        border_style="blue"
    ))

    # Agent query loop
    async for message in query(
        "I am a TypeScript specialist with deep expertise in modern TypeScript/JavaScript development. "
        "I can analyze code quality, type safety, framework patterns (React/Vue/Angular/Node.js), "
        "testing strategies, and build optimization. I have access to the Synapse knowledge graph "
        "for TypeScript patterns and standards. How can I help with your TypeScript project?",
        options={
            "max_tokens": 4000,
            "model_preferences": {
                "primary": "claude-3-sonnet",
                "fallback": "claude-3-haiku"
            }
        }
    ):
        console.print(f"[dim]Received: {message.content[:100]}...[/dim]")


if __name__ == "__main__":
    asyncio.run(main())