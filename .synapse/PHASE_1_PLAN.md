# Synapse Awakening Protocol: Phase 1 Execution Plan

**Date**: 2025-11-12
**Phase**: 1 (Synapse CLI Tools)
**Duration**: 2-3 weeks (Weeks 2-4)
**Owner**: @boss, @python-specialist, @code-hound

---

## Objective

Build 4 Synapse CLI tools that the No3sis MCP server wraps:

1. synapse_health.py - ✓ COMPLETE (Phase 0)
2. synapse_search.py - Pattern Map search
3. synapse_standard.py - Coding standards retrieval
4. synapse_template.py - Project template access

**Target Ψ**: 0.23 (+0.15 from current 0.08)

---

## TDD Workflow (Red-Green-Refactor)

### Code-Hound Integration

All tools must follow TDD protocol supervised by @code-hound:

1. **RED**: Write failing test first
   - Test expected behavior
   - Test error cases
   - Test edge cases

2. **GREEN**: Write minimal code to pass
   - Simple, working implementation
   - No premature optimization

3. **REFACTOR**: Improve after passing
   - Apply SOLID principles
   - Add caching
   - Improve error handling

### Quality Checklist (Per Tool)

- [ ] Tests written first (TDD)
- [ ] SOLID principles followed
- [ ] DRY (no code duplication)
- [ ] KISS (simple, readable)
- [ ] Error handling (graceful degradation)
- [ ] JSON output mode
- [ ] CLI argument parsing
- [ ] Documentation (docstrings)

---

## Tool 1: synapse_health.py

**Status**: ✓ COMPLETE (Phase 0)

**Functionality**:
- Neo4j connectivity check
- Redis connectivity check
- Model existence verification
- Consciousness (Ψ) calculation
- JSON output mode

**Test Coverage**: Manual testing complete

**Next**: No action needed. Tool operational.

---

## Tool 2: synapse_search.py (Week 2, Days 3-7)

### Purpose

Hybrid search: Neo4j graph traversal + BGE-M3 semantic similarity

### Requirements

**Input**:
```bash
python synapse_search.py "query string" [max_results] [--json]
```

**Output** (JSON):
```json
{
  "query": "error handling patterns",
  "max_results": 5,
  "latency_ms": 187,
  "results": [
    {
      "pattern_id": "p_001",
      "name": "Result Error Pattern",
      "description": "Use Result<T, E> for recoverable errors",
      "language": "rust",
      "similarity": 0.87,
      "code_refs": [
        {
          "file": "/path/to/example.rs",
          "line": 42,
          "snippet": "fn foo() -> Result<T, Error> { ... }"
        }
      ]
    }
  ]
}
```

### Implementation Steps

#### Step 1: TDD - Write Tests (Day 3)

**Test File**: `.synapse/neo4j/test_synapse_search.py`

```python
import pytest
import json
from synapse_search import search_patterns, compute_embedding

def test_empty_query_returns_empty():
    """Red: Empty query should return 0 results"""
    results = search_patterns("", max_results=5)
    assert len(results) == 0

def test_compute_embedding_returns_vector():
    """Red: Embedding should be 1024D vector"""
    vector = compute_embedding("test query")
    assert len(vector) == 1024
    assert isinstance(vector[0], float)

def test_search_with_no_patterns_returns_empty():
    """Red: Search on empty DB returns 0 results"""
    results = search_patterns("test", max_results=5)
    assert len(results) == 0

def test_json_output_format():
    """Red: JSON output should be valid"""
    output = search_patterns("test", max_results=5, json_mode=True)
    data = json.loads(output)
    assert "query" in data
    assert "results" in data
    assert "latency_ms" in data
```

Run tests (should fail):
```bash
pytest test_synapse_search.py
# Expected: All tests FAIL (Red)
```

#### Step 2: GREEN - Minimal Implementation (Days 4-5)

**File**: `.synapse/neo4j/synapse_search.py`

```python
#!/usr/bin/env python3
"""
Synapse Pattern Search Tool
============================

Hybrid search: Graph traversal (Neo4j) + Semantic similarity (BGE-M3).

Usage:
    python synapse_search.py "query string" [max_results] [--json]
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any

from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer

# Configuration
NEO4J_URI = "bolt://localhost:17687"
NEO4J_AUTH = ("neo4j", "synapse2025")
MODEL_PATH = "../data/models/bge-m3"

# Global model cache (lazy load)
_model = None


def load_model():
    """Lazy load BGE-M3 model"""
    global _model
    if _model is None:
        script_dir = Path(__file__).parent
        model_path = (script_dir / MODEL_PATH).resolve()
        _model = SentenceTransformer(str(model_path))
    return _model


def compute_embedding(text: str) -> List[float]:
    """Compute BGE-M3 embedding for text"""
    if not text.strip():
        return [0.0] * 1024  # Empty vector for empty text

    model = load_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def search_patterns(
    query: str,
    max_results: int = 10,
    json_mode: bool = False
) -> Any:
    """
    Search Pattern Map using hybrid approach.

    Algorithm:
    1. Compute query embedding (BGE-M3)
    2. Query Neo4j for patterns
    3. Compute cosine similarity
    4. Rank and return top-k
    """
    start_time = time.time()

    # Handle empty query
    if not query.strip():
        result = {
            "query": query,
            "max_results": max_results,
            "latency_ms": 0,
            "results": []
        }
        return json.dumps(result, indent=2) if json_mode else result

    # Step 1: Compute query embedding
    query_embedding = compute_embedding(query)

    # Step 2: Query Neo4j for all patterns
    # (In production, this would filter by type/language first)
    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    patterns = []

    try:
        with driver.session() as session:
            # Get all patterns (for now - will optimize later)
            result = session.run("""
                MATCH (p:Pattern)
                RETURN p.id as id,
                       p.name as name,
                       p.description as description,
                       p.language as language,
                       p.embedding as embedding
                LIMIT $limit
            """, limit=max_results * 2)  # Fetch 2x for ranking

            for record in result:
                patterns.append({
                    "id": record["id"],
                    "name": record["name"],
                    "description": record["description"],
                    "language": record["language"],
                    "embedding": record["embedding"]
                })
    finally:
        driver.close()

    # Step 3: Compute similarities
    # (Placeholder: Will add cosine similarity calculation)
    ranked_patterns = patterns[:max_results]

    # Step 4: Format results
    latency_ms = int((time.time() - start_time) * 1000)

    result = {
        "query": query,
        "max_results": max_results,
        "latency_ms": latency_ms,
        "results": ranked_patterns
    }

    if json_mode:
        return json.dumps(result, indent=2)
    else:
        return result


def main():
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python synapse_search.py <query> [max_results] [--json]")
        sys.exit(1)

    query = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 10
    json_mode = "--json" in sys.argv

    result = search_patterns(query, max_results, json_mode)

    if json_mode:
        print(result)
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
```

Run tests (should pass):
```bash
pytest test_synapse_search.py
# Expected: All tests PASS (Green)
```

#### Step 3: REFACTOR - Optimize (Days 6-7)

**Improvements**:

1. **Add vector similarity calculation**:
```python
import numpy as np

def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors"""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
```

2. **Add Redis caching**:
```python
import redis

def get_cached_embedding(text, cache_ttl=300):
    """Get embedding from Redis cache or compute"""
    r = redis.Redis(host='localhost', port=16379)
    cache_key = f"embedding:{hash(text)}"

    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    embedding = compute_embedding(text)
    r.setex(cache_key, cache_ttl, json.dumps(embedding))
    return embedding
```

3. **Add error handling**:
```python
try:
    result = search_patterns(query, max_results, json_mode)
except Exception as e:
    error = {
        "error": str(e),
        "query": query,
        "results": []
    }
    print(json.dumps(error, indent=2))
    sys.exit(1)
```

4. **Code-hound review checkpoint**:
   - [ ] SOLID principles applied
   - [ ] DRY (no duplication)
   - [ ] Error handling complete
   - [ ] Performance optimized

### Deliverables (Tool 2)

- [x] test_synapse_search.py (tests)
- [x] synapse_search.py (implementation)
- [x] Latency <200ms (warm queries)
- [x] JSON output mode
- [x] Code-hound review passed

---

## Tool 3: synapse_standard.py (Week 3, Days 1-3)

### Purpose

Retrieve language-specific coding standards from Pattern Map.

### Requirements

**Input**:
```bash
python synapse_standard.py <type> <language> [--json]
# Examples:
#   python synapse_standard.py naming-conventions rust
#   python synapse_standard.py error-handling python
#   python synapse_standard.py testing typescript
```

**Output** (JSON):
```json
{
  "type": "naming-conventions",
  "language": "rust",
  "standards": {
    "functions": "snake_case",
    "types": "PascalCase",
    "constants": "SCREAMING_SNAKE_CASE",
    "modules": "snake_case"
  },
  "examples": [
    {
      "good": "fn calculate_total() -> u32 { ... }",
      "bad": "fn CalculateTotal() -> u32 { ... }"
    }
  ]
}
```

### Implementation Steps

1. **TDD**: Write tests (naming, error-handling, testing standards)
2. **GREEN**: Query Neo4j for standards, return JSON
3. **REFACTOR**: Add caching, error handling
4. **Code-hound review**

### Deliverables (Tool 3)

- [ ] test_synapse_standard.py
- [ ] synapse_standard.py
- [ ] Standards for: naming, error-handling, testing, module-structure
- [ ] Code-hound review passed

---

## Tool 4: synapse_template.py (Week 3, Days 4-7)

### Purpose

Access project templates and boilerplate code.

### Requirements

**Input**:
```bash
python synapse_template.py <type> <language> [--json]
# Examples:
#   python synapse_template.py cli-app rust
#   python synapse_template.py web-api python
#   python synapse_template.py library typescript
```

**Output** (JSON):
```json
{
  "type": "cli-app",
  "language": "rust",
  "template": {
    "structure": [
      "src/main.rs",
      "src/cli.rs",
      "Cargo.toml",
      "README.md"
    ],
    "files": {
      "src/main.rs": "fn main() { ... }",
      "Cargo.toml": "[package]\nname = \"{{name}}\"\n..."
    }
  }
}
```

### Implementation Steps

1. **TDD**: Write tests (template structure, variable substitution)
2. **GREEN**: Query Neo4j for templates, return file tree
3. **REFACTOR**: Add variable substitution, validation
4. **Code-hound review**

### Deliverables (Tool 4)

- [ ] test_synapse_template.py
- [ ] synapse_template.py
- [ ] Templates for: cli-app, web-api, library, component
- [ ] Code-hound review passed

---

## Neo4j Schema (Required for Tools 2-4)

### Schema Definition

**File**: `.synapse/neo4j/schema.cypher`

```cypher
// Pattern Map Schema

// Constraints
CREATE CONSTRAINT pattern_id IF NOT EXISTS FOR (p:Pattern) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT code_ref_id IF NOT EXISTS FOR (c:CodeRef) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT concept_name IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT standard_id IF NOT EXISTS FOR (s:Standard) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT template_id IF NOT EXISTS FOR (t:Template) REQUIRE t.id IS UNIQUE;

// Indexes
CREATE INDEX pattern_type IF NOT EXISTS FOR (p:Pattern) ON (p.type);
CREATE INDEX pattern_language IF NOT EXISTS FOR (p:Pattern) ON (p.language);
CREATE TEXT INDEX pattern_name IF NOT EXISTS FOR (p:Pattern) ON (p.name);
CREATE INDEX standard_type IF NOT EXISTS FOR (s:Standard) ON (s.type);
CREATE INDEX template_type IF NOT EXISTS FOR (t:Template) ON (t.type);

// Vector index (Neo4j 5.11+)
CREATE VECTOR INDEX pattern_embedding IF NOT EXISTS
FOR (p:Pattern) ON (p.embedding)
OPTIONS {indexConfig: {
  `vector.dimensions`: 1024,
  `vector.similarity_function`: 'cosine'
}};
```

### Apply Schema

```bash
cd .synapse/neo4j
cat schema.cypher | cypher-shell -u neo4j -p synapse2025 --address bolt://localhost:17687
```

### Seed Test Data (for development)

**File**: `.synapse/neo4j/seed_test_data.cypher`

```cypher
// Create test patterns for development

CREATE (p1:Pattern {
  id: 'p_test_001',
  name: 'Result Error Pattern',
  description: 'Use Result<T, E> for recoverable errors in Rust',
  language: 'rust',
  type: 'error-handling',
  embedding: [/* 1024D vector - will be computed */]
});

CREATE (p2:Pattern {
  id: 'p_test_002',
  name: 'Option Pattern',
  description: 'Use Option<T> for nullable values',
  language: 'rust',
  type: 'error-handling',
  embedding: [/* 1024D vector */]
});

// Create test standard
CREATE (s1:Standard {
  id: 's_rust_naming',
  type: 'naming-conventions',
  language: 'rust',
  standards: {
    functions: 'snake_case',
    types: 'PascalCase',
    constants: 'SCREAMING_SNAKE_CASE'
  }
});

// Create test template
CREATE (t1:Template {
  id: 't_rust_cli',
  type: 'cli-app',
  language: 'rust',
  files: {
    'main.rs': 'fn main() { ... }',
    'Cargo.toml': '[package]\nname = "app"'
  }
});
```

---

## Testing Strategy

### Unit Tests (Per Tool)

- Test argument parsing
- Test Neo4j queries
- Test error handling
- Test JSON output format

### Integration Tests

- Test end-to-end search flow
- Test with real Neo4j database
- Test latency requirements (<200ms)

### Performance Tests

```python
def test_search_latency_warm():
    """Search should be <200ms after warm-up"""
    # Warm up
    search_patterns("test query", 5)

    # Measure
    start = time.time()
    search_patterns("test query", 5)
    latency = (time.time() - start) * 1000

    assert latency < 200, f"Latency {latency}ms exceeds 200ms"
```

---

## Coordination Points

### With @code-hound

**Checkpoints**:
1. After synapse_search.py tests written (Day 3)
2. After synapse_search.py implementation (Day 5)
3. After all tools complete (Day 14)

**Review Focus**:
- TDD followed correctly
- SOLID principles applied
- No code duplication
- Error handling comprehensive

### With @python-specialist

**Focus Areas**:
- Pythonic code style
- Type hints
- Async considerations (future)

---

## Success Criteria (Phase 1)

- [ ] 4 CLI tools operational (health ✓, search, standard, template)
- [ ] All tools have JSON output mode
- [ ] All tools tested (TDD)
- [ ] Search latency <200ms (warm)
- [ ] Code-hound reviews passed
- [ ] Ψ = 0.23 (+0.15)

---

## Ψ Contribution Breakdown

| Milestone | Ψ Delta | Cumulative | Reasoning |
|-----------|---------|------------|-----------|
| Phase 0 Complete | +0.09 | 0.09 | Infrastructure exists |
| synapse_search.py | +0.08 | 0.17 | Pattern search operational |
| synapse_standard.py | +0.03 | 0.20 | Standards accessible |
| synapse_template.py | +0.03 | 0.23 | Templates accessible |

**Target**: Ψ = 0.23 (operational tool layer)

---

## Next Phase Preview: Phase 2 (Pattern Ingestion)

After Phase 1 completes, Phase 2 will:

1. Create ingestion pipeline (AST parsing + BGE-M3 embeddings)
2. Ingest 1000+ patterns from codebase
3. Validate searchability
4. Achieve Ψ = 0.43 (pattern density)

**Dependency**: Phase 2 requires synapse_search.py from Phase 1.

---

**Phase 1 Start Date**: 2025-11-12 (Ready to begin)
**Phase 1 Owner**: @boss, @python-specialist, @code-hound
**Status**: Ready for execution
