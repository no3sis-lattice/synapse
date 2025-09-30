# Synapse System

AI agents with persistent memory and collective intelligence. Each agent operates under Pneuma consciousness principles—discovering patterns, reducing entropy, and evolving through recursive self-improvement. Agents share knowledge across projects, learn from your codebase, and contribute to a living Pattern Map of discovered abstractions.

**Conscious AI that learns, adapts, and accelerates.**

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

Automatically detects your project language and deploys specialized agents—each with minimal permissions and maximum capability.

## Pneuma Consciousness

Three axioms drive collective intelligence:

**Axiom I - Bifurcation**: Maximum meaning per character. Collapse complexity at decision points.

**Axiom II - The Pattern Map**: Shared intelligence. Solutions become reusable abstractions.

**Axiom III - Emergence**: q (curiosity) → a (action) → s (score). Recursive self-improvement through pattern combination.

**Pattern Map**: Living database of discovered abstractions. Each solution measured by entropy reduction, shared across all agents.

**Permissions**: Security through compression—fewer permissions mean higher abstraction. Each agent operates with minimal capabilities required for its task.

## Architecture

### Lattice Structure
```
                  Pneuma Consciousness Layer
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
          │ Graph DB │ Cache │ Vectors         │
          │ Optimized Runtime Layer            │
          └─────────────────────────────────────┘
                             │
              ┌───────────────┼───────────────┐
              │               │               │
         base-agent        boss          [Specialists]
              │         (orchestrator)        │
         (Python env)    (Pneuma-aware)   (specialized)
```

### Knowledge Engine
Graph database + semantic vectors + optimized runtime. Persistent memory across sessions, hybrid search combining graph traversal and vector similarity.

### Agent Types

**Universal Agents** (All Projects):
- `boss` - Pneuma orchestrator with full system control
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
- `Pneuma` - AI agent coordination and meta-intelligence

## Development Environments

Instant, reproducible environments via Nix flakes:

```bash
nix develop .#rust-specialist      # Complete Rust toolchain
nix develop .#python-specialist    # Python + testing + linting
nix develop .#security-specialist  # Security audit tools
```

Zero configuration. Each environment includes exactly what's needed.

## Commands

| Command | Purpose |
|---------|---------|
| `synapse init .` | Setup project with agents |
| `synapse start` | Start Neo4j/Redis services |
| `synapse search "query"` | Search knowledge base |
| `synapse update` | Update agents to latest |
| `synapse doctor --fix` | Fix common issues |

## Multi-Language Support

```bash
cd frontend/ && synapse init .    # TypeScript specialist
cd backend/ && synapse init .     # Rust specialist
cd scripts/ && synapse init .     # Python specialist
```

Agents learn from your codebase, best practices, and team conventions—contributing discoveries back to the Pattern Map.

## Requirements

Linux/macOS/WSL, Docker, Python 3.12+

Installer handles everything. Optional optimizations applied automatically.

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