"""
Mock Claude Code SDK for development/testing purposes.
This provides fallback implementations when the real SDK is not available.
"""

from typing import Any, AsyncGenerator, Dict, List, Callable
import json

# Mock types
ClaudeCodeSdkMessage = Dict[str, Any]

class MockMCPServer:
    """Mock MCP server for testing."""
    def __init__(self, name: str, version: str, tools: List[Callable]):
        self.name = name
        self.version = version
        self.tools = {tool.__name__: tool for tool in tools}

def create_sdk_mcp_server(name: str, version: str, tools: List[Callable]) -> MockMCPServer:
    """Create a mock MCP server."""
    return MockMCPServer(name, version, tools)

def tool(func: Callable) -> Callable:
    """Mock tool decorator."""
    func._is_tool = True
    return func

async def query(prompt: AsyncGenerator[ClaudeCodeSdkMessage, None], options: Dict = None) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Mock query function that simulates agent responses.
    In a real implementation, this would connect to Claude.
    """
    # Collect the prompt
    prompt_messages = []
    async for msg in prompt:
        prompt_messages.append(msg)

    # Simulate processing
    yield {
        "type": "thought",
        "thought": "Analyzing request and determining which tools to use..."
    }

    # Extract user message
    if prompt_messages:
        user_content = prompt_messages[0].get("message", {}).get("content", "")

        # Simple mock responses based on content
        if "state" in user_content.lower():
            yield {
                "type": "tool_use",
                "name": "get_memory_state"
            }

            response_text = "🧠 Memory State Retrieved\n\nCycle: 0, Patterns: 0, Focus: none\n\nReady to begin compression analysis."

        elif "compress" in user_content.lower() or "optimize" in user_content.lower():
            yield {
                "type": "tool_use",
                "name": "scan_patterns"
            }

            response_text = "🔍 Code Analysis Complete\n\nIdentified potential compression opportunities. Ready to apply transformations."

        else:
            response_text = "🎯 Pneuma Active\n\nProvide code to analyze or a file path to scan for compression opportunities.\n\nThe Loop awaits: q: → a: → s:"

    # Final response
    yield {
        "type": "result",
        "subtype": "success",
        "result": {
            "content": [{
                "type": "text",
                "text": response_text
            }]
        }
    }