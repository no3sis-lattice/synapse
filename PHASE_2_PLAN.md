# Phase 2 Execution Plan: Pattern Ingestion Pipeline

**Date**: 2025-11-13
**Status**: Planning Complete - Ready for Execution
**Estimated Duration**: 12-15 days
**Consciousness Growth**: Ψ 0.23 → 0.43 (+87%)

---

## Executive Summary

Phase 2 establishes the Pattern Map foundation through a pragmatic 5-stage pipeline: (1) Extract patterns from synapse codebase + curated open-source repos, (2) Score quality via composite metrics (complexity, SOLID, coverage), (3) Categorize via hybrid rule-ML taxonomy, (4) Ingest to Neo4j with embeddings/relationships, (5) Validate search efficacy. Estimated 12-15 days. Target: 1000+ patterns @ 70+ quality score, Ψ: 0.23→0.43. Risk: extraction complexity (mitigate via incremental scope). Start simple (Python AST), iterate to tree-sitter multi-language.

---

## Phase 1 Foundation (Completed)

**Achievement Summary**:
- ✅ 4/4 CLI tools operational (search, standard, template, health)
- ✅ 1,320 LOC implementation, 1,081 LOC tests
- ✅ 98% test coverage (53/54 tests passing)
- ✅ Quality progression: 85% → 88% → 95% → 100%
- ✅ Velocity improvement: 4.1x faster by Phase 1.4
- ✅ Current Ψ: 0.23 (48% of target achieved)

**Infrastructure Ready**:
- Neo4j graph database (operational)
- Redis cache (operational)
- BGE-M3 embeddings (operational)
- All CLI tools tested and working
- MCP server wrapper ready for integration

---

## Detailed Sub-Phases

### Phase 2.1: Pattern Extraction Tool
**Goal**: Extract 1000+ code patterns from source repositories
**Duration**: 3-4 days
**Dependencies**: None (can start immediately)

#### Pattern Definition

- **Code Pattern**: Reusable code structure (function, class, module) demonstrating best practice
- **Size Range**: 5-200 LOC (exclude trivial getters, massive monoliths)
- **Pattern Types**:
  - Implementation patterns (error handling, logging, config)
  - Architectural patterns (layering, dependency injection)
  - Testing patterns (fixtures, mocks, assertions)

#### Source Strategy (Priority Order)

1. **Synapse Codebase** (500 patterns)
   - `/home/m0xu/1-projects/synapse/src/` (Python modules)
   - `/home/m0xu/1-projects/synapse/tests/` (testing patterns)
   - High quality baseline (we control it)

2. **Curated Open-Source** (500+ patterns)
   - FastAPI (Python web patterns)
   - Tokio (Rust async patterns)
   - TypeScript stdlib (TS patterns)
   - Clone locally, extract patterns

3. **Manual Curation** (100+ patterns)
   - Design Patterns (Gang of Four) - code examples
   - Refactoring.guru examples
   - Bootstrap initially, automate later

#### Extraction Method

**Tool**: Python AST module (stdlib, no deps)

**Algorithm**:
1. Parse `.py` files → AST
2. Extract nodes: `FunctionDef`, `ClassDef`, `Module`
3. Filter by size (5-200 LOC)
4. Capture context: docstrings, decorators, type hints
5. Serialize to JSON schema

**JSON Schema Example**:
```json
{
  "id": "uuid4",
  "name": "validate_email_format",
  "language": "python",
  "type": "function",
  "code": "def validate_email_format(email: str) -> bool:\n    ...",
  "context": {
    "file": "src/utils/validation.py",
    "module": "utils.validation",
    "docstring": "Validates email using RFC 5322 regex",
    "decorators": ["@lru_cache"],
    "imports": ["re", "typing"]
  },
  "metadata": {
    "loc": 12,
    "extracted_at": "2025-11-13T10:00:00Z",
    "source_repo": "synapse",
    "commit_hash": "fdd6258"
  }
}
```

#### Deliverables

- `scripts/extract_patterns.py` (CLI tool)
  - Args: `--repo-path`, `--language`, `--output-json`
  - Batch processing (100 files/run)
- `data/patterns_raw.json` (1000+ patterns)
- Unit tests (pytest, 90%+ coverage)
- Documentation (usage, schema spec)

#### Open Questions

- **Q**: Extract from Git history (pattern evolution)?
  **Decision**: No (Phase 3 feature)

- **Q**: Multi-language (Rust/TS) now or later?
  **Decision**: Later (2.1 = Python only, simplicity)

---

### Phase 2.2: Quality Scoring System
**Goal**: Assign 0-100 quality score to each pattern
**Duration**: 2-3 days
**Dependencies**: 2.1 complete (needs extracted patterns)

#### Quality Dimensions (Weighted Composite)

| Metric | Weight | Tool | Range |
|--------|--------|------|-------|
| Complexity (Cognitive) | 25% | radon | 0-100 (inverse) |
| SOLID Compliance | 30% | Custom | 0-100 |
| Documentation | 20% | Custom | 0-100 |
| Test Coverage | 15% | coverage.py | 0-100 |
| Usage Frequency | 10% | AST grep | 0-100 |

#### Scoring Algorithm

```python
def calculate_quality_score(pattern: dict) -> float:
    """Composite quality score (0-100)"""

    # 1. Complexity (inverse - lower is better)
    cc = radon.complexity.cc_visit(pattern['code'])
    complexity_score = max(0, 100 - (cc.complexity * 5))  # CC 20 → score 0

    # 2. SOLID Compliance
    solid_score = check_solid_principles(pattern)  # Custom heuristics

    # 3. Documentation Quality
    doc_score = score_documentation(pattern['context']['docstring'])

    # 4. Test Coverage (if applicable)
    coverage_score = get_test_coverage(pattern['id'])  # From coverage.py

    # 5. Usage Frequency
    usage_score = count_pattern_usages(pattern) * 10  # 10 uses → score 100

    # Weighted composite
    return (
        complexity_score * 0.25 +
        solid_score * 0.30 +
        doc_score * 0.20 +
        coverage_score * 0.15 +
        usage_score * 0.10
    )
```

#### SOLID Heuristics (Rule-Based)

- **SRP**: Count responsibilities (< 3 = 100, 3-5 = 70, > 5 = 30)
  - Heuristic: Unique verb count in function names called
- **OCP**: Check for strategy/template pattern (abstract base)
- **LSP**: Verify subclass contracts (Liskov substitution)
- **ISP**: Interface size (< 5 methods = 100, > 10 = 50)
- **DIP**: Dependency on abstractions vs concrete (ABC ratio)

#### Documentation Scoring

- Has docstring: +40
- Has parameter docs: +20
- Has return docs: +15
- Has examples: +15
- Has type hints: +10

#### Quality Thresholds

- **Ingest**: Score ≥ 40 (minimum viable pattern)
- **Recommend**: Score ≥ 70 (high-quality pattern)
- **Featured**: Score ≥ 85 (exemplar pattern)

#### Deliverables

- `scripts/score_patterns.py` (CLI tool)
- `src/quality/scorer.py` (scoring logic)
- `data/patterns_scored.json` (patterns + scores)
- Unit tests (edge cases: empty code, no docs, etc.)
- Quality distribution report (histogram, percentiles)

#### Open Questions

- **Q**: ML-based scoring (train on human ratings)?
  **Decision**: Phase 3 (start rule-based)

- **Q**: Language-specific weights (Python vs Rust)?
  **Decision**: No (universal initially)

---

### Phase 2.3: Categorization System
**Goal**: Assign categories/tags to enable faceted search
**Duration**: 2 days
**Dependencies**: 2.2 complete (needs scored patterns)

#### Taxonomy Design (3-Tier Hierarchy)

**Level 1: Domain (WHERE used)**
- web (FastAPI, Flask, HTTP)
- data (pandas, SQL, ETL)
- cli (argparse, Click, rich)
- testing (pytest, fixtures, mocks)
- infrastructure (Docker, CI/CD, monitoring)
- core (algorithms, data structures, utilities)

**Level 2: Type (WHAT it is)**
- architectural (layering, microservices, event-driven)
- design (creational, structural, behavioral)
- implementation (error-handling, logging, config)
- testing (unit-test-patterns, integration-patterns)

**Level 3: Principle (WHY/HOW)**
- srp (Single Responsibility)
- ocp (Open/Closed)
- lsp (Liskov Substitution)
- isp (Interface Segregation)
- dip (Dependency Inversion)
- dry (Don't Repeat Yourself)
- kiss (Keep It Simple)

#### Classification Method (Hybrid)

1. **Rule-Based** (70% coverage):
   - Keyword matching: `"pytest.fixture"` → `testing/implementation`
   - Import analysis: `from fastapi import` → `web/architectural`
   - Decorator heuristics: `@dataclass` → `core/design`

2. **Embedding-Based** (30% coverage):
   - Generate BGE-M3 embedding for pattern
   - Find K-nearest neighbors in labeled seed data
   - Assign majority-vote category
   - Confidence threshold: 0.75 (else flag for manual review)

#### Seed Data Strategy

- Manually curate 100 patterns (10 per category)
- Use synapse codebase (we know the categories)
- Bootstrap ML classifier with high-confidence labels

#### Category Assignment Algorithm

```python
def categorize_pattern(pattern: dict, seed_patterns: list) -> dict:
    """Assign domain, type, principle tags"""

    # Rule-based (deterministic)
    domain = classify_by_imports(pattern['context']['imports'])
    type_ = classify_by_structure(pattern['type'])  # function/class/module

    # Embedding-based (probabilistic)
    embedding = generate_embedding(pattern['code'])
    neighbors = find_knn(embedding, seed_patterns, k=5)
    principle = majority_vote([n['principle'] for n in neighbors])
    confidence = max([n['similarity'] for n in neighbors])

    return {
        'domain': domain,
        'type': type_,
        'principle': principle if confidence > 0.75 else 'uncategorized',
        'confidence': confidence,
        'needs_review': confidence < 0.75
    }
```

#### Deliverables

- `scripts/categorize_patterns.py` (CLI tool)
- `src/categorization/classifier.py` (logic)
- `data/taxonomy.json` (category definitions)
- `data/seed_patterns.json` (100 manually labeled)
- `data/patterns_categorized.json` (all patterns + categories)
- Manual review queue (low-confidence patterns)

#### Open Questions

- **Q**: Multi-label (pattern belongs to 2+ categories)?
  **Decision**: Yes (use tags for multi-label)

- **Q**: Category evolution (new categories over time)?
  **Decision**: Phase 3 (fixed taxonomy initially)

---

### Phase 2.4: Neo4j Ingestion Pipeline
**Goal**: Load patterns into Neo4j with embeddings + relationships
**Duration**: 4-5 days
**Dependencies**: 2.3 complete (needs categorized patterns)

#### Neo4j Schema Design

**Node Types**:

```cypher
// Core entity
CREATE CONSTRAINT pattern_id IF NOT EXISTS FOR (p:Pattern) REQUIRE p.id IS UNIQUE;
CREATE INDEX pattern_name IF NOT EXISTS FOR (p:Pattern) ON (p.name);
CREATE INDEX pattern_quality IF NOT EXISTS FOR (p:Pattern) ON (p.quality_score);

(:Pattern {
  id: string,               // UUID
  name: string,             // "validate_email_format"
  code: string,             // Full source code
  description: string,      // From docstring
  quality_score: float,     // 0-100
  embedding: list[float],   // BGE-M3 (1024-dim)
  loc: int,                 // Lines of code
  created_at: datetime,
  language: string,         // Redundant (also relationship)
  source_repo: string,
  source_file: string
})

// Taxonomy nodes
(:Domain {name: string, description: string})      // web, data, cli, etc.
(:Type {name: string, description: string})        // architectural, design, etc.
(:Principle {name: string, description: string})   // srp, ocp, dry, etc.
(:Language {name: string, version: string})        // python, rust, typescript

// Metadata
(:Author {name: string, email: string})
(:Repository {url: string, name: string})
```

**Relationship Types**:

```cypher
// Categorization
(:Pattern)-[:IN_DOMAIN]->(:Domain)
(:Pattern)-[:OF_TYPE]->(:Type)
(:Pattern)-[:DEMONSTRATES]->(:Principle)
(:Pattern)-[:WRITTEN_IN]->(:Language)

// Provenance
(:Pattern)-[:AUTHORED_BY]->(:Author)
(:Pattern)-[:FROM_REPO]->(:Repository)

// Pattern-to-Pattern
(:Pattern)-[:DEPENDS_ON {type: string}]->(:Pattern)           // imports, calls
(:Pattern)-[:SIMILAR_TO {score: float}]->(:Pattern)          // cosine similarity
(:Pattern)-[:ALTERNATIVE_TO {context: string}]->(:Pattern)   // same problem, different approach
(:Pattern)-[:EXTENDS]->(:Pattern)                            // specialization
(:Pattern)-[:COMPOSES_WITH {rationale: string}]->(:Pattern)  // work well together
```

#### Ingestion Algorithm

```python
def ingest_patterns_to_neo4j(patterns: list[dict]):
    """Bulk ingestion with embeddings + relationship detection"""

    # 1. Create taxonomy nodes (one-time setup)
    create_taxonomy_nodes()

    # 2. Batch create pattern nodes
    for batch in chunk(patterns, 100):
        embeddings = generate_embeddings_batch([p['code'] for p in batch])

        tx.run("""
            UNWIND $patterns AS pattern
            CREATE (p:Pattern {
                id: pattern.id,
                name: pattern.name,
                code: pattern.code,
                quality_score: pattern.quality_score,
                embedding: pattern.embedding
            })
        """, patterns=[{**p, 'embedding': emb} for p, emb in zip(batch, embeddings)])

    # 3. Create categorization relationships
    create_categorization_relationships(patterns)

    # 4. Detect pattern dependencies (code analysis)
    detect_dependency_relationships(patterns)

    # 5. Compute similarity relationships (embedding-based)
    compute_similarity_graph(threshold=0.80)  # Only high-similarity edges

    # 6. Create vector index (for fast similarity search)
    tx.run("""
        CALL db.index.vector.createNodeIndex(
            'pattern_embeddings',
            'Pattern',
            'embedding',
            1024,
            'cosine'
        )
    """)
```

#### Relationship Detection

1. **DEPENDS_ON** (Static Analysis):
   - Parse imports: `from utils.validation import validate_email` → dependency edge
   - Parse function calls: AST analysis
   - Type: `import`, `call`, `inheritance`

2. **SIMILAR_TO** (Embedding-Based):
   - Compute pairwise cosine similarity (embeddings)
   - Create edge if similarity > 0.80 (high threshold)
   - Bidirectional relationship
   - Limit: Top-K=10 per pattern (avoid dense graph)

3. **ALTERNATIVE_TO** (Manual Curation - Phase 3):
   - Example: `sync_http_request` ↔ `async_http_request`
   - Requires domain knowledge
   - Start with empty, populate later

4. **EXTENDS** (Inheritance Analysis):
   - Detect subclass relationships: `class Child(Parent)`
   - Create edge: Child →[:EXTENDS]→ Parent

#### Deliverables

- `scripts/ingest_patterns.py` (CLI tool)
  - Args: `--input-json`, `--neo4j-uri`, `--batch-size`
- `src/ingestion/neo4j_loader.py` (logic)
- `cypher/schema.cypher` (DDL script)
- `cypher/indexes.cypher` (performance indexes)
- Ingestion report (node counts, relationship counts, errors)
- Validation queries (sample Cypher to verify data)

#### Open Questions

- **Q**: Incremental updates (add patterns without full reload)?
  **Decision**: Phase 3 (batch-only for Phase 2)

- **Q**: Relationship versioning (patterns change over time)?
  **Decision**: Phase 3

---

### Phase 2.5: Validation & Testing
**Goal**: Verify Pattern Map enables effective search + standards retrieval
**Duration**: 2-3 days
**Dependencies**: 2.4 complete (needs ingested data)

#### Validation Strategy (3 Tiers)

**1. Data Quality Tests**:
- [ ] Total patterns ≥ 1000
- [ ] Average quality score ≥ 70
- [ ] Zero patterns uncategorized (all have domain/type/principle)
- [ ] At least 50% of patterns have ≥1 relationship
- [ ] No orphan nodes (except seed taxonomy nodes)
- [ ] Embedding dimension = 1024 for all patterns
- [ ] No null fields (code, name, quality_score)

**2. Search Efficacy Tests** (via `synapse_search.py`):
```bash
# Test semantic search
synapse_search.py "error handling best practices" --max-results 10
# Expected: Patterns with try/except, logging, custom exceptions

synapse_search.py "dependency injection pattern" --max-results 5
# Expected: Patterns demonstrating DIP principle

synapse_search.py "async database queries" --max-results 10
# Expected: Patterns with async/await + DB connectors
```

**Success Criteria**:
- [ ] Top-3 results are relevant (manual review)
- [ ] Average similarity score ≥ 0.70 for top-5
- [ ] Query latency < 200ms (p95)
- [ ] Zero crashes on diverse queries

**3. Standards Retrieval Tests** (via `synapse_standard.py`):
```bash
# Test standards extraction
synapse_standard.py python
# Expected: Patterns demonstrating PEP 8, type hints, docstrings

synapse_standard.py rust
# Expected: Patterns using Result<T, E>, ownership patterns

synapse_standard.py testing python
# Expected: pytest patterns, fixtures, parametrize
```

**Success Criteria**:
- [ ] Returns ≥5 relevant patterns per query
- [ ] Patterns organized by quality score (descending)
- [ ] Includes pattern explanations (from docstrings)
- [ ] No duplicate patterns in results

#### Performance Benchmarks

| Query Type | Target Latency (p95) | Target Throughput |
|------------|----------------------|-------------------|
| Semantic Search (top-10) | < 200ms | > 50 qps |
| Standards Retrieval | < 150ms | > 100 qps |
| Pattern Lookup (by ID) | < 50ms | > 500 qps |
| Relationship Traversal | < 300ms | > 20 qps |

#### Load Testing

- Use `locust` or `k6` to simulate concurrent queries
- Target: 100 concurrent users, 10 qps each
- Verify Redis caching reduces Neo4j load (80%+ cache hit rate)

#### Deliverables

- `tests/integration/test_pattern_map.py` (data quality tests)
- `tests/integration/test_search_efficacy.py` (search tests)
- `tests/integration/test_performance.py` (latency benchmarks)
- Validation report (pass/fail for all criteria)
- Performance report (latency histograms, throughput metrics)
- User acceptance testing (manual evaluation of search results)

#### Open Questions

- **Q**: Define "relevance" formally (NDCG, precision@k)?
  **Decision**: Manual review initially (automate in Phase 3)

- **Q**: A/B test different similarity thresholds?
  **Decision**: No (fixed threshold = 0.70)

---

## Neo4j Schema (Complete Cypher DDL)

```cypher
// ============================================
// CONSTRAINTS & INDEXES
// ============================================

// Uniqueness constraints
CREATE CONSTRAINT pattern_id IF NOT EXISTS FOR (p:Pattern) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT domain_name IF NOT EXISTS FOR (d:Domain) REQUIRE d.name IS UNIQUE;
CREATE CONSTRAINT type_name IF NOT EXISTS FOR (t:Type) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT principle_name IF NOT EXISTS FOR (pr:Principle) REQUIRE pr.name IS UNIQUE;
CREATE CONSTRAINT language_name IF NOT EXISTS FOR (l:Language) REQUIRE l.name IS UNIQUE;
CREATE CONSTRAINT repo_url IF NOT EXISTS FOR (r:Repository) REQUIRE r.url IS UNIQUE;

// Lookup indexes
CREATE INDEX pattern_name IF NOT EXISTS FOR (p:Pattern) ON (p.name);
CREATE INDEX pattern_quality IF NOT EXISTS FOR (p:Pattern) ON (p.quality_score);
CREATE INDEX pattern_language IF NOT EXISTS FOR (p:Pattern) ON (p.language);
CREATE INDEX pattern_created IF NOT EXISTS FOR (p:Pattern) ON (p.created_at);

// Vector index (for similarity search)
CALL db.index.vector.createNodeIndex(
    'pattern_embeddings',
    'Pattern',
    'embedding',
    1024,
    'cosine'
) YIELD name, state
RETURN name, state;

// ============================================
// SEED TAXONOMY NODES
// ============================================

// Domains
MERGE (d1:Domain {name: 'web', description: 'Web frameworks, HTTP, REST, GraphQL'})
MERGE (d2:Domain {name: 'data', description: 'Data processing, ETL, databases, analytics'})
MERGE (d3:Domain {name: 'cli', description: 'Command-line interfaces, terminal tools'})
MERGE (d4:Domain {name: 'testing', description: 'Test frameworks, fixtures, mocks, assertions'})
MERGE (d5:Domain {name: 'infrastructure', description: 'DevOps, CI/CD, containers, monitoring'})
MERGE (d6:Domain {name: 'core', description: 'Algorithms, data structures, utilities'});

// Types
MERGE (t1:Type {name: 'architectural', description: 'System-level design patterns'})
MERGE (t2:Type {name: 'design', description: 'Object-oriented design patterns (GoF)'})
MERGE (t3:Type {name: 'implementation', description: 'Code-level patterns (error handling, logging)'})
MERGE (t4:Type {name: 'testing', description: 'Test patterns and strategies'});

// Principles
MERGE (pr1:Principle {name: 'srp', description: 'Single Responsibility Principle'})
MERGE (pr2:Principle {name: 'ocp', description: 'Open/Closed Principle'})
MERGE (pr3:Principle {name: 'lsp', description: 'Liskov Substitution Principle'})
MERGE (pr4:Principle {name: 'isp', description: 'Interface Segregation Principle'})
MERGE (pr5:Principle {name: 'dip', description: 'Dependency Inversion Principle'})
MERGE (pr6:Principle {name: 'dry', description: 'Don\'t Repeat Yourself'})
MERGE (pr7:Principle {name: 'kiss', description: 'Keep It Simple, Stupid'});

// Languages
MERGE (l1:Language {name: 'python', version: '3.11'})
MERGE (l2:Language {name: 'rust', version: '1.70'})
MERGE (l3:Language {name: 'typescript', version: '5.0'})
MERGE (l4:Language {name: 'go', version: '1.21'});

// ============================================
// USEFUL QUERIES
// ============================================

// Search by semantic similarity (vector search)
CALL db.index.vector.queryNodes(
    'pattern_embeddings',
    10,
    $query_embedding
) YIELD node, score
RETURN node.name, node.quality_score, score
ORDER BY score DESC;

// Find patterns demonstrating a principle
MATCH (p:Pattern)-[:DEMONSTRATES]->(pr:Principle {name: 'dip'})
WHERE p.quality_score >= 70
RETURN p.name, p.quality_score, p.description
ORDER BY p.quality_score DESC
LIMIT 10;

// Find related patterns (dependency graph)
MATCH (p:Pattern {name: 'validate_email_format'})-[:DEPENDS_ON*1..2]->(related:Pattern)
RETURN related.name, related.quality_score;

// Find similar patterns (high cosine similarity)
MATCH (p:Pattern {id: $pattern_id})-[s:SIMILAR_TO]->(similar:Pattern)
WHERE s.score >= 0.80
RETURN similar.name, s.score
ORDER BY s.score DESC;

// Statistics
MATCH (p:Pattern)
RETURN
    count(p) AS total_patterns,
    avg(p.quality_score) AS avg_quality,
    percentileCont(p.quality_score, 0.5) AS median_quality,
    percentileCont(p.quality_score, 0.95) AS p95_quality;

// Category distribution
MATCH (p:Pattern)-[:IN_DOMAIN]->(d:Domain)
RETURN d.name, count(p) AS pattern_count
ORDER BY pattern_count DESC;
```

---

## Success Criteria (Measurable KPIs)

### Quantitative Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| **Total Patterns** | ≥ 1000 | `MATCH (p:Pattern) RETURN count(p)` |
| **Avg Quality Score** | ≥ 70 | `MATCH (p:Pattern) RETURN avg(p.quality_score)` |
| **Categorization Coverage** | 100% | Zero patterns without domain/type/principle |
| **Relationship Density** | ≥ 50% | % of patterns with ≥1 outgoing relationship |
| **Search Relevance** | Top-3 @ 80%+ | Manual review (80% of queries return relevant top-3) |
| **Search Latency (p95)** | < 200ms | Performance testing (locust) |
| **Cache Hit Rate** | > 80% | Redis metrics (hits / (hits + misses)) |
| **Consciousness (Ψ)** | 0.43 | Pattern diversity × quality × connectivity |

### Qualitative Metrics

- [ ] **Search Utility**: Developers can find relevant patterns for common tasks
- [ ] **Standards Emergence**: Querying standards returns cohesive, actionable guidelines
- [ ] **Graph Connectivity**: Pattern relationships enable discovery
- [ ] **Documentation Quality**: Patterns include sufficient context

### Phase Transition Criteria

✅ **Phase 2 → Phase 3** when:
1. All 1000+ patterns ingested to Neo4j
2. Search queries return relevant results (manual validation)
3. Performance benchmarks met (< 200ms latency)
4. No critical bugs in ingestion pipeline
5. Ψ ≥ 0.40 (minimum threshold for Phase 3)

---

## Risk Mitigation Strategy

### Risk Matrix

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **R1: Extraction complexity** | High | Medium | Start Python-only, iterate to tree-sitter |
| **R2: Quality scoring subjectivity** | Medium | High | Define objective metrics, test on sample |
| **R3: Neo4j performance at scale** | High | Low | Index optimization, query profiling, Redis caching |
| **R4: Embedding generation bottleneck** | Medium | Medium | Batch processing (100 patterns/call), GPU acceleration |
| **R5: Insufficient pattern diversity** | High | Low | Curate from multiple repos (FastAPI, Tokio, stdlib) |
| **R6: Relationship detection accuracy** | Medium | Medium | Start with high-confidence (imports), manual review |
| **R7: Time estimation errors** | Low | High | Agile iteration, daily progress check-ins |

### Mitigation Details

**R1: Extraction Complexity**
- **Trigger**: AST parsing fails for complex Python syntax
- **Response**: Fallback to regex extraction, flag for manual review
- **Prevention**: Test on diverse codebases (synapse, FastAPI, pytest)

**R2: Quality Scoring Subjectivity**
- **Trigger**: Human disagreement on pattern quality (>20% variance)
- **Response**: Calibration session (3 reviewers score 50 patterns, adjust weights)
- **Prevention**: Document scoring rationale, automate objective metrics

**R3: Neo4j Performance**
- **Trigger**: Query latency > 500ms (p95)
- **Response**: Add indexes, optimize Cypher queries, increase Neo4j memory
- **Prevention**: Performance testing at 500 patterns, 1000 patterns

**R4: Embedding Generation Bottleneck**
- **Trigger**: BGE-M3 inference takes >10s per pattern
- **Response**: Batch processing (100 patterns → 1 GPU call), consider quantization
- **Prevention**: Benchmark on small batch (100 patterns), extrapolate to 1000

**R5: Insufficient Pattern Diversity**
- **Trigger**: All patterns from synapse codebase (limited domain coverage)
- **Response**: Expand to FastAPI (web), Tokio (Rust async), TypeScript stdlib
- **Prevention**: Define diversity metrics (language, domain, type distribution)

**R6: Relationship Detection Accuracy**
- **Trigger**: False positives (unrelated patterns marked as SIMILAR_TO)
- **Response**: Increase similarity threshold (0.80 → 0.85), manual review
- **Prevention**: Sample validation (review 50 relationships for accuracy)

---

## Timeline & Milestones

### Gantt Chart (12-15 days)

```
Phase 2.1: Pattern Extraction         [Days 1-4]    ████░░░░░░░░░░░
Phase 2.2: Quality Scoring             [Days 4-6]        ███░░░░░░░░░
Phase 2.3: Categorization              [Days 6-8]            ██░░░░░░░
Phase 2.4: Neo4j Ingestion             [Days 8-12]              █████░░
Phase 2.5: Validation & Testing        [Days 12-15]                 ███
```

### Milestone Deliverables

**M1: Extraction Complete** (Day 4)
- ✅ 1000+ patterns extracted to JSON
- ✅ Extraction tool tested (pytest)
- ✅ Documentation complete

**M2: Scoring Complete** (Day 6)
- ✅ All patterns scored (0-100)
- ✅ Quality distribution report
- ✅ Scoring logic tested

**M3: Categorization Complete** (Day 8)
- ✅ All patterns categorized (domain/type/principle)
- ✅ Seed data curated (100 patterns)
- ✅ Classification logic tested

**M4: Ingestion Complete** (Day 12)
- ✅ Patterns loaded to Neo4j
- ✅ Embeddings generated (BGE-M3)
- ✅ Relationships detected
- ✅ Schema validated

**M5: Validation Complete** (Day 15)
- ✅ All success criteria met
- ✅ Performance benchmarks passed
- ✅ Search efficacy validated
- ✅ Phase 2 complete 🎉

### Daily Progress Checkpoints

- **Daily**: Update progress log
- **Every 3 days**: Review metrics (patterns extracted, quality scores, latency)
- **Day 7**: Mid-phase review (adjust timeline if needed)
- **Day 15**: Final report (Ψ calculation, retrospective)

---

## Key Decisions (User Approval Required)

### Q1: Pattern Source Prioritization
**Question**: Which open-source repos to prioritize for extraction?

**Options**:
- A) FastAPI + Tokio + TypeScript stdlib (language diversity) ⭐ **RECOMMENDED**
- B) Django + Flask + Requests (Python web ecosystem depth)
- C) Manual curation from refactoring.guru (design patterns focus)

**Rationale**: Option A provides language diversity, aligns with multi-language agent goals

---

### Q2: Quality Score Weights
**Question**: Validate proposed quality metric weights?

**Proposed**: ⭐ **RECOMMENDED**
- Complexity: 25%
- SOLID: 30%
- Documentation: 20%
- Test Coverage: 15%
- Usage Frequency: 10%

**Alternative**: Equal weights (20% each) for simplicity

**Rationale**: SOLID priority aligns with CLAUDE.md axioms

---

### Q3: Categorization Confidence Threshold
**Question**: What confidence threshold for embedding-based categorization?

**Options**:
- A) 0.75 (conservative - more manual review) ⭐ **RECOMMENDED**
- B) 0.65 (balanced)
- C) 0.50 (aggressive - less manual review)

**Rationale**: Quality > quantity, align with Phase 1 standards

---

### Q4: Multi-Language Scope
**Question**: Expand to Rust/TypeScript in Phase 2, or defer to Phase 3?

**Options**:
- A) Python-only Phase 2 (simplicity, faster completion) ⭐ **RECOMMENDED**
- B) Python + Rust Phase 2 (leverage existing infrastructure)
- C) Python + Rust + TypeScript Phase 2 (full multi-language)

**Rationale**: KISS principle - validate pipeline with Python, scale to Rust/TS in Phase 3

---

### Q5: Relationship Similarity Threshold
**Question**: What cosine similarity threshold for SIMILAR_TO relationships?

**Options**:
- A) 0.90 (very conservative - sparse graph)
- B) 0.80 (balanced) ⭐ **RECOMMENDED**
- C) 0.70 (liberal - dense graph)

**Rationale**: Balance discoverability vs noise

---

### Q6: Manual Curation Effort
**Question**: How many patterns to manually curate (seed data)?

**Options**:
- A) 50 patterns (minimal viable)
- B) 100 patterns (recommended) ⭐ **RECOMMENDED**
- C) 200 patterns (high-quality seed)

**Rationale**: 10 patterns per category × 10 categories = 100

---

### Q7: Performance Testing Scope
**Question**: Load testing in Phase 2, or defer to Phase 3?

**Options**:
- A) Basic latency testing only (simple pytest)
- B) Load testing with locust (100 concurrent users) ⭐ **RECOMMENDED**
- C) Full stress testing (1000 users, chaos engineering)

**Rationale**: Validate performance before Phase 3 scaling

---

## Tool & Technology Stack

### Extraction Tools
- **Primary**: Python `ast` module (stdlib, zero deps)
- **Future**: `tree-sitter` (multi-language, Phase 3)
- **Fallback**: Regex extraction (complex syntax edge cases)

### Quality Metrics Tools
- **Complexity**: `radon` (cyclomatic, cognitive complexity)
- **SOLID**: Custom heuristics (rule-based initially)
- **Coverage**: `coverage.py` (already integrated in synapse)
- **Linting**: `pylint`, `flake8` (optional - Phase 3)

### Categorization Tools
- **Embeddings**: BGE-M3 (already integrated)
- **KNN**: `scikit-learn` (for nearest-neighbor classification)
- **Manual Review**: Custom CLI tool (`scripts/review_categories.py`)

### Neo4j Integration
- **Driver**: `neo4j` Python library (already using)
- **Schema Migration**: Cypher scripts (idempotent MERGE statements)
- **Bulk Ingestion**: Batch transactions (100 nodes/tx)
- **Monitoring**: Neo4j Browser + Prometheus metrics

### Testing Tools
- **Unit Tests**: `pytest` (already using)
- **Integration Tests**: `pytest` + Neo4j test fixtures
- **Performance Tests**: `locust` (HTTP load testing)
- **Coverage**: `coverage.py` (target: 90%+)

---

## Consciousness (Ψ) Calculation

**Phase 2 Target**: Ψ = 0.43 (↑ from 0.23)

**Formula**:
```
Ψ = λ·energy + (1-λ)·persistence
  = 0.6 · (patterns × quality × diversity) + 0.4 · (connectivity)
```

**Components**:
- **Patterns**: 1000+ (normalized to 0-1 scale)
- **Quality**: Avg score ≥ 70 (0.70)
- **Diversity**: Language × Domain × Type entropy (0.80 target)
- **Connectivity**: % patterns with ≥1 relationship (0.50 target)

**Calculation** (estimated):
```
energy = (1000/2000) × 0.70 × 0.80 = 0.28
persistence = 0.50
Ψ = 0.6 × 0.28 + 0.4 × 0.50 = 0.168 + 0.20 = 0.368
```

**Gap Analysis**: Target 0.43, projected 0.37 → need optimization:
- Increase quality (70 → 75): Ψ = 0.39
- Increase connectivity (50% → 60%): Ψ = 0.41
- Increase diversity (0.80 → 0.90): Ψ = 0.43 ✅

**Recommendation**: Prioritize diversity (extract from 3+ repos, not just synapse)

---

## Expected Outcomes

**After Phase 2 Completion**:
- 1000+ high-quality patterns in Neo4j Pattern Map
- Semantic search returns relevant results
- Standards retrieval provides actionable guidelines
- Pattern relationships enable discovery ("people who used this also used...")
- Consciousness (Ψ): 0.23 → 0.43 (+87% increase!)
- Ready for Phase 3 (MCP integration & deployment)

**Maintains Phase 1 Quality Standards**:
- TDD approach (tests first, RED-GREEN-REFACTOR)
- KISS principle (start simple, iterate to complexity)
- DRY compliance (reuse infrastructure from Phase 1)
- SOLID architecture (clean separation of concerns)
- 90%+ test coverage maintained

---

**Plan Status**: ✅ Ready for User Approval & Execution
**Generated**: 2025-11-13
**Path**: `/home/m0xu/1-projects/synapse/PHASE_2_PLAN.md`
