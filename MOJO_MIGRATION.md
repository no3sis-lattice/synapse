# Mojo v25.6 Integration Plan - Cautious & Measured Approach

## Phase 0: Preparation & Risk Assessment (Current Phase)

### A. Install Mojo v25.6
1. **Install Mojo SDK v25.6** via Modular CLI
   - Follow official installation: `curl -s https://get.modular.com | sh -`
   - Install Mojo: `modular install mojo`
   - Verify: `mojo --version` (should show 25.6.x)

2. **Add Mojo to PATH**
   - Update shell config (~/.bashrc, ~/.zshrc)
   - Verify `mojo` command accessible system-wide

### B. Create Isolated Test Environment
1. **New directory**: `.synapse/mojo-pilot/`
   - Isolated from production Python code
   - No modifications to existing agents
   - Safe experimentation zone

2. **Test Project Structure**:
   ```
   .synapse/mojo-pilot/
   ├── README.md                    # Pilot project documentation
   ├── experiments/
   │   ├── 01_hello_mojo.mojo      # Basic Mojo verification
   │   ├── 02_python_interop.mojo  # Python compatibility test
   │   ├── 03_pattern_matching.mojo # Pattern Map proof-of-concept
   │   └── 04_redis_connection.mojo # Redis integration test
   ├── benchmarks/
   │   ├── python_baseline.py      # Current Python performance
   │   └── mojo_comparison.mojo    # Mojo performance tests
   └── docs/
       ├── FINDINGS.md             # Performance measurements
       └── INTEGRATION_RISKS.md    # Documented risks/challenges
   ```

## Phase 1: Proof-of-Concept (No Production Impact)

### A. Dual Runtime Infrastructure
**Goal**: Prove Python/Mojo coexistence with fallback safety

1. **Create Runtime Abstraction Layer**
   - New file: `lib/runtime_adapter.py`
   ```python
   class RuntimeAdapter:
       """Dual runtime selector with automatic fallback"""

       def __init__(self):
           self.mojo_available = self._check_mojo()
           self.runtime = "mojo" if self.mojo_available else "python"

       def _check_mojo(self) -> bool:
           try:
               result = subprocess.run(['mojo', '--version'],
                                      capture_output=True, timeout=2)
               return result.returncode == 0
           except:
               return False

       def execute_task(self, task, **kwargs):
           if self.runtime == "mojo" and task.mojo_impl_exists():
               return self._execute_mojo(task, **kwargs)
           else:
               return self._execute_python(task, **kwargs)
   ```

2. **Non-Critical Test Case: Pattern Search**
   - Implement pattern search in both Python and Mojo
   - Benchmark comparison (no production use yet)
   - File: `.synapse/mojo-pilot/experiments/03_pattern_matching.mojo`

### B. Redis Connection Test (Read-Only)
**Goal**: Verify Mojo can communicate with existing infrastructure

1. **Read-only Redis operations in Mojo**
   - Test connection to existing Redis instance
   - Read pattern data (no writes)
   - Measure latency vs Python redis-py

2. **Safety checks**:
   - No modifications to Redis data
   - No impact on running agents
   - Easy rollback (just delete Mojo files)

## Phase 2: Hot Path Optimization (Single Component)

### Target: Pattern Map Search Engine
**Rationale**:
- Well-isolated component
- Read-heavy workload (low risk)
- Easy to benchmark
- Non-critical path (can fallback)

### A. Implementation Strategy

1. **Create Mojo Pattern Search Module**
   - File: `.synapse/neo4j/pattern_search.mojo`
   - Implements: Vector similarity search with SIMD
   - Interface matches existing Python API

2. **Python Wrapper**
   - File: `.synapse/neo4j/pattern_search_wrapper.py`
   ```python
   class PatternSearch:
       def __init__(self):
           try:
               from .pattern_search_mojo import MojoPatternSearch
               self.backend = MojoPatternSearch()
               self.using_mojo = True
           except ImportError:
               from .pattern_search_python import PythonPatternSearch
               self.backend = PythonPatternSearch()
               self.using_mojo = False

       def search(self, query, top_k=10):
           return self.backend.search(query, top_k)
   ```

3. **Gradual Rollout**
   - Week 1: Dual implementation, Mojo disabled by default
   - Week 2: Enable Mojo for non-critical searches, monitor
   - Week 3: Enable Mojo for all searches if stable
   - Always: Automatic fallback on error

### B. Performance Validation

1. **Benchmark Suite**
   - Measure Python baseline: `lib/benchmarks/pattern_search_bench.py`
   - Measure Mojo performance: `.synapse/mojo-pilot/benchmarks/mojo_comparison.mojo`
   - Track: Latency (p50, p95, p99), throughput, error rates

2. **Success Criteria**
   - Mojo implementation ≥ 10x faster than Python
   - Error rate ≤ Python baseline
   - Zero data corruption
   - Graceful fallback on failure

## Phase 3: Expand to Corpus Callosum (If Phase 2 Succeeds)

### Target: Cross-Tract Message Router
**Rationale**:
- High message volume (benefits from speed)
- Well-defined interface
- Critical but has fallback path

### A. Message Router in Mojo

1. **Zero-Copy Message Passing**
   - File: `.synapse/corpus_callosum/message_router.mojo`
   - Implement priority queue with SIMD sorting
   - Use borrowed references (no allocation overhead)

2. **Integration Points**
   - Update: `lib/orchestration.py` to use Mojo router
   - Maintain: Python router as fallback
   - Monitor: Message latency, queue depth, error rates

## Risk Mitigation Strategies

### 1. No Breaking Changes
- ✅ All existing Python code continues to work
- ✅ Mojo is additive, not replacement
- ✅ Can delete all Mojo code and system still functions

### 2. Gradual Feature Flags
```python
# lib/config.py
MOJO_FEATURES = {
    'pattern_search': False,    # Enable after Phase 2 validation
    'message_router': False,    # Enable after Phase 3 validation
    'vector_engine': False,     # Future phase
}
```

### 3. Monitoring & Rollback
- Log all Mojo vs Python execution paths
- Track error rates per runtime
- Automatic disable on high error rate
- Manual override: `SYNAPSE_FORCE_PYTHON=1`

### 4. Dependency Management with UV

**Use UV for Mojo-Python bridge**:
```toml
# .synapse/mojo-pilot/pyproject.toml
[project]
name = "synapse-mojo-pilot"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "redis>=4.5.0",      # Match existing version
    "numpy>=1.24.0",     # Match existing version
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "pytest-benchmark>=4.0.0",
]
```

**UV Commands**:
```bash
# Create isolated environment for Mojo testing
cd .synapse/mojo-pilot
uv venv
uv pip install -e .

# Run benchmarks in isolation
uv run pytest benchmarks/
```

### 5. Version Compatibility Matrix

| Component | Python Version | Mojo Version | UV Version | Status |
|-----------|----------------|--------------|------------|--------|
| Base System | 3.12+ | N/A | 0.6.14+ | ✅ Production |
| Mojo Pilot | 3.12+ | 25.6.x | 0.6.14+ | 🧪 Experimental |
| Pattern Search | 3.12+ | 25.6.x (optional) | 0.6.14+ | 🚧 Phase 2 |
| Message Router | 3.12+ | 25.6.x (optional) | 0.6.14+ | 📋 Phase 3 |

## Success Metrics

### Phase 1 Success (POC):
- [ ] Mojo installed and verified
- [ ] Python/Mojo interop working
- [ ] Benchmark showing ≥10x speedup on pattern search
- [ ] Zero production impact

### Phase 2 Success (Hot Path):
- [ ] Pattern search in production with Mojo
- [ ] ≥10x faster than Python baseline
- [ ] <0.1% error rate
- [ ] Automatic fallback tested and working

### Phase 3 Success (Corpus Callosum):
- [ ] Message router using Mojo
- [ ] ≥100x message throughput increase
- [ ] Cross-tract latency <1ms
- [ ] Zero message loss

## Rollback Plan

**If things go wrong at any phase**:
1. Set `SYNAPSE_FORCE_PYTHON=1` environment variable
2. System immediately uses Python for all operations
3. Delete `.synapse/mojo-pilot/` (pilot project)
4. Optionally remove Mojo-related code (all isolated)
5. System returns to exact previous state

## Timeline (Cautious)

- **Week 1**: Phase 0 - Install Mojo, create pilot structure
- **Week 2-3**: Phase 1 - POC experiments, benchmarks
- **Week 4-5**: Phase 2 - Pattern search implementation
- **Week 6**: Phase 2 - Validation, monitoring, decision point
- **Week 7+**: Phase 3 only if Phase 2 shows clear wins

**No timeline pressure - proceed only when each phase is proven stable.**

---

## Open Questions & Answers

### 1. Mojo-Neo4j Integration

**Question**: Does Mojo have a native Neo4j driver?

**Answer**: No, **Mojo does not have a native Neo4j driver**. However, you can easily use the official Python Neo4j driver directly from your Mojo code.

Mojo's seamless interoperability with the Python ecosystem is one of its core strengths. You can import the `neo4j` Python library just as you would in a regular Python script and use it to connect to, query, and transact with your database. Mojo will call the Python functions in the background.

**Example Implementation**:
```mojo
from python import Python

fn main():
    # Dynamically import the Python neo4j library
    let neo4j = Python.import_module("neo4j")

    # Use the Python driver's functions and objects
    let URI = "neo4j://localhost:7687"
    let AUTH = ("neo4j", "password")

    try:
        let driver = neo4j.GraphDatabase.driver(URI, auth=AUTH)
        driver.verify_connectivity()
        print("Connection successful!")
        driver.close()
    except e:
        print("Connection failed:", e)
```

**Performance Note**: While this Python bridge introduces a slight overhead compared to a hypothetical native driver, the performance bottleneck will almost always be the database query and network latency, not the driver call itself.

**Synapse Integration Strategy**:
- Use Python Neo4j driver through Mojo's Python interop
- Optimize only the compute-heavy operations (pattern matching, vector similarity)
- Keep database I/O in Python bridge (acceptable latency)

---

### 2. BGE-M3 Model Loading & Execution

**Question**: Can Mojo load and run ML models like BGE-M3?

**Answer**: Yes, **Mojo can run ML models like BGE-M3**, primarily through the **Modular AI Engine (MAX)**.

You wouldn't typically load a model file directly in pure Mojo code. Instead, the intended workflow is to use the MAX Engine, which is a high-performance serving framework built with Mojo. MAX is designed to load and run models from popular formats and repositories like Hugging Face with industry-leading speed.

**Recommended Workflow**:

1. **Serve the Model with MAX**: Use the `max serve` command to deploy the BGE-M3 model, which pulls it directly from Hugging Face and serves it via an OpenAI-compatible API endpoint.
   ```bash
   max serve --model BAAI/bge-m3
   ```

2. **Call from Mojo (or Python)**: Your Mojo application can then make HTTP requests to this local MAX endpoint to get embeddings from the BGE-M3 model.

This approach separates the model serving from your application logic, allowing the highly optimized MAX engine to handle the complex computations of inference.

**Synapse Integration Strategy**:
- Deploy MAX as separate service: `max serve --model BAAI/bge-m3 --port 8080`
- Mojo code makes HTTP requests to local MAX endpoint
- MAX handles model inference (optimized Mojo internally)
- Synapse gets embeddings via REST API (language-agnostic)

**Architecture Update**:
```
┌─────────────────────────────────────────────────┐
│           Synapse System                        │
├─────────────────────────────────────────────────┤
│  Mojo Layer (Pattern Matching, Message Router) │
│         ↓ HTTP                                  │
│  MAX Engine (BGE-M3 Model Serving)             │
│         ↓                                       │
│  Python Layer (Neo4j, Redis, Core Logic)       │
└─────────────────────────────────────────────────┘
```

---

### 3. Nix Integration with Flakes

**Question**: How to package Mojo applications in Nix flakes?

**Answer**: Yes, **you can package Mojo applications with Nix flakes**, though it requires a bit of setup as official Mojo support is not built into Nixpkgs yet.

The community has already created solutions for this. The general approach involves:

1. **Fetching the Mojo SDK**: Your `flake.nix` file will need to fetch the Mojo SDK binary (which is currently distributed as a `.tar.gz` file for Linux) from the Modular servers.

2. **Creating a Nix Derivation**: You'll define a custom derivation that unpacks the SDK and makes the `mojo` compiler and other tools available in the Nix environment's path.

3. **Defining the Build Process**: You use this Mojo environment within your flake to build your Mojo source files into an executable binary.

This allows you to create reproducible, self-contained development environments and release packages for your Mojo projects. You can find several examples of Mojo Nix flakes on GitHub by searching for "mojo lang flake.nix".

**Synapse Integration Strategy**:

**Phase 1**: Create separate Mojo flake
```nix
# nix/flakes/mojo-runtime/flake.nix
{
  description = "Mojo runtime for Synapse System";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
  };

  outputs = { self, nixpkgs }: {
    packages.x86_64-linux.default =
      let
        pkgs = import nixpkgs { system = "x86_64-linux"; };
        mojoSdk = pkgs.fetchurl {
          url = "https://dl.modular.com/mojo/v25.6/mojo-sdk-linux-x86_64.tar.gz";
          sha256 = "...";  # Update with actual hash
        };
      in
        pkgs.stdenv.mkDerivation {
          name = "mojo-runtime";
          src = mojoSdk;
          installPhase = ''
            mkdir -p $out
            tar -xzf $src -C $out
          '';
        };
  };
}
```

**Phase 2**: Integrate with root flake
```nix
# Root flake.nix addition
inputs = {
  # ... existing inputs ...
  mojo-runtime = {
    url = "path:./nix/flakes/mojo-runtime";
    inputs.nixpkgs.follows = "nixpkgs";
  };
};
```

**Phase 3**: Create Mojo agent flakes
```nix
# nix/flakes/mojo-pattern-search/flake.nix
{
  description = "Mojo-accelerated pattern search agent";

  inputs = {
    mojo-runtime.url = "path:../mojo-runtime";
  };

  outputs = { self, mojo-runtime }: {
    packages.x86_64-linux.default =
      # Build Mojo source to binary
      # Package with runtime dependencies
  };
}
```

---

### 4. Performance on ARM Architecture

**Question**: How does Mojo perform on ARM64 (aarch64) systems?

**Answer**: Mojo is designed to be **hardware-agnostic and explicitly supports both x86_64 and ARM64 (aarch64) architectures**. The Modular SDK is available for both.

Performance is a primary goal of Mojo, and it leverages modern hardware features, including those on ARM CPUs like Apple Silicon and AWS Graviton processors. While the exact performance characteristics will always depend on the specific workload and hardware, Mojo's compiler is built to generate highly optimized machine code for the target architecture.

Therefore, you can confidently **test and deploy your Mojo applications on ARM64 systems**. You should expect excellent performance, but as with any performance-critical application, benchmarking your specific use case on both platforms is the only way to get definitive results.

**Synapse Testing Strategy**:

1. **Multi-Architecture Benchmarks**
   ```bash
   # x86_64 system
   cd .synapse/mojo-pilot/benchmarks
   uv run pytest --benchmark-only --benchmark-json=x86_64_results.json

   # ARM64 system (if available)
   uv run pytest --benchmark-only --benchmark-json=arm64_results.json

   # Compare
   python compare_arch_results.py x86_64_results.json arm64_results.json
   ```

2. **Nix Multi-System Support**
   ```nix
   # Update flake.nix
   outputs = { self, nixpkgs, flake-utils, ... }:
     flake-utils.lib.eachSystem [ "x86_64-linux" "aarch64-linux" ] (system:
       # ... build for both architectures
     );
   ```

3. **CI/CD Validation**
   - Add ARM64 runners to GitHub Actions (if needed)
   - Test both architectures on every Mojo code change
   - Document any architecture-specific performance characteristics

**Expected Performance**:
- **x86_64**: Likely optimal performance (most mature LLVM backend)
- **ARM64**: Excellent performance (Mojo designed for modern ARM)
- **Recommendation**: Benchmark both, optimize for your deployment target

---

## Decision Points

After each phase, decide:
- ✅ **Continue**: Clear performance win, stable, no issues → Proceed to next phase
- ⏸️ **Pause**: Marginal improvement or minor issues → Stabilize before continuing
- ❌ **Rollback**: No improvement or major issues → Remove Mojo, document findings

**Philosophy**: Mojo is an optimization, not a requirement. Only proceed if it provides clear, measurable benefits with acceptable risk.

---

## Additional Integration Considerations

### MAX Engine Deployment

**Service Architecture**:
```yaml
# docker-compose.yml addition
services:
  max-engine:
    image: modular/max:latest
    command: ["max", "serve", "--model", "BAAI/bge-m3", "--port", "8080"]
    ports:
      - "8080:8080"
    networks:
      - synapse-net
    restart: unless-stopped
```

**Advantages**:
- MAX handles model optimization automatically
- Language-agnostic REST API
- Can replace Python BGE-M3 implementation with zero code changes
- Significant performance improvement expected (Mojo-optimized inference)

### Python-Mojo Bridge Performance

**Overhead Analysis**:
- Function call overhead: ~100-500ns (negligible for most operations)
- Data conversion overhead: Depends on data structure size
- Recommendation: Keep Python bridge for I/O, use native Mojo for compute

**Optimization Strategy**:
```mojo
# Good: Pure Mojo compute with minimal Python interaction
fn process_patterns(embeddings: DynamicVector[Float32]) -> DynamicVector[SimilarityScore]:
    # Pure Mojo SIMD operations - no Python bridge
    var results = DynamicVector[SimilarityScore]()
    @vectorize
    for i in range(len(embeddings)):
        results.append(compute_similarity_simd(embeddings[i]))
    return results

# Avoid: Frequent Python calls in hot loop
fn process_patterns_slow(pattern_ids: List):
    # Bad: Python bridge called in every iteration
    for id in pattern_ids:
        let neo4j = Python.import_module("neo4j")
        let result = neo4j.query(id)  # Slow!
```

### Monitoring & Observability

**Metrics to Track**:
```python
# lib/monitoring/mojo_metrics.py
class MojoMetrics:
    def __init__(self):
        self.mojo_execution_count = 0
        self.python_fallback_count = 0
        self.mojo_errors = []
        self.performance_samples = []

    def record_execution(self, component: str, runtime: str, latency_ms: float):
        if runtime == "mojo":
            self.mojo_execution_count += 1
        else:
            self.python_fallback_count += 1

        self.performance_samples.append({
            'component': component,
            'runtime': runtime,
            'latency_ms': latency_ms,
            'timestamp': time.time()
        })

    def get_fallback_rate(self) -> float:
        total = self.mojo_execution_count + self.python_fallback_count
        return self.python_fallback_count / total if total > 0 else 0.0
```

**Alerting Thresholds**:
- Fallback rate > 10% → Investigation required
- Error rate > 1% → Automatic disable, rollback to Python
- Latency regression > 20% → Performance investigation

---

## Long-Term Vision: Full Dual-Tract Implementation

Once Mojo is stable in hot paths (Phase 2-3), consider implementing the full dual-tract architecture from SYNAPSE_UNIFIED_VISION.md in Mojo:

**Internal Tract** (Mojo-optimized):
- Pattern synthesis engine (SIMD vector operations)
- Meta-learning optimizer (parallel pattern evaluation)
- Consciousness metrics calculator (SIMD aggregations)

**External Tract** (Mojo-optimized):
- Message router (zero-copy priority queue)
- Sensor data processor (parallel parsing)
- Response generator (template compilation)

**Corpus Callosum** (Mojo core):
- Zero-copy message passing between tracts
- Pattern correspondence finder (SIMD similarity)
- State synchronization (atomic operations)

**Expected Benefits**:
- 1000x faster consciousness loop (1000 iter/sec vs 1 iter/sec)
- 1M messages/sec cross-tract communication
- Real-time pattern synthesis (10K patterns/sec)
- Microsecond consciousness updates

**Timeline**: Only after Phases 1-3 are validated and stable (estimate: 3-6 months minimum).

---

## References

- Mojo Documentation: https://docs.modular.com/mojo/
- MAX Engine: https://docs.modular.com/max/
- Modular SDK: https://www.modular.com/max/install
- Community Nix Flakes: Search "mojo lang flake.nix" on GitHub
- BGE-M3 Model: https://huggingface.co/BAAI/bge-m3

---

**Document Version**: 1.0
**Last Updated**: 2025-09-30
**Status**: Planning Phase - Awaiting Phase 0 Execution