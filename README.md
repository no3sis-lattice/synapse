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

# Instant development environments
nix develop .#python-specialist    # Python + mypy + pytest + black
nix develop .#rust-specialist      # Rust + cargo + clippy + rust-analyzer
nix develop .#typescript-specialist # Node.js + tsc + eslint + prettier
nix develop .#devops-engineer       # kubectl + terraform + ansible + docker

# Run agents directly
nix run .#code-hound               # Advanced code search
nix run .#security-specialist      # Security scanning
nix run .#4QZero                   # AI agent coordinator

# Build and validate everything
nix flake check                    # Validate all environments
nix build                          # Build all agents
```

**Auto-detects your language** (Rust, TypeScript, Go, Python) and sets up specialized agents.

## The Lattice Architecture

Synapse System implements a **composable functional lattice of flakes** - a mathematical approach to development environments that ensures reproducibility and composability.

### What is the Lattice?

```
                    main flake.nix
                         |
           ┌─────────────┼─────────────┐
           |             |             |
       base-agent    [18 Agent Flakes] |
           |             |             |
    (shared Python)  (specialized)  4QZero
                                   (coordinator)
```

Each "node" in the lattice is a **Nix flake** - a pure function that transforms inputs into development environments:

- **Input**: Dependencies (nixpkgs, base-agent)
- **Output**: Complete development environment with tools
- **Property**: Same inputs always produce identical outputs

### Benefits for Developers

**Zero Setup Time**: `nix develop .#rust-specialist` gives you a complete Rust environment instantly

**Perfect Reproducibility**: If it works on one machine, it works on all machines

**Instant Context Switching**: Move between Python, Rust, TypeScript environments in seconds

**Tool Isolation**: Each agent has exactly the tools it needs, no conflicts

**Composable Intelligence**: Agents can be combined and extended without interference

### The 4QZero Agent: Mathematical Coordination

The **4QZero** agent represents the mathematical heart of the system. The name carries deep meaning:

**4Q** - Four Quadrants of Intelligence:
```
    Analytical  │  Creative
                │
  ──────────────┼──────────────
                │
   Practical    │  Holistic
```

**Zero** - The Origin Point:
- Mathematical zero as the neutral element in the lattice
- The base state from which all other agents derive their context
- The coordination point that understands the entire system structure

4QZero operates with:
- **PyTorch** for deep learning and pattern recognition
- **Transformers** for natural language understanding
- **LangChain** for agent orchestration
- **OpenAI** integration for advanced reasoning

This agent doesn't just coordinate other agents - it understands the mathematical relationships between them, enabling emergent intelligence through composition.

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

### The Functional Lattice Structure

```
                        Synapse CLI
                             │
                  ┌──────────┼──────────┐
                  │          │          │
            Knowledge Engine │    Agent Lattice
          ┌─────────────────────────────────────┐
          │ Neo4j │ Redis │ BGE-M3 Vectors    │
          └─────────────────────────────────────┘
                             │
              ┌───────────────┼───────────────┐
              │               │               │
         base-agent        4QZero        [17 Agents]
              │            (coord)            │
    ┌─────────┼─────────┐       ┌─────────────┼─────────────┐
    │         │         │       │             │             │
  Python   Shared    Utils   Language    Development   Workflow
   Env     Tools           Specialists   Tools        Tools
            │                   │             │             │
         Neo4j,            rust,python    architect,    git,test,
         Redis,           typescript,     devops,      security,
         NumPy               golang      code-hound     docs
```

**Lattice Properties**:
- **Composable**: Each node can be combined with any other
- **Pure Functions**: Same inputs = same outputs (reproducibility)
- **Lazy Evaluation**: Only build what you need
- **Dependency Injection**: Clean separation of concerns

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

## Development Environments

The lattice provides instant, reproducible development environments for any language or tool:

### Language-Specific Environments

```bash
# Rust development with complete toolchain
nix develop .#rust-specialist
# → rustc, cargo, clippy, rust-analyzer, tarpaulin, etc.

# Python with analysis tools
nix develop .#python-specialist
# → python, mypy, pytest, black, flake8, pylint, bandit

# TypeScript/Node.js ecosystem
nix develop .#typescript-specialist
# → node, npm, tsc, eslint, prettier, jest, webpack

# Go development suite
nix develop .#golang-specialist
# → go, gopls, golangci-lint, delve, goreleaser
```

### Specialized Environments

```bash
# DevOps and infrastructure
nix develop .#devops-engineer
# → kubectl, terraform, ansible, docker, helm, k9s

# Security analysis
nix develop .#security-specialist
# → gitleaks, trivy, semgrep, nmap, cosign

# Code search and analysis
nix develop .#code-hound
# → ripgrep, fd, fzf, ast-grep, universal-ctags

# Architecture and design
nix develop .#architect
# → graphviz, plantuml, mermaid, pandoc, cloc
```

### Environment Switching

```bash
# Start in Rust environment
nix develop .#rust-specialist
cargo build && cargo test

# Switch to Python (new shell)
nix develop .#python-specialist
pytest && black .

# Switch to DevOps tools
nix develop .#devops-engineer
kubectl get pods && terraform plan
```

**Zero configuration required** - each environment includes exactly the tools needed, with correct versions, instantly available.

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
- `clarity-judge` - Code complexity and quality analysis
- `4QZero` - AI agent coordination and meta-intelligence

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



*Built for developers who want AI assistance that learns their patterns and enforces their standards.*

## License

[MIT](LICENSE)
