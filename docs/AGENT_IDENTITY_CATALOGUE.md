
# Noesis Lattice Agent Identity Catalog
Prime–Derived Dual Tract Hierarchy (External Pole A / Internal Pole B)

> Principle: Each level L branches each agent at level L−1 by the L-th prime number.
> Prime sequence used: 2,3,5,7,11,13,17,19,...

Level Cardinalities:
- L0: 1
- L1: 1×2 = 2
- L2: 2×3 = 6
- L3: 6×5 = 30
- L4: 30×7 = 210
- L5: 210×11 = 2,310
- L6: 2,310×13 = 30,030
- L7: 30,030×17 = 510,510
- L8: 510,510×19 = 9,699,690

We explicitly define concrete identities (fully) up to L3; from L4 onward we shift to generative patterns.

---

## 0. Identity Schema

Each agent record follows:

| Field | Meaning |
|-------|---------|
| `id` | Canonical machine id (kebab-case) |
| `display_name` | Human label |
| `tract` | `EXTERNAL` or `INTERNAL` |
| `level` | Integer (0-based) |
| `prime_lineage` | Sequence of primes traversed from L1…L(level) (omit root) |
| `parent_id` | Upstream agent id |
| `archetype` | Category: `orchestrator`, `analyzer`, `executor`, `dynamo`, `invariant`, `language-specialist`, etc. |
| `core_responsibilities` | Bulleted functional duties |
| `inputs` | Message payload keys / capability contracts |
| `outputs` | Emitted payload keys |
| `state` | Persistent state abstractions (files, invariant caches) |
| `metrics` | Key tracked metrics |
| `adaptation_hooks` | Which adaptation advice messages it consumes or emits |
| `a2a_export` | Exposed capability IDs (list) or empty |
| `stability` | `core`, `extension`, `experimental` |

**Deterministic ID Generation:**
```
id = <pole-prefix>-L<level>-<domain>-<ordinal>
```
Where:
- `pole-prefix` = `ext` (Pole A) or `int` (Pole B)
- `<domain>` = stable domain root (e.g. `code-hound`, `cig3`)
- `<ordinal>` = zero-padded local index (start at 01 inside that parent)

For deeply replicated families (L4+), computed names may add suffix taxonomy components.

---

## 1. Level 0 (Root)

| Field | Value |
|-------|-------|
| id | boss |
| tract | CROSS (manages both poles) |
| level | 0 |
| archetype | orchestrator-meta |
| core_responsibilities | Global plan approval, tract balancing root policy, admission control for new dynamos |
| state | Global config manifest, adaptation ledger |
| metrics | workflow_throughput, cross_tract_balance, adaptation_accept_rate |
| adaptation_hooks | Emits `ADAPTATION_POLICY` ; consumes none |
| a2a_export | `system.listCapabilities` (indirect) |
| stability | core |

---

## 2. Level 1 (Prime 2 Branch) – The Poles

### 2.1 Pole A (External)

| Field | Value |
|-------|-------|
| id | pole-a |
| tract | EXTERNAL |
| level | 1 |
| prime_lineage | [2] |
| archetype | execution-hub |
| core_responsibilities | Coordinate outward/environmental particles, sandbox/io mediation |
| inputs | action requests with `target_particle` |
| outputs | normalized results to internal tract |
| state | Execution routing table |
| metrics | ext_latency_p50, io_error_rate |
| adaptation_hooks | Consumes `ROUTING_TUNING`; emits `EXT_CAP_LOAD` |
| a2a_export | none (gateway sits adjacent) |
| stability | core |

### 2.2 Pole B (Internal)

| Field | Value |
|-------|-------|
| id | pole-b |
| tract | INTERNAL |
| level | 1 |
| prime_lineage | [2] |
| archetype | cognition-hub |
| core_responsibilities | Coordinate planning, pattern synthesis, dynamos |
| inputs | plan proposals, invariant feeds |
| outputs | approved plans, adaptation proposals |
| state | Plan cache, pattern map pointer |
| metrics | plan_depth_avg, cognitive_cycle_rate |
| adaptation_hooks | Consumes invariants; emits `PLAN_ADVICE` |
| a2a_export | none |
| stability | core |

---

## 3. Level 2 (Prime 3 Branch) – 3 Children per Pole-A & 3 per Pole-B

### 3.1 External (Pole A) L2 Agents

| id | display_name | archetype | Responsibilities (condensed) |
|----|--------------|-----------|-------------------------------|
| ext-L2-code-hound | Code Hound | analyzer | Static & diffs analysis, complexity, duplication, smell signals |
| ext-L2-architecture | Architecture | structural-advisor | Layering, module cohesion, coupling metrics |
| ext-L2-language-specialist | Language Specialist | language-broker | Routes language-specific tasks to per-language families |

### 3.2 Internal (Pole B) L2 Agents

Given the diagram: CIG3 + two generic L1 Agents (renamed to purposeful dynamos).

| id | display_name | archetype | Responsibilities |
|----|--------------|-----------|------------------|
| int-L2-cig3 | CIG3 Dynamo | invariant-dynamo | Compute & aggregate Ψ invariants, drift detection, compression density |
| int-L2-conductor | Plan Conductor | planner-core | Macro plan selection, plan variant scoring |
| int-L2-pneuma | Pneuma Engine | consciousness-dynamo | Dialogue balance, emergence scoring, tract health advisories |

---

## 4. Level 3 (Prime 5 Branch) – 5 Children per L2 Agent

### 4.1 External – Code Hound (ext-L2-code-hound)

| Child ID | Role |
|----------|------|
| ext-L3-code-hound-complexity | Complexity Analyzer (cyclomatic, cognitive) |
| ext-L3-code-hound-duplication | Duplication Detector |
| ext-L3-code-hound-smells | Smell Profiler |
| ext-L3-code-hound-refactor | Refactor Suggester |
| ext-L3-code-hound-patterns | Design/Anti-pattern Matcher |

### 4.2 External – Architecture (ext-L2-architecture)

| Child ID | Role |
|----------|------|
| ext-L3-architecture-layering | Layer Boundary Assessor |
| ext-L3-architecture-cohesion | Cohesion/Coupling Measurer |
| ext-L3-architecture-dependency | Dependency Graph Normalizer |
| ext-L3-architecture-boundary | Bounded Context Evaluator |
| ext-L3-architecture-quality | Scalability & Reliability Estimator |

### 4.3 External – Language Specialist (ext-L2-language-specialist)

5 language families (you showed these already):

| Child ID | Language Family Coordinator |
|----------|-----------------------------|
| ext-L3-lang-rust | Rust Coordinator |
| ext-L3-lang-go | Go Coordinator |
| ext-L3-lang-zig | Zig Coordinator |
| ext-L3-lang-typescript | TypeScript Coordinator |
| ext-L3-lang-python | Python Coordinator |

### 4.4 Internal – CIG3 Dynamo (int-L2-cig3)

| Child ID | Role |
|----------|------|
| int-L3-cig3-local | Local Feature Collector (Φ) |
| int-L3-cig3-spectral | Spectral Reducer (Σ) |
| int-L3-cig3-topology | Topology / Persistence (Π) |
| int-L3-cig3-invariant | Ψ Aggregator & Smoother |
| int-L3-cig3-advisor | Invariant Drift Advisor (emits adaptation proposals) |

### 4.5 Internal – Plan Conductor (int-L2-conductor)

| Child ID | Role |
|----------|------|
| int-L3-conductor-expansion | Goal Decomposition & branching |
| int-L3-conductor-ranking | Plan Variant Ranker (MTF/Huffman synergy) |
| int-L3-conductor-scheduler | Phase/parallel scheduling |
| int-L3-conductor-risk | Risk & fallback planner |
| int-L3-conductor-metrics | Plan telemetry consolidator |

### 4.6 Internal – Pneuma Engine (int-L2-pneuma)

| Child ID | Role |
|----------|------|
| int-L3-pneuma-dialogue | Tract Dialogue Balancer |
| int-L3-pneuma-emergence | Emergence Pattern Detector |
| int-L3-pneuma-circuit | Circuit Stress Monitor |
| int-L3-pneuma-resonance | Cross-invariant resonance correlator |
| int-L3-pneuma-advisor | Consciousness Adaptation Advisor |

---

## 5. Level 4 (Prime 7 Branch) – Generative Pattern Definitions

Rather than enumerating 210 agents, we define **branch families** for automatic generation.

### 5.1 Naming Grammar

```
<id> = <parent-id> + "-" + <family-code><index>
<family-code> choices per archetype:
  complexity → "cx"
  duplication → "dup"
  smells → "sm"
  refactor → "rf"
  patterns → "pt"
  rust coordinator children: "rs" + (parser|type|borrow|perf|sec|build|doc) mapped to indices 01..07
```

### 5.2 Example Expansion (Rust Coordinator → 7 children)

| Child ID | Domain Role |
|----------|-------------|
| ext-L4-lang-rust-rs01 | Rust Parser Front-End |
| ext-L4-lang-rust-rs02 | Type Inference Engine |
| ext-L4-lang-rust-rs03 | Borrow/Ownership Analyzer |
| ext-L4-lang-rust-rs04 | Performance Hotspot Profiler |
| ext-L4-lang-rust-rs05 | Security/Lint Auditor |
| ext-L4-lang-rust-rs06 | Build/Crate Integrator |
| ext-L4-lang-rust-rs07 | Documentation Synthesizer |

Apply same template for Go, Zig, TypeScript, Python with domain-appropriate seven-skill sets (parser, type-check, concurrency/memory model, performance, security, packaging, docs).

### 5.3 CIG3 Spectral Child -> 7 specialized decomposition strategies

Example:
- int-L4-cig3-spectral-spec01 (PCA)
- spec02 (Randomized SVD)
- spec03 (Diffusion Maps)
- spec04 (Laplacian Eigen)
- spec05 (Wavelet Scattering)
- spec06 (Incremental / streaming)
- spec07 (Entropy-guided adaptive)

*Mass generation rule stored as JSON pattern config*.

---

## 6. Level 5 (Prime 11 Branch) – Arity Schema

At this scale we only define **attribute matrices**; each L4 agent becomes a *family root* generating 11 micro-agents with role vectors:

```
Vector slots (11):
[collect, normalize, validate, enrich, transform-A, transform-B, correlate, score, persist, emit, adapt]
```

Mapping:
- Assign binary or weight per micro-agent to avoid duplication.
- Deterministic seeding: hash(parent-id) → permutation of 11 canonical suffixes.

Suffix pattern:
```
suffixes = ["c","n","v","e","tA","tB","co","sc","ps","em","ad"]
```
ID example:
```
ext-L5-lang-rust-rs01-c
ext-L5-lang-rust-rs01-n
...
```

---

## 7. Metrics & Adaptation Inheritance Rules

| Layer | Mandatory Metrics | Adaptive Signals Upstream |
|-------|-------------------|---------------------------|
| L2 | success_rate, avg_latency, backlog_depth | emits capacity / drift |
| L3 | domain_specific_quality, error_profile | aggregates to L2 parent |
| L4 | micro_success_rate, specialization_load | threshold triggers scaling hints |
| L5+ | minimal (heartbeat + failure counts) | only bubble anomalies |

**Aggregation Rule:**
```
parent.success_rate = weighted_mean(child_i.success_rate, weight=child_i.invocation_count)
parent.drift = max(child_i.drift_indicator)
```

---

## 8. A2A Capability Export Policy

| Level | Export Policy |
|-------|---------------|
| L2 | Only aggregated capabilities (e.g. `code.analyze`, `architecture.assess`, `cig3.computeInvariant`) |
| L3 | Export **optionally** as parameterized forms (`code.analyze?facet=complexity`) |
| L4+ | Never directly exported (internal specialization) unless whitelisted for debugging |
| Dynamos (CIG3, Pneuma) | Export read-only metrics endpoints (`cig3.getInvariantSummary`, `pneuma.getConsciousnessState`)—no internal mutation invocation from A2A |

---

## 9. Adaptation Hooks (Cross-Cutting)

| Hook Name | Emitted By | Consumed By | Payload Keys |
|-----------|------------|------------|--------------|
| `PLAN_ADVICE` | conductor ranking / risk | planner core | { recommended_plan_mods } |
| `INVARIANT_DRIFT` | cig3-advisor | conductor, pneuma | { psi_delta, suggested_k } |
| `DIALOGUE_BALANCE` | pneuma-dialogue | pole-a, pole-b | { imbalance_ratio } |
| `RESOURCE_STRain` | circuit monitors | boss | { target, throttle_suggestion } |
| `CAPABILITY_RERANK` | pattern learner | code-hound, architecture | { capability_weights } |

---

## 10. Example Full Identity Records (Representative Subset)

### ext-L3-code-hound-refactor

| Field | Value |
|-------|-------|
| id | ext-L3-code-hound-refactor |
| parent_id | ext-L2-code-hound |
| tract | EXTERNAL |
| level | 3 |
| prime_lineage | [2,3,5] |
| archetype | analyzer-refactor |
| core_responsibilities | Suggest refactor opportunities; compute refactor impact score |
| inputs | { repo_snapshot, diff_blocks } |
| outputs | { refactor_candidates[], impact_estimates[] } |
| state | JSON cache of accepted refactors; success ledger |
| metrics | candidate_yield_rate, acceptance_ratio, est_accuracy |
| adaptation_hooks | consumes `CAPABILITY_RERANK`; emits `REFAC_OPPORTUNITY` |
| a2a_export | `code.analyze?facet=refactor` |
| stability | core |

### int-L3-cig3-invariant

| Field | Value |
|-------|-------|
| id | int-L3-cig3-invariant |
| parent_id | int-L2-cig3 |
| tract | INTERNAL |
| level | 3 |
| prime_lineage | [2,3,5] |
| archetype | invariant-aggregator |
| core_responsibilities | Aggregate Ψ across batches; smoothing; anomaly tagging |
| inputs | { partial_invariants[], batch_metadata } |
| outputs | { psi_aggregate, drift_indicator } |
| state | rolling_window.sqlite (or JSON lines), smoothing parameters |
| metrics | psi_mean, psi_std, drift_events |
| adaptation_hooks | emits `INVARIANT_DRIFT`; consumes none |
| a2a_export | `cig3.getInvariantSummary` (read-only) |
| stability | extension |

---

## 11. Deterministic Generation Algorithm (Pseudo)

```python
def generate_children(parent_id, level, prime, taxonomy):
    """
    parent_id: string
    level: int
    prime: next prime branching factor
    taxonomy: list[str] or dynamic pattern generator
    returns list of child IDs
    """
    base = parent_id
    chosen = taxonomy[:prime]  # if longer, slice; if shorter, procedurally extend
    return [f"{base}-{code}" for code in chosen]
```

Taxonomy selection by archetype using registry:
```
taxonomy_map = {
  "language-rust": ["rs01","rs02","rs03","rs04","rs05","rs06","rs07"],
  "cig3-spectral": ["spec01","spec02","spec03","spec04","spec05","spec06","spec07"],
  ...
}
```

---

## 12. Implementation To-Do (Practical Next Steps)

| Step | Action | Artifact |
|------|--------|----------|
| 1 | Serialize above L0–L3 identities into `registry.json` | registry update |
| 2 | Add taxonomy maps for L4 programmatic generation | `taxonomies.json` |
| 3 | Build generator script: `scripts/generate_agents.py` | dynamic expansion |
| 4 | Add adaptation hook enums | `lib/core/adaptation_hooks.py` |
| 5 | Enforce A2A export policy (filter on level ≤3) | gateway check |
| 6 | Persist identity hash for confluence | `IDENTITY_HASH` file |

---

## 13. Identity Hash (Concept)

Canonical ordering:
1. Sort agents by `(level, id)`.
2. Serialize minimal signature fields: `id|parent|level|archetype|prime_lineage`.
3. Hash (blake2s) → used to detect drift between deployments.

---

## 14. Glossary

| Term | Definition |
|------|------------|
| Conceptual Dynamo | Adaptive meta-layer module (e.g., CIG3, Pneuma) living in L2 extension bay |
| Invariant Ψ | Scalar or low-dim vector summarizing structural cognition (compression / topology) |
| Prime Lineage | Sequence of branching primes identifying structural ancestry |
| Quasi-Confluence | Operational equivalence up to tolerance ε in invariant & result metrics |
| Capability Rerank | Weight adjustment broadcast influencing invocation priority |

---

## 15. Change Control

All modifications to L2 or taxonomy seeds require:
1. Proposal PR referencing effect on capability hash.
2. Regeneration of `IDENTITY_HASH`.
3. Update of A2A capability card if exported set changes.

---

*End of Catalog (v0.1.0)*
