#!/usr/bin/env python3
"""
Golang Language Specialist Agent

A specialized agent for Go programming tasks with deep expertise in:
- Concurrency patterns (goroutines, channels, select)
- Interface design and composition
- Error handling and wrapping
- Testing patterns and benchmarks
- Module management and dependencies
- Performance optimization and profiling
"""

import asyncio
import os
import sys
from pathlib import Path
import yaml
from typing import Any, Dict, List, Optional, Union, AsyncGenerator

# Add the parent directory to the Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from claude_agent_sdk import create_sdk_mcp_server, tool, query, ClaudeAgentOptions
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

# Import tool modules
from tools import go_analysis_tools, concurrency_tools, interface_tools, testing_tools, module_tools

# Load configuration
def _load_config() -> Dict[str, Any]:
    """Load agent configuration."""
    config_path = Path(__file__).parent / "golang_specialist_config.yml"
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"⚠️  Config file not found: {config_path}")
        return {}

CONFIG = _load_config()

# Tool functions

@tool(
    "analyze_go_code",
    "Analyze Go source code for patterns, idioms, and potential issues",
    {
        "file_path": str,
        "analysis_type": str
    }
)
async def analyze_go_code(args: dict) -> Dict[str, Any]:
    """Analyze Go source code for patterns, idioms, and potential issues."""
    result = go_analysis_tools.analyze_go_code(
        args["file_path"],
        args.get("analysis_type", "comprehensive"),
        CONFIG
    )
    return {
        "content": [{
            "type": "text",
            "text": str(result)
        }]
    }

@tool(
    "check_go_conventions",
    "Check Go code against standard conventions and style guidelines",
    {
        "file_path": str,
        "strict_mode": bool
    }
)
async def check_go_conventions(args: dict) -> Dict[str, Any]:
    """Check Go code against standard conventions and style guidelines."""
    result = go_analysis_tools.check_go_conventions(
        args["file_path"],
        args.get("strict_mode", False),
        CONFIG
    )
    return {
        "content": [{
            "type": "text",
            "text": str(result)
        }]
    }

@tool(
    "suggest_improvements",
    "Suggest improvements for Go code quality and performance",
    {
        "file_path": str,
        "focus_area": str
    }
)
async def suggest_improvements(args: dict) -> Dict[str, Any]:
    """Suggest improvements for Go code quality and performance."""
    result = go_analysis_tools.suggest_improvements(
        args["file_path"],
        args.get("focus_area", "all"),
        CONFIG
    )
    return {
        "content": [{
            "type": "text",
            "text": str(result)
        }]
    }

@tool(
    "analyze_goroutines",
    "Analyze goroutine usage patterns and potential issues",
    {
        "file_path": str,
        "check_leaks": bool
    }
)
async def analyze_goroutines(args: dict) -> Dict[str, Any]:
    """Analyze goroutine usage patterns and potential issues."""
    result = concurrency_tools.analyze_goroutines(
        args["file_path"],
        args.get("check_leaks", True),
        CONFIG
    )
    return {
        "content": [{
            "type": "text",
            "text": str(result)
        }]
    }

@tool(
    "check_channel_patterns",
    "Analyze channel usage patterns and detect common anti-patterns",
    {
        "file_path": str,
        "pattern_type": str
    }
)
async def check_channel_patterns(args: dict) -> Dict[str, Any]:
    """Analyze channel usage patterns and detect common anti-patterns."""
    result = concurrency_tools.check_channel_patterns(
        args["file_path"],
        args.get("pattern_type", "all"),
        CONFIG
    )
    return {
        "content": [{
            "type": "text",
            "text": str(result)
        }]
    }

@tool(
    "detect_race_conditions",
    "Detect potential race conditions in Go code",
    {
        "directory": str,
        "include_tests": bool
    }
)
async def detect_race_conditions(args: dict) -> Dict[str, Any]:
    """Detect potential race conditions in Go code."""
    result = concurrency_tools.detect_race_conditions(
        args["directory"],
        args.get("include_tests", True),
        CONFIG
    )
    return {
        "content": [{
            "type": "text",
            "text": str(result)
        }]
    }

@tool(
    "analyze_interfaces",
    "Analyze interface design and usage patterns",
    {
        "file_path": str,
        "check_satisfaction": bool
    }
)
async def analyze_interfaces(args: dict) -> Dict[str, Any]:
    """Analyze interface design and usage patterns."""
    result = interface_tools.analyze_interfaces(
        args["file_path"],
        args.get("check_satisfaction", True),
        CONFIG
    )
    return {
        "content": [{
            "type": "text",
            "text": str(result)
        }]
    }

@tool(
    "check_interface_satisfaction",
    "Check which types satisfy a given interface",
    {
        "interface_name": str,
        "directory": str
    }
)
async def check_interface_satisfaction(args: dict) -> Dict[str, Any]:
    """Check which types satisfy a given interface."""
    result = interface_tools.check_interface_satisfaction(
        args["interface_name"],
        args["directory"],
        CONFIG
    )
    return {
        "content": [{
            "type": "text",
            "text": str(result)
        }]
    }

@tool(
    "suggest_interface_design",
    "Suggest interface design improvements following Go best practices",
    {
        "file_path": str,
        "minimize": bool
    }
)
async def suggest_interface_design(args: dict) -> Dict[str, Any]:
    """Suggest interface design improvements following Go best practices."""
    result = interface_tools.suggest_interface_design(
        args["file_path"],
        args.get("minimize", True),
        CONFIG
    )
    return {
        "content": [{
            "type": "text",
            "text": str(result)
        }]
    }

@tool(
    "analyze_tests",
    "Analyze Go test patterns and quality",
    {
        "test_path": str,
        "coverage_check": bool
    }
)
async def analyze_tests(args: dict) -> Dict[str, Any]:
    """Analyze Go test patterns and quality."""
    result = testing_tools.analyze_tests(
        args["test_path"],
        args.get("coverage_check", True),
        CONFIG
    )
    return {
        "content": [{
            "type": "text",
            "text": str(result)
        }]
    }

@tool(
    "generate_table_tests",
    "Generate table-driven tests for a Go function",
    {
        "function_name": str,
        "file_path": str
    }
)
async def generate_table_tests(args: dict) -> Dict[str, Any]:
    """Generate table-driven tests for a Go function."""
    result = testing_tools.generate_table_tests(
        args["function_name"],
        args["file_path"],
        CONFIG
    )
    return {
        "content": [{
            "type": "text",
            "text": str(result)
        }]
    }

@tool(
    "check_test_coverage",
    "Check test coverage for Go packages",
    {
        "package_path": str,
        "threshold": float
    }
)
async def check_test_coverage(args: dict) -> Dict[str, Any]:
    """Check test coverage for Go packages."""
    threshold = args.get("threshold") or CONFIG.get('testing', {}).get('coverage_threshold', 80.0)
    result = testing_tools.check_test_coverage(
        args["package_path"],
        threshold,
        CONFIG
    )
    return {
        "content": [{
            "type": "text",
            "text": str(result)
        }]
    }

@tool(
    "manage_dependencies",
    "Manage Go module dependencies",
    {
        "operation": str,
        "module_name": str
    }
)
async def manage_dependencies(args: dict) -> Dict[str, Any]:
    """Manage Go module dependencies."""
    result = module_tools.manage_dependencies(
        args["operation"],
        args.get("module_name"),
        CONFIG
    )
    return {
        "content": [{
            "type": "text",
            "text": str(result)
        }]
    }

@tool(
    "analyze_modules",
    "Analyze Go module structure and dependencies",
    {
        "project_path": str,
        "check_vulnerabilities": bool
    }
)
async def analyze_modules(args: dict) -> Dict[str, Any]:
    """Analyze Go module structure and dependencies."""
    result = module_tools.analyze_modules(
        args["project_path"],
        args.get("check_vulnerabilities", True),
        CONFIG
    )
    return {
        "content": [{
            "type": "text",
            "text": str(result)
        }]
    }

# MCP Server creation
async def create_mcp_server():
    """Create and configure the MCP server with all Golang tools."""
    tools = [
        analyze_go_code,
        check_go_conventions,
        suggest_improvements,
        analyze_goroutines,
        check_channel_patterns,
        detect_race_conditions,
        analyze_interfaces,
        check_interface_satisfaction,
        suggest_interface_design,
        analyze_tests,
        generate_table_tests,
        check_test_coverage,
        manage_dependencies,
        analyze_modules
    ]

    return create_sdk_mcp_server(
        name="golang_specialist_tools",
        version="1.0.0",
        tools=tools
    )

async def golang_agent_prompt() -> AsyncGenerator[ClaudeAgentOptions, None]:
    """Generate the Golang agent system prompt."""
    prompt_path = Path(__file__).parent / "golang_specialist_prompt.md"

    try:
        with open(prompt_path, 'r') as f:
            prompt = f.read()
    except FileNotFoundError:
        prompt = """You are a Go language specialist agent with deep expertise in:
- Concurrency patterns (goroutines, channels, select)
- Interface design and composition
- Error handling and wrapping
- Testing patterns and benchmarks
- Module management and dependencies
- Performance optimization and profiling

Ready to assist with Go development tasks."""

    yield {
        "message": {
            "role": "system",
            "content": prompt
        }
    }

async def main():
    """Main entry point for the Golang specialist agent."""
    print("🚀 Golang Specialist Agent starting...")

    # Create MCP server
    server = await create_mcp_server()

    print(f"🔧 Loaded {len(server.tools)} Golang tools")
    print("Ready to assist with Go development tasks\n")

    try:
        # Agent event loop
        async for response in query(golang_agent_prompt()):
            if response.get("type") == "result":
                result_content = response.get("result", {}).get("content", [])
                for content_item in result_content:
                    if content_item.get("type") == "text":
                        print(content_item["text"])
    except KeyboardInterrupt:
        print("\n👋 Golang Specialist Agent shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Golang Specialist Agent stopped")