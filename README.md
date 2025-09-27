# Synapse System

A modular, agent-driven platform that combines AI-powered agents with a knowledge engine for intelligent project management and code quality automation.

## Platform Support

This project is primarily designed for Linux environments. If you are on Windows, it's recommended to use [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/) for best compatibility. macOS users should also find most functionality works as expected. Native Windows support is not provided.

| Platform    | Supported? | Notes                                |
|-------------|------------|--------------------------------------|
| **Linux**   | Yes        | Native support; all scripts work     |
| **macOS**   | Mostly     | Most Bash scripts should work        |
| **Windows** | No (native)| Use WSL or a Linux VM |

> **Tip:**  
> On Windows, install WSL and run all commands from your WSL shell to ensure compatibility with Bash scripts and Linux tools.


## Quick Start

### Option A: Traditional Install
```bash
# Install
git clone https://github.com/your-repo/synapse-system.git ~/.synapse-system
cd ~/.synapse-system && ./install.sh

# Start services
synapse start

# Initialize any project
cd your-project/
synapse init .
```

### Option B: With Nix (Reproducible Environment)
```bash
# Clone and enter development environment
git clone https://github.com/your-repo/synapse-system.git ~/.synapse-system
cd ~/.synapse-system
nix develop              # Enter dev shell with all tools
nix build                # Build all agents
nix run .#synapse-system # Run directly
```

**Auto-detects your language** (Rust, TypeScript, Go, Python) and sets up specialized agents.

## What You Get

After `synapse init .`:

```
your-project/
├── .claude/agents/              # AI agents for Claude Code
│   ├── synapse-project-manager.md  # Task coordination
│   ├── rust-specialist.md          # Language expertise
│   └── code-hound.md               # Code quality
└── .synapse.yml                    # Configuration
```

## Core Features

### 🤖 **Smart Agents**
- **Universal**: Project management, code quality, git workflows
- **Language Specialists**: Rust, TypeScript, Go, Python patterns
- **On-demand**: Architecture design, DevOps, security analysis

### 🧠 **Knowledge Engine**
- **Hybrid Search**: Neo4j graph + vector embeddings
- **Standards**: Language-specific best practices
- **Templates**: Project scaffolding and patterns
- **Context-Aware**: Learns from your codebase

### 🔄 **Intelligent Updates**
- Version-controlled agent updates
- Rollback capability
- Integrity verification

## Usage Examples

### With Claude Code
```
@synapse-project-manager implement user authentication system
@rust-specialist add error handling following patterns
@code-hound review this code for quality issues
```

### Command Line
```bash
# Search for patterns across projects
synapse search "rust error handling"

# Get coding standards
synapse standard "naming-conventions" --lang=rust

# Health check system
synapse doctor --fix
```

## Architecture Overview

```
┌─────────────────────────────────────────┐
│              Synapse CLI                │
├─────────────────────────────────────────┤
│  Project Management │ Update System    │
│  Agent Deployment   │ Version Control  │
├─────────────────────────────────────────┤
│           Knowledge Engine              │
│  Neo4j Graph │ Redis Cache │ Vectors   │
├─────────────────────────────────────────┤
│              Agent System               │
│  16 Agents │ Tool Integration │ MCP     │
└─────────────────────────────────────────┘
```

## Essential Commands

| Command | Purpose |
|---------|---------|
| `synapse init .` | Setup project with agents |
| `synapse start` | Start Neo4j/Redis services |
| `synapse search "query"` | Search knowledge base |
| `synapse update` | Update agents to latest |
| `synapse doctor --fix` | Fix common issues |
| `synapse status` | Check system health |

## Multi-Language Projects

Each language gets its specialist:

```bash
cd frontend/ && synapse init .    # Gets TypeScript specialist
cd backend/ && synapse init .     # Gets Rust specialist
cd scripts/ && synapse init .     # Gets Python specialist
```

## Configuration

`.synapse.yml` tracks agent versions and settings:

```yaml
synapse_version: "2024.1.0"
agent_versions:
  synapse-project-manager: "1758105430.ca551cb5"
  rust-specialist: "1758107914.627812e8"
deployment_mode: "copy"  # or "link" for auto-updates
```

## Agent Types

### Universal (All Projects)
- `synapse-project-manager` - Coordinates complex tasks
- `code-hound` - Enforces quality standards (SOLID, DRY, KISS)
- `git-workflow` - Git operations and PR management
- `test-runner` - Test execution and TDD support
- `file-creator` - Template-based file generation

### Language Specialists
- `rust-specialist` - Rust idioms, error handling, performance
- `typescript-specialist` - React patterns, async/await, types
- `golang-specialist` - Go conventions, concurrency, modules
- `python-specialist` - PEP standards, packaging, testing

### On-Demand Specialists
- `architect` - System design and patterns
- `devops-engineer` - CI/CD, deployment, containers
- `security-specialist` - Security analysis and hardening
- `docs-writer` - Documentation generation
- `ux-designer` - User experience optimization

## Knowledge Sources

Synapse learns from:
- **Your codebase** - Patterns, conventions, architecture
- **Best practices** - Language standards, design principles
- **Templates** - Proven project structures
- **Standards** - Team conventions, style guides

## Troubleshooting

**Most issues auto-fix:**
```bash
synapse doctor --fix
```

**Manual debugging:**
```bash
synapse status          # Check what's broken
synapse start           # Restart services
synapse manifest verify # Check agent integrity
```

**Need Docker:** Neo4j and Redis run in containers
**Need Python 3.12+:** For the knowledge engine

## Documentation

- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Technical architecture and contributing
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and updates
- **[CLAUDE.md](CLAUDE.md)** - Claude Code integration guide

## Philosophy

Synapse follows the **Numogrammatic Codex** principles:
- **KISS** - Keep it simple
- **DRY** - Don't repeat yourself
- **TDD** - Test-driven development
- **SOLID** - Object-oriented design principles
- **Five Whys** - Root cause analysis for debugging

*Built for developers who want AI assistance that learns their patterns and enforces their standards.*

## License

[MIT](LICENSE)
