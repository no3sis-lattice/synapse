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
from typing import Any, Dict, List, Optional, Union

# Add the parent directory to the Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from claude_code_sdk import create_sdk_mcp_server, tool, query
except ImportError:
    # Fallback to mock implementation for development
    print("⚠️  Claude Code SDK not available, using mock implementation")
    from tools.mock_sdk import create_sdk_mcp_server, tool, query

# Import tool modules
from tools import (
    go_analysis_tools,
    concurrency_tools,
    interface_tools,
    testing_tools,
    module_tools,
    synapse_integration
)


class GolangSpecialistAgent:
    """Main agent class for Golang language specialist."""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or str(Path(__file__).parent / "golang_specialist_config.yml")
        self.config = self._load_config()
        self.server = create_sdk_mcp_server("golang-specialist")
        self._register_tools()

    def _load_config(self) -> Dict[str, Any]:
        """Load agent configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️  Config file not found: {self.config_path}")
            return {}

    def _register_tools(self):
        """Register all tools with the MCP server."""
        tools = [
            self.analyze_go_code,
            self.check_go_conventions,
            self.suggest_improvements,
            self.analyze_goroutines,
            self.check_channel_patterns,
            self.detect_race_conditions,
            self.analyze_interfaces,
            self.check_interface_satisfaction,
            self.suggest_interface_design,
            self.analyze_tests,
            self.generate_table_tests,
            self.check_test_coverage,
            self.manage_dependencies,
            self.analyze_modules
        ]

        for tool_func in tools:
            self.server.add_tool(tool_func)

    @tool
    def analyze_go_code(self, file_path: str, analysis_type: str = "comprehensive") -> str:
        """
        Analyze Go source code for patterns, idioms, and potential issues.

        Args:
            file_path: Path to the Go file to analyze
            analysis_type: Type of analysis (basic, comprehensive, performance)

        Returns:
            Analysis report with findings and recommendations
        """
        return go_analysis_tools.analyze_go_code(file_path, analysis_type, self.config)

    @tool
    def check_go_conventions(self, file_path: str, strict_mode: bool = False) -> str:
        """
        Check Go code against standard conventions and style guidelines.

        Args:
            file_path: Path to the Go file to check
            strict_mode: Whether to apply strict convention checking

        Returns:
            Convention compliance report
        """
        return go_analysis_tools.check_go_conventions(file_path, strict_mode, self.config)

    @tool
    def suggest_improvements(self, file_path: str, focus_area: str = "all") -> str:
        """
        Suggest improvements for Go code quality and performance.

        Args:
            file_path: Path to the Go file to analyze
            focus_area: Area to focus on (performance, readability, idiomatic, all)

        Returns:
            Improvement suggestions with code examples
        """
        return go_analysis_tools.suggest_improvements(file_path, focus_area, self.config)

    @tool
    def analyze_goroutines(self, file_path: str, check_leaks: bool = True) -> str:
        """
        Analyze goroutine usage patterns and potential issues.

        Args:
            file_path: Path to the Go file containing goroutines
            check_leaks: Whether to check for potential goroutine leaks

        Returns:
            Goroutine analysis report
        """
        return concurrency_tools.analyze_goroutines(file_path, check_leaks, self.config)

    @tool
    def check_channel_patterns(self, file_path: str, pattern_type: str = "all") -> str:
        """
        Analyze channel usage patterns and detect common anti-patterns.

        Args:
            file_path: Path to the Go file with channel usage
            pattern_type: Type of patterns to check (buffered, unbuffered, select, all)

        Returns:
            Channel pattern analysis
        """
        return concurrency_tools.check_channel_patterns(file_path, pattern_type, self.config)

    @tool
    def detect_race_conditions(self, directory: str, include_tests: bool = True) -> str:
        """
        Detect potential race conditions in Go code.

        Args:
            directory: Directory to scan for race conditions
            include_tests: Whether to include test files in analysis

        Returns:
            Race condition detection report
        """
        return concurrency_tools.detect_race_conditions(directory, include_tests, self.config)

    @tool
    def analyze_interfaces(self, file_path: str, check_satisfaction: bool = True) -> str:
        """
        Analyze interface design and usage patterns.

        Args:
            file_path: Path to the Go file containing interfaces
            check_satisfaction: Whether to check interface satisfaction

        Returns:
            Interface analysis report
        """
        return interface_tools.analyze_interfaces(file_path, check_satisfaction, self.config)

    @tool
    def check_interface_satisfaction(self, interface_name: str, directory: str) -> str:
        """
        Check which types satisfy a given interface.

        Args:
            interface_name: Name of the interface to check
            directory: Directory to search for implementations

        Returns:
            Interface satisfaction report
        """
        return interface_tools.check_interface_satisfaction(interface_name, directory, self.config)

    @tool
    def suggest_interface_design(self, file_path: str, minimize: bool = True) -> str:
        """
        Suggest interface design improvements following Go best practices.

        Args:
            file_path: Path to the Go file with interfaces
            minimize: Whether to suggest minimal interfaces

        Returns:
            Interface design recommendations
        """
        return interface_tools.suggest_interface_design(file_path, minimize, self.config)

    @tool
    def analyze_tests(self, test_path: str, coverage_check: bool = True) -> str:
        """
        Analyze Go test patterns and quality.

        Args:
            test_path: Path to test files or directory
            coverage_check: Whether to include coverage analysis

        Returns:
            Test analysis report
        """
        return testing_tools.analyze_tests(test_path, coverage_check, self.config)

    @tool
    def generate_table_tests(self, function_name: str, file_path: str) -> str:
        """
        Generate table-driven tests for a Go function.

        Args:
            function_name: Name of the function to test
            file_path: Path to the file containing the function

        Returns:
            Generated table-driven test code
        """
        return testing_tools.generate_table_tests(function_name, file_path, self.config)

    @tool
    def check_test_coverage(self, package_path: str, threshold: float = None) -> str:
        """
        Check test coverage for Go packages.

        Args:
            package_path: Path to the Go package
            threshold: Minimum coverage threshold (uses config default if not provided)

        Returns:
            Coverage analysis report
        """
        threshold = threshold or self.config.get('testing', {}).get('coverage_threshold', 80.0)
        return testing_tools.check_test_coverage(package_path, threshold, self.config)

    @tool
    def manage_dependencies(self, operation: str, module_name: str = None) -> str:
        """
        Manage Go module dependencies.

        Args:
            operation: Operation to perform (list, update, add, remove, tidy)
            module_name: Name of module for add/remove operations

        Returns:
            Dependency management result
        """
        return module_tools.manage_dependencies(operation, module_name, self.config)

    @tool
    def analyze_modules(self, project_path: str, check_vulnerabilities: bool = True) -> str:
        """
        Analyze Go module structure and dependencies.

        Args:
            project_path: Path to the Go project
            check_vulnerabilities: Whether to check for known vulnerabilities

        Returns:
            Module analysis report
        """
        return module_tools.analyze_modules(project_path, check_vulnerabilities, self.config)

    async def run(self):
        """Run the Golang specialist agent server."""
        prompt_path = Path(__file__).parent / "golang_specialist_prompt.md"

        try:
            with open(prompt_path, 'r') as f:
                system_prompt = f.read()
        except FileNotFoundError:
            system_prompt = "You are a Go language specialist agent."

        print(f"🚀 Golang Specialist Agent starting...")
        print(f"📁 Config: {self.config_path}")
        print(f"🔧 Registered {len(self.server.tools)} tools")

        # Query with the system prompt to initialize the agent
        async for message in query(system_prompt, {
            "model": self.config.get("model", {}).get("default", "claude-sonnet-4"),
            "temperature": self.config.get("model", {}).get("temperature", 0.1)
        }):
            print(f"🤖 {message.content}")


def main():
    """Main entry point for the Golang specialist agent."""
    agent = GolangSpecialistAgent()
    asyncio.run(agent.run())


if __name__ == "__main__":
    main()