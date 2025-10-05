
# Cognitive Invariant Generator (CIG-3) Specification

Pipeline: Ψ = I ∘ Π ∘ Σ ∘ Φ

## 1. Interfaces

- Φ (LocalExtractor): (tokens, aux) -> F ∈ R^{T×d_L}
- Σ (SpectralOperator): F -> {U_k, S_k, energy_fraction}
- Π (DualConstructor): {U_k, S_k, ...} -> {dual_object, persistence, metadata}
- I (InvariantReducer): paired_dict -> scalar Ψ

## 2. Default Configuration (CSD Invariant)

| Parameter | Default | Description |
|-----------|---------|-------------|
| spectral_k_max | 128 | Hard cap on retained components |
| energy_threshold | 0.90 | Cumulative energy fraction target |
| lambda_weight | 0.6 | Energy vs persistence blend |
| homology_dim | 1 | Max dimension for PH (0 & 1) |
| min_persistence | 0.01 | Filter noise bars |

## 3. Invariant Formula

CSD = λ * (retained_energy) + (1-λ) * (Σ lifetimes / normalization)

## 4. Robustness Tests

See table in main README section.

## 5. Failure Modes & Mitigations

(Reference separate section)

## 6. Extensibility

Implement new spectral operators by extending `SpectralOperator` protocol.


# Addition Analysis

# Cognitive Invariant Generator (CIG‑3)  
Mnemonic Lattice: **Local → Spectral → Paired → Invariant (Ψ)**

You’ve got a solid conceptual scaffold. Below is a structured enhancement turning the mnemonic into an implementable, testable pipeline with clear type signatures, mathematical framing, evaluation protocol, extensibility hooks, and integration points with your existing particle / pattern-learning ecosystem.

---

## 1. Formal Layering

| Symbol | Layer Name | Type (Abstract) | Typical Concrete Form | Output Cardinality |
|--------|------------|-----------------|-----------------------|--------------------|
| φ_local | Local Feature Field | Map: Raw Input → $\mathbb{R}^{d_L}$ (possibly multiset / sequence) | n‑gram attention tensor, patch activations, temporal primitives | Many (per token / patch) |
| σ_spectral | Spectral Embedding | Transform: $\mathbb{R}^{d_L \times T} \to \mathbb{R}^{d_S \times k}$ | SVD, FFT, Laplacian eigenvectors, diffusion map, PCA of deltas | Reduced basis components |
| π_paired | Dual Structure Construction | Pairing / Cochain builder: spectral objects → algebraic object | Co-occurrence homology, persistence diagram, cross-basis Gram matrix, contrastive dual | Structured object (graph, chain complex, matrix) |
| Ψ | Emergent Invariant | Functional: π_paired → scalar / vector invariant | Betti signature hash, compression density, spectral entropy fixed point | 1 (or low-dim) |

### Compositional Signature
\[
\Psi = \mathcal{I} \circ \Pi \circ \Sigma \circ \Phi (X)
\]
Where:
- $\Phi$ extracts local micro-features.
- $\Sigma$ performs basis consolidation / globalization.
- $\Pi$ forms a dual object enabling invariant formation.
- $\mathcal{I}$ final invariant extraction (fixed point, minimizer, attractor, compression functional).

---

## 2. Design Goals of Ψ (Pick One or Combine)

| Invariant Family | Description | Mathematical Proxy |
|------------------|-------------|--------------------|
| Compressive Semantic Density (CSD) | “How densely meaningful content can be compressed without semantic loss.” | Ratio: (Info preserved in low-rank spectral slice) / (Raw tokens entropy) |
| Stability Index | Resistance to perturbations of φ_local | Lipschitz constant / normalized Jacobian norm |
| Structural Entropy Drop | Redundancy removed after spectral basis & pairing | $H(\text{tokens}) - H(\text{spectral coefficients})$ |
| Homological Persistence Core | Persistent features across resolution scales | Count / weighted persistence of top k features |
| Attractor Convergence | Fixed-point signature of iterative refinement | Distance to stable embedding across iterations |

---

## 3. Concrete Algorithm (AG News Example: CSD Variant)

### Input
Tokenized batch: $X = \{x_1, \dots, x_T\}$; attention maps $A \in \mathbb{R}^{H \times T \times T}$ from a transformer.

### Step 1: Local (φ_local)
1. Aggregate per-token saliency vector:  
   \( s_t = \text{mean}_h A_{h,t,:} \in \mathbb{R}^{T} \)  
2. Construct local feature matrix: \( F \in \mathbb{R}^{T \times T} \) (or truncated).
3. Optional normalization: row-stochastic or symmetric Laplacian form.

Output: \( F \) (local interaction field).

### Step 2: Spectral (σ_spectral)
1. Compute SVD / truncated eigendecomposition:  
   \( F \approx U_k \Sigma_k V_k^\top \)
2. Retain top k singular triplets capturing cumulative energy ≥ threshold α (e.g. 0.9).
3. Derive delta basis (temporal / cross-layer differences) if using “attention deltas”:
   \( D = F^{(layer\;l)} - F^{(layer\;l-1)} \) → SVD on D.

Output: \( B = \{(u_i, \sigma_i)\}_{i=1..k} \)

### Step 3: Paired (π_paired)
Construct dual object enabling invariant:
Options:
- **Cluster-based pairing**: Project tokens into spectral subspace \( Z = F U_k \) then cluster → cluster adjacency graph.
- **Homology pairing**: Treat distance graph over \( Z \), build Vietoris–Rips filtration, compute persistent homology.
- **Concept alignment**: Compare spectral atoms with a library of concept vectors (e.g. centroid embeddings) → similarity matrix \( M \in \mathbb{R}^{k \times C} \).

Choose: For CSD, use homology + spectral energy pairing.

Output: Pair \((\Sigma_k, \text{PersistenceDiagram})\).

### Step 4: Invariant (Ψ)
Define CSD score:
\[
\text{CSD} = \lambda \cdot \frac{\sum_{i=1}^{k} \sigma_i}{\sum_{j} \sigma_j^{\text{(all)}}} 
+ (1-\lambda)\cdot \frac{\sum_{p \in \text{Diag}} \text{life}(p)}{\text{Normalization}}
\]
- First term: retained compression energy fraction
- Second term: weighted total persistence (structural richness)
- λ tunes balance (e.g. 0.6)

Output: Scalar Ψ per sample or per batch.

---

## 4. Typing & Interfaces

```python
from typing import Protocol, Any, List, Tuple, Dict
import numpy as np

class LocalExtractor(Protocol):
    def __call__(self, tokens: List[str], aux: Dict[str, Any]) -> np.ndarray: ...

class SpectralOperator(Protocol):
    def __call__(self, F: np.ndarray) -> Dict[str, Any]: ...

class DualConstructor(Protocol):
    def __call__(self, spectral: Dict[str, Any]) -> Dict[str, Any]: ...

class InvariantReducer(Protocol):
    def __call__(self, paired: Dict[str, Any]) -> float: ...
```

---

## 5. Alternative Choices by Slot

| Slot | Option A (Fast) | Option B (Richer) | Option C (Research) |
|------|-----------------|-------------------|---------------------|
| φ_local | n-gram TF-IDF matrix | Multi-head mean attention delta | Patchwise causal attribution |
| σ_spectral | PCA / Truncated SVD | Diffusion maps / Laplacian eigen | Wavelet packet / scattering transform |
| π_paired | Gram matrix vs concept library | Persistent homology (Ripser) | Higher categorical nerve (experimental) |
| Ψ | Energy ratio | Energy + persistence fusion | Fixed-point iterative contraction metric |

---

## 6. Invariance & Robustness Tests

| Test | Procedure | Expected Stable Behavior |
|------|-----------|--------------------------|
| Token Shuffle (within low-saliency zones) | Randomly permute low-attention tokens | CSD changes < ε |
| Noise Injection | Add embedding Gaussian noise | Smooth decay of CSD, no spikes |
| Synonym Substitution | Replace nouns with synonyms | Small variation; persistence topology stable |
| Compression Stress | Apply aggressive subword dropping | CSD decreases predictably (monotonic) |
| Scale Drift | Increase sequence length with padding | CSD normalized (length-invariant scaling) |

---

## 7. Particle Integration (Your Ecosystem)

| Particle | Role in Pipeline |
|----------|------------------|
| `attention_extractor` | Implements φ_local |
| `spectral_reducer` | Implements σ_spectral |
| `topology_builder` | Implements π_paired (e.g., builds VR filtration) |
| `invariant_computer` | Produces Ψ and posts metric |
| `csd_aggregator` | Aggregates CSD over corpus; updates pattern_learner |
| `invariant_reporter` | Publishes daily invariants to orchestrator |

You can orchestrate these via a Plan:
```
Plan:
  1. attention_extractor (per batch)
  2. spectral_reducer
  3. topology_builder
  4. invariant_computer
  5. csd_aggregator
```

---

## 8. Pattern Learner Feedback Loop

- Feed Ψ time series into pattern_learner as a new “optimization pattern” dimension.
- Detect shifts: ΔΨ > threshold → trigger adaptive re-composition (e.g., adjust k).
- Store persistence diagram sketches → cluster for emergent semantic regimes.

---

## 9. Complexity & Scaling

| Component | Time (Approx) | Notes |
|-----------|---------------|------|
| φ_local (attention aggregation) | O(H·T²) baseline (can prune) | Use sparsification (top-k heads) |
| σ_spectral (SVD k) | O(T²k) (randomized SVD → O(T·k²)) | Use randomized algorithms |
| π_paired (homology) | Worst O(n^{⌈d/3⌉}) | Keep dimension ≤ 1 or use witness complexes |
| Invariant reduction | O(k + |Diag|) | Usually negligible |

Optimization:
- Downsample tokens with low saliency before topology.
- Use approximate PH (giotto-tda, ripser++).
- Cache spectral bases per domain.

---

## 10. Evaluation Metrics

| Metric | Purpose | Calculation |
|--------|---------|-------------|
| CSD Variance Across Augmentations | Robustness | Var(Ψ_aug) |
| Predictive Utility | Correlate with downstream accuracy / perplexity | Pearson/Spearman(Ψ, task metric) |
| Compression Predictivity | Correlate with gzip/bpe compression ratio | corr(Ψ, compression_gain) |
| Drift Sensitivity | Early detection | KL divergence of Ψ distribution windows |
| Topological Stability | Structural robustness | Bottleneck distance between diagrams |

---

## 11. Failure / Anti-Pattern Detection

| Symptom | Cause | Fix |
|---------|-------|-----|
| Ψ saturates at 1.0 | Over-retaining energy (k too large) | Lower k or raise α threshold |
| Ψ nearly zero always | Local features weakly structured | Switch φ_source or improve normalization |
| High variance run-to-run | Stochastic SVD instability | Fix random seed / use power iterations |
| Persistence term dominates | Scale mismatch | Rescale: normalize lifetimes to [0,1] before fusion |
| Drift undetected | Invariant too coarse | Add multi-scale Ψ vector (per k slice) |

---

## 12. Future Extensions

| Direction | Idea |
|-----------|------|
| Multi-Ψ Vector | Track (energy fraction, persistence, spectral entropy) triple |
| Recursive CIG (CIG‑k) | Reapply pipeline on clusters produced by π_paired |
| Cross-Domain Alignment | Use canonical correlation in σ stage across domains |
| Adaptive k | Choose k minimizing MDL or AIC-like penalty |
| Differentiable Ψ | Backpropagatable invariant for representation learning |

---

## 13. Deliverable Files (Spec + Prototype)

Below are ready-to-drop starter files.

````markdown name=docs/cig3_spec.md
# Cognitive Invariant Generator (CIG-3) Specification

Pipeline: Ψ = I ∘ Π ∘ Σ ∘ Φ

## 1. Interfaces

- Φ (LocalExtractor): (tokens, aux) -> F ∈ R^{T×d_L}
- Σ (SpectralOperator): F -> {U_k, S_k, energy_fraction}
- Π (DualConstructor): {U_k, S_k, ...} -> {dual_object, persistence, metadata}
- I (InvariantReducer): paired_dict -> scalar Ψ

## 2. Default Configuration (CSD Invariant)

| Parameter | Default | Description |
|-----------|---------|-------------|
| spectral_k_max | 128 | Hard cap on retained components |
| energy_threshold | 0.90 | Cumulative energy fraction target |
| lambda_weight | 0.6 | Energy vs persistence blend |
| homology_dim | 1 | Max dimension for PH (0 & 1) |
| min_persistence | 0.01 | Filter noise bars |

## 3. Invariant Formula

CSD = λ * (retained_energy) + (1-λ) * (Σ lifetimes / normalization)

## 4. Robustness Tests

See table in main README section.

## 5. Failure Modes & Mitigations

(Reference separate section)

## 6. Extensibility

Implement new spectral operators by extending `SpectralOperator` protocol.

````

```python name=lib/cig3/pipeline.py
from dataclasses import dataclass
from typing import List, Dict, Any
import numpy as np
from numpy.linalg import svd

try:
    import ripser  # optional
    HAVE_RIPSER = True
except ImportError:
    HAVE_RIPSER = False


@dataclass
class CIG3Config:
    energy_threshold: float = 0.90
    k_max: int = 128
    lambda_weight: float = 0.6
    homology_dim: int = 1
    min_persistence: float = 0.01


def local_attention_extractor(tokens: List[str], attention: np.ndarray) -> np.ndarray:
    """
    tokens: length T list
    attention: shape (H, T, T)
    Returns F: (T, T) aggregated local feature matrix
    """
    assert attention.ndim == 3
    F = attention.mean(axis=0)  # (T,T)
    # Optional normalization (symmetric)
    F = 0.5 * (F + F.T)
    return F


def truncated_spectral(F: np.ndarray, cfg: CIG3Config) -> Dict[str, Any]:
    U, S, VT = svd(F, full_matrices=False)
    total = S.sum()
    cumulative = np.cumsum(S) / total
    k = int(np.searchsorted(cumulative, cfg.energy_threshold)) + 1
    k = min(k, cfg.k_max)
    return {
        "U_k": U[:, :k],
        "S_k": S[:k],
        "energy_fraction": S[:k].sum() / total,
        "k": k
    }


def build_persistence(spectral: Dict[str, Any], cfg: CIG3Config) -> Dict[str, Any]:
    if not HAVE_RIPSER:
        return {
            "persistence": [],
            "lifetimes_sum": 0.0,
            "note": "ripser not installed"
        }
    # Project original basis points
    # Coordinates: X = U_k * diag(S_k) to weight by singular values
    U_k = spectral["U_k"]
    S_k = spectral["S_k"]
    X = U_k * S_k  # broadcast weighting
    # Compute PH in low dimension
    res = ripser.ripser(X, maxdim=cfg.homology_dim)
    dgms = res["dgms"]
    lifetimes = []
    for dim_dgm in dgms:
        for birth, death in dim_dgm:
            life = death - birth
            if np.isfinite(life) and life >= cfg.min_persistence:
                lifetimes.append(life)
    lifetimes_sum = float(np.sum(lifetimes)) if lifetimes else 0.0
    return {
        "persistence": lifetimes,
        "lifetimes_sum": lifetimes_sum
    }


def invariant_csd(spectral: Dict[str, Any], paired: Dict[str, Any], cfg: CIG3Config) -> float:
    energy = spectral["energy_fraction"]
    persistence = paired["lifetimes_sum"]
    # Normalize persistence (simple heuristic)
    norm_persistence = persistence / (spectral["k"] + 1e-8)
    return cfg.lambda_weight * energy + (1 - cfg.lambda_weight) * norm_persistence


def compute_cig3(tokens: List[str],
                 attention: np.ndarray,
                 cfg: CIG3Config = CIG3Config()) -> Dict[str, Any]:
    F = local_attention_extractor(tokens, attention)
    spectral = truncated_spectral(F, cfg)
    paired = build_persistence(spectral, cfg)
    psi = invariant_csd(spectral, paired, cfg)
    return {
        "Ψ": psi,
        "spectral_k": spectral["k"],
        "energy_fraction": spectral["energy_fraction"],
        "persistence_count": len(paired["persistence"]),
        "persistence_sum": paired.get("lifetimes_sum", 0.0)
    }
```

```python name=lib/cig3/evaluation.py
import numpy as np
from typing import Callable, Dict, Any, List
from .pipeline import compute_cig3, CIG3Config

def perturb_shuffle(tokens: List[str], frac: float = 0.1) -> List[str]:
    n = len(tokens)
    k = max(1, int(frac * n))
    idx = np.random.choice(n, k, replace=False)
    tokens_new = tokens.copy()
    subset = [tokens_new[i] for i in idx]
    np.random.shuffle(subset)
    for i, val in zip(idx, subset):
        tokens_new[i] = val
    return tokens_new

def robustness_profile(tokens: List[str],
                       attention: np.ndarray,
                       cfg: CIG3Config,
                       trials: int = 8) -> Dict[str, Any]:
    base = compute_cig3(tokens, attention, cfg)
    psi_base = base["Ψ"]
    deltas = []
    for _ in range(trials):
        t2 = perturb_shuffle(tokens)
        # (Assume attention unchanged for lexical shuffle)
        res = compute_cig3(t2, attention, cfg)
        deltas.append(abs(res["Ψ"] - psi_base))
    return {
        "base_Ψ": psi_base,
        "mean_abs_delta": float(np.mean(deltas)),
        "max_abs_delta": float(np.max(deltas)),
        "stable": float(np.mean(deltas)) < 0.05
    }
```

---

## 14. Practical Next Steps

| Priority | Action | Outcome |
|----------|--------|---------|
| High | Implement pipeline on a small AG News subset | Sanity check Ψ distribution |
| High | Add persistence library (ripser / giotto-tda) | Enable π_paired homology mode |
| Medium | Plug Ψ into pattern_learner as additional feature | Detect macro-pattern shifts |
| Medium | Build particles: `attention_extractor`, `spectral_reducer`, `topology_builder`, `invariant_computer` | Architectural alignment |
| Medium | Add robustness profile test to CI | Early regression signal |
| Low | Introduce alternative spectral operator (diffusion maps) | Comparative study |
| Low | Extend invariant to vector (energy, entropy, persistence) | Richer analytics |

---

## 15. Validation Checklist

- [ ] Ψ reproducible under fixed seed.
- [ ] Ψ variance under benign perturbations < threshold.
- [ ] Ψ correlates with compression ratio (gzip/BPE) positively.
- [ ] Persistence component non-zero for >30% of samples (else adjust min_persistence).
- [ ] Spectral k distribution not collapsing (monitor mean k).

---

## 16. Optional Extensions

| Extension | Benefit |
|-----------|---------|
| Multi-head differential φ (layer-to-layer delta attention) | Captures semantic shift depth |
| Persistent cohomology pairing | Orientation-sensitive signal |
| Entropic weighting of singular values before persistence | Emphasizes rare structured modes |
| Adaptive λ via cross-validation on predictive auxiliary task | Auto-tuned invariant blend |

---

## 17. Summary

Your mnemonic lattice is now a typed, testable compositional pipeline:
**Local (Φ) → Spectral (Σ) → Paired (Π) → Invariant (Ψ)**

This bridges:
- Local saliency patterns
- Global compressed bases
- Dual algebraic / topological structure
- A scalar (or vector) invariant capturing compressive semantic density and structural richness.

Let me know if you’d like:
1. A particleization mapping (actual class stubs for your architecture).
2. A notebook-ready demo outline.
3. A variant for multimodal inputs (text + image patches).

Just pick one and I’ll generate it.
