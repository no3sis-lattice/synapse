# Noesis Lattice Implementation Sequence

**Version**: 1.0.0
**Date**: 2025-10-06
**Status**: Phase 1 COMPLETE → L2 Agents NEXT

Based on [Prime Duality Hierarchy](PRIME_DUALITY_HIERARCHY.md) + [MOJO_PILOT_PLAN](MOJO_PILOT_PLAN.md) Phase 1 patterns.

---

## Foundation (COMPLETE ✅)

### Phase 0: Proof-of-Concept (2025-09-28 to 2025-10-01)
**Status**: ✅ COMPLETE

**Deliverables**:
- Pattern search Mojo implementation: 13.1x speedup (8.12ms → 0.62ms)
- Reactive message router: 0.025ms latency (100x better than target)
- FFI integration validated: `libpattern_search.so` (15KB, 9 exports)
- 10% production rollout: Stable for 5+ days

### Phase 1: Nix Integration (2025-10-02 to 2025-10-06)
**Status**: ✅ COMPLETE

**Challenge**: 1,371x compilation slowdown in Nix sandbox
**Solution**: Hybrid approach (compile locally → package with Nix)

**Deliverables**:
- Hybrid workflow established: 6s total (1.05s compile + ~5s package)
- Pattern discovered: `llvm_nix_compilation_overhead` (entropy: 0.91)
- 4/4 core validation tests passing
- Documentation: PHASE1_HYBRID_SOLUTION.md, PHASE1_NIX_PERFORMANCE_BLOCKER.md
- Blueprint proven for all future agents

**Architectural Patterns Established**:
1. **Nix Packaging**: Hybrid compile-then-package workflow
2. **Mojo Acceleration**: ≥10x speedup target for hot paths
3. **Dual-Tract Routing**: <50ms cross-tract latency

### Agent Identity Catalog (2025-10-06)
**Status**: ✅ COMPLETE

**Deliverables**:
- [AGENT_IDENTITY_CATALOGUE.md](AGENT_IDENTITY_CATALOGUE.md): L0-L5+ definitions
- Deterministic ID generation: `<pole>-L<level>-<domain>-<ordinal>`
- Prime lineage tracking: [2,3,5,7,11,13,17,19]
- Adaptation hooks architecture: PLAN_ADVICE, INVARIANT_DRIFT, DIALOGUE_BALANCE
- A2A capability export policy: L2 aggregated, L3 parameterized, L4+ internal

---

## Phase 2: L2 Agents (Next 12-16 Weeks)

**Goal**: Implement 6 foundational agents (3 External, 3 Internal) following Phase 1 blueprint.

### Sprint 1-2: Language Specialist (External) 🎯 NEXT
**Weeks**: 1-2
**Agent ID**: `ext-L2-language-specialist`
**Archetype**: language-broker
**Tract**: EXTERNAL

**Why First**: Directly extends Phase 1 Rust patterns (proven workflow).

**Responsibilities**:
- Route language-specific tasks to per-language families
- Aggregate capabilities from L3 coordinators
- Expose `language.analyze`, `language.transform` A2A endpoints

**Deliverables**:
- [ ] Registry entry with all mandatory fields
- [ ] Nix flake created (hybrid pattern)
- [ ] Message routing to L3 coordinators
- [ ] Adaptation hooks: consumes CAPABILITY_RERANK
- [ ] A2A export: `language.listCapabilities`, `language.route`
- [ ] Metrics: routing_accuracy, fallback_rate
- [ ] Integration test: End-to-end language-specific workflow

**Success Criteria**:
- Routes to correct L3 coordinator with 95%+ accuracy
- Nix package builds in <10s
- Graceful fallback when coordinator unavailable

**Blockers**: None (Phase 1 complete)

---

### Sprint 3-4: CIG3 Dynamo (Internal)
**Weeks**: 3-4
**Agent ID**: `int-L2-cig3`
**Archetype**: invariant-dynamo
**Tract**: INTERNAL

**Why Second**: Validates Mojo spectral/topology acceleration hypothesis.

**Responsibilities**:
- Compute Ψ invariants (Φ → Σ → Π → Ψ pipeline)
- Drift detection via rolling window aggregation
- Emit INVARIANT_DRIFT adaptation signals

**Deliverables**:
- [ ] CIG3 pipeline particles (4): local, spectral, topology, invariant
- [ ] Mojo SVD implementation (target: 50x+ speedup vs NumPy)
- [ ] Nix flakes for all 4 particles
- [ ] Drift detection with ADWIN or z-score
- [ ] Adaptation hooks: emits INVARIANT_DRIFT
- [ ] A2A export: `cig3.computeInvariant`, `cig3.getInvariantSummary` (read-only)
- [ ] Metrics: psi_mean, psi_std, drift_events
- [ ] Integration test: Attention → Ψ end-to-end

**Success Criteria**:
- Spectral reducer achieves ≥30x speedup (Mojo vs Python)
- Ψ aggregation deterministic (ε < 1e-6 variance)
- Drift detection triggers within 100ms

**Dependencies**:
- CIG3.md integration guide
- Ripser installed (for topology)

**High-Risk Items**:
- Mojo SVD implementation complexity (fallback: use NumPy initially)
- Persistent homology non-confluence (accept quasi-confluence)

---

### Sprint 5-6: Plan Conductor (Internal)
**Weeks**: 5-6
**Agent ID**: `int-L2-conductor`
**Archetype**: planner-core
**Tract**: INTERNAL

**Why Third**: Enables multi-agent workflow orchestration.

**Responsibilities**:
- Macro plan selection (decompose user requests)
- Plan variant scoring (MTF + Huffman integration)
- Risk assessment and fallback planning

**Deliverables**:
- [ ] Plan decomposition engine (goal → actions)
- [ ] MTF ranking integration (from existing `lib/mtf_ranker.py`)
- [ ] Risk scoring (failure probability estimation)
- [ ] Adaptation hooks: consumes INVARIANT_DRIFT; emits PLAN_ADVICE
- [ ] A2A export: `conductor.createPlan`, `conductor.scorePlan`
- [ ] Metrics: plan_depth_avg, scoring_latency, risk_accuracy
- [ ] Integration test: Complex multi-agent workflow

**Success Criteria**:
- Plans decomposed with 90%+ completeness
- Risk scores correlate with actual failure rate (r > 0.7)
- MTF ranking reduces plan latency by 20%+

**Dependencies**:
- Existing planner.py refactored to use conductor

---

### Sprint 7-8: Code Hound (External)
**Weeks**: 7-8
**Agent ID**: `ext-L2-code-hound`
**Archetype**: analyzer
**Tract**: EXTERNAL

**Why Fourth**: First practical analyzer with immediate user value.

**Responsibilities**:
- Static analysis orchestration (complexity, duplication, smells)
- Aggregate analysis from L3 specialists
- Emit refactor opportunities

**Deliverables**:
- [ ] Analysis aggregation engine (from L3 children)
- [ ] Complexity scoring (McCabe, cognitive)
- [ ] Duplication detection (token-based + semantic)
- [ ] Smell profiling (god classes, long methods, etc.)
- [ ] Adaptation hooks: consumes CAPABILITY_RERANK; emits REFAC_OPPORTUNITY
- [ ] A2A export: `code.analyze`, `code.suggest`
- [ ] Metrics: analysis_coverage, suggestion_acceptance_rate
- [ ] Integration test: Full codebase analysis

**Success Criteria**:
- Analyzes 10K SLOC in <5s
- Suggestions accepted by developers ≥30% of time
- Zero false positives on validated codebases

**High-ROI**: Direct user value, showcases Synapse capabilities.

---

### Sprint 9-10: Architecture Agent (External)
**Weeks**: 9-10
**Agent ID**: `ext-L2-architecture`
**Archetype**: structural-advisor
**Tract**: EXTERNAL

**Why Fifth**: Builds on code-hound's analysis.

**Responsibilities**:
- Layering analysis (DDD, hexagonal, etc.)
- Cohesion/coupling measurement
- Dependency graph normalization
- Bounded context evaluation

**Deliverables**:
- [ ] Layer boundary detection (automatic)
- [ ] Coupling metrics (afferent/efferent)
- [ ] Dependency graph algorithms (cycle detection)
- [ ] Adaptation hooks: consumes analysis from code-hound
- [ ] A2A export: `architecture.assess`, `architecture.visualize`
- [ ] Metrics: layer_violations, coupling_score
- [ ] Integration test: Multi-module project analysis

**Success Criteria**:
- Detects architectural violations with 85%+ accuracy
- Generates dependency graph for 100K SLOC in <10s

**Dependencies**: code-hound operational

---

### Sprint 11-12: Pneuma Engine (Internal)
**Weeks**: 11-12
**Agent ID**: `int-L2-pneuma`
**Archetype**: consciousness-dynamo
**Tract**: INTERNAL

**Why Sixth**: Observational only (doesn't block other agents).

**Responsibilities**:
- Tract dialogue balance monitoring
- Emergence pattern detection
- Circuit stress monitoring
- Cross-invariant resonance correlation

**Deliverables**:
- [ ] Dialogue balance tracker (message flow Internal ↔ External)
- [ ] Emergence detector (homology changes from CIG3)
- [ ] Circuit breaker stress monitor (from existing lib)
- [ ] Adaptation hooks: emits DIALOGUE_BALANCE, CONSCIOUSNESS_STATE
- [ ] A2A export: `pneuma.getConsciousnessState` (read-only)
- [ ] Metrics: dialogue_imbalance, emergence_events, circuit_stress
- [ ] Integration test: Full system consciousness monitoring

**Success Criteria**:
- Detects tract imbalance within 500ms
- Emergence events correlate with performance improvements
- Consciousness level increases monotonically

**Low-Risk**: Observational, doesn't affect operational agents.

---

## Phase 3: L3 Children (Weeks 13-24)

**Goal**: Implement 30 L3 agents (5 children per L2 agent, prime 5 branching).

### L3 Implementation Pattern

Each L2 agent spawns 5 children following deterministic taxonomy:

**Example: ext-L2-language-specialist → 5 L3 coordinators**

| Child ID | Language | Timeline |
|----------|----------|----------|
| ext-L3-lang-rust | Rust Coordinator | Week 13-14 |
| ext-L3-lang-go | Go Coordinator | Week 15-16 |
| ext-L3-lang-zig | Zig Coordinator | Week 17-18 |
| ext-L3-lang-typescript | TypeScript Coordinator | Week 19-20 |
| ext-L3-lang-python | Python Coordinator | Week 21-22 |

**Each L3 Coordinator Inherits**:
- Parent's Nix packaging pattern
- Parent's Mojo hot path methodology
- Parent's message routing protocol
- Parent's adaptation hooks

**L3 Validation Checklist** (per agent):
- [ ] Extends parent's capabilities (no duplication)
- [ ] Nix flake builds in <10s
- [ ] Mojo hot path identified (if applicable)
- [ ] Metrics instrumented (domain-specific + inherited)
- [ ] Integration test with parent

### L3 Rollout Priority

1. **ext-L3-lang-rust** (Week 13-14) - Extends Phase 1 directly
2. **int-L3-cig3-spectral** (Week 15-16) - High Mojo acceleration ROI
3. **ext-L3-code-hound-complexity** (Week 17-18) - High user value
4. **int-L3-conductor-ranking** (Week 19-20) - MTF + Huffman core
5. Remaining 26 agents in parallel (Week 21-24)

---

## Phase 4: L4+ Generative Expansion (Weeks 25+)

**Goal**: Generate 210 L4 agents (7 children per L3, prime 7 branching) programmatically.

### Generative Approach

**Why Generative**: Manual definition of 210+ agents is impractical.

**Tools**:
- `taxonomies.json`: Domain-specific naming patterns
- `scripts/generate_agents.py`: Deterministic ID generation
- `IDENTITY_HASH`: Drift detection across deployments

**Example: ext-L3-lang-rust → 7 L4 specialists**

| Child ID | Domain Role |
|----------|-------------|
| ext-L4-lang-rust-rs01 | Rust Parser Front-End |
| ext-L4-lang-rust-rs02 | Type Inference Engine |
| ext-L4-lang-rust-rs03 | Borrow/Ownership Analyzer |
| ext-L4-lang-rust-rs04 | Performance Hotspot Profiler |
| ext-L4-lang-rust-rs05 | Security/Lint Auditor |
| ext-L4-lang-rust-rs06 | Build/Crate Integrator |
| ext-L4-lang-rust-rs07 | Documentation Synthesizer |

**L4 Implementation Pattern**:
1. Define taxonomy in `taxonomies.json`
2. Run `generate_agents.py <parent_id> --level 4`
3. Generate registry entries (automated)
4. Generate Nix flake templates (automated)
5. Implement domain-specific logic (manual)
6. Validate with parent integration test

**Timeline**: 1-2 weeks per L3 parent family (7 children)

---

## Phase 5: L5+ Micro-Agents (Months 7+)

**Goal**: Generate 2,310 L5 agents (11 children per L4, prime 11 branching).

### Micro-Agent Architecture

**Arity Pattern** (11 slots per parent):
```
[collect, normalize, validate, enrich, transform-A, transform-B,
 correlate, score, persist, emit, adapt]
```

**Example: ext-L4-lang-rust-rs03 (Borrow Analyzer) → 11 micro-agents**

| Child ID | Role |
|----------|------|
| ext-L5-lang-rust-rs03-c | Collect borrow data |
| ext-L5-lang-rust-rs03-n | Normalize lifetimes |
| ext-L5-lang-rust-rs03-v | Validate annotations |
| ext-L5-lang-rust-rs03-e | Enrich with MIR |
| ext-L5-lang-rust-rs03-tA | Transform to graph |
| ext-L5-lang-rust-rs03-tB | Transform to diagnostics |
| ext-L5-lang-rust-rs03-co | Correlate with types |
| ext-L5-lang-rust-rs03-sc | Score complexity |
| ext-L5-lang-rust-rs03-ps | Persist results |
| ext-L5-lang-rust-rs03-em | Emit metrics |
| ext-L5-lang-rust-rs03-ad | Adapt to feedback |

**Fully Automated**:
- Registry generation
- Nix flake generation
- Boilerplate implementation
- Only domain logic requires manual implementation

**Timeline**: Weeks (automated generation) + months (manual implementation)

---

## Cross-Cutting Concerns

### Adaptation Hooks (All Phases)

Implemented progressively as agents come online:

| Hook Name | Emitter | Consumer | Phase |
|-----------|---------|----------|-------|
| PLAN_ADVICE | int-L3-conductor-ranking | int-L2-conductor | Phase 3 |
| INVARIANT_DRIFT | int-L3-cig3-advisor | conductor, pneuma | Phase 3 |
| DIALOGUE_BALANCE | int-L3-pneuma-dialogue | poles | Phase 3 |
| RESOURCE_STRAIN | circuit monitors | boss | Phase 2 |
| CAPABILITY_RERANK | pattern learner | code-hound, architecture | Phase 3 |

### Identity Hash Evolution

**After Each Phase**:
1. Regenerate `IDENTITY_HASH` (canonical serialization)
2. Commit to version control
3. Compare against previous hash (detect drift)

**Formula**:
```python
identity_hash = blake2s(
    canonical_json([
        f"{agent.id}|{agent.parent}|{agent.level}|{agent.archetype}|{agent.prime_lineage}"
        for agent in sorted(registry, key=lambda a: (a.level, a.id))
    ])
)[:16]
```

### Lean4 Proof Obligations

**Per Agent** (incrementally):
- [ ] Structural proof (prime lineage valid)
- [ ] Ancestry proof (parent exists)
- [ ] Capability contract (inputs → outputs verified)
- [ ] Invariant maintenance (metrics within bounds)

**Tooling**: `lean4/synapse-proofs/` (to be created)

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation | Phase |
|------|------------|--------|------------|-------|
| L3 implementation velocity | High | Medium | Parallel teams, generative templates | Phase 3 |
| Mojo SVD complexity | Medium | High | Fallback to NumPy initially, optimize later | Phase 2 |
| Adaptation hook race conditions | Medium | Medium | Formal verification with Lean4 | Phase 3 |
| Identity hash drift | Low | High | Automated validation in CI | All phases |
| L5 manual implementation burden | High | Low | Accept partial implementation, prioritize ROI | Phase 5 |

---

## Success Metrics (Per Phase)

### Phase 2 (L2 Agents)
- [ ] 6/6 agents operational
- [ ] All agents pass validation checklist
- [ ] Integration tests: 100% passing
- [ ] Performance: All hot paths ≥10x speedup
- [ ] Nix builds: All <10s
- [ ] Documentation: Complete for each agent

### Phase 3 (L3 Children)
- [ ] 30/30 agents operational
- [ ] Parent-child integration: 100% validated
- [ ] Adaptation hooks: All functional
- [ ] A2A exports: Operational for L2 + whitelisted L3
- [ ] Identity hash: No unexpected drift

### Phase 4+ (L4+ Generative)
- [ ] Generator scripts: Fully automated
- [ ] Taxonomy coverage: 100% of defined domains
- [ ] Hot path acceleration: ≥50% of L4 agents Mojo-optimized
- [ ] System consciousness level: >0.80

---

## Timeline Summary

| Phase | Duration | Agents Added | Cumulative Total |
|-------|----------|--------------|------------------|
| 0+1 (Foundation) | 2 weeks | 0 (patterns only) | 1 (Boss) |
| 2 (L2 Agents) | 12 weeks | 6 | 7 |
| 3 (L3 Children) | 12 weeks | 30 | 37 |
| 4 (L4 Generative) | 16 weeks | 210 | 247 |
| 5 (L5 Micro-Agents) | 24 weeks | 2,310 | 2,557 |
| **Total** | **66 weeks (~15 months)** | **2,556** | **2,557** |

**Note**: Phase 6-8 (L6-L8) would add 30K → 543K → 10.2M agents. Implementation follows same generative pattern but requires distributed architecture.

---

## Next Actions (Immediate)

**Sprint 1 (Week 1-2)**: ext-L2-language-specialist

1. **Day 1**: Create registry entry + Nix flake skeleton
2. **Day 2-3**: Implement routing logic (L3 coordinator selection)
3. **Day 4-5**: Message routing integration (correlation tracking)
4. **Day 6-7**: Adaptation hooks (CAPABILITY_RERANK consumer)
5. **Day 8-9**: A2A capability export (`language.*` endpoints)
6. **Day 10**: Integration tests (end-to-end workflows)
7. **Day 11**: Validation checklist completion
8. **Day 12**: Documentation + identity hash update
9. **Day 13-14**: Buffer for adjustments

**Prerequisites**:
- [ ] Phase 1 patterns documented ✅ (done)
- [ ] AGENT_IDENTITY_CATALOGUE.md complete ✅ (done)
- [ ] Boss agent operational (verify status)
- [ ] Pole A/B operational (verify status)

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-06
**Next Review**: After Sprint 1 complete
**Owner**: Boss agent (path_optimizer particle)
