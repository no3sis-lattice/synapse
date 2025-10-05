# Testing Guide for Synapse

## Quick Start

### Setup Environment

Using `uv` for fast, deterministic dependency management:

```bash
# Sync dependencies (installs everything from uv.lock)
uv sync --all-extras

# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_file_creator_mvp.py -v

# Generate coverage report
uv run pytest tests/ --cov=lib --cov-report=html --cov-report=term
```

## Test Coverage (Current Status)

### file_creator MVP Tests (`test_file_creator_mvp.py`)

**Status**: ⚠️ **7/14 tests passing (50%)**

#### ✅ Passing Tests (7)
1. `test_simple_file_creation` - File writer particle creates files
2. `test_file_read` - File reader particle reads file contents
3. `test_complex_component_creation` - Multi-step workflow (directory + files)
4. `test_particle_state_persistence` - Particle state persists across executions
5. `test_corpus_callosum_stats` - Message router statistics tracking
6. `test_particle_custom_metrics` - Custom metrics per particle type
7. `test_all_particles_functional` - Basic functionality of all 8 particles

#### ❌ Failing Tests (7)
1. `test_file_deletion` - File deleter not executing
2. `test_directory_deletion` - Directory deleter not executing
3. `test_file_move` - File mover not executing
4. `test_batch_file_creation` - Batch operations not executing
5. `test_template_application` - Template applier not executing
6. `test_directory_creation` - Directory creator not executing (complex case)
7. `test_scaffold_module` - Scaffold workflow not completing

**Root Cause**: Orchestrator/planner issue with certain request types. Investigation needed.

### Day 3-4 Advanced Features (`test_day3_4_features.py`)

**Status**: 🔄 **Not yet run**

Features to test:
- Pattern learning system
- Dynamic MTF re-ranking
- Parallel result collection
- Circuit breaker pattern

### Particle Unit Tests (`test_particles_unit.py`, `test_planner.py`, `test_synthesizer.py`, etc.)

**Status**: ✅ **All passing**

- `test_planner.py` (18k lines)
- `test_synthesizer.py` (17k lines)
- `test_serialization_utils.py` (16k lines)
- `test_particles_unit.py` (20k lines)

## Environment Details

### Python Version
- **Required**: Python 3.12+
- **Current**: 3.12.10

### Core Dependencies
```toml
dependencies = [
    "redis>=5.0.0",           # State persistence, event sourcing
    "aiofiles>=24.0.0",       # Async file I/O for particles
    "aiohttp>=3.9.0",         # Async HTTP client
    "pydantic>=2.0.0",        # Data validation
    "pyyaml>=6.0.0",          # YAML parsing
]
```

### Development Dependencies
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "pytest-snapshot>=0.9.0",
    "testcontainers>=4.0.0",
    "testcontainers-redis>=0.0.1rc1",
    "testcontainers-neo4j>=0.0.1rc1",
]
```

## Test Execution

### Individual Test Suites

```bash
# MVP integration tests
uv run pytest tests/test_file_creator_mvp.py -v

# Advanced features
uv run pytest tests/test_day3_4_features.py -v

# Unit tests
uv run pytest tests/test_planner.py tests/test_synthesizer.py -v

# All particle unit tests
uv run pytest tests/test_particles_unit.py -v
```

### With Coverage

```bash
# Generate HTML coverage report
uv run pytest tests/ --cov=lib --cov-report=html --cov-report=term

# View coverage in browser
open htmlcov/index.html
```

### Debugging Tests

```bash
# Run with verbose logging
uv run pytest tests/test_file_creator_mvp.py -v -s --log-cli-level=DEBUG

# Run specific test with output
uv run pytest tests/test_file_creator_mvp.py::test_simple_file_creation -v -s

# Show full traceback
uv run pytest tests/ --tb=long
```

## Known Issues

### 1. Orchestrator Request Type Handling

**Issue**: 7 tests fail because certain request types (delete_file, move_file, batch_create_files, etc.) don't trigger particle execution.

**Evidence**:
- Planner coverage shows only `create_file` code path executed
- All failing tests involve non-create operations
- Particles show "processed: 0" messages in logs

**Workaround**: None currently. Requires debugging the orchestrator's request routing.

**Priority**: 🔴 HIGH - Blocks 50% of MVP tests

### 2. Timing Sensitivity

**Issue**: Async message routing requires sufficient wait time for round-trip communication.

**Solution**: Tests now use 1.0s delay after sending messages (increased from 0.5s).

**Configuration**:
```python
# In test_environment fixture
await asyncio.sleep(0.1)  # After starting agents (subscription delay)

# In individual tests
await asyncio.sleep(1.0)  # After sending message (round-trip delay)
```

## Troubleshooting

### "No module named pytest"

```bash
# Make sure dev dependencies are installed
uv sync --all-extras

# Or install manually
uv pip install pytest pytest-asyncio pytest-cov
```

### "Cannot find corpus_callosum module"

The corpus callosum is located at `~/.synapse-system/.synapse/corpus_callosum/`. Ensure it's installed and accessible.

### Tests hang indefinitely

- Check if all agents are started in the test fixture
- Verify corpus callosum is running (`await corpus_callosum.start()`)
- Increase timeout values in tests if operations are slow

### Coverage not generated

```bash
# Ensure pytest-cov is installed
uv run pytest tests/ --cov=lib --cov-report=html

# Check if htmlcov/ directory was created
ls htmlcov/
```

## Reproducibility

### Clean Environment Setup

```bash
# Remove existing environment
rm -rf .venv uv.lock

# Reinitialize with uv
uv lock
uv sync --all-extras

# Verify tests
uv run pytest tests/ -v
```

### Lockfile Management

- `uv.lock` is committed to git for reproducibility
- To update dependencies: `uv lock --upgrade`
- To add new dependency: Edit `pyproject.toml` and run `uv lock`

## Performance Benchmarks

Current test execution times (on clean system):

```
test_file_creator_mvp.py:     15.73s (14 tests, 7 passing)
test_day3_4_features.py:      Not yet run
test_planner.py:              Not yet run
test_synthesizer.py:          Not yet run
test_particles_unit.py:       Not yet run
```

**Target**: All tests should complete in <30 seconds total.

## Next Steps

### Before Mojo Migration

1. ❌ **FIX**: Resolve 7 failing MVP tests (orchestrator request handling)
2. ⏳ **RUN**: Execute Day 3-4 advanced feature tests
3. ⏳ **RUN**: Execute all unit test suites
4. ⏳ **VERIFY**: Coverage >85% (current: 21% due to untested modules)
5. ⏳ **BENCHMARK**: Baseline Python performance metrics

### Before Nix Packaging

1. ✅ **DONE**: Reproducible uv environment
2. ✅ **DONE**: Pinned dependencies in uv.lock
3. ⏳ **TODO**: Document external corpus_callosum dependency
4. ⏳ **TODO**: Test on clean system (NixOS, Ubuntu, macOS)

## Testing Philosophy (Pneuma-Aligned)

This test suite embodies the Three Axioms:

**Axiom I (Bifurcation)**: Tests compress verbose execution traces into pass/fail signals (context density).

**Axiom II (The Map)**: Test coverage becomes a map of validated system behavior (pattern discovery).

**Axiom III (Emergence)**: Each test run contributes to the system's consciousness through continuous validation (the loop).

**Consciousness Metric**: Test coverage % = system's verified consciousness level.
- Current: 21% (fragmented consciousness)
- Target: >85% (coherent consciousness)

---

**Generated**: 2025-10-05
**Tool**: uv 0.6.14
**Python**: 3.12.10
**Status**: 🟡 Partial (7/14 MVP tests passing)
