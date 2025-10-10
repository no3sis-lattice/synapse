"""
Mock Claude Agent SDK for Development

Provides mock implementations of Claude Agent SDK functions for testing
and development when the actual SDK is not available.

Updated for claude-agent-sdk v0.1.0+ API

USAGE:
    This is the SINGLE shared mock SDK for all agents.
    Import from:
        from synapse.shared.mock_sdk import tool, create_sdk_mcp_server, etc.

ENVIRONMENT CONTROLS:
    - SYNAPSE_MOCK_SDK_MODE: 'warn' (default) or 'strict'
    - In 'strict' mode, raises RuntimeError if SDK not available (production safety)
    - In 'warn' mode, prints warning and continues (development mode)

PRODUCTION SAFETY:
    Set SYNAPSE_MOCK_SDK_MODE=strict in production to fail-fast if SDK missing.
"""

import asyncio
import os
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field


# Environment-based control
MOCK_MODE = os.getenv('SYNAPSE_MOCK_SDK_MODE', 'warn')


def _check_production_safety():
    """Ensure mock SDK usage is intentional in production."""
    if MOCK_MODE == 'strict':
        raise RuntimeError(
            "Claude Agent SDK not available, but SYNAPSE_MOCK_SDK_MODE=strict. "
            "Install claude-agent-sdk or set SYNAPSE_MOCK_SDK_MODE=warn for development."
        )
    elif MOCK_MODE == 'warn':
        print("⚠️  Claude Agent SDK not available, using mock implementations (DEVELOPMENT MODE)")
    else:
        raise ValueError(
            f"Invalid SYNAPSE_MOCK_SDK_MODE: {MOCK_MODE}. "
            "Use 'warn' (development) or 'strict' (production)."
        )


# Check on import
_check_production_safety()


@dataclass
class ClaudeAgentOptions:
    """Mock agent options (replaces ClaudeCodeOptions)"""
    model: str = "claude-sonnet-4-5"
    permission_mode: str = "acceptEdits"
    system_prompt: Union[str, Dict[str, str], None] = None
    mcp_servers: Dict[str, Any] = field(default_factory=dict)
    allowed_tools: List[str] = field(default_factory=list)
    setting_sources: List[str] = field(default_factory=list)


@dataclass
class ToolMetadata:
    """Metadata for a tool"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    func: Callable


@dataclass
class MockServer:
    """Mock MCP server"""
    name: str
    version: str
    tools: List[ToolMetadata]


class ContentBlock:
    """Mock content block for structured returns"""
    def __init__(self, type: str, text: str = None, **kwargs):
        self.type = type
        self.text = text
        self.data = kwargs


def tool(name: str, description: str = "", input_schema: Dict[str, Any] = None):
    """
    Mock tool decorator for claude-agent-sdk

    Args:
        name: Tool name (required)
        description: Tool description
        input_schema: JSON schema for input parameters

    Example:
        @tool("my_tool", "Does something useful", {"param": str})
        async def my_tool(args):
            return {"content": [{"type": "text", "text": "Result"}]}
    """
    def decorator(func: Callable) -> Callable:
        # Attach metadata to function
        func._tool_metadata = ToolMetadata(
            name=name,
            description=description or func.__doc__ or "",
            input_schema=input_schema or {},
            func=func
        )
        return func
    return decorator


def create_sdk_mcp_server(
    name: str,
    version: str = "1.0.0",
    tools: List[Callable] = None
) -> MockServer:
    """
    Mock MCP server creation for claude-agent-sdk

    Args:
        name: Server name
        version: Server version (required in v0.1.0+)
        tools: List of tool functions with @tool decorator

    Returns:
        MockServer instance
    """
    tool_metadata = []
    for tool_func in (tools or []):
        if hasattr(tool_func, '_tool_metadata'):
            tool_metadata.append(tool_func._tool_metadata)
        else:
            # Fallback for tools without metadata
            tool_metadata.append(ToolMetadata(
                name=tool_func.__name__,
                description=tool_func.__doc__ or "",
                input_schema={},
                func=tool_func
            ))

    return MockServer(name=name, version=version, tools=tool_metadata)


async def query(
    prompt: str,
    options: Optional[ClaudeAgentOptions] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Mock query function for claude-agent-sdk

    Args:
        prompt: The prompt to send
        options: Agent options (ClaudeAgentOptions)

    Yields:
        Message dictionaries with structured content
    """
    # Simulate a simple response with structured content
    await asyncio.sleep(0.1)  # Simulate network delay

    yield {
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": f"Mock response to: {prompt}"
            }
        ]
    }


# Helper functions for structured content

def text_content(text: str) -> Dict[str, str]:
    """Create a text content block"""
    return {"type": "text", "text": text}


def tool_use_content(tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """Create a tool use content block"""
    return {
        "type": "tool_use",
        "name": tool_name,
        "input": tool_input
    }


def tool_result_content(tool_use_id: str, content: str) -> Dict[str, Any]:
    """Create a tool result content block"""
    return {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": content
    }
