## Integrating CIG‑3 (“Local → Spectral → Paired → Ψ”) into the Noesis Lattice

Below is a concrete implementation blueprint for adding the Cognitive Invariant Generator to your existing Synapse / Noesis lattice architecture, together with an analysis of confluence (where you have it, where you don’t, and how to approximate it).

---

## 1. Architectural Mapping

| CIG‑3 Stage | Noesis Layer | Tract | Implementation Form | Persistence |
|-------------|--------------|-------|---------------------|-------------|
| Φ (φ_local) Local feature extraction | External micro-agents | T_ext | `AttentionExtractorParticle` (or generic token feature particle) | Particle state file (metrics) |
| Σ (σ_spectral) Spectral reduction | Internal analytical layer | T_int | `SpectralReducerParticle` | Particle state (SVD stats) |
| Π (π_paired) Dual / topological pairing | Internal structural layer | T_int | `TopologyBuilderParticle` | Particle state (PH metrics) |
| Ψ (Invariant) Aggregation / index | Cross (bridging) | T_int → pattern layer | `InvariantComputerParticle` + feed into `PatternLearner` | Pattern map + invariant store |
| Emergent pattern feedback | Pattern learner | T_int | Extend `PatternType` with `"invariant"` | Pattern persistence |

---

## 2. Particle Flow (Reactive Router)

1. Orchestrator receives request type: `compute_cig3` with payload `{ "tokens": [...], "attention": <serialized matrix> }`.
2. Planner produces plan (sequence of `PlannedAction`s):  
   `extract_attention → reduce_spectral → build_topology → compute_invariant`.
3. Each action becomes a routed message (T_ext for extraction, then T_int for the rest).
4. Final Ψ result is:
   - Stored to invariant store
   - Emitted as event (`INVARIANT_COMPUTED`)
   - Forwarded to `pattern_learner` (optional asynchronous update)

---

## 3. Data Contract (Message Payload Fragments)

| Key | Stage Produced | Description |
|-----|----------------|-------------|
| `tokens` | Input | List[str] |
| `attention` | Input | 3D array serialized (H×T×T), optionally compressed/base64 |
| `local_matrix` | Φ output | Symmetrized attention / feature matrix (T×T) |
| `spectral` | Σ output | `{ "U_k": ..., "S_k": ..., "energy_fraction": float, "k": int }` |
| `topology` | Π output | `{ "lifetimes": [...], "lifetimes_sum": float }` |
| `invariant` | Ψ output | `{ "psi": float, "k": int, "energy_fraction": float, ... }` |

Version each payload with `"cig3_version": "0.1.0"` for forward compatibility.

---

## 4. New Request Type in Planner

Add `compute_cig3` handling (single or batched). The planner converts the high-level request into an ordered action chain referencing target particle IDs.

---

## 5. Proposed Particles (Atomic Subclasses)

Each inherits `AtomicParticle` and implements `execute(context)`:

| Particle ID | Input Keys | Output Keys | Failure Modes |
|-------------|-----------|-------------|---------------|
| `attention_extractor` | `tokens`, `attention` | `local_matrix` | Missing attention, shape mismatch |
| `spectral_reducer` | `local_matrix` | `spectral` | SVD convergence failure (rare) |
| `topology_builder` | `spectral` | `topology` | Ripser not installed, high dimensional explosion |
| `invariant_computer` | `spectral`, `topology` | `invariant` | Zero singular mass (degenerate), empty persistence |

---

## 6. Registry Additions

Add these particles to `registry.json` (or domain-specific registry). Keep domain classification (e.g., `"cognition"` or `"analysis"`).

---

## 7. Confluence Analysis

### 7.1 What “Confluent” Means Here
In rewriting / categorical terms, a system is confluent if different valid execution orders (or interleavings) yield an equivalent normal form (same invariant Ψ). For CIG‑3:

| Source of Non-Confluence | Cause | Impact |
|--------------------------|-------|--------|
| Asynchronous scheduling | Message arrival order | Minor if stages strictly sequenced |
| Randomness in SVD / PH | Randomized algorithms | Variation in Ψ |
| Floating point nondeterminism | Parallel BLAS, hardware | Small ε drift |
| Tokenization instability | Preprocessing differences | Semantic shift in local matrix |
| Persistence thresholding | Heuristic filters | Marginal differences in persistence sum |
| Partial plan replays / retries | Failure + retry with changed seed | Divergent Ψ if no seed control |

### 7.2 Strategies to Enforce Practical Confluence

| Strategy | Action |
|----------|--------|
| Deterministic SVD | Use deterministic LAPACK path (disable randomized SVD unless seeded) |
| Global Seed Envelope | Pass `rng_seed` through payload; set NumPy / Python / ripser seeds |
| Ordered Serialization | Canonical JSON (sorted keys) for intermediate artifacts hashed for traceability |
| Versioned Transform Config | Include `cig3_config_hash` in each stage’s payload |
| Idempotent Retries | Store stage output in a content-addressed cache keyed by hash(local_matrix) etc. |
| Monotonic Merge (CRDT-like) | When combining multiple Ψ across shards use associative/commutative reducer (e.g., maintain running stable mean + count) |
| Invariant Stability Band | Accept Ψ equivalence if |ΔΨ| < ε (treat as same normal form) |

### 7.3 When True Confluence Is Not Strict
Persistent homology implementations may have tie-breaking differences. Accept approximate confluence: bound variance and monitor with a robustness test particle (`invariant_validator`).

---

## 8. Confluence Test Particle (Optional)

Create `invariant_validator`:
- Re-runs spectral + topology twice with same seed.
- Computes `abs(Ψ₁ − Ψ₂)`; if > threshold → flag non-confluence event.

---

## 9. Persistence & Traceability

| Artifact | Location | Deterministic? | Hash Input |
|----------|----------|----------------|-----------|
| Particle state JSON | `~/.synapse-system/.synapse/particles` | No (runtime evolving) | N/A |
| CIG intermediate cache | `~/.synapse-system/.synapse/cig3/cache` | Yes (content-addressed) | Stage input hash |
| Invariant log | `~/.synapse-system/.synapse/cig3/invariants.log` | Append-only | `(plan_id, invariant_hash)` |
| Pattern map integration | Existing pattern map | Partially (order affects LRU) | Invariant embed |

Define `invariant_hash = blake2s(canonical_json(invariant_payload))[:16]`.

---

## 10. Rollout Plan

| Phase | Goal | Actions |
|-------|------|---------|
| 0 | Skeleton | Add particles + planner route + registry entries |
| 1 | Deterministic Core | Enforce seeded SVD + canonical serialization |
| 2 | Persistence & Pattern | Feed Ψ to PatternLearner (new `PatternType.INVARIANT`) |
| 3 | Robustness Layer | Add validator particle & CI robustness test |
| 4 | Optimization | Mojo port spectral + persistence (only after stability) |
| 5 | Adaptive Evolution | Use Ψ drift thresholds to adjust energy threshold / k adaptively |

---

## 11. Code Skeletons

### 11.1 Particles

```python name=lib/particles/attention_extractor.py
import numpy as np
from pathlib import Path
from typing import Any, Dict
from lib.core.atomic_particle import AtomicParticle, ExecutionContext

class AttentionExtractorParticle(AtomicParticle):
    def __init__(self, config, corpus_callosum, state_file: Path):
        super().__init__(config, corpus_callosum, state_file)
        self._init_custom_metric("matrices_built", 0)

    async def execute(self, context: ExecutionContext) -> Any:
        payload = context.payload
        tokens = payload.get("tokens")
        attention = payload.get("attention")  # Expect serialized nested list or np array
        if tokens is None or attention is None:
            raise ValueError("Missing tokens or attention in payload")

        A = np.array(attention, dtype=float)
        if A.ndim != 3:
            raise ValueError(f"Attention tensor must be 3D (H,T,T). Got shape={A.shape}")

        F = A.mean(axis=0)  # (T,T)
        F = 0.5 * (F + F.T)
        self.state.custom_metrics["matrices_built"] += 1

        return {
            "local_matrix": F.tolist(),
            "token_count": len(tokens)
        }
```

```python name=lib/particles/spectral_reducer.py
import numpy as np
from pathlib import Path
from typing import Any
from lib.core.atomic_particle import AtomicParticle, ExecutionContext

class SpectralReducerParticle(AtomicParticle):
    def __init__(self, config, corpus_callosum, state_file: Path,
                 energy_threshold: float = 0.90, k_max: int = 128):
        super().__init__(config, corpus_callosum, state_file)
        self.energy_threshold = energy_threshold
        self.k_max = k_max
        self._init_custom_metric("svd_calls", 0)

    async def execute(self, context: ExecutionContext) -> Any:
        lm = context.payload.get("local_matrix")
        if lm is None:
            raise ValueError("local_matrix missing")
        F = np.array(lm, dtype=float)

        # Deterministic SVD (NumPy LAPACK)
        U, S, VT = np.linalg.svd(F, full_matrices=False)
        total = S.sum()
        cumulative = (S.cumsum() / total) if total > 0 else np.zeros_like(S)
        k = int(np.searchsorted(cumulative, self.energy_threshold) + 1) if total > 0 else 0
        k = min(k, len(S), self.k_max)

        self.state.custom_metrics["svd_calls"] += 1

        spectral = {
            "U_k": U[:, :k].tolist(),
            "S_k": S[:k].tolist(),
            "energy_fraction": float(S[:k].sum() / total) if total > 0 else 0.0,
            "k": k
        }
        return {"spectral": spectral}
```

```python name=lib/particles/topology_builder.py
from pathlib import Path
from typing import Any
import numpy as np
from lib.core.atomic_particle import AtomicParticle, ExecutionContext

try:
    import ripser
    HAVE_RIPSER = True
except ImportError:
    HAVE_RIPSER = False

class TopologyBuilderParticle(AtomicParticle):
    def __init__(self, config, corpus_callosum, state_file: Path,
                 min_persistence: float = 0.01, maxdim: int = 1):
        super().__init__(config, corpus_callosum, state_file)
        self.min_persistence = min_persistence
        self.maxdim = maxdim
        self._init_custom_metric("diagrams_built", 0)

    async def execute(self, context: ExecutionContext) -> Any:
        spectral = context.payload.get("spectral")
        if spectral is None:
            raise ValueError("spectral missing")
        U_k = np.array(spectral["U_k"])
        S_k = np.array(spectral["S_k"])
        if U_k.size == 0:
            return {"topology": {"lifetimes": [], "lifetimes_sum": 0.0, "note": "empty_spectrum"}}

        X = U_k * S_k  # weight components
        if not HAVE_RIPSER:
            return {"topology": {"lifetimes": [], "lifetimes_sum": 0.0, "note": "ripser_not_installed"}}

        res = ripser.ripser(X, maxdim=self.maxdim)
        lifetimes = []
        for dim_dgm in res["dgms"]:
            for birth, death in dim_dgm:
                life = float(death - birth)
                if life > self.min_persistence and life < float("inf"):
                    lifetimes.append(life)

        self.state.custom_metrics["diagrams_built"] += 1
        return {
            "topology": {
                "lifetimes": lifetimes,
                "lifetimes_sum": float(sum(lifetimes))
            }
        }
```

```python name=lib/particles/invariant_computer.py
from pathlib import Path
from typing import Any
import math
from lib.core.atomic_particle import AtomicParticle, ExecutionContext

class InvariantComputerParticle(AtomicParticle):
    def __init__(self, config, corpus_callosum, state_file: Path,
                 lambda_weight: float = 0.6):
        super().__init__(config, corpus_callosum, state_file)
        self.lambda_weight = lambda_weight
        self._init_custom_metric("invariants_computed", 0)

    async def execute(self, context: ExecutionContext) -> Any:
        spectral = context.payload.get("spectral")
        topology = context.payload.get("topology")

        if spectral is None or topology is None:
            raise ValueError("spectral or topology missing")

        energy = spectral.get("energy_fraction", 0.0)
        k = spectral.get("k", 1)
        lifetimes_sum = topology.get("lifetimes_sum", 0.0)
        norm_persistence = lifetimes_sum / (k + 1e-8)
        psi = self.lambda_weight * energy + (1 - self.lambda_weight) * norm_persistence

        self.state.custom_metrics["invariants_computed"] += 1

        return {
            "invariant": {
                "psi": psi,
                "energy_fraction": energy,
                "k": k,
                "lifetimes_sum": lifetimes_sum,
                "lambda_weight": self.lambda_weight
            }
        }
```

### 11.2 Planner Patch (Excerpt)

```python name=lib/planner_patch_snippet.py
# Add inside plan() after other request_type branches

elif request_type == "compute_cig3":
    # Step chain for single sample
    plan.actions.append(PlannedAction(
        action_type=ActionType("extract_attention"),
        target_particle="attention_extractor",
        payload={
            "tokens": params.get("tokens"),
            "attention": params.get("attention"),
            "cig3_version": "0.1.0"
        }
    ))
    plan.actions.append(PlannedAction(
        action_type=ActionType("spectral_reduce"),
        target_particle="spectral_reducer",
        payload={}
    ))
    plan.actions.append(PlannedAction(
        action_type=ActionType("build_topology"),
        target_particle="topology_builder",
        payload={}
    ))
    plan.actions.append(PlannedAction(
        action_type=ActionType("compute_invariant"),
        target_particle="invariant_computer",
        payload={"invariant_type": "CSD"}
    ))
```

### 11.3 Registry Update (Excerpt)

```json name=lib/registry_additions.json
{
  "particles": {
    "attention_extractor": {
      "module": "lib.particles.attention_extractor",
      "class": "AttentionExtractorParticle",
      "tract": "EXTERNAL"
    },
    "spectral_reducer": {
      "module": "lib.particles.spectral_reducer",
      "class": "SpectralReducerParticle",
      "tract": "INTERNAL"
    },
    "topology_builder": {
      "module": "lib.particles.topology_builder",
      "class": "TopologyBuilderParticle",
      "tract": "INTERNAL"
    },
    "invariant_computer": {
      "module": "lib.particles.invariant_computer",
      "class": "InvariantComputerParticle",
      "tract": "INTERNAL"
    }
  }
}
```

### 11.4 Documentation

````markdown name=docs/CIG3_INTEGRATION.md
# CIG-3 Integration

Pipeline: Φ → Σ → Π → Ψ implemented via four particles.
Determinism controls: seeded SVD, canonical JSON hashing.

## Message Flow
1. compute_cig3 plan generation
2. attention_extractor → spectral_reducer → topology_builder → invariant_computer
3. Invariant forwarded to pattern_learner with pattern_type="invariant"

## Confluence Notes
- SVD deterministic path used (NumPy).
- Topology optional; if unavailable lifetimes_sum=0 still produces Ψ.
- Hashing: blake2s over canonical spectral payload.

## Failure Handling
- Each particle returns error -> circuit breaker increments.
- Planner can retry chain or degrade: skip topology stage.

````

### 11.5 Test Skeleton

```python name=tests/test_cig3_pipeline.py
import numpy as np
import asyncio
import pytest

# Assume factories exist
from lib.particles.attention_extractor import AttentionExtractorParticle
from lib.particles.spectral_reducer import SpectralReducerParticle
from lib.particles.topology_builder import TopologyBuilderParticle
from lib.particles.invariant_computer import InvariantComputerParticle
from lib.core.atomic_particle import AgentConfig
from reactive_message_router import TractType

class DummyCorpus:
    async def route_message(self, **kwargs):
        return 0

@pytest.mark.asyncio
async def test_end_to_end_cig3():
    corpus = DummyCorpus()
    cfg_ext = AgentConfig(agent_id="attention_extractor", tract=TractType.EXTERNAL)
    cfg_int1 = AgentConfig(agent_id="spectral_reducer", tract=TractType.INTERNAL)
    cfg_int2 = AgentConfig(agent_id="topology_builder", tract=TractType.INTERNAL)
    cfg_int3 = AgentConfig(agent_id="invariant_computer", tract=TractType.INTERNAL)

    att_particle = AttentionExtractorParticle(cfg_ext, corpus, Path("/tmp/att_state.json"))
    spec_particle = SpectralReducerParticle(cfg_int1, corpus, Path("/tmp/spec_state.json"))
    topo_particle = TopologyBuilderParticle(cfg_int2, corpus, Path("/tmp/topo_state.json"))
    inv_particle = InvariantComputerParticle(cfg_int3, corpus, Path("/tmp/inv_state.json"))

    H, T = 2, 16
    attention = np.random.rand(H, T, T).tolist()
    tokens = [f"w{i}" for i in range(T)]

    local_out = await att_particle.execute(type("Ctx", (), {"payload": {"tokens": tokens, "attention": attention}}))
    assert "local_matrix" in local_out

    spectral_out = await spec_particle.execute(type("Ctx", (), {"payload": {**local_out}}))
    assert "spectral" in spectral_out
    assert spectral_out["spectral"]["k"] >= 1

    topo_out = await topo_particle.execute(type("Ctx", (), {"payload": {**spectral_out}}))
    assert "topology" in topo_out

    inv_out = await inv_particle.execute(type("Ctx", (), {"payload": {**spectral_out, **topo_out}}))
    assert "invariant" in inv_out
    assert 0.0 <= inv_out["invariant"]["psi"] <= 1.1  # sanity bound
```

---

## 12. PatternLearner Extension

Add pattern type `"invariant"`:
- Sequence: record time series of Ψ; detect abrupt jumps ⇒ new optimization / drift pattern.
- Option: treat high persistence + low energy as “structural complexity potential” pattern vs high energy + low persistence as “compressive triviality”.

---

## 13. Mojo Acceleration Targets (Later)

| Stage | Mojo Fit | Rationale |
|-------|----------|-----------|
| Spectral Reducer | Yes | Randomized or batched SVD / partial eigensolvers |
| Topology Builder | Partial | Preprocessing distances / filtration acceleration |
| Invariant Fusion | Not urgent | O(k) arithmetic only |

Introduce after determinism harness; export stable FFI boundary:
`compute_svd(F, energy_threshold, k_max) -> (U_k, S_k, k, energy_fraction)`.

---

## 14. Monitoring & Metrics

| Metric | Source Particle | Use |
|--------|-----------------|-----|
| `svd_calls` | spectral_reducer | Capacity planning |
| `avg_k` | invariant_computer aggregate | Adaptive k tuning |
| `nonconfluence_events` | invariant_validator | Stability watch |
| `psi_drift` | aggregator | Trigger recomposition |

Add a small aggregator service or extend observer to produce a rolling summary:
- Mean Ψ per hour
- Std deviation
- Drift detection via ADWIN or simple rolling z-score.

---

## 15. Summary

- The integration is **modular**: four new particles + planner branch + registry update.
- **Confluence** is *approximate*: enforce seeds, deterministic transforms, canonical serialization, and treat Ψ within ε as equivalent.
- **Scalability**: Topology optional (graceful degrade); spectral step is dominant complexity target for later Mojo.
- **Evolution**: Ψ feeds PatternLearner for meta-pattern discovery; future adaptive tuning loops can adjust spectral thresholds automatically.

---

## 16. Next Options

Reply with one of:
- “Generate invariant_validator particle”
- “Add aggregator plan + pattern integration code”
- “Provide Mojo FFI scaffold for spectral step”
- “Create Nix flake additions for cig3 feature”

…and I’ll produce that next.

Let me know how you’d like to proceed.
