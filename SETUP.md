# No3sis Setup Guide

Quick start guide for setting up and testing the No3sis MCP server.

## Prerequisites

✅ **Already installed** (based on your setup):
- Python 3.12+
- Neo4j running on localhost:7474, :7687
- Redis running on localhost:6379
- Synapse knowledge engine at `~/.synapse-system/.synapse/neo4j/`

## Installation

### 1. Install No3sis

From the `no3sis/` directory:

```bash
cd /home/m0xu/1-projects/no3sis

# Create environment file
cp .env.example .env

# Edit .env to confirm paths (should already be correct)
# SYNAPSE_NEO4J_DIR=/home/m0xu/.synapse-system/.synapse/neo4j

# Install package
pip install -e .
```

### 2. Verify Synapse Tools Are Available

```bash
# Check that Synapse tools exist
ls ~/.synapse-system/.synapse/neo4j/synapse_*.py

# Should show:
# synapse_health.py
# synapse_search.py
# synapse_standard.py
# synapse_template.py
```

### 3. Test No3sis Tools

```bash
# Test health check
python -m no3sis.server health

# Test pattern search
python -m no3sis.server search "error handling" 3

# Test getting standards
python -m no3sis.server standard naming-conventions rust

# Test template retrieval
python -m no3sis.server template cli-app rust
```

Expected output: JSON responses from each tool

## Usage Examples

### From Python

```python
from no3sis.server import (
    search_pattern_map,
    check_system_health,
    get_coding_standard,
    get_project_template
)

# Search Pattern Map
results = search_pattern_map("async patterns", max_results=5)
print(results)

# Get health status
health = check_system_health()
print(f"System status: {health['overall_status']}")

# Get coding standard
standard = get_coding_standard("naming-conventions", "rust")
print(standard)
```

### From Command Line

```bash
# Search
python -m no3sis.server search "testing strategies" 10

# Standards
python -m no3sis.server standard error-handling golang

# Templates
python -m no3sis.server template web-api rust

# Health
python -m no3sis.server health
```

## Testing Against Real Synapse Infrastructure

### 1. Verify Infrastructure is Running

```bash
# Check Docker containers
docker ps | grep -E "neo4j|redis"

# Should show both containers running
```

### 2. Run Integration Tests

```bash
# From no3sis directory
pytest tests/test_integration.py -v

# Or run manually
python tests/test_integration.py
```

### 3. Expected Results

- **Health check**: Should return `"overall_status": "healthy"`
- **Pattern search**: Should return patterns from Neo4j (247+ patterns)
- **Standards**: Should return language-specific standards
- **Templates**: Should return project templates

## Troubleshooting

### Tool Not Found Errors

**Error**: `Synapse tool not found: synapse_search.py`

**Solution**: Check `SYNAPSE_NEO4J_DIR` in `.env`:
```bash
# Verify path
ls $SYNAPSE_NEO4J_DIR/synapse_search.py

# Update .env if needed
SYNAPSE_NEO4J_DIR=/correct/path/to/.synapse/neo4j
```

### Connection Errors

**Error**: `Neo4j service not accessible`

**Solution**:
```bash
# Restart containers
cd ~/.synapse-system/.synapse/neo4j
docker-compose up -d

# Or use synapse CLI
~/.synapse-system/synapse start
```

### --json Flag Not Recognized

**Error**: `unrecognized arguments: --json`

**Solution**: Synapse tools need to support `--json` flag. Check tool version:
```bash
python ~/.synapse-system/.synapse/neo4j/synapse_search.py --help
```

If `--json` is not supported, update the tools or modify `no3sis/src/no3sis/server.py` to parse non-JSON output.

## Integration with Claude Code

### Register MCP Server

Add to Claude Code's MCP configuration:

```json
{
  "mcpServers": {
    "no3sis": {
      "command": "python",
      "args": ["-m", "no3sis.server"],
      "cwd": "/home/m0xu/1-projects/no3sis"
    }
  }
}
```

### Test from Claude Code

```
@boss Use mcp__no3sis_search to find error handling patterns
```

Agent should be able to invoke the tool and receive Pattern Map results.

## Moving to Separate Repo

The No3sis directory is designed to be portable:

```bash
# Copy to new location
cp -r /home/m0xu/1-projects/no3sis /path/to/new/repo

# Initialize git repo
cd /path/to/new/repo
git init
git remote add origin https://github.com/no3sis-lattice/synapse.git

# Commit and push
git add .
git commit -m "Initial commit: No3sis MCP server"
git push -u origin main
```

The only dependency is that `SYNAPSE_NEO4J_DIR` in `.env` points to the correct Synapse installation.

## Next Steps

1. **Test with Claude Code agents**: Verify all 11 agents can use `mcp__no3sis_*` tools
2. **Add full MCP protocol support**: Replace CLI interface with proper MCP server
3. **Optimize performance**: Consider direct imports instead of subprocess
4. **Add monitoring**: Track tool usage, latency, cache hit rates
5. **Extend functionality**: Add pattern storage API, real-time updates

## Status

✅ No3sis server implemented
✅ All 4 tools functional
✅ Agent definitions updated
⏳ MCP protocol integration (using CLI interface for now)
⏳ Claude Code testing

**Ready for initial testing!**
