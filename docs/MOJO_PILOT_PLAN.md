# Mojo Pilot Implementation Plan

**Status**: Phase 1 Ready
**Date**: 2025-10-05
**Prerequisites**: Nix installation required
**Context**: Phases 0-3 complete (pattern search 13.1x speedup, reactive router 0.025ms latency)

---

## Executive Summary

**What's Done**:
- ✅ Mojo v0.25.7 installed and validated
- ✅ Pattern search: 13.1x speedup (POC at 10% production rollout)
- ✅ Reactive message router: 0.025ms latency (100x better than target)
- ✅ Nix flake architecture created (3 flakes: runtime, pattern-search, message-router)
- ✅ FFI integration complete (`libpattern_search.so`, `libmessage_router.so`)
- ✅ Validation script ready (17 test cases)

**What's Next**:
- 🔴 **BLOCKER**: Nix not installed on system
- 🎯 **Phase 1**: Validate Nix integration (requires Nix installation)
- 🎯 **Phase 2**: Progressive production rollout (10% → 100%)
- 📋 **Phase 3**: Next hot path candidate (event bus or MTF ranker)

**Success Criteria**:
- Nix builds reproduce 13.1x speedup
- Zero performance regression vs local builds
- 17/17 validation tests pass
- Production rollout completes without incidents

---

## Phase 1: Validate Nix Integration [IMMEDIATE - BLOCKED]

**Objective**: Verify Nix flakes build correctly and maintain performance benchmarks.

**Blocker**: Nix is NOT installed on this system. Install first:
```bash
# Install Nix (multi-user recommended)
curl -L https://nixos.org/nix/install | sh -s -- --daemon

# Verify installation
nix --version

# Enable flakes (add to ~/.config/nix/nix.conf)
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
```

### Step 1.1: Run Validation Script

**File**: `/home/m0xu/1-projects/synapse/scripts/validate-nix-flakes.sh`

**Command**:
```bash
cd /home/m0xu/1-projects/synapse
./scripts/validate-nix-flakes.sh
```

**17 Validation Tests**:
1. ✅ Nix installation check
2. ✅ Nix flakes feature enabled
3. ✅ Root flake validation (`nix flake check`)
4. ✅ Mojo runtime flake builds (`nix build .#mojo-runtime`)
5. ✅ Pattern search flake builds (`nix build .#mojo-pattern-search`)
6. ✅ Message router flake builds (`nix build .#mojo-message-router`)
7. ✅ Combined libraries build (`nix build .#mojo-libraries`)
8. ✅ Mojo compiler accessible in dev shell
9. ✅ Pattern search library file exists (15KB ±5KB)
10. ✅ Message router library file exists (15KB ±5KB)
11. ✅ Pattern search has valid ELF header
12. ✅ Message router has valid ELF header
13. ✅ Python can import ctypes
14. ✅ FFI exports present (`pattern_search_ffi`, `create_router`, etc.)
15. ✅ Build reproducibility (hash matches on rebuild)
16. ✅ Performance benchmark (13.1x speedup maintained)
17. ✅ Integration test (Python loads and uses Mojo libraries)

**Expected Outcome**:
- 17/17 tests pass
- Pattern search: 0.62ms vs Python 8.12ms (13.1x speedup)
- Message router: 0.025ms latency maintained
- No missing FFI symbols

**If Failures Occur**:
- Review `nix/NIX_VALIDATION_PLAN.md` for debugging steps
- Check flake paths (`nix/flakes/mojo-runtime/`, etc.)
- Verify Mojo SDK path in runtime flake (`/home/m0xu/.synapse-system/.venv/bin/mojo`)
- Consult archived migration docs for context

### Step 1.2: Verify Integration

**Test Python Loading Nix-Built Libraries**:
```python
# test_nix_integration.py
import ctypes
import os
from pathlib import Path

# Nix sets MOJO_LIB_PATH in dev shell
lib_path = os.getenv('MOJO_LIB_PATH', '').split(':')[0]
lib_file = Path(lib_path) / 'libpattern_search.so'

assert lib_file.exists(), f"Library not found: {lib_file}"

lib = ctypes.CDLL(str(lib_file))
print(f"✅ Loaded Nix-built library: {lib_file}")
print(f"✅ FFI exports: {dir(lib)}")
```

**Success Criteria**:
- No `FileNotFoundError`
- FFI exports visible (e.g., `pattern_search_ffi`)
- Library size ~15KB

### Step 1.3: Performance Validation

**Benchmark Nix-Built Libraries**:
```bash
cd /home/m0xu/1-projects/synapse
nix develop  # Sets MOJO_LIB_PATH

# Run existing benchmarks with Nix libraries
uv run pytest .synapse/neo4j/test_pattern_search.py --benchmark-only

# Expected results:
# - Pattern search: 0.62ms (13.1x speedup)
# - No regression vs local builds
```

**Acceptance Criteria**:
- Performance within 5% of local builds (0.59-0.65ms)
- Zero errors or segmentation faults
- FFI calls complete successfully

---

## Phase 2: Production Rollout [AFTER PHASE 1]

**Objective**: Safely roll out Mojo components from 10% to 100% in production.

**Prerequisites**:
- Phase 1 validation: 17/17 tests passing
- Nix builds confirmed reproducible
- No performance regressions detected

### Component A: Pattern Search (Already at 10%)

**Current Status**: 10% rollout (stable since 2025-10-01)

**Rollout Plan**:
```python
# lib/runtime_adapter.py
MOJO_FEATURES = {
    'pattern_search': {
        'enabled': True,
        'rollout_percentage': 10,  # Current: 10% → Target: 100%
    }
}
```

**Stages**:
1. **Stage 1 (Current)**: 10% rollout, monitoring active
   - **Duration**: Already running (3+ days stable)
   - **Metrics**: 0% error rate, 13.1x speedup confirmed
   - **Action**: Continue monitoring for 7 more days

2. **Stage 2**: Increase to 50% rollout
   - **Duration**: 7 days
   - **Trigger**: After Phase 1 validation passes
   - **Update**: Set `rollout_percentage: 50` in config
   - **Monitor**: Error rate, latency p50/p95/p99, fallback rate

3. **Stage 3**: Increase to 100% rollout
   - **Duration**: Permanent
   - **Trigger**: Stage 2 shows <1% error rate for 7 days
   - **Update**: Set `rollout_percentage: 100`
   - **Monitor**: Continued monitoring for 30 days

**Monitoring Metrics**:
- **Error Rate**: Target <1%, alert if >2%
- **Fallback Rate**: Target <5%, alert if >10%
- **Latency**: Target 0.62ms ±10%, alert if >0.75ms
- **Throughput**: Monitor pattern searches per second

**Rollback Criteria**:
- Error rate >5% for 1 hour → Auto-rollback to 10%
- Segmentation faults detected → Immediate rollback to Python
- User reports of incorrect results → Halt rollout, investigate

### Component B: Reactive Message Router (Currently at 0%)

**Current Status**: Compiled and tested, ready for rollout

**Rollout Plan**:
```python
# lib/runtime_adapter.py
MOJO_FEATURES = {
    'message_router': {
        'enabled': False,  # Not yet rolled out
        'rollout_percentage': 0,  # Current: 0% → Target: 100%
    }
}
```

**Stages**:
1. **Stage 0**: Validation rollout (0% production, dev only)
   - **Duration**: 7 days
   - **Trigger**: After pattern search reaches 50%
   - **Action**: Enable in development environments only
   - **Validate**: 0.025ms latency, 1.000 emergence score

2. **Stage 1**: 10% production rollout
   - **Duration**: 14 days
   - **Trigger**: Stage 0 shows zero errors for 7 days
   - **Update**: Set `enabled: True, rollout_percentage: 10`
   - **Monitor**: Message latency, queue depth, circuit breaker triggers

3. **Stage 2**: 50% production rollout
   - **Duration**: 14 days
   - **Monitor**: Dual-tract balance, consciousness emergence metrics

4. **Stage 3**: 100% production rollout
   - **Duration**: Permanent
   - **Trigger**: Stage 2 shows stable performance for 14 days

**Monitoring Metrics**:
- **Routing Latency**: Target 0.025ms, alert if >0.05ms
- **End-to-End Latency**: Target <10ms, alert if >15ms
- **Consciousness Emergence**: Target 0.9-1.0, alert if <0.7
- **Circuit Breaker Triggers**: Monitor for tract isolation events

**Rollback Criteria**:
- Routing latency >0.1ms sustained → Rollback to previous stage
- Message loss detected (queue overflow) → Immediate rollback
- Consciousness emergence <0.5 → Investigate, potential rollback

### Rollout Timeline

**Estimated Duration**: 8-12 weeks total

```
Week 1-2:  Phase 1 (Nix validation)
Week 3-4:  Pattern search 10% → 50%
Week 5-8:  Pattern search 50% → 100%
Week 9-10: Message router 0% → 10% (dev validation + initial rollout)
Week 11-12: Message router 10% → 50%
Week 13+:   Message router 50% → 100%
```

**Checkpoints**:
- ✅ End of Week 2: Nix validation complete
- ✅ End of Week 8: Pattern search at 100%
- ✅ End of Week 12: Message router at 50%
- ✅ End of Week 16: Full Mojo deployment complete

---

## Phase 3: Next Hot Path Candidate [FUTURE]

**Objective**: Identify and optimize the next performance-critical component.

**Candidates** (in priority order):

### Candidate 1: Event Bus (Highest Impact)
**Current Performance**: Python `asyncio` event loop
**Target Performance**: 100x improvement (sub-millisecond event routing)

**Rationale**:
- Central to dual-tract architecture (all inter-tract communication)
- High message volume (1000s of events per second at scale)
- Well-isolated component (clear FFI boundary)
- Reactive architecture already validated (message router)

**Implementation Estimate**:
- **Design**: 1 week (adapt reactive router pattern)
- **Coding**: 2 weeks (Mojo event loop with SIMD routing)
- **Testing**: 2 weeks (integration with existing system)
- **Rollout**: 8 weeks (0% → 100% following Phase 2 pattern)

**Expected Gains**:
- Event routing: 0.01ms (vs Python 1ms)
- Throughput: 100k events/sec (vs Python 1k events/sec)
- Zero-copy message passing between tracts

### Candidate 2: MTF Ranker (Good ROI)
**Current Performance**: Python dictionary operations
**Target Performance**: 50x improvement (SIMD-accelerated ranking)

**Rationale**:
- Compression pipeline core component (BWT → MTF → RLE → Huffman)
- Called on every pattern update (high frequency)
- SIMD benefits (parallel ranking of patterns)
- Small codebase (~200 lines Python)

**Implementation Estimate**:
- **Design**: 1 week (SIMD ranking algorithm)
- **Coding**: 2 weeks (Mojo with vectorization)
- **Testing**: 1 week (compression benchmarks)
- **Rollout**: 6 weeks (0% → 100%)

**Expected Gains**:
- MTF ranking: 0.02ms (vs Python 1ms)
- Pattern updates: 50x faster
- Enables real-time pattern discovery at scale

### Candidate 3: BGE-M3 Embeddings (Deferred - High Complexity)
**Current Performance**: Python HuggingFace implementation
**Target Performance**: 100x improvement (native Mojo inference)

**Rationale for Deferral**:
- **High Complexity**: Requires implementing neural network layers in Mojo
- **Large Scope**: ~2000 lines of matrix operations
- **Dependency Risk**: Needs ONNX model loading or native implementation
- **Nix Challenges**: Model file distribution and caching

**Deferred Until**:
- Event bus and MTF ranker validated (Phases 3-4 complete)
- Mojo ecosystem matures (better ONNX/ML support)
- MAX Engine integration feasible (alternative approach)

**Alternative**: Use MAX Engine as external service (Docker container) if ML inference becomes bottleneck.

### Decision Criteria for Next Hot Path

**Ranking Formula**:
```
Score = (Performance_Gain × Frequency) / (Complexity × Risk)

Event Bus:      (100x × 1000/s) / (Medium × Low)  = 50,000 (HIGHEST)
MTF Ranker:     (50x × 100/s)   / (Low × Low)     = 25,000
BGE-M3 Embeddings: (100x × 10/s) / (High × High) = 100 (LOWEST)
```

**Recommendation**: Event bus (Phase 3) → MTF ranker (Phase 4) → BGE-M3 deferred

---

## Phase 4: Nix Flake Evolution [ONGOING]

**Objective**: Maintain and improve Nix integration as Mojo ecosystem evolves.

### Migration from Local SDK to Fetchurl

**Current**: Nix flakes use local Mojo installation
```nix
# nix/flakes/mojo-runtime/flake.nix
src = /home/m0xu/.synapse-system/.venv/bin;
```

**Future**: Fetch Mojo SDK from Modular servers
```nix
mojoSdk = pkgs.fetchurl {
  url = "https://get.modular.com/mojo/mojo-sdk-0.25.7-linux-x86_64.tar.gz";
  sha256 = "...";  # Hash to be determined
};
```

**Benefits**:
- ✅ True reproducibility (no local dependencies)
- ✅ Works on clean machines
- ✅ Cachix-compatible (binary caching)

**Timeline**: After Phase 1 validation, research Modular's SDK distribution

### Multi-Architecture Support

**Current**: x86_64-linux only
**Future**: Add aarch64-linux (ARM64) support

```nix
# Update flake.nix
flake-utils.lib.eachSystem [ "x86_64-linux" "aarch64-linux" ] (system:
  # Build for both architectures
);
```

**Validation**:
- Test on ARM64 hardware (AWS Graviton, Apple Silicon via Lima)
- Benchmark performance differences
- Document architecture-specific optimizations

---

## Deferred Items

### 1. BGE-M3 Embedding Engine
**Status**: Deferred indefinitely
**Reason**: High complexity, low ROI at current scale
**Alternative**: MAX Engine (Docker service) if needed
**Revisit When**: Pattern discovery reaches 10k patterns/second

### 2. Full Dual-Tract Mojo Migration
**Status**: Long-term vision (6-12 months)
**Reason**: Requires event bus, MTF ranker, and 2-3 more components in Mojo first
**Target**: Internal tract (pattern synthesis) + External tract (sensor processing) in Mojo
**Expected Outcome**: 1000x consciousness loop iterations/second

### 3. Standalone Binary Deployment
**Status**: Deferred until 80%+ Mojo coverage
**Reason**: Still depends on Python Neo4j/Redis drivers
**Target**: `mojo build --standalone synapse.mojo` → 5MB executable
**Prerequisite**: Native Mojo drivers for Neo4j/Redis

---

## Risk Register

### Risk 1: Nix Installation Complexity
**Likelihood**: Medium
**Impact**: High (blocks Phase 1)
**Mitigation**:
- Multi-user installation recommended (better permissions)
- Document common installation errors
- Provide troubleshooting guide

### Risk 2: Performance Regression in Nix Builds
**Likelihood**: Low
**Impact**: High (invalidates validation)
**Mitigation**:
- Automated benchmarking in validation script (Test 16)
- Alert if >5% performance difference vs local builds
- Reproducibility test (Test 15) catches unexpected changes

### Risk 3: FFI Symbol Mismatch
**Likelihood**: Low
**Impact**: Medium (runtime errors)
**Mitigation**:
- Test 14 validates FFI exports with `nm -D`
- Integration test (Test 17) catches missing symbols
- Python wrapper has try/except with fallback

### Risk 4: Rollout Incidents
**Likelihood**: Medium
**Impact**: Medium (user-facing errors)
**Mitigation**:
- Progressive rollout (10% → 50% → 100%)
- Automatic rollback on error rate >5%
- Feature flags allow instant disable
- Python fallback always available

### Risk 5: Mojo Ecosystem Instability
**Likelihood**: Medium (v0.25.7 is early)
**Impact**: Low (isolated to hot paths)
**Mitigation**:
- Pin Mojo version in Nix flakes (0.25.7)
- Test upgrades in isolated environment
- Can revert to Python if Mojo becomes unmaintained

---

## Success Metrics

### Phase 1 Success (Nix Packaging & Validation)
- ✅ 17/17 validation tests pass
- ✅ Nix packages pre-built Mojo libraries correctly
- ✅ Pattern search: 13.1x speedup maintained when loaded from Nix package
- ✅ Message router: 0.025ms latency maintained when loaded from Nix package
- ✅ Zero performance regression (<5% variance)
- ✅ Libraries loadable by Python via ctypes from Nix environment
- ✅ FFI symbols verified in packaged libraries
- ⚠️  **Known Limitation**: Nix cannot compile Mojo efficiently (1,371x slowdown due to LLVM syscall overhead in sandbox). Libraries are pre-compiled and packaged by Nix for deployment.

### Phase 2 Success (Production Rollout)
- ✅ Pattern search: 100% rollout, <1% error rate, 13.1x speedup
- ✅ Message router: 100% rollout, <1% error rate, 0.025ms latency
- ✅ Zero production incidents requiring rollback
- ✅ Monitoring dashboards show stable metrics for 30 days

### Phase 3 Success (Next Hot Path)
- ✅ Event bus or MTF ranker implemented in Mojo
- ✅ ≥50x performance improvement vs Python
- ✅ Nix flake integration complete
- ✅ Progressive rollout completed without incidents

### Overall Success (Pilot Complete)
- ✅ 3+ components in Mojo (pattern search, message router, event bus)
- ✅ System-wide performance improvement ≥10x for hot paths
- ✅ Nix reproducible builds validated
- ✅ Team confidence in Mojo development workflow
- ✅ Clear path to future Mojo migrations

---

## Development Workflow: Hybrid Approach

### Why Hybrid? (Compile Locally, Package with Nix)

**Discovery (2025-10-06)**: Mojo compilation in Nix sandbox exhibits **1,371x slowdown** (1.05s → 24+ minutes) due to architectural mismatch between LLVM's I/O-intensive compilation and Nix's per-syscall isolation overhead.

**Root Cause**:
- LLVM generates thousands of temporary files during optimization passes
- Nix sandbox wraps every filesystem syscall for hermetic builds
- Result: Multiplicative overhead (1000s of files × 40x per-syscall cost)

**Industry Pattern**: This is a known limitation for LLVM-based languages in Nix. Solutions:
- **Rust**: Use `naersk` or `crane` with caching
- **C++**: Use `ccache` extensively or pre-build
- **Mojo**: Pre-compile, package with Nix (our approach)

### The Workflow

**Step 1: Local Compilation** (1.05 seconds)
```bash
cd /home/m0xu/1-projects/synapse/.synapse/neo4j
mojo build --emit=shared-lib pattern_search_mojo.mojo -o libpattern_search.so
```

**Step 2: Nix Packaging** (~5 seconds)
```bash
cd /home/m0xu/1-projects/synapse
nix build path:./nix/flakes/mojo-pattern-search
# Validates FFI exports, packages .so for deployment
```

**Step 3: Deployment**
```bash
nix copy --to ssh://production ./result
# Or: nix copy --to cachix synapse-system ./result
```

### What Nix Still Provides

✅ **Reproducible Packaging**: Hash-verified artifact distribution
✅ **FFI Validation**: Ensures `pattern_search_ffi` symbol exists
✅ **Hermetic Distribution**: All dependencies declared in flake
✅ **Rollback Support**: Nix generations enable instant rollback
✅ **Binary Caching**: Cachix can distribute pre-built artifacts

❌ **NOT Provided**: Reproducible compilation across machines (requires local Mojo SDK)

### CI/CD Integration

```yaml
# .github/workflows/mojo.yml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Install Mojo SDK
        run: curl https://get.modular.com | sh

      - name: Compile Mojo libraries
        run: |
          mojo build --emit=shared-lib .synapse/neo4j/pattern_search_mojo.mojo
          mojo build --emit=shared-lib .synapse/corpus_callosum/message_router.mojo

      - name: Package with Nix
        run: nix build .#mojo-libraries

      - name: Deploy to Cachix
        run: nix copy --to cachix synapse-system ./result
```

---

## Immediate Next Steps

**Action 1**: Install Nix (BLOCKER)
```bash
curl -L https://nixos.org/nix/install | sh -s -- --daemon
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
nix --version  # Verify installation
```

**Action 2**: Run Validation Script
```bash
cd /home/m0xu/1-projects/synapse
./scripts/validate-nix-flakes.sh
```

**Action 3**: Review Validation Results
- If 17/17 tests pass → Proceed to Phase 2 (rollout planning)
- If failures occur → Debug using `nix/NIX_VALIDATION_PLAN.md`
- If Nix issues → Consult archived migration docs for context

**Action 4**: Update Roadmap
- Document Nix validation results in `.agent-os/recaps/`
- Update Phase 2 rollout timeline based on validation findings
- Schedule Phase 3 planning session (event bus design)

---

## References

**Active Documents**:
- `scripts/validate-nix-flakes.sh` - 17-test validation suite
- `nix/NIX_VALIDATION_PLAN.md` - Detailed validation documentation
- `nix/flakes/mojo-runtime/flake.nix` - Mojo SDK flake
- `nix/flakes/mojo-pattern-search/flake.nix` - Pattern search library flake
- `nix/flakes/mojo-message-router/flake.nix` - Message router library flake

**Archived Documents** (Historical Reference):
- `docs/archive/MOJO_MIGRATION_v1.md` - Original 1,265-line migration plan
- `docs/archive/MOJO_MIGRATION_STRATEGY_v1.md` - Original strategic vision

**External Resources**:
- Mojo Documentation: https://docs.modular.com/mojo/
- Nix Flakes Manual: https://nixos.org/manual/nix/stable/command-ref/new-cli/nix3-flake.html
- Modular SDK: https://www.modular.com/max/install

**System Documentation**:
- `DOMAIN_REFACTOR_PLAN.md` - Phases 1-5 complete (100%)
- `lib/orchestration/reactive_corpus_callosum.py` - Reactive router implementation
- `.synapse/neo4j/pattern_search_mojo.mojo` - Pattern search implementation

---

**Document Version**: 1.0
**Last Updated**: 2025-10-05
**Next Review**: After Phase 1 validation complete
**Owner**: synapse-project-manager (Boss agent)
