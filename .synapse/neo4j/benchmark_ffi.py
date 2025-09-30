#!/usr/bin/env python3
"""
Benchmark Mojo FFI vs Python performance
Phase 2 Week 3: Validate 22x speedup
"""

import sys
from pathlib import Path
import numpy as np
import time

sys.path.insert(0, str(Path(__file__).parent))

from pattern_search import PatternSearch

def benchmark():
    print("=" * 70)
    print("Phase 2 Week 3: Performance Benchmark (Mojo FFI vs Python)")
    print("=" * 70)

    # Create searcher
    searcher = PatternSearch()

    # Test sizes
    test_sizes = [100, 500, 1000]

    for num_patterns in test_sizes:
        print(f"\n📊 Benchmarking with {num_patterns} patterns:")
        print("-" * 70)

        # Generate test data
        np.random.seed(42)
        query = np.random.randn(1024).astype(np.float32)
        patterns = [np.random.randn(1024).astype(np.float32) for _ in range(num_patterns)]

        # Warmup
        searcher.search(query, patterns, top_k=10)

        # Benchmark Mojo (if enabled)
        mojo_times = []
        for _ in range(10):
            indices, scores, result = searcher.search(query, patterns, top_k=10)
            if result.runtime_used.value == "mojo":
                mojo_times.append(result.execution_time_ms)

        # Benchmark Python (force fallback)
        searcher.adapter.force_python = True
        python_times = []
        for _ in range(10):
            indices, scores, result = searcher.search(query, patterns, top_k=10)
            python_times.append(result.execution_time_ms)
        searcher.adapter.force_python = False

        # Calculate statistics
        if mojo_times:
            mojo_mean = np.mean(mojo_times)
            mojo_std = np.std(mojo_times)
            python_mean = np.mean(python_times)
            python_std = np.std(python_times)
            speedup = python_mean / mojo_mean

            print(f"  Mojo:   {mojo_mean:.3f}ms ± {mojo_std:.3f}ms")
            print(f"  Python: {python_mean:.3f}ms ± {python_std:.3f}ms")
            print(f"  Speedup: {speedup:.1f}x faster with Mojo")

            if speedup >= 10:
                print(f"  ✅ SUCCESS: {speedup:.1f}x speedup (target: ≥10x)")
            else:
                print(f"  ⚠️  Below target: {speedup:.1f}x (target: ≥10x)")
        else:
            python_mean = np.mean(python_times)
            python_std = np.std(python_times)
            print(f"  Python: {python_mean:.3f}ms ± {python_std:.3f}ms")
            print(f"  ⚠️  Mojo not used (fell back to Python)")

    print("\n" + "=" * 70)
    print("Benchmark complete!")
    print("=" * 70)

if __name__ == "__main__":
    benchmark()