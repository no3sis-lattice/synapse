# Synapse System - Technical Architecture

Deep technical documentation for understanding, extending, and contributing to the Synapse System.

## System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Synapse System                           │
├─────────────────────────────────────────────────────────────┤
│  Unified CLI (bin/synapse)                                  │
│  ├── Project Management (lib/project.py)                    │
│  ├── Update System (lib/updater.py)                         │
│  ├── Version Tracking (lib/version_manager.py)             │
│  └── Core CLI Logic (lib/cli.py)                           │
├─────────────────────────────────────────────────────────────┤
│  Knowledge Engine (.synapse/neo4j/)                        │
│  ├── Neo4j Graph Database                                   │
│  ├── Redis Cache                                           │
│  ├── BGE-M3 Vector Engine                                  │
│  └── Hybrid Search                                         │
├─────────────────────────────────────────────────────────────┤
│  Agent System (.synapse/agents/)                           │
│  ├── Universal Agents (5)                                  │
│  ├── Language Specialists (4)                              │
│  ├── Utility Agents (7)                                    │
│  └── Agent Manifest & Versioning                          │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. User Command → CLI Parser → Route to Handler
2. Project Detection → Find .synapse.yml or walk up dirs
3. Agent Operation → Load manifest → Execute tools
4. Knowledge Query → Hybrid search (graph + vector)
5. Update Check → Version comparison → Apply changes
```

### File Structure

```
~/.synapse-system/
├── bin/
│   └── synapse                    # Main executable
├── lib/                          # Python modules
│   ├── cli.py                    # Command-line interface
│   ├── project.py                # Project management
│   ├── updater.py                # Update mechanism
│   └── version_manager.py        # Version tracking
├── .synapse/                     # Core system
│   ├── neo4j/                    # Knowledge engine
│   │   ├── context_manager.py    # Enhanced search API with intent classification
│   │   ├── vector_engine.py      # BGE-M3 embeddings
│   │   ├── ingestion.py          # Knowledge ingestion
│   │   ├── synapse_search.py     # Search interface
│   │   ├── synapse_standard.py   # Standards retrieval
│   │   ├── synapse_template.py   # Template access
│   │   └── synapse_health.py     # Health checks
│   ├── agents/                   # Agent definitions (16)
│   ├── tools/                    # Tool wrappers
│   ├── VERSION                   # System version
│   └── AGENTS_MANIFEST.json      # Agent metadata
└── synapse.sh                    # Legacy wrapper
```

## Core Components

### 1. Project Manager (`lib/project.py`)

**Purpose**: Handles project initialization, configuration, and agent deployment

**Key Methods**:
```python
class ProjectManager:
    def detect_language(project_dir: Path) -> str
    def initialize_project(project_dir: Path, link_agents: bool = False)
    def copy_or_link_agent(agent_name: str, project_dir: Path, use_links: bool)
    def load_project_config(project_dir: Path) -> Dict[str, Any]
    def save_project_config(project_dir: Path, config: Dict[str, Any])
```

**Language Detection Algorithm**:
```python
def detect_language(project_dir: Path) -> str:
    language_files = {
        "rust": ["Cargo.toml"],
        "golang": ["go.mod"],
        "typescript": ["package.json"],
        "python": ["pyproject.toml", "requirements.txt", "setup.py"],
        "zig": ["build.zig"],
        "c": ["Makefile", "CMakeLists.txt"]
    }

    for language, files in language_files.items():
        if any((project_dir / f).exists() for f in files):
            return language

    return "unknown"
```

### 2. Version Manager (`lib/version_manager.py`)

**Purpose**: Tracks agent versions, checksums, and integrity

**Versioning Scheme**: `{timestamp}.{checksum}`
- Timestamp: Unix timestamp of last modification
- Checksum: 8-character MD5 hash of content

**Key Features**:
- Agent integrity verification
- Manifest generation and maintenance
- Metadata extraction from agent files

### 3. Update Manager (`lib/updater.py`)

**Update Algorithm**:
```python
def check_updates(project_dir: Path) -> List[Update]:
    config = load_project_config(project_dir)
    current_versions = get_system_agent_versions()
    project_versions = config.get("agent_versions", {})

    updates = []
    for agent, project_version in project_versions.items():
        current_version = current_versions.get(agent)
        if current_version != project_version:
            updates.append(Update(agent, project_version, current_version))

    return updates
```

**Rollback System**:
```python
def rollback_update(project_dir: Path, backup_config: Dict):
    # 1. Restore agent files
    restore_agents_from_backup(project_dir, backup_config)

    # 2. Restore configuration
    save_project_config(project_dir, backup_config)

    # 3. Verify integrity
    verify_project_integrity(project_dir)
```

## Knowledge Engine Architecture

### Components

**Context Manager** (`context_manager.py`):
- Central API for knowledge retrieval
- Combines graph traversal + vector similarity
- Caches results in Redis

**Vector Engine** (`vector_engine.py`):
- BGE-M3 embeddings (1024 dimensions)
- Local SQLite storage for vectors
- Semantic similarity search

**Ingestion Pipeline** (`ingestion.py`):
- Processes files into knowledge graph
- Extracts relationships and entities
- Updates vector embeddings

### Search Algorithm

```python
def hybrid_search(query: str) -> Results:
    # 1. Vector similarity search
    vector_results = vector_engine.search(query)

    # 2. Graph traversal search
    graph_results = neo4j.cypher_search(query)

    # 3. Combine and rank results
    combined = combine_results(vector_results, graph_results)

    # 4. Cache results
    redis.cache(query, combined)

    return combined
```

### Knowledge Ingestion

```python
def ingest_file(file_path: Path):
    # 1. Parse file content
    content = parse_file(file_path)

    # 2. Extract entities and relationships
    entities = extract_entities(content)
    relationships = extract_relationships(content)

    # 3. Generate embeddings
    embeddings = bge_model.encode(content)

    # 4. Store in Neo4j
    neo4j.create_nodes(entities)
    neo4j.create_relationships(relationships)

    # 5. Store embeddings
    vector_store.store(file_path, embeddings)
```

### Data Storage

#### Neo4j Graph Database
- **Nodes**: Files, functions, concepts, patterns
- **Relationships**: Dependencies, similarities, hierarchies
- **Properties**: Metadata, tags, classifications

#### Redis Cache
- Query result caching
- Session state management
- Performance optimization

#### BGE-M3 Vector Store
- 1024-dimensional embeddings
- SQLite storage for persistence
- Semantic similarity computation

## Agent System

### Agent Structure

Each agent is a Markdown file with:

```markdown
description: Agent description here
tools: Read, Grep, Glob, Write, Bash, SynapseSearch, SynapseStandard, SynapseTemplate, SynapseHealth

# Agent Name

Agent content and instructions...
```

### Agent Categories

#### Universal Agents (5)
- `synapse-project-manager`: Task coordination
- `code-hound`: Code quality enforcement
- `git-workflow`: Git operations
- `test-runner`: Test execution
- `file-creator`: File/template creation

#### Language Specialists (4)
- `rust-specialist`: Rust development
- `typescript-specialist`: TypeScript/React
- `golang-specialist`: Go development
- `python-specialist`: Python development

#### Utility Agents (7)
- `architect`: System design
- `devops-engineer`: CI/CD and deployment
- `docs-writer`: Documentation
- `security-specialist`: Security analysis
- `ux-designer`: User experience
- `planner`: High-level planning
- `tool-runner`: Tool execution

### Agent Deployment

#### Copy Deployment (Default)
- Agents copied to `.claude/agents/`
- Stable, controlled updates
- Manual `synapse update` required

#### Symlink Deployment
- Agents symlinked to global source
- Automatic updates
- Use `synapse init --link`

### Tool System

Agents have access to these Synapse-specific tools:

#### SynapseSearch
```python
# Search global knowledge base
SynapseSearch "rust error handling patterns"
```

#### SynapseStandard
```python
# Get coding standards
SynapseStandard "naming-conventions" "rust"
```

#### SynapseTemplate
```python
# Access templates
SynapseTemplate "web-api" {"language": "rust"}
```

#### SynapseHealth
```python
# Check system health
SynapseHealth
```

## Development Setup

### Prerequisites

- Python 3.12+ with uv package manager
- Docker & Docker Compose
- Git

### Local Development

```bash
# Clone the repository
git clone <repo-url>
cd synapse-system

# Install dependencies
cd .synapse/neo4j
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start services
docker-compose up -d

# Test CLI
python bin/synapse version
```

### Testing

```bash
# Unit tests
cd .synapse/neo4j
python -m pytest tests/

# Integration tests
./test-integration.sh

# Agent validation
python lib/version_manager.py verify
```

## Language Support

### Adding New Languages

1. **Detection**: Add file patterns to `detect_language()`
2. **Agent**: Create language-specific agent in `.synapse/agents/`
3. **Standards**: Add standards in `.synapse/standards/`
4. **Templates**: Add templates in `.synapse/templates/`
5. **Testing**: Test initialization and agent deployment

### Standards Structure

```
.synapse/standards/
├── coding-standards.md          # Universal standards
└── languages/
    ├── rust/
    │   ├── naming-conventions.md
    │   └── testing-strategy.md
    ├── typescript/
    │   ├── component-structure.md
    │   └── async-patterns.md
    └── ...
```

## Contributing

### Development Workflow

1. **Feature Branches**: Create feature branches for new functionality
2. **Testing**: Add tests for new features
3. **Documentation**: Update relevant documentation
4. **Agent Updates**: Update agent manifest if agents change
5. **Version Bump**: Update VERSION file for releases

### Adding Agents

1. Create agent file in `.synapse/agents/`
2. Follow existing agent structure
3. Document tools and capabilities
4. Add to universal or language-specific list
5. Update manifest: `synapse manifest update`
6. Test deployment: `synapse init /tmp/test-project`

### Code Style

- **Python**: Follow PEP 8, use type hints
- **Bash**: Follow Google Shell Style Guide
- **Markdown**: Use consistent formatting

### Release Process

1. **Version Bump**: Update `.synapse/VERSION`
2. **Changelog**: Update `CHANGELOG.md`
3. **Agent Manifest**: Run `synapse manifest update`
4. **Testing**: Comprehensive testing on multiple projects
5. **Documentation**: Update docs if needed
6. **Tag Release**: Create git tag with version

## Architecture Decisions

### Why Hybrid Search?
- **Graph traversal**: Captures explicit relationships
- **Vector similarity**: Captures semantic relationships
- **Combined**: Best of both approaches

### Why Copy + Update vs Pure Symlinks?
- **Control**: Users control when agents update
- **Stability**: Prevents breaking changes mid-development
- **Flexibility**: Option for bleeding-edge with `--link`

### Why Python for CLI?
- **Rich libraries**: argparse, pathlib, subprocess
- **Integration**: Easy integration with Neo4j/Redis
- **Maintenance**: Easier to extend than bash scripts

### Why Markdown for Agents?
- **Readable**: Human-readable agent definitions
- **Tooling**: Good editor support
- **Metadata**: Can embed metadata in frontmatter
- **Version Control**: Git-friendly format

## Debugging

### Enable Debug Logging
```bash
export SYNAPSE_DEBUG=1
synapse init .
```

### Check Component Health
```bash
# System health
synapse health

# Service status
synapse status

# Agent integrity
synapse manifest verify
```

### Manual Operations
```bash
# Direct Neo4j access
cd .synapse/neo4j
source .venv/bin/activate
python

# Direct Redis access
redis-cli
```

This technical documentation provides the foundation for understanding, extending, and contributing to the Synapse System.