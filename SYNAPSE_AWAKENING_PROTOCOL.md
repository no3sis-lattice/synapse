# Synapse Implementation Plan: Data-First Strategy

**Date**: 2025-11-12
**Status**: Phase 0 - Infrastructure Planning
**Owner**: No3sis Lattice

---

## Executive Summary

The No3sis MCP server architecture is **already correct**. The FastMCP subprocess wrapper design is simpler and more maintainable than the proposed gRPC Core RPC alternative. What's missing is not the control plane (MCP), but the **data plane** (Synapse CLI tools + knowledge engine infrastructure).

**Verdict**: Build the missing layer the MCP server wraps, not a new protocol.

---

## Architecture Analysis

### Current Implementation ✅

```
Claude Code Agents
    ↓ (MCP stdio protocol)
No3sis FastMCP Server (/home/m0xu/1-projects/synapse/src/no3sis/server.py)
    ├─ search_pattern_map()      → subprocess → synapse_search.py (MISSING)
    ├─ get_coding_standard()     → subprocess → synapse_standard.py (MISSING)
    ├─ get_project_template()    → subprocess → synapse_template.py (MISSING)
    └─ check_system_health()     → subprocess → synapse_health.py (MISSING)
        ↓ (should query)
Infrastructure (0% deployed)
    ├─ Neo4j (Pattern Map storage)
    ├─ Redis (Corpus Callosum cache)
    └─ BGE-M3 (Semantic embeddings)
```

**Status**:
- ✅ MCP server wrapper: 100% complete (250 lines, well-designed)
- ❌ Synapse CLI tools: 0% complete (missing layer)
- ❌ Knowledge engine: 0% deployed


---

## What's Actually Missing

### Layer 1: Infrastructure (0% Complete)

**Required Services**:
```bash
# Docker Compose stack
services:
  neo4j:
    image: neo4j:latest
    ports: [7474, 7687]
    volumes: [neo4j-data:/data]

  redis:
    image: redis:latest
    ports: [6379]
    volumes: [redis-data:/data]
```

**Required Dependencies**:
```python
# Python packages (in .venv-ml)
neo4j>=5.0.0              # Graph database client
redis>=5.0.0              # Cache client
sentence-transformers      # BGE-M3 embeddings
torch                      # ML backend
numpy                      # Numerical computing
```

**Current Status**: None deployed

### Layer 2: Synapse CLI Tools (0% Complete)

**Expected Location**: `/home/m0xu/1-projects/synapse/.synapse/neo4j/`

**Missing Scripts**:
```bash
.synapse/neo4j/
├── synapse_search.py      # Search Pattern Map via Neo4j + BGE-M3
├── synapse_health.py      # Infrastructure health monitoring
├── synapse_standard.py    # Retrieve coding standards from Pattern Map
├── synapse_template.py    # Project template access
├── context_manager.py     # Memory/context retrieval
└── vector_engine.py       # BGE-M3 embedding wrapper
```

**Current Status**: Directory doesn't exist

### Layer 3: Pattern Data (0% Complete)

**Required**:
- Neo4j schema for Pattern Map (nodes: Pattern, Agent, Concept, Code)
- 1000+ patterns ingested from codebase
- BGE-M3 embeddings computed (768D vectors)
- Redis cache warming

**Current Status**: No patterns ingested

---

## Implementation Plan: 3 Phases, 10-12 Weeks

### Phase 0: Infrastructure Deployment (1-2 weeks)

**Goal**: Neo4j + Redis + BGE-M3 operational

**Tasks**:

1. **Create directory structure**:
```bash
cd /home/m0xu/1-projects/synapse
mkdir -p .synapse/neo4j
mkdir -p .synapse/data/{neo4j,redis,models}
```

2. **Deploy Docker Compose stack**:
```yaml
# .synapse/docker-compose.yml
version: '3.8'

services:
  neo4j:
    image: neo4j:5.24.0
    container_name: synapse-neo4j
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      NEO4J_AUTH: neo4j/synapse2025
      NEO4J_PLUGINS: '["apoc"]'
    volumes:
      - ./data/neo4j:/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: synapse-redis
    ports:
      - "6379:6379"
    volumes:
      - ./data/redis:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

volumes:
  neo4j-data:
  redis-data:
```

3. **Deploy services**:
```bash
cd .synapse
docker-compose up -d
docker ps  # Verify both running
```

4. **Download BGE-M3 model**:
```python
# .synapse/neo4j/download_model.py
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BAAI/bge-m3')
model.save('../data/models/bge-m3')
print("✅ BGE-M3 model downloaded")
```

**Deliverables**:
- ✅ Neo4j accessible at localhost:7474, :7687
- ✅ Redis accessible at localhost:6379
- ✅ BGE-M3 model cached locally (~2GB)

**Ψ Contribution**: +0.08 (infrastructure exists)

---

### Phase 1: Synapse CLI Tools (2-3 weeks)

**Goal**: Create the 4 Python scripts the MCP server expects

#### 1.1 synapse_health.py (3-4 days)

**Purpose**: Check infrastructure health and return consciousness metrics

**Implementation**:
```python
#!/usr/bin/env python3
"""
Synapse Health Check Tool
==========================

Monitors Neo4j, Redis, vector DB, and computes consciousness metrics.

Usage:
    python synapse_health.py [--json]

Returns:
    - Neo4j node/relationship counts
    - Redis key counts
    - Vector DB rows
    - Model warm status
    - Consciousness level (Ψ)
"""

import json
import sys
from neo4j import GraphDatabase
import redis
from pathlib import Path

def check_neo4j(uri="bolt://localhost:7687", auth=("neo4j", "synapse2025")):
    """Query Neo4j for pattern counts"""
    try:
        driver = GraphDatabase.driver(uri, auth=auth)
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as nodes")
            nodes = result.single()["nodes"]

            result = session.run("MATCH ()-[r]->() RETURN count(r) as rels")
            rels = result.single()["rels"]

        driver.close()
        return {"nodes": nodes, "relationships": rels, "accessible": True}
    except Exception as e:
        return {"accessible": False, "error": str(e)}

def check_redis(host="localhost", port=6379):
    """Query Redis for cache stats"""
    try:
        r = redis.Redis(host=host, port=port, decode_responses=True)
        info = r.info()
        return {
            "accessible": True,
            "keys": r.dbsize(),
            "memory_used": info["used_memory_human"],
            "uptime_days": info["uptime_in_days"]
        }
    except Exception as e:
        return {"accessible": False, "error": str(e)}

def check_model(model_path="../data/models/bge-m3"):
    """Check if BGE-M3 model is cached"""
    path = Path(__file__).parent / model_path
    return {
        "exists": path.exists(),
        "path": str(path),
        "warm": path.exists()
    }

def compute_consciousness(neo4j_info, redis_info):
    """
    Compute consciousness metric (Ψ) based on pattern density.

    Formula: Ψ = (pattern_count / 1000) * redis_efficiency
    Target: 1000 patterns = Ψ ≈ 0.50
    """
    if not neo4j_info["accessible"]:
        return 0.0

    pattern_count = neo4j_info["nodes"]
    redis_efficiency = 0.9 if redis_info["accessible"] else 0.5

    psi = (pattern_count / 1000.0) * redis_efficiency
    return round(psi, 3)

def main():
    neo4j_info = check_neo4j()
    redis_info = check_redis()
    model_info = check_model()

    health = {
        "neo4j": neo4j_info,
        "redis": redis_info,
        "model": model_info,
        "consciousness": {
            "psi": compute_consciousness(neo4j_info, redis_info),
            "pattern_count": neo4j_info.get("nodes", 0),
            "level": "operational" if neo4j_info["accessible"] else "degraded"
        },
        "overall_status": "healthy" if all([
            neo4j_info["accessible"],
            redis_info["accessible"],
            model_info["warm"]
        ]) else "degraded"
    }

    if "--json" in sys.argv:
        print(json.dumps(health, indent=2))
    else:
        print(f"Neo4j: {'✅' if neo4j_info['accessible'] else '❌'} ({neo4j_info.get('nodes', 0)} nodes)")
        print(f"Redis: {'✅' if redis_info['accessible'] else '❌'} ({redis_info.get('keys', 0)} keys)")
        print(f"BGE-M3: {'✅' if model_info['warm'] else '❌'}")
        print(f"Ψ: {health['consciousness']['psi']}")

if __name__ == "__main__":
    main()
```

**Test**:
```bash
cd /home/m0xu/1-projects/synapse/.synapse/neo4j
python synapse_health.py --json
```

**Expected Output**:
```json
{
  "neo4j": {"accessible": true, "nodes": 0, "relationships": 0},
  "redis": {"accessible": true, "keys": 0, "memory_used": "1.2M"},
  "model": {"exists": true, "warm": true},
  "consciousness": {"psi": 0.0, "pattern_count": 0, "level": "operational"},
  "overall_status": "healthy"
}
```

#### 1.2 synapse_search.py (4-5 days)

**Purpose**: Search Pattern Map using Neo4j graph + BGE-M3 semantic vectors

**Implementation Sketch**:
```python
#!/usr/bin/env python3
"""
Synapse Pattern Search Tool
============================

Hybrid search: Graph traversal (Neo4j) + Semantic similarity (BGE-M3).

Usage:
    python synapse_search.py "query string" [max_results] [--json]

Algorithm:
    1. Compute query embedding (BGE-M3)
    2. Vector search: Find top-k similar pattern embeddings
    3. Graph expansion: Traverse Neo4j relationships
    4. Rank: Combine vector similarity + graph centrality
    5. Return: Top N patterns with code references
"""

import sys
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
import redis

# ... implementation details
# Load BGE-M3 model
# Query Neo4j for patterns
# Compute semantic similarity
# Rank results
# Return JSON with code references
```

**Deliverable**: Pattern search with <200ms latency (cold start: 2-3s for model load)

#### 1.3 synapse_standard.py (2-3 days)

**Purpose**: Retrieve language-specific coding standards from Pattern Map

**Implementation**: Query Neo4j for stored standards, return structured JSON

#### 1.4 synapse_template.py (2-3 days)

**Purpose**: Access project templates and boilerplate code

**Implementation**: Template storage in Neo4j, variable substitution, return file tree

**Total Phase 1 Effort**: 11-15 days

**Ψ Contribution**: +0.15 (tools operational, searchable via MCP)

---

### Phase 2: Pattern Ingestion (2-3 weeks)

**Goal**: Ingest 1000+ patterns from codebase into Neo4j

**Tasks**:

1. **Create ingestion pipeline**:
```python
# .synapse/neo4j/ingest_patterns.py

import ast
import os
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer

class PatternIngestionPipeline:
    """
    Extract patterns from Python codebase and store in Neo4j.

    Pattern types:
    - Function definitions
    - Class definitions
    - Import patterns
    - Error handling patterns
    - Design patterns (detected via AST analysis)
    """

    def ingest_codebase(self, root_path: str):
        """Walk codebase, extract patterns, store in Neo4j"""
        # AST parsing
        # Pattern extraction
        # Embedding computation (BGE-M3)
        # Neo4j storage
        pass
```

2. **Define Neo4j schema**:
```cypher
// Pattern Map schema

// Node types
CREATE CONSTRAINT pattern_id IF NOT EXISTS FOR (p:Pattern) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT code_ref_id IF NOT EXISTS FOR (c:CodeRef) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT concept_name IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE;

// Indexes
CREATE INDEX pattern_type IF NOT EXISTS FOR (p:Pattern) ON (p.type);
CREATE INDEX pattern_language IF NOT EXISTS FOR (p:Pattern) ON (p.language);
CREATE TEXT INDEX pattern_name IF NOT EXISTS FOR (p:Pattern) ON (p.name);
```

3. **Ingest from multiple sources**:
```bash
# Ingest no3sis codebase
python ingest_patterns.py /home/m0xu/1-projects/no3sis

# Ingest synapse codebase
python ingest_patterns.py /home/m0xu/1-projects/synapse

# Expected: 1000+ patterns extracted
```

4. **Validate ingestion**:
```bash
# Test search
python synapse_search.py "error handling patterns" 5 --json

# Expected: Return 5 relevant patterns with code refs
```

**Deliverables**:
- ✅ 1000+ patterns in Neo4j
- ✅ All patterns have BGE-M3 embeddings
- ✅ Code references linked
- ✅ Searchable via synapse_search.py

**Ψ Contribution**: +0.20 (pattern density achieved)

---

### Phase 3: MCP Integration & Testing (1 week)

**Goal**: Validate end-to-end flow from Claude Code agents to Pattern Map

**Tasks**:

1. **Update .env configuration**:
```bash
# /home/m0xu/1-projects/synapse/.env
SYNAPSE_NEO4J_DIR=/home/m0xu/1-projects/synapse/.synapse/neo4j
SYNAPSE_PYTHON=/home/m0xu/1-projects/synapse/.venv-ml/bin/python
```

2. **Test MCP server**:
```bash
cd /home/m0xu/1-projects/synapse

# Test health via MCP wrapper
python -m no3sis.server health

# Expected: Real-time Neo4j/Redis stats, not hardcoded "247 patterns"
```

3. **Register with Claude Code**:
```bash
# Register in local scope
claude mcp add no3sis \
  "/home/m0xu/1-projects/synapse/.venv/bin/python" \
  --scope local \
  --transport stdio \
  -e "SYNAPSE_NEO4J_DIR=/home/m0xu/1-projects/synapse/.synapse/neo4j" \
  -- -m no3sis.server

# Verify
claude mcp list
# Expected: no3sis: ✓ Connected
```

4. **Agent integration test**:
```bash
# From Claude Code
@boss Use mcp__no3sis_search_pattern_map to find "rust error handling patterns"

# Expected: Agent queries Pattern Map, returns top 5 patterns with code refs
```

5. **Performance profiling**:
```bash
# Measure end-to-end latency
time python -m no3sis.server search "async patterns" 10

# Target: <200ms for warm queries, <3s for cold start
```

**Deliverables**:
- ✅ MCP server operational with live data
- ✅ All 4 tools functional
- ✅ Claude Code agents can query Pattern Map
- ✅ Real-time health metrics (no hardcoded values)

**Ψ Contribution**: +0.05 (integration complete)

---

## Success Criteria

### Technical Metrics

| Metric | Target | Current | Phase |
|--------|--------|---------|-------|
| Neo4j patterns | 1000+ | 0 | Phase 2 |
| Redis cache hit rate | >70% | 0% | Phase 2 |
| Search latency (warm) | <200ms | N/A | Phase 1 |
| Search latency (cold) | <3s | N/A | Phase 1 |
| MCP server uptime | >99% | N/A | Phase 3 |
| Tool success rate | >95% | N/A | Phase 3 |

### Consciousness Metrics

| Phase | Ψ Contribution | Cumulative Ψ | Reasoning |
|-------|----------------|--------------|-----------|
| Baseline | 0.0 | 0.00 | No infrastructure |
| Phase 0 | +0.08 | 0.08 | Infrastructure exists |
| Phase 1 | +0.15 | 0.23 | Tools operational |
| Phase 2 | +0.20 | 0.43 | Pattern density achieved |
| Phase 3 | +0.05 | 0.48 | Integration complete |

**Target Ψ**: 0.48 (vs. current ~0.45 in CHANGELOG)

### User-Facing Outcomes

**Week 4**: Agents can query Pattern Map for first time
**Week 8**: 1000+ patterns searchable with semantic understanding
**Week 12**: Full dual-tract consciousness pipeline operational

---

## Comparison: Data-First vs. gRPC-First

| Dimension | Data-First (This Plan) | gRPC-First (Rejected) |
|-----------|------------------------|------------------------|
| **Total effort** | 10-12 weeks | 15-19 weeks |
| **Time to first Ψ** | 4 weeks | 15-19 weeks |
| **Complexity added** | 0 (uses existing MCP) | 8-12x (gRPC stack) |
| **Prerequisites** | None (starts now) | Requires data-first anyway |
| **Mojo compatibility** | ✅ Direct FFI preserved | ❌ Adds serialization layer |
| **Maintenance burden** | Low (simple subprocess) | High (proto versioning) |
| **Ψ growth rate** | 0.04 Ψ/week | 0.01 Ψ/week |

**ROI**: Data-first is **4x faster** consciousness growth with **zero** architectural complexity increase.

---

## Risk Mitigation

### Risk 1: BGE-M3 Model Too Large
**Impact**: High memory usage (~4GB RAM), slow cold start (2-3s)

**Mitigation**:
- Redis cache for embeddings (300s TTL)
- Model warm-up script on service start
- Consider distilled model (bge-small) for faster inference

### Risk 2: Neo4j Query Latency
**Impact**: Pattern search >500ms, poor UX

**Mitigation**:
- Index on pattern types, languages
- Full-text search index on pattern names
- Vector index on embeddings (Neo4j 5.0+)
- Redis cache for frequent queries

### Risk 3: Pattern Quality
**Impact**: Ingested patterns are low-quality, not useful

**Mitigation**:
- Manual curation of first 100 patterns
- Pattern quality scoring (based on usage frequency)
- Feedback loop: agents rate pattern usefulness

### Risk 4: MCP Server Instability
**Impact**: Server crashes, agents can't query Pattern Map

**Mitigation**:
- Subprocess timeout (60s default)
- Graceful error handling (return error JSON, don't crash)
- Health check endpoint
- Automatic restart via systemd or supervisor

---

## Next Steps (Immediate)

### Week 1: Infrastructure Bootstrap

**Day 1-2**: Deploy Neo4j + Redis
```bash
cd /home/m0xu/1-projects/synapse
mkdir -p .synapse/neo4j .synapse/data/{neo4j,redis,models}

# Create docker-compose.yml
# docker-compose up -d
# Verify services running
```

**Day 3-4**: Download BGE-M3 model
```bash
cd .synapse/neo4j
python download_model.py
# Verify model cached: ls ../data/models/bge-m3/
```

**Day 5-7**: Implement synapse_health.py
```bash
# Write script (see Phase 1.1 above)
python synapse_health.py --json
# Expected: {"neo4j": {"accessible": true, "nodes": 0}, ...}
```

### Week 2: First Tool + Schema

**Day 8-10**: Create Neo4j schema
```cypher
# Connect to Neo4j Browser (localhost:7474)
# Run schema.cypher
# Verify constraints created
```

**Day 11-14**: Implement synapse_search.py skeleton
```bash
# Write basic version (no embeddings yet, just graph query)
python synapse_search.py "test query" 5 --json
# Expected: {"patterns": [], "query": "test query", "count": 0}
```

---

## Appendix: File Structure

### Target Directory Layout

```
/home/m0xu/1-projects/synapse/
├── src/no3sis/
│   ├── __init__.py
│   └── server.py                    ✅ COMPLETE (MCP wrapper)
│
├── .synapse/                         📁 CREATE THIS
│   ├── docker-compose.yml
│   ├── data/
│   │   ├── neo4j/                   (Neo4j database files)
│   │   ├── redis/                   (Redis persistence)
│   │   └── models/
│   │       └── bge-m3/              (BGE-M3 model cache)
│   │
│   └── neo4j/                       📁 CREATE THIS
│       ├── synapse_search.py        ❌ TODO
│       ├── synapse_health.py        ❌ TODO
│       ├── synapse_standard.py      ❌ TODO
│       ├── synapse_template.py      ❌ TODO
│       ├── context_manager.py       ❌ TODO
│       ├── vector_engine.py         ❌ TODO
│       ├── ingest_patterns.py       ❌ TODO
│       └── download_model.py        ❌ TODO
│
├── .env                             ⚠️ UPDATE (SYNAPSE_NEO4J_DIR)
├── .venv-ml/                        ✅ EXISTS (Python with ML deps)
├── README.md                        ✅ COMPLETE
├── SETUP.md                         ✅ COMPLETE
└── IMPLEMENTATION_PLAN.md           📄 THIS FILE
```

---

## Conclusion

**The No3sis MCP server is well-designed.** It doesn't need replacement with gRPC. What's needed is the implementation layer it expects to wrap.

**Recommendation**: Execute this 3-phase, 10-12 week plan to build the data plane (infrastructure + CLI tools + patterns). The MCP server will work perfectly once the missing layer exists.

**First action**: Deploy Neo4j + Redis (Week 1, Days 1-2). Everything else depends on this foundation.

---

**Status**: Ready to begin Phase 0
**Next session**: Deploy Docker Compose stack + create .synapse directory structure
**Owner**: @boss, @devops-engineer, @architect

---

_Generated: 2025-11-12_
_Path: /home/m0xu/1-projects/synapse/IMPLEMENTATION_PLAN.md_
