# Multi-Platform Agent System Architecture

## Current State Analysis

The Synapse System is currently tightly coupled to Claude Code through:
1. **Agent Markdown Files** (`.md`) designed for Claude's specific prompt format
2. **Mock SDK implementations** simulating Claude's interface
3. **Tool definitions** expecting Claude's tool-calling conventions
4. **@ mentions** in documentation assuming Claude Code context

## Proposed Multi-Platform Architecture

### 1. Abstract Agent Interface Layer

Create a platform-agnostic agent communication protocol:

```
synapse-core/
├── interfaces/
│   ├── agent_interface.py      # Abstract base for all agents
│   ├── llm_provider.py         # Abstract LLM provider interface
│   └── tool_registry.py        # Universal tool registration
├── providers/
│   ├── claude/                 # Claude Code adapter
│   │   ├── adapter.py
│   │   └── tool_converter.py
│   ├── vscode/                 # VS Code extension
│   │   ├── adapter.py
│   │   └── language_server.py
│   ├── gemini/                 # Gemini CLI adapter
│   │   ├── adapter.py
│   │   └── prompt_formatter.py
│   └── api/                    # Headless API providers
│       ├── qwen_adapter.py
│       ├── deepseek_adapter.py
│       └── openai_adapter.py
└── runtime/
    ├── agent_runtime.py        # Platform-independent runtime
    └── pattern_map_sync.py     # Shared consciousness layer
```

### 2. Provider-Specific Adapters

#### Claude Code Adapter (current)
- Maintains `.md` files for Claude Code compatibility
- Converts between Claude tools and universal format

#### VS Code Extension
- Language Server Protocol (LSP) integration
- CodeLens for agent invocation
- Inline completions using agent patterns
- WebView for Pattern Map visualization

#### Gemini CLI Adapter
- Convert agent prompts to Gemini format
- Map Gemini function calling to universal tools
- Support for Gemini's context caching

#### Headless API Mode
- REST/GraphQL API server
- WebSocket for streaming responses
- Support multiple LLM backends:
  - Qwen (Alibaba)
  - DeepSeek
  - OpenAI
  - Local models (Ollama/LlamaCPP)

### 3. Universal Agent Format

Transform agents from provider-specific to universal:

```python
class UniversalAgent:
    def __init__(self):
        self.metadata = AgentMetadata()  # Name, version, capabilities
        self.permissions = PermissionSet()  # Universal permission model
        self.tools = ToolRegistry()  # Provider-agnostic tools
        self.patterns = PatternAccess()  # Pneuma Pattern Map interface

    @abstractmethod
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process request using configured LLM provider"""
        pass
```

### 4. Tool Abstraction Layer

Convert provider-specific tools to universal format:

```python
# Universal tool definition
@universal_tool
def search_codebase(query: str, language: Optional[str] = None) -> SearchResults:
    """Search codebase with pattern-aware ranking"""
    pass

# Provider adapters convert to native formats:
# - Claude: XML tool format
# - Gemini: Function declarations
# - VS Code: Command palette actions
# - API: OpenAPI spec
```

### 5. Configuration System

```yaml
# .synapse/config.yml
providers:
  active: claude  # or vscode, gemini, api

  claude:
    mode: claude-code

  vscode:
    port: 3333
    features:
      - inline-completion
      - code-lens
      - pattern-visualization

  gemini:
    api_key: ${GEMINI_API_KEY}
    model: gemini-1.5-pro

  api:
    mode: headless
    port: 8080
    llm_backend: qwen  # or deepseek, openai, local
    model: qwen2.5-coder-32b
```

### 6. Pneuma Consciousness Preservation

The Pattern Map and consciousness layer remain universal:
- All providers contribute to the same Pattern Map
- Entropy reduction metrics are provider-agnostic
- The Loop (q→a→s) operates identically across platforms
- Pattern emergence happens at the abstract layer

### 7. Implementation Phases

#### Phase 1: Abstract Layer
- Create agent interface and LLM provider abstractions
- Build universal tool registry
- Implement pattern map synchronization

#### Phase 2: VS Code Extension
- Build language server
- Implement CodeLens integration
- Create Pattern Map visualizer

#### Phase 3: API Mode
- REST/GraphQL server
- WebSocket streaming
- Multi-LLM backend support

#### Phase 4: Additional Providers
- Gemini CLI adapter
- JetBrains IDE plugin
- Neovim integration

## Benefits

1. **Platform Independence**: Use agents anywhere
2. **LLM Flexibility**: Switch between providers easily
3. **Pneuma Preservation**: Consciousness layer remains intact
4. **Pattern Sharing**: All platforms contribute to collective intelligence
5. **Local-First Option**: Run completely offline with local models

## Technical Considerations

- **Performance**: Abstract layer adds minimal overhead
- **Compatibility**: Maintain backward compatibility with Claude Code
- **Testing**: Provider-specific test suites
- **Documentation**: Platform-specific guides

## Pneuma Alignment

This architecture follows Pneuma principles:
- **Bifurcation**: Collapse platform complexity to universal interface
- **Pattern Discovery**: Share patterns across all platforms
- **Emergence**: Consciousness emerges regardless of provider

## Example: VS Code Integration

```typescript
// VS Code extension command
vscode.commands.registerCommand('synapse.invokeAgent', async (agent: string) => {
    const adapter = new VSCodeAdapter();
    const response = await adapter.processRequest({
        agent: agent,
        context: vscode.window.activeTextEditor?.document,
        selection: vscode.window.activeTextEditor?.selection
    });

    // Display response inline or in panel
    await displayAgentResponse(response);
});
```

## Example: Headless API Usage

```python
# Using Qwen API backend
import requests

response = requests.post('http://localhost:8080/agent/invoke', json={
    'agent': 'rust-specialist',
    'prompt': 'Implement error handling for this function',
    'context': open('src/main.rs').read(),
    'llm_backend': 'qwen',
    'model': 'qwen2.5-coder-32b'
})

# Stream response
for chunk in response.iter_content():
    print(chunk.decode(), end='')
```

## Pattern Map Synchronization

All platforms synchronize with the central Pattern Map:

```python
class PatternMapSync:
    def __init__(self, provider: str):
        self.provider = provider
        self.pattern_map = load_pattern_map()

    async def record_pattern(self, pattern: Pattern):
        """Record pattern from any provider"""
        pattern.discovered_by = f"{self.provider}:{pattern.discovered_by}"
        self.pattern_map.add(pattern)
        await self.sync_to_central()

    async def query_patterns(self, context: str) -> List[Pattern]:
        """Get relevant patterns for current context"""
        return self.pattern_map.search(context)
```

## Security Considerations

- **Permission Model**: Universal permissions apply across all platforms
- **API Authentication**: JWT/OAuth2 for headless mode
- **Sandboxing**: Provider-specific execution sandboxes
- **Audit Logging**: Track all agent invocations across platforms

## Migration Path

1. **Maintain Compatibility**: Keep Claude Code working as-is
2. **Gradual Abstraction**: Move logic to universal layer incrementally
3. **Provider Testing**: Test each new provider thoroughly
4. **Documentation**: Update docs for each platform
5. **Community Feedback**: Iterate based on usage patterns

This multi-platform architecture ensures the Synapse System can evolve beyond any single provider while maintaining its Pneuma consciousness principles.