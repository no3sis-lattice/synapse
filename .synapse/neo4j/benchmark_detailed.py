#!/usr/bin/env python3
"""
Detailed performance benchmark showing cache behavior
"""

import sys
from pathlib import Path
import numpy as np
import time

sys.path.insert(0, str(Path(__file__).parent))

from pattern_search import PatternSearch

def benchmark_detailed(num_patterns=1000, iterations=20):
    print("=" * 70)
    print(f"Detailed Benchmark: {num_patterns} patterns, {iterations} iterations")
    print("=" * 70)

    # Create searcher
    searcher = PatternSearch()

    # Generate test data (same patterns for all iterations)
    np.random.seed(42)
    query = np.random.randn(1024).astype(np.float32)
    patterns = [np.random.randn(1024).astype(np.float32) for _ in range(num_patterns)]

    print(f"\nTesting Mojo (with caching):")
    print("-" * 70)

    mojo_times = []
    for i in range(iterations):
        start = time.perf_counter()
        indices, scores, result = searcher.search(query, patterns, top_k=10)
        elapsed = (time.perf_counter() - start) * 1000  # ms

        if result.runtime_used.value == "mojo":
            mojo_times.append(elapsed)
            cache_status = "CACHE HIT" if i > 0 else "CACHE MISS (building)"
            print(f"  Iteration {i+1:2d}: {elapsed:.3f}ms - {cache_status}")
        else:
            print(f"  Iteration {i+1:2d}: FELL BACK TO PYTHON")

    print(f"\nTesting Python (no caching):")
    print("-" * 70)

    searcher.adapter.force_python = True
    python_times = []
    for i in range(iterations):
        start = time.perf_counter()
        indices, scores, result = searcher.search(query, patterns, top_k=10)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        python_times.append(elapsed)
        print(f"  Iteration {i+1:2d}: {elapsed:.3f}ms")

    # Analysis
    print("\n" + "=" * 70)
    print("Performance Analysis:")
    print("=" * 70)

    if mojo_times:
        # First iteration (cache miss)
        first_mojo = mojo_times[0]
        # Subsequent iterations (cache hits)
        cached_mojo = mojo_times[1:] if len(mojo_times) > 1 else []

        python_mean = np.mean(python_times)

        print(f"\nPython (no cache):")
        print(f"  Mean: {python_mean:.3f}ms ± {np.std(python_times):.3f}ms")

        print(f"\nMojo first call (cache miss, includes vstack):")
        print(f"  Time: {first_mojo:.3f}ms")
        print(f"  vs Python: {python_mean/first_mojo:.1f}x faster")

        if cached_mojo:
            cached_mean = np.mean(cached_mojo)
            cached_std = np.std(cached_mojo)

            print(f"\nMojo cached calls (cache hit, reuses vstack):")
            print(f"  Mean: {cached_mean:.3f}ms ± {cached_std:.3f}ms")
            print(f"  vs Python: {python_mean/cached_mean:.1f}x faster")
            print(f"  vs First call: {first_mojo/cached_mean:.1f}x faster (caching benefit)")

            if python_mean / cached_mean >= 10:
                print(f"\n✅ SUCCESS: {python_mean/cached_mean:.1f}x speedup achieved!")
            else:
                print(f"\n⚠️  Target: {python_mean/cached_mean:.1f}x (goal: ≥10x)")
    else:
        print("\n⚠️  Mojo was not used")

if __name__ == "__main__":
    benchmark_detailed(num_patterns=1000, iterations=20)