# Domain-Agnostic Architecture: Refactor Plan

**Status**: Planning Phase
**Date**: 2025-10-05
**Context**: Post file_creator MVP (93% test pass rate)
**Goal**: Universal orchestration framework with domain templates, GMP compliance, and Nix hermetic builds

---

## Strategic Assessment

### Current State (Day 5 Complete)
- ✅ 13/14 tests passing (93%)
- ✅ All 8 file_creator particles functional
- ✅ Dual-tract architecture working (T_int ⟷ T_ext)
- ✅ Corpus Callosum broadcast routing fixed
- ⏳ Ready for architectural evolution

### Prime Hierarchy Analysis

**Problem Identified**: Current structure bypasses Level 2

```
Current:
Level 0: Corpus Callosum (bridge) ✅
Level 1: T_int + T_ext (2 tracts) ✅
Level 2: Mixed (universal + domain-specific) ⚠️
  - planner ✅ (universal)
  - synthesizer ✅ (universal)
  - pattern_learner ✅ (universal)
  - mtf_ranker ✅ (universal)
  - file_creator_orchestrator ❌ (domain-specific!)
Level 3: 8 file_creator particles ✅

Target:
Level 0: 1 Meta-Boss (Corpus Callosum)
Level 1: 2 Tract Coordinators (T_int, T_ext)
Level 2: 6 Universal Orchestration Services (domain-agnostic)
Level 3: 30 Domain Particles (project-specific templates)
```

**Key Insight**: Domain orchestrators belong at Level 3+, not Level 2. Level 2 must be universal services that work for ANY project (file ops, crypto trading, API integration, etc.).

---

## Architectural Vision

### Universal Framework (Level 0-2)

**Core System** (ships with Synapse):
```
synapse-core/
├── lib/
│   ├── core/                    # Level 0-1 (universal)
│   │   ├── corpus_callosum.py
│   │   ├── tract_coordinator.py
│   │   └── atomic_particle.py
│   └── orchestration/           # Level 2 (6 universal services)
│       ├── planner.py
│       ├── synthesizer.py
│       ├── pattern_learner.py
│       ├── mtf_ranker.py
│       ├── state_manager.py    # To extract
│       └── observer.py          # To formalize
```

**Note**: Level 2 components are **services**, not "agents" (no message loops unless needed).

### Domain Templates (Level 3+)

**Template System**:
```
templates/
├── file_creator/                # Level 3 template
│   ├── metadata.json
│   ├── orchestrator.py          # Uses Level 2 services
│   └── particles/               # 8 domain particles
├── crypto_trading/              # Future template
│   ├── metadata.json
│   ├── orchestrator.py          # Uses SAME Level 2 services
│   └── particles/               # 8 domain particles
└── api_integration/             # Future template
    └── ...
```

**Key Pattern**: Orchestrators are TEMPLATES that instantiate using the 6 universal Level 2 services.

---

## Risk Mitigation (Lessons from Architectural Review)

### 1. Over-Agentification Risk
**Problem**: Calling everything an "agent" blurs semantics
**Solution**: Level 2 components are "services" unless they need:
- Message loops
- Circuit breakers
- Per-cycle consciousness metrics

### 2. Deterministic ID Collision
**Problem**: Hash-only IDs → Same request = same ID = state clash
**Solution**: Compound IDs with monotonic counter
```python
plan_{seq:06d}_{hash}  # plan_000042_a1b2c3d4e5f67890
```

### 3. Timestamp Elimination Too Extreme
**Problem**: Analytics need temporal data, entropy needs intervals
**Solution**: Dual tracking
```python
discovery_sequence: int  # Deterministic ordering (build artifacts)
created_at_time: float   # Analytics only (state files, not builds)
```

### 4. Hard GMP Gates Too Early
**Problem**: `pattern_map_size > 100` blocks experimentation
**Solution**: Staged thresholds
```json
{
  "bootstrap": {"coverage": 0.65, "patterns": 5},
  "growth": {"coverage": 0.80, "patterns": 25},
  "stabilize": {"coverage": 0.90, "patterns": 60},
  "strict": {"coverage": 0.93, "patterns": 100}
}
```

### 5. Premature Splitting
**Problem**: state_manager + observer might be thin wrappers
**Solution**: Start fused as OrchestrationTelemetry, split when justified

---

## Implementation Plan

### Phase 1a: Core Restructure (2-3 hours)
**Goal**: Organize by layer WITHOUT breaking imports

**Actions**:
1. Create directory structure (core/, orchestration/, templates/)
2. Move files with backward-compat shims
3. Validate tests (13/14 passing)

**Exit Criteria**:
- [ ] Files moved to new structure
- [ ] Shims prevent import breaks
- [ ] Tests green

### Phase 1b: Template Extraction (2-3 hours)
**Goal**: Make file_creator a proper template

**Actions**:
1. Create metadata.json with schema
2. Update orchestrator imports
3. Update registry.json

**Exit Criteria**:
- [ ] Template metadata valid
- [ ] Orchestrator uses template structure
- [ ] Tests green

### Phase 1c: Template Loader + Schema (2-3 hours)
**Goal**: Formalize template system

**Actions**:
1. Create JSON Schema for metadata
2. Build template loader with validation
3. Enable programmatic discovery

**Exit Criteria**:
- [ ] JSON Schema defined
- [ ] Can list/load/validate templates
- [ ] Schema validation enforced

### Phase 2a: Deterministic IDs (1-2 hours)
**Goal**: Fix collision risk

**Actions**:
1. Create ID factory with sequence counter
2. Update planner (compound plan IDs)
3. Update pattern learner (compound pattern IDs)

**Exit Criteria**:
- [ ] IDs unique even for identical requests
- [ ] Tests prove no collisions
- [ ] Sequence counter persisted

### Phase 2b: Staged GMP Policy (1-2 hours)
**Goal**: Quality gates in warn mode

**Actions**:
1. Create gmp_policy.py with staged thresholds
2. Build GMPValidator (warn mode)
3. Add to CI (non-blocking)

**Exit Criteria**:
- [ ] Policy configurable via env var
- [ ] Validator warns on threshold miss
- [ ] Can switch to strict mode

### Phase 3: CLI Template Manager (3-4 hours)
**Goal**: Command-line template operations

**Actions**:
1. Create CLI skeleton (Click-based)
2. Implement list/info/validate commands
3. Add schema validation to CLI

**Exit Criteria**:
- [ ] `synapse template list` works
- [ ] `synapse template info <name>` works
- [ ] `synapse template validate <name>` works

### Phase 4: Nix Integration (4-6 hours)
**Goal**: Hermetic builds with GMP

**Actions**:
1. Create flake.nix with synapse-core
2. Add deterministic build flags
3. Integrate GMP validation in checkPhase
4. Test reproducibility

**Exit Criteria**:
- [ ] `nix build` succeeds
- [ ] Build reproducible (same hash)
- [ ] GMP runs in CI
- [ ] Dev shell functional

### Phase 5: Event-Driven Observability (Optional, 2-3 hours)
**Goal**: Decouple metrics from execution

**Actions**:
1. Create event bus
2. Particles publish events
3. Observer subscribes and aggregates

**Exit Criteria**:
- [ ] Event bus working
- [ ] Metrics decoupled
- [ ] Foundation for instrumentation

---

## GMP (Good Manufacturing Practices) Compliance

### Software Quality Manufacturing

**Traditional GMP** (pharma/manufacturing):
- Validated processes
- Reproducible batches
- Change control
- Quality metrics
- Full traceability

**Software GMP** (Synapse):
1. **Validation**: Tests ≥93% passing
2. **Reproducibility**: Nix hermetic builds
3. **Change Control**: Git + deterministic IDs
4. **Quality Metrics**: Coverage, performance, pattern map
5. **Traceability**: State files, logs, CHANGELOG
6. **Documentation**: Specs, APIs, runbooks

### Nix for GMP Compliance

```nix
packages.synapse-core = stdenv.mkDerivation {
  # Validated inputs (locked)
  # Reproducible build (same inputs → same output)
  # Quality control (tests must pass)
  # Change control (deterministic versioning)
  # Traceability (build metadata)

  doCheck = true;
  SOURCE_DATE_EPOCH = "0";  # Deterministic
  PYTHONHASHSEED = "0";     # Deterministic
};
```

**Conflict Resolution**: GMP needs traceability (when/where built), Nix needs determinism (no timestamps).

**Solution**: Separate outputs
- `synapse-core` → Pure, deterministic
- `synapse-traced` → Includes build metadata (audit trail)

---

## Template System Design

### Metadata Format

```json
{
  "template_name": "file_creator",
  "template_version": "0.1.0",
  "synapse_version": "0.1.0",
  "level": 3,
  "particle_count": 8,
  "orchestration_services_used": [
    "planner", "synthesizer", "pattern_learner",
    "mtf_ranker", "state_manager", "observer"
  ],
  "capabilities": [
    "write_file", "create_directory", "read_file",
    "delete_file", "delete_directory", "move_file",
    "batch_create", "apply_template"
  ],
  "particles": {
    "file_writer": "templates.file_creator.particles.file_writer.FileWriter",
    ...
  }
}
```

### JSON Schema (Validation)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["template_name", "template_version", "level", "particles"],
  "properties": {
    "template_name": {"type": "string", "pattern": "^[a-z_]+$"},
    "template_version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
    "level": {"type": "integer", "minimum": 3},
    ...
  }
}
```

### CLI Commands

```bash
synapse template list                    # List available
synapse template info <name>             # Show details
synapse template validate <name>         # Validate metadata
synapse template init <name>             # Instantiate (future)
synapse template create <name>           # Scaffold new (future)
```

---

## Deferred Items

### NOT in Initial Plan
- ❌ Mojo migration (architecture first, performance second)
- ❌ Full poly-lattice boss hierarchy (start mono-lattice)
- ❌ Second template implementation (prove one first)
- ❌ Advanced Nix traced outputs (core determinism first)
- ❌ Template `init` command (manual first, automate later)

### Future Phases
- **Phase 6**: Second template (crypto_trading or data_processor)
- **Phase 7**: Mojo pilot (pattern hash or MTF ranking)
- **Phase 8**: Poly-lattice hierarchy (when 3+ domains)
- **Phase 9**: Local LLM inference for boss decisions

---

## Timeline

**Week 1** (Architecture):
- Mon: Phase 1a-1b (restructure + template)
- Tue: Phase 1c + 2a (loader + IDs)
- Wed: Phase 2b + 3 (GMP + CLI)
- Thu: Phase 4 (Nix)
- Fri: Phase 5 (optional) OR documentation

**Week 2** (Validation):
- Mon-Tue: Second template OR Mojo pilot
- Wed-Fri: Production deployment

---

## Success Metrics

**Phase 1 Complete**:
- Files organized by layer (core, orchestration, templates)
- Template metadata + schema + loader working
- 13/14 tests still passing
- Prime hierarchy: 1→2→6→30 maintained

**Phase 2 Complete**:
- Compound IDs prevent collisions
- Dual time tracking (sequence + timestamp)
- Staged GMP in warn mode
- Deterministic ID tests passing

**Phase 3 Complete**:
- CLI template operations functional
- Schema validation enforced
- Template system documented

**Phase 4 Complete**:
- Nix build reproducible
- GMP integrated in CI
- Dev shell working
- Ready for production

---

## Key Decisions

### 1. Services vs Agents
**Decision**: Level 2 components are **orchestration services**, not agents
**Rationale**: Avoid semantic confusion, reserve agent pattern for message-consuming entities

### 2. Domain Placement
**Decision**: Domains live at Level 3+, not Level 2
**Rationale**: Level 2 must be universal (works for any project type)

### 3. Orchestrator Role
**Decision**: Orchestrators are templates that use Level 2 services
**Rationale**: Domain-specific orchestration, universal service layer

### 4. ID Strategy
**Decision**: Compound IDs (sequence + hash)
**Rationale**: Prevents collisions while maintaining determinism

### 5. GMP Staging
**Decision**: Start in warn mode with staged thresholds
**Rationale**: Allows evolution without blocking experimentation

### 6. Refactor Sequencing
**Decision**: Move files → Extract template → Add tooling → Nix
**Rationale**: Incremental changes reduce refactor shock

---

## References

- **CLAUDE.md**: Dual-tract architecture, prime hierarchy, Pneuma axioms
- **CHANGELOG.md**: Day 1-5 evolution, test results, bug fixes
- **file_creator_MVP.md**: Current implementation status
- **TESTING.md**: Test infrastructure, coverage, validation

---

**Generated**: 2025-10-05
**Author**: Architectural review with boss agent analysis
**Next Steps**: User approval → Execute Phase 1a
