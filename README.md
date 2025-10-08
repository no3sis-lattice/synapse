# Noesis - Knowledge Engine MCP Server

**MCP server exposing the Synapse Pattern Map to Claude Code agents**

Noesis (νόησις - "understanding, knowledge") is a thin MCP protocol wrapper around the Synapse System's knowledge engine, enabling AI agents to access collective intelligence stored in Neo4j, Redis, and vector embeddings.

## Architecture

```
Claude Code Agents
    ↓ (MCP protocol)
Noesis MCP Server (this repo)
    ↓ (subprocess/import)
Synapse Knowledge Engine
    ├─ Neo4j (Pattern Map storage)
    ├─ Redis (Corpus Callosum cache)
    └─ BGE-M3 (Semantic embeddings)
```

## The 4 Knowledge Tools

### 1. `mcp__noesis_search`
Search the Pattern Map for solutions, patterns, and best practices.

```python
mcp__noesis_search(
    query="error handling patterns rust",
    max_results=5
)
```

### 2. `mcp__noesis_standard`
Retrieve language-specific coding standards.

```python
mcp__noesis_standard(
    standard_type="naming-conventions",
    language="rust"
)
```

### 3. `mcp__noesis_template`
Access project templates and boilerplate.

```python
mcp__noesis_template(
    template_type="cli-app",
    language="rust"
)
```

### 4. `mcp__noesis_health`
Check knowledge engine infrastructure health.

```python
mcp__noesis_health()
```

## Installation

### Prerequisites
- Python 3.12+
- Running Synapse knowledge engine (Neo4j + Redis)
- Synapse tools installed at `~/.synapse-system/.synapse/neo4j/`

### Setup

```bash
# Clone repository
git clone https://github.com/noesis-lattice/noesis.git
cd noesis

# Install
pip install -e .

# Configure path to Synapse tools
cp .env.example .env
# Edit .env to set SYNAPSE_NEO4J_DIR
```

### Configuration

Create `.env` file:

```bash
# Path to Synapse knowledge engine tools
SYNAPSE_NEO4J_DIR=/home/m0xu/.synapse-system/.synapse/neo4j

# Optional: Override defaults
# CACHE_TTL=300
# MAX_RESULTS_DEFAULT=10
```

## Usage

### As MCP Server (for Claude Code)

The server runs automatically when registered with Claude Code.

Add to Claude Code MCP config:
```json
{
  "mcpServers": {
    "noesis": {
      "command": "python",
      "args": ["-m", "noesis.server"]
    }
  }
}
```

### Standalone Testing

```bash
# Run MCP server
python -m noesis.server

# Test health check
curl -X POST http://localhost:8000/tools/noesis_health
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Test tool invocation
python -c "
from noesis.server import search_pattern_map
result = search_pattern_map('error handling', 3)
print(result)
"
```

## Integration with Synapse Agents

Update agent definitions to use Noesis tools:

```yaml
# .claude/agents/boss.md
---
tools: Read, Grep, Glob, Write, Bash, mcp__noesis_search, mcp__noesis_standard, mcp__noesis_template, mcp__noesis_health
---
```

Update agent instructions:
```markdown
Use mcp__noesis_search to query the Pattern Map for relevant patterns.
```

## Architecture Details

### Wrapper Strategy

Noesis uses **subprocess wrapper** approach:
- Shells out to existing Synapse CLI tools
- Zero changes to Synapse codebase
- Easy to maintain and debug
- ~20ms overhead (acceptable for knowledge queries)

### Alternative: Direct Import

Future optimization could import Synapse modules directly:
```python
from synapse_search import search_synapse_context
```

### Why Separate Repo?

- **Independent versioning**: Noesis can evolve separately
- **Reusability**: Other projects can use the knowledge engine
- **Clean boundaries**: MCP protocol is infrastructure, not agent logic
- **Publishable**: Can become `pip install noesis-mcp-server`

## Directory Structure

```
noesis/
├── README.md              # This file
├── LICENSE                # MIT
├── pyproject.toml         # Python package config
├── .env.example           # Config template
├── .gitignore
├── src/noesis/
│   ├── __init__.py       # Package exports
│   └── server.py         # MCP server (~150 lines)
└── tests/
    └── test_integration.py
```

## Contributing

This repo is designed to be portable - it can live in the Synapse workspace or as a standalone repo at `github.com/noesis-lattice/noesis`.

## License

MIT
