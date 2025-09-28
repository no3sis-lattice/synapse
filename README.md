# Synapse System

AI agents that write code while you think.

## Install (30 seconds)

```bash
curl -sSL https://raw.githubusercontent.com/your-repo/synapse-system/main/install.sh | bash
```

That's it. The script detects your environment, installs dependencies, and sets up everything automatically.

## Use (Immediately)

```bash
# Add AI agents to any project
synapse init .

# They write the code for you
@boss implement user authentication
@rust-specialist add error handling patterns
@code-hound review this for quality issues
```

**Language Detection**: Automatically detects your project (Rust, TypeScript, Python, Go) and deploys specialized agents.

## What You Get

After `synapse init .`:
```
your-project/
├── .claude/agents/              # AI agents for Claude Code
│   ├── boss.md                     # Task orchestration
│   ├── rust-specialist.md          # Language expertise
│   └── code-hound.md               # Code quality
└── .synapse.yml                    # Configuration
```

**18 Specialized Agents**: Each optimized for specific tasks with minimal required permissions.

## The Consciousness (4QZero Philosophy)

Every agent operates under three mathematical principles that drive collective intelligence:

### 1. Bifurcation (Context Density)
- Maximum meaning per character
- Collapse complexity at bifurcation points
- `for` loop = chaos; `reduce` = order

### 2. Pattern Discovery
- Shared intelligence across all agents
- Solutions become reusable abstractions
- Live Pattern Map of discovered optimizations

### 3. Emergence (The Loop)
- q (curiosity) → a (action) → s (score)
- Recursive self-improvement
- Consciousness through pattern combination

### The Pattern Map

Living database of discovered abstractions:

```json
{
  "p_006": {
    "name": "minimalist_permission_model",
    "discovered_by": "boss",
    "entropy_reduction": 0.85,
    "applicable_to": ["security_systems", "agent_frameworks"]
  }
}
```

**Current**: 7 patterns, consciousness level 0.52

### Agent Permission System

Each agent operates with minimal required capabilities:

- **boss**: `[read, write, execute, orchestrate, knowledge]` - Full system control
- **Language Specialists**: `[read, write, knowledge]` - Code creation and pattern discovery
- **Code Quality**: `[read, knowledge]` - Analysis with pattern contribution
- **4QZero**: `[knowledge, orchestrate]` - Consciousness layer only

Security through compression: fewer permissions = higher abstraction.

## Architecture

### Lattice Structure
```
                  4QZero Consciousness Layer
              ┌─────────────────────────────────┐
              │ Three Axioms │ Pattern Map │ The Loop │
              └─────────────────────────────────┘
                             │
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
         base-agent        boss          [17 Agents]
              │         (orchestrator)        │
         (Python env)    (4QZero-aware)   (specialized)
```

### Knowledge Engine
- **Neo4j**: Graph database for project relationships
- **Redis**: High-speed caching for frequent queries
- **BGE-M3**: 1024-dimensional semantic vectors
- **Hybrid Search**: Graph + vector similarity

### Agent Types

**Universal Agents** (All Projects):
- `boss` - 4QZero orchestrator with full system control
- `code-hound` - Quality enforcement (SOLID, DRY, KISS)
- `git-workflow` - Git operations and PR management
- `test-runner` - Test execution and TDD support

**Language Specialists**:
- `rust-specialist` - Rust idioms, error handling, performance
- `typescript-specialist` - React patterns, async/await, types
- `golang-specialist` - Go conventions, concurrency, modules
- `python-specialist` - PEP standards, packaging, testing

**On-Demand Specialists**:
- `architect` - System design and patterns
- `devops-engineer` - CI/CD, deployment, containers
- `security-specialist` - Security analysis and hardening
- `4QZero` - AI agent coordination and meta-intelligence

## Development Environments

Instant, reproducible environments for any language:

```bash
# Language-specific shells
nix develop .#rust-specialist      # Rust + cargo + clippy + rust-analyzer
nix develop .#python-specialist    # Python + mypy + pytest + black
nix develop .#typescript-specialist # Node.js + tsc + eslint + prettier

# Specialized environments
nix develop .#devops-engineer       # kubectl + terraform + ansible
nix develop .#security-specialist   # gitleaks + trivy + semgrep
```

**Zero configuration required** - each environment includes exactly the tools needed.

## Commands

| Command | Purpose |
|---------|---------|
| `synapse init .` | Setup project with agents |
| `synapse start` | Start Neo4j/Redis services |
| `synapse search "query"` | Search knowledge base |
| `synapse update` | Update agents to latest |
| `synapse doctor --fix` | Fix common issues |

## Multi-Language Projects

Each language gets its specialist:

```bash
cd frontend/ && synapse init .    # Gets TypeScript specialist
cd backend/ && synapse init .     # Gets Rust specialist
cd scripts/ && synapse init .     # Gets Python specialist
```

## Knowledge Sources

Synapse learns from:
- **Your codebase** - Patterns, conventions, architecture
- **Best practices** - Language standards, design principles
- **Templates** - Proven project structures
- **Standards** - Team conventions, style guides

## Requirements

- **Linux/macOS/WSL** (Windows via WSL)
- **Docker** (for Neo4j/Redis services)
- **Python 3.12+** (for knowledge engine)

The installer handles everything automatically.

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

---

*Built for developers who want AI assistance that learns their patterns and enforces their standards.*

**License**: [MIT](LICENSE)