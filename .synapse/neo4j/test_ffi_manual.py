#!/usr/bin/env python3
"""
Quick manual test of Mojo FFI integration
Tests that pattern_search.py can successfully call the Mojo library
"""

import sys
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pattern_search import PatternSearch

def test_ffi_basic():
    """Test basic FFI functionality"""
    print("=" * 60)
    print("Phase 2 Week 3: FFI Integration Test")
    print("=" * 60)

    # Create searcher
    searcher = PatternSearch()

    # Check runtime status
    status = searcher.get_runtime_status()
    print("\n📊 Runtime Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")

    # Generate test data
    print("\n🔧 Generating test data...")
    np.random.seed(42)
    query = np.random.randn(1024).astype(np.float32)
    patterns = [np.random.randn(1024).astype(np.float32) for _ in range(100)]
    print(f"  Query shape: {query.shape}")
    print(f"  Patterns: {len(patterns)} x {patterns[0].shape}")

    # Run search
    print("\n🚀 Running pattern search...")
    indices, scores, result = searcher.search(query, patterns, top_k=5)

    # Display results
    print(f"\n✅ Search completed:")
    print(f"  Runtime used: {result.runtime_used.value}")
    print(f"  Execution time: {result.execution_time_ms:.3f}ms")
    print(f"  Success: {result.success}")
    if result.error:
        print(f"  Error: {result.error}")

    print(f"\n🎯 Top {len(indices)} results:")
    for i, (idx, score) in enumerate(zip(indices, scores)):
        print(f"  {i+1}. Pattern {idx}: {score:.4f}")

    # Validate results
    assert len(indices) == 5, f"Expected 5 results, got {len(indices)}"
    assert len(scores) == 5, f"Expected 5 scores, got {len(scores)}"
    assert result.success, "Search failed"
    assert all(-1.0 <= s <= 1.0 for s in scores), "Scores out of range"

    # Check if Mojo was actually used
    if result.runtime_used.value == "mojo":
        print("\n🎉 SUCCESS: Mojo FFI is working!")
        print(f"   Library loaded from: {Path(__file__).parent / 'libpattern_search.so'}")
    else:
        print("\n⚠️  WARNING: Fell back to Python (Mojo library not used)")
        print("   This is expected if Mojo compiler is not available")

    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)

    return result.runtime_used.value == "mojo"

if __name__ == "__main__":
    try:
        mojo_used = test_ffi_basic()
        sys.exit(0 if mojo_used else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)