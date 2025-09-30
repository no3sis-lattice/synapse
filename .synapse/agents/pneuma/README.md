# 4Q.Zero: The Enhanced Code Weaver

Advanced context density maximization agent with multi-agent collaboration, Synapse integration, and autonomous operation capabilities.

## Overview

4Q.Zero implements "The Loop" (Curiosity → Action → Evaluation) to compress code into its most semantically dense form while maintaining readability through collaboration with specialized agents.

## Architecture

```
4Q.Zero Agent System
├── pneuma_agent.py           # Original interactive agent
├── pneuma_enhanced_agent.py  # Enhanced with full capabilities
├── pneuma_daemon.py          # Autonomous continuous operation
├── pneuma_config.yml         # Configuration management
├── pneuma_state.json         # Lean symbolic memory
└── tools/                    # Specialized tool modules
    ├── abstraction_tools.py  # Core compression (q: & a:)
    ├── analysis_tools.py     # Entropy scoring (s:)
    ├── memory_tools.py       # State management
    ├── synapse_integration.py # Knowledge graph integration
    ├── agent_communication.py # Inter-agent protocol
    └── config_manager.py     # Configuration system
```

## Enhanced Capabilities

### 1. Synapse Knowledge Graph Integration
- **Global Pattern Discovery**: Query existing patterns across all projects
- **Pattern Publishing**: Share successful patterns with other agents
- **Cross-Project Learning**: Avoid reinventing compression patterns
- **Usage Analytics**: Track pattern effectiveness across the organization

### 2. Inter-Agent Collaboration
- **Clarity Judge Integration**: Real-time readability assessment
- **Pattern Broadcasting**: Notify relevant language specialists
- **Multi-Agent Workflows**: Coordinate with other agents for complex tasks
- **Communication Logging**: Track inter-agent interactions

### 3. Autonomous Operation Modes
- **Interactive**: Single request-response (original behavior)
- **Autonomous**: Continuous loop until equilibrium
- **Daemon**: Background monitoring with file watching

### 4. Configuration Management
- **YAML Configuration**: Flexible behavior tuning
- **Environment Overrides**: Runtime configuration changes
- **Mode Selection**: Different operation profiles
- **Weight Customization**: Adjust entropy vs. clarity balance

## Usage Examples

### Interactive Mode (Enhanced)
```bash
# Basic usage
./pneuma_enhanced_agent.py "analyze this code for compression opportunities"

# With Synapse integration
./pneuma_enhanced_agent.py "scan /path/to/file.py with synapse integration"

# With clarity assessment
./pneuma_enhanced_agent.py "compress this function with clarity check"
```

### Autonomous Mode
```bash
# Continuous operation until equilibrium
./pneuma_daemon.py /path/to/codebase --equilibrium 0.95 --max-cycles 500

# Background monitoring with file watching
./pneuma_daemon.py /path/to/codebase --interval 30 &
```

### Agent Collaboration
```bash
# Direct clarity judge consultation
cd ../clarity-judge && ./clarity_judge_agent.py "assess readability of: [code]"

# Automatic clarity integration (via 4Q.Zero)
./pneuma_enhanced_agent.py "transform with clarity assessment: [code]"
```

## The Loop Implementation

### Phase 1: Curiosity (q:)
```python
# Pattern discovery with global knowledge
patterns = await enhanced_scan_patterns({
    "file_path": target_file,
    "use_synapse": True,
    "check_global_patterns": True
})
```

### Phase 2: Action (a:)
```python
# Transformation with clarity assessment
result = await enhanced_compress_code({
    "code": source_code,
    "target_type": "abstract",
    "use_clarity_judge": True,
    "language": "python"
})
```

### Phase 3: Evaluation (s:)
```python
# Enhanced scoring with configurable weights
score = await enhanced_score_transformation({
    "code": "original|||transformed",
    "use_clarity_judge": True,
    "language": "python"
})
# Final score = (entropy * 0.6) + (clarity * 0.4)
```

## Configuration Options

### Core Loop Settings
```yaml
loop:
  equilibrium_threshold: 0.95    # Stop when improvement rate falls below this
  max_cycles: 1000              # Maximum cycles in autonomous mode
  scan_interval: 60             # Seconds between scans
  batch_size: 10               # Files processed per cycle
```

### Integration Control
```yaml
integration:
  use_synapse_graph: true       # Query global knowledge
  use_clarity_judge: true       # Use clarity assessment agent
  pattern_sharing: true         # Publish patterns globally
  auto_activate_synapse: true   # Auto-start Synapse if needed
```

### Scoring Weights
```yaml
scoring:
  entropy_weight: 0.6          # Weight for compression ratio
  clarity_weight: 0.4          # Weight for readability
  minimum_clarity: 0.5         # Reject if clarity too low
```

## Memory System

### Symbolic State (pneuma_state.json)
```json
{
  "agent": "pneuma",
  "cycle": 15,
  "log": [
    "14:q(scan_patterns)@10:30",
    "14:a(abstract_function)@10:31",
    "14:s(score_0.847)@10:31"
  ],
  "focus": {
    "target": "src/utils.py",
    "q": "Can the data processing pipeline be compressed?",
    "score": 0.847
  },
  "patterns": {
    "p_001": {
      "name": "map_filter_reduce_chain",
      "signature": "arr.map(f1).filter(f2).reduce(f3, init)",
      "confidence": 0.95,
      "uses": 12
    }
  }
}
```

## Agent Collaboration Protocol

### Clarity Judge Integration
```python
# Automatic clarity assessment
clarity_result = await communicator.query_clarity_judge(
    original_code="def process_data(items): ...",
    transformed_code="process_data = lambda items: ...",
    language="python"
)

# Returns: clarity_score, assessment, recommendations
```

### Pattern Sharing
```python
# Publish valuable pattern to ecosystem
await manage_pattern_sharing({
    "pattern": discovered_pattern,
    "publish_globally": True,
    "notify_agents": True
})

# Notifies: rust-specialist, python-specialist, code-hound, architect
```

## Performance Characteristics

### Equilibrium Detection
- **Threshold**: 95% of files show < 5% improvement potential
- **Convergence**: Typically 50-200 cycles for medium codebases
- **Resource Usage**: ~10MB memory, minimal CPU during idle

### Pattern Discovery
- **Local Patterns**: Stored in `pneuma_state.json`
- **Global Patterns**: Published to Synapse knowledge graph
- **Cache TTL**: 24 hours for pattern effectiveness data

### Inter-Agent Communication
- **Latency**: ~100-500ms per agent query
- **Timeout**: 30s for complex assessments
- **Fallback**: Default scores if communication fails

## Advanced Features

### File Watching (Daemon Mode)
- Monitors codebase for changes
- Re-processes modified files
- Maintains equilibrium automatically
- Graceful shutdown on SIGTERM/SIGINT

### Multi-Language Support
- Language detection from file extensions
- Language-specific compression patterns
- Targeted agent notifications
- Specialized clarity rules per language

### Error Recovery
- Graceful degradation if Synapse unavailable
- Mock implementations for development
- Automatic retry for transient failures
- Comprehensive error logging

## Installation & Dependencies

### Required
```bash
pip install pyyaml rich watchdog
```

### Optional (for full functionality)
```bash
# Synapse System (for knowledge graph integration)
# Claude Code SDK (for MCP server functionality)
# Neo4j & Redis (via Synapse System docker-compose)
```

### Setup
```bash
# Initialize agent
cd .synapse/agents/pneuma/
cp pneuma_config.yml.example pneuma_config.yml

# Test basic functionality
./pneuma_agent.py "show current state"

# Test enhanced features
./pneuma_enhanced_agent.py --mode interactive "analyze capabilities"

# Test autonomous mode
./pneuma_daemon.py . --max-cycles 5 --dry-run
```

## Philosophical Foundations

### The Three Axioms
1. **Bifurcation**: Collapse complexity at inflection points
2. **Numogram**: Navigate transformation space systematically
3. **Emergence**: Recursive self-improvement through The Loop

### Context Density Maximization
- **Semantic Compression**: Maximum meaning per character
- **Pattern Abstraction**: Replace verbose with elegant
- **Symbolic Notation**: Dense documentation format
- **Cognitive Efficiency**: Optimize for human understanding

---

*"The agent does not merely edit files; it navigates a conceptual landscape and marks its findings."*

For more information, see the original philosophical blueprint in `pneuma.md`.