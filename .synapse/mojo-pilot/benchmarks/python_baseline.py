"""
Python Baseline - Pattern Search Implementation
Purpose: Establish performance baseline for Mojo comparison
"""

import time
import numpy as np
from typing import List, Tuple


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors"""
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def pattern_search_python(
    query_vector: np.ndarray,
    pattern_vectors: List[np.ndarray],
    top_k: int = 10
) -> List[Tuple[int, float]]:
    """
    Search for most similar patterns using vector similarity.

    Args:
        query_vector: Query embedding (1024-dim for BGE-M3)
        pattern_vectors: List of pattern embeddings
        top_k: Number of results to return

    Returns:
        List of (pattern_id, similarity_score) tuples
    """
    similarities = []

    for idx, pattern_vec in enumerate(pattern_vectors):
        score = cosine_similarity(query_vector, pattern_vec)
        similarities.append((idx, score))

    # Sort by score descending
    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities[:top_k]


def generate_test_data(
    num_patterns: int = 1000,
    embedding_dim: int = 1024
) -> Tuple[np.ndarray, List[np.ndarray]]:
    """Generate synthetic test data"""
    np.random.seed(42)

    query = np.random.randn(embedding_dim).astype(np.float32)
    patterns = [
        np.random.randn(embedding_dim).astype(np.float32)
        for _ in range(num_patterns)
    ]

    return query, patterns


def benchmark_pattern_search(
    num_patterns: int = 1000,
    num_iterations: int = 100,
    top_k: int = 10
):
    """Run benchmark on pattern search"""
    print("🐍 Python Baseline Benchmark")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Patterns: {num_patterns}")
    print(f"  Iterations: {num_iterations}")
    print(f"  Top-K: {top_k}")
    print(f"  Embedding dimension: 1024 (BGE-M3)")
    print()

    # Generate test data
    print("Generating test data...")
    query, patterns = generate_test_data(num_patterns)
    print(f"  Query shape: {query.shape}")
    print(f"  Pattern count: {len(patterns)}")
    print()

    # Warmup
    print("Warmup...")
    for _ in range(10):
        pattern_search_python(query, patterns, top_k)
    print("  ✓ Complete")
    print()

    # Benchmark
    print("Running benchmark...")
    times = []

    for i in range(num_iterations):
        start = time.perf_counter()
        results = pattern_search_python(query, patterns, top_k)
        end = time.perf_counter()

        elapsed_ms = (end - start) * 1000
        times.append(elapsed_ms)

        if i % 20 == 0:
            print(f"  Iteration {i}/{num_iterations}: {elapsed_ms:.3f}ms")

    print()

    # Statistics
    times_array = np.array(times)
    mean_time = np.mean(times_array)
    median_time = np.median(times_array)
    p95_time = np.percentile(times_array, 95)
    p99_time = np.percentile(times_array, 99)
    min_time = np.min(times_array)
    max_time = np.max(times_array)

    print("=" * 60)
    print("Results:")
    print(f"  Mean:     {mean_time:.3f}ms")
    print(f"  Median:   {median_time:.3f}ms")
    print(f"  P95:      {p95_time:.3f}ms")
    print(f"  P99:      {p99_time:.3f}ms")
    print(f"  Min:      {min_time:.3f}ms")
    print(f"  Max:      {max_time:.3f}ms")
    print()
    print(f"  Throughput: {1000 / mean_time:.1f} searches/sec")
    print("=" * 60)
    print()

    # Verify correctness
    results = pattern_search_python(query, patterns, top_k)
    print("Sample results (top 3):")
    for idx, score in results[:3]:
        print(f"  Pattern {idx}: {score:.4f}")
    print()

    return {
        'mean_ms': mean_time,
        'median_ms': median_time,
        'p95_ms': p95_time,
        'p99_ms': p99_time,
        'min_ms': min_time,
        'max_ms': max_time,
        'throughput': 1000 / mean_time,
        'num_patterns': num_patterns,
        'num_iterations': num_iterations,
    }


if __name__ == "__main__":
    # Run with default configuration
    results = benchmark_pattern_search()

    print("✨ Python baseline complete!")
    print()
    print("Next steps:")
    print("  1. Run Mojo implementation: mojo run benchmarks/mojo_comparison.mojo")
    print("  2. Compare results for 10x+ speedup")
    print("  3. Document findings in docs/FINDINGS.md")