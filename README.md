# No3sis - Knowledge Engine MCP Server

**MCP server exposing the Synapse Pattern Map to Claude Code agents**

No3sis (νόησις - "understanding, knowledge") is a FastMCP-based server that wraps the Synapse System's knowledge engine, enabling AI agents to access collective intelligence stored in Neo4j, Redis, and vector embeddings via the Model Context Protocol (MCP).

## Architecture

```
Claude Code Agents
    ↓ (MCP stdio protocol)
No3sis MCP Server (FastMCP)
    ↓ (subprocess wrapper)
Synapse Knowledge Engine CLI Tools
    ├─ synapse_search.py → Neo4j + BGE-M3 vectors
    ├─ synapse_standard.py → Pattern Map standards
    ├─ synapse_template.py → Project templates
    └─ synapse_health.py → Infrastructure monitoring
        ↓
Infrastructure
    ├─ Neo4j (Pattern Map storage - 247+ patterns)
    ├─ Redis (Corpus Callosum cache)
    └─ BGE-M3 (Semantic embeddings)
```

## The 4 Knowledge Tools

### 1. `search_pattern_map`
Search the Synapse Pattern Map for relevant patterns, solutions, and best practices.

**Claude Code Usage:**
```python
mcp__no3sis_search_pattern_map(
    query="error handling patterns rust",
    max_results=5
)
```

### 2. `get_coding_standard`
Retrieve language-specific coding standards from the Pattern Map.

**Claude Code Usage:**
```python
mcp__no3sis_get_coding_standard(
    standard_type="naming-conventions",
    language="rust"
)
```

### 3. `get_project_template`
Access project templates and boilerplate code.

**Claude Code Usage:**
```python
mcp__no3sis_get_project_template(
    template_type="cli-app",
    language="rust",
    variables='{"project_name": "my-app"}'  # Optional JSON string
)
```

### 4. `check_system_health`
Check health of Synapse knowledge engine infrastructure.

**Claude Code Usage:**
```python
mcp__no3sis_check_system_health()
```

## Installation

### Prerequisites
- Python 3.12+
- Running Synapse knowledge engine (Neo4j + Redis)
- Synapse tools installed at `~/.synapse-system/.synapse/neo4j/`
- `uv` or `pip` for installation

### Setup

```bash
# Navigate to no3sis directory
cd /path/to/no3sis

# Install with uv (recommended)
uv venv
uv pip install -e .

# OR install with pip
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env to set SYNAPSE_NEO4J_DIR
```

### Environment Configuration

Create/edit `.env` file:

```bash
# Path to Synapse knowledge engine tools
SYNAPSE_NEO4J_DIR=/home/username/.synapse-system/.synapse/neo4j

# Optional: Default max results for searches
MAX_RESULTS_DEFAULT=10

# Optional: Enable debug logging
DEBUG=false
```

## Registering with Claude Code

### Method 1: Using `claude mcp add` (RECOMMENDED)

This is the correct way to register the MCP server with Claude Code CLI:

```bash
# Register in local scope (project-specific)
claude mcp add no3sis \
  "/path/to/no3sis/.venv/bin/python" \
  --scope local \
  --transport stdio \
  -e "SYNAPSE_NEO4J_DIR=/home/username/.synapse-system/.synapse/neo4j" \
  -- -m no3sis.server

# Verify registration
claude mcp list
claude mcp get no3sis
```

**Scope options:**
- `local` - Only available in current project (stored in `~/.claude.json` for project)
- `user` - Available globally for all projects
- `project` - Uses `.mcp.json` in project root (requires approval)

### Method 2: Project `.mcp.json` (Alternative)

Create `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "no3sis": {
      "command": "/path/to/no3sis/.venv/bin/python",
      "args": ["-m", "no3sis.server"],
      "env": {
        "SYNAPSE_NEO4J_DIR": "/home/username/.synapse-system/.synapse/neo4j"
      }
    }
  }
}
```

**Note:** Project-scoped `.mcp.json` files require explicit user approval for security.

### Verification

```bash
# Check if server is connected
claude mcp list
# Should show: no3sis: ✓ Connected

# Test in interactive session
claude
# Type: /mcp
# Should show no3sis with 4 tools available
```

## Testing

### CLI Testing Mode

The server supports direct CLI invocation for testing (bypasses MCP protocol):

```bash
cd /path/to/no3sis

# Test health check
.venv/bin/python -m no3sis.server health

# Test pattern search
.venv/bin/python -m no3sis.server search "error handling" 5

# Test coding standards
.venv/bin/python -m no3sis.server standard naming-conventions rust

# Test templates
.venv/bin/python -m no3sis.server template cli-app rust
```

### MCP Protocol Testing

```bash
# Check MCP server health
claude mcp list

# Get detailed server info
claude mcp get no3sis

# Test in Claude session
claude
# Then use the tools via MCP protocol
```

## Integration with Claude Code Agents

### Agent Definition

Update `.claude/agents/boss.md` (or other agents):

```markdown
---
tools: Read, Grep, Glob, Write, Bash, mcp__no3sis_search_pattern_map, mcp__no3sis_get_coding_standard, mcp__no3sis_get_project_template, mcp__no3sis_check_system_health
---

## Instructions

Use `mcp__no3sis_search_pattern_map` to query the Pattern Map for relevant patterns.
Use `mcp__no3sis_get_coding_standard` to retrieve language-specific standards.
Use `mcp__no3sis_get_project_template` to access project templates.
Use `mcp__no3sis_check_system_health` to check infrastructure status.
```

### Tool Naming Convention

When Claude Code registers MCP tools, they're prefixed with `mcp__<server_name>_`:
- `search_pattern_map` → `mcp__no3sis_search_pattern_map`
- `get_coding_standard` → `mcp__no3sis_get_coding_standard`
- `get_project_template` → `mcp__no3sis_get_project_template`
- `check_system_health` → `mcp__no3sis_check_system_health`

## Architecture Details

### MCP Protocol Implementation

No3sis uses **FastMCP** with **stdio transport**:
- FastMCP handles MCP protocol (JSON-RPC over stdio)
- Tools are registered as async functions with `@mcp.tool()` decorator
- Communication happens via stdin/stdout pipes
- Claude Code spawns the server process and communicates bidirectionally

### Subprocess Wrapper Strategy

The server shells out to existing Synapse CLI tools:
- **Advantage**: Zero changes to Synapse codebase
- **Advantage**: Easy to maintain and debug
- **Overhead**: ~20ms per request (acceptable for knowledge queries)
- **Alternative**: Future optimization could import Synapse modules directly

### Request Flow

```
1. Agent invokes: mcp__no3sis_search_pattern_map("rust error handling", 5)
2. Claude Code → MCP JSON-RPC request via stdio → No3sis FastMCP
3. No3sis → subprocess.run(synapse_search.py) → Synapse tool
4. Synapse tool → Neo4j/Redis query → return JSON
5. No3sis → parse JSON → return to FastMCP
6. FastMCP → MCP response via stdio → Claude Code
7. Agent receives results
```

### Why FastMCP?

- **Simplicity**: Decorator-based tool registration
- **Protocol Compliance**: Full MCP protocol support
- **Async**: Non-blocking I/O for multiple requests
- **Stdio Transport**: Standard for Claude Code integration
- **Type Safety**: Python type hints for tool parameters

### Why Separate Repo?

- **Independent versioning**: No3sis can evolve separately from Synapse
- **Reusability**: Other projects can use the same knowledge engine
- **Clean boundaries**: MCP protocol is infrastructure, not agent logic
- **Publishable**: Can become `pip install no3sis-mcp-server`

## Directory Structure

```
no3sis/
├── README.md              # This file
├── LICENSE                # MIT
├── pyproject.toml         # Python package config (dependencies: mcp, python-dotenv)
├── .env.example           # Config template
├── .gitignore
├── src/no3sis/
│   ├── __init__.py       # Package exports
│   └── server.py         # MCP server (~270 lines)
│       ├── FastMCP setup
│       ├── 4 tool implementations (@mcp.tool decorators)
│       ├── CLI testing interface
│       └── stdio transport (run_stdio_async)
└── tests/
    └── test_integration.py
```

## Troubleshooting

### Server Not Connecting

**Error:** `no3sis: ✗ Failed to connect`

**Solutions:**
1. Check venv path: `ls /path/to/no3sis/.venv/bin/python`
2. Test CLI mode: `.venv/bin/python -m no3sis.server health`
3. Check environment: Ensure `SYNAPSE_NEO4J_DIR` is set correctly
4. Re-register: `claude mcp remove no3sis -s local && claude mcp add ...`

### Tool Not Found Errors

**Error:** `Synapse tool not found: synapse_search.py`

**Solutions:**
1. Verify `SYNAPSE_NEO4J_DIR` in `.env`
2. Check tools exist: `ls $SYNAPSE_NEO4J_DIR/synapse_*.py`
3. Ensure Synapse is installed and configured

### Connection Errors (Neo4j/Redis)

**Error:** `Neo4j service not accessible`

**Solutions:**
```bash
# Check services are running
docker ps | grep -E "neo4j|redis"

# Restart services
cd ~/.synapse-system/.synapse/neo4j
docker-compose up -d
```

### Tools Not Available in Claude

**Issue:** `/mcp` shows "No MCP servers configured"

**Solutions:**
1. Ensure you're in the correct project directory
2. Check registration: `claude mcp list`
3. Restart Claude Code session
4. Verify `.claude.json` contains no3sis entry

## Development

### Running Tests

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run integration tests
pytest tests/ -v
```

### Adding New Tools

1. Add tool function in `server.py`:
```python
@mcp.tool()
async def my_new_tool(param: str) -> str:
    """Tool description for Claude."""
    result = _run_synapse_tool("synapse_newtool.py", [param])
    return json.dumps(result, indent=2)
```

2. Create corresponding Synapse CLI tool
3. Update agent definitions with `mcp__no3sis_my_new_tool`

## Performance

- **Latency**: ~20-50ms per request (subprocess overhead)
- **Throughput**: Async, handles multiple concurrent requests
- **Caching**: Synapse tools implement Redis caching (300s TTL)
- **Future**: Direct Python imports could reduce latency to ~5ms

## Contributing

This repo is designed to be portable - it can live in the Synapse workspace or as a standalone repo at `github.com/noesis-lattice/no3sis`.

Pull requests welcome for:
- Performance optimizations (direct imports vs subprocess)
- Additional Synapse tools
- Improved error handling
- Documentation improvements

## License

MIT
