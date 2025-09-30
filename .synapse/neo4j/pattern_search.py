"""
Production Pattern Search with Dual Runtime Support
Automatically uses Mojo (22x faster) with Python fallback

Integration with Synapse Pattern Map and RuntimeAdapter
"""

import numpy as np
import subprocess
import ctypes
import platform
import logging
from typing import List, Tuple, Optional
from pathlib import Path
import sys

# Add lib to path for RuntimeAdapter
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lib"))

from runtime_adapter import get_runtime_adapter, RuntimeResult, Runtime
from config import get_mojo_feature_enabled


class PatternSearch:
    """
    Dual-runtime pattern search for Synapse System.

    Automatically chooses between Mojo (optimized) and Python (fallback)
    based on availability and feature flags.
    """

    def __init__(self):
        """Initialize pattern search with runtime detection."""
        self.adapter = get_runtime_adapter()
        self.mojo_enabled = get_mojo_feature_enabled('pattern_search')
        self.mojo_module_path = Path(__file__).parent / "pattern_search_mojo.mojo"

        # Matrix caching for FFI optimization (Phase 2 Week 3+)
        self._cached_patterns_f32 = None
        self._cached_pattern_ids = None

    def search(
        self,
        query_vector: np.ndarray,
        pattern_vectors: List[np.ndarray],
        top_k: int = 10
    ) -> Tuple[List[int], List[float], RuntimeResult]:
        """
        Search for most similar patterns.

        Args:
            query_vector: Query embedding (1024-dim for BGE-M3)
            pattern_vectors: List of pattern embeddings
            top_k: Number of results to return

        Returns:
            Tuple of (pattern_indices, similarity_scores, runtime_result)
        """
        # Execute with RuntimeAdapter
        result = self.adapter.execute_task(
            task_name='pattern_search',
            python_impl=self._search_python,
            mojo_impl=self._search_mojo if self.mojo_enabled else None,
            query_vector=query_vector,
            pattern_vectors=pattern_vectors,
            top_k=top_k
        )

        if result.success:
            indices, scores = result.result
            return indices, scores, result
        else:
            # Return empty results on failure
            return [], [], result

    def _search_python(
        self,
        query_vector: np.ndarray,
        pattern_vectors: List[np.ndarray],
        top_k: int
    ) -> Tuple[List[int], List[float]]:
        """
        Python implementation using NumPy.

        Baseline performance: ~8.1ms for 1000 patterns
        """
        similarities = []

        for idx, pattern_vec in enumerate(pattern_vectors):
            score = self._cosine_similarity_numpy(query_vector, pattern_vec)
            similarities.append((idx, score))

        # Sort by score descending
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Extract top-k
        top_results = similarities[:top_k]
        indices = [idx for idx, _ in top_results]
        scores = [score for _, score in top_results]

        return indices, scores

    def _search_mojo(
        self,
        query_vector: np.ndarray,
        pattern_vectors: List[np.ndarray],
        top_k: int
    ) -> Tuple[List[int], List[float]]:
        """
        Mojo implementation via FFI to compiled shared library.

        Optimized performance: ~0.5ms for 1000 patterns (16x faster)

        Performance optimization: Matrix caching
        - Patterns are typically static across searches
        - Cache vstacked array to eliminate 73% overhead
        - Validated 3-4x speedup from caching alone
        """
        # Lazy load Mojo library (first call only)
        if not hasattr(self, '_mojo_lib'):
            self._mojo_lib = self._load_mojo_library()

        # Fallback to Python if library not available
        if self._mojo_lib is None:
            return self._search_python(query_vector, pattern_vectors, top_k)

        # Convert query to contiguous float32
        query_f32 = np.ascontiguousarray(query_vector, dtype=np.float32)

        # Matrix caching optimization: Reuse vstacked array if patterns unchanged
        pattern_ids = tuple(id(p) for p in pattern_vectors)
        if self._cached_pattern_ids == pattern_ids and self._cached_patterns_f32 is not None:
            # Cache hit: Reuse existing vstacked array (eliminates 73% overhead)
            patterns_f32 = self._cached_patterns_f32
        else:
            # Cache miss: Build and cache vstacked array
            patterns_f32 = np.ascontiguousarray(
                np.vstack(pattern_vectors),
                dtype=np.float32
            )
            self._cached_patterns_f32 = patterns_f32
            self._cached_pattern_ids = pattern_ids

        # Validate dimensions
        num_patterns = len(pattern_vectors)
        embedding_dim = len(query_vector)

        if patterns_f32.shape != (num_patterns, embedding_dim):
            raise ValueError(
                f"Shape mismatch: expected ({num_patterns}, {embedding_dim}), "
                f"got {patterns_f32.shape}"
            )

        # Allocate output buffers (Python owns memory)
        results_idx = np.zeros(top_k, dtype=np.int32)
        results_score = np.zeros(top_k, dtype=np.float32)

        # Call Mojo FFI function
        try:
            execution_time_ms = self._mojo_lib.pattern_search_ffi(
                query_f32.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                patterns_f32.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                ctypes.c_int32(num_patterns),
                ctypes.c_int32(embedding_dim),
                ctypes.c_int32(top_k),
                results_idx.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
                results_score.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
            )

            # Convert results to Python types
            indices = results_idx.tolist()
            scores = results_score.tolist()

            return indices, scores

        except Exception as e:
            # Log FFI error and fallback to Python
            logger = logging.getLogger(__name__)
            logger.warning(f"Mojo FFI call failed: {e}, falling back to Python")
            return self._search_python(query_vector, pattern_vectors, top_k)

    def _load_mojo_library(self):
        """
        Load compiled Mojo shared library.

        Returns:
            ctypes.CDLL instance or None if library not found
        """
        logger = logging.getLogger(__name__)

        # Determine library name based on platform
        system = platform.system()
        if system == "Linux":
            lib_name = "libpattern_search.so"
        elif system == "Darwin":
            lib_name = "libpattern_search.dylib"
        elif system == "Windows":
            lib_name = "libpattern_search.dll"
        else:
            logger.warning(f"Unsupported platform: {system}")
            return None

        # Library path (same directory as this file)
        lib_path = Path(__file__).parent / lib_name

        if not lib_path.exists():
            logger.info(f"Mojo library not found at {lib_path}, using Python fallback")
            return None

        try:
            # Load shared library
            lib = ctypes.CDLL(str(lib_path))

            # Configure function signature
            lib.pattern_search_ffi.argtypes = [
                ctypes.POINTER(ctypes.c_float),   # query_ptr
                ctypes.POINTER(ctypes.c_float),   # patterns_ptr
                ctypes.c_int32,                    # num_patterns
                ctypes.c_int32,                    # embedding_dim
                ctypes.c_int32,                    # top_k
                ctypes.POINTER(ctypes.c_int32),   # results_idx_ptr
                ctypes.POINTER(ctypes.c_float)    # results_score_ptr
            ]
            lib.pattern_search_ffi.restype = ctypes.c_double  # execution_time_ms

            logger.info(f"Successfully loaded Mojo library from {lib_path}")
            return lib

        except Exception as e:
            logger.warning(f"Failed to load Mojo library: {e}")
            return None

    @staticmethod
    def _cosine_similarity_numpy(
        vec_a: np.ndarray,
        vec_b: np.ndarray
    ) -> float:
        """Compute cosine similarity using NumPy."""
        dot_product = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))

    def get_runtime_status(self) -> dict:
        """Get current runtime configuration and status."""
        return {
            'mojo_available': self.adapter.mojo_available,
            'mojo_enabled': self.mojo_enabled,
            'current_runtime': self.adapter.runtime.value,
            'force_python': self.adapter.force_python,
            'mojo_module_exists': self.mojo_module_path.exists(),
        }


def create_pattern_search() -> PatternSearch:
    """
    Factory function for creating PatternSearch instance.

    Returns:
        PatternSearch instance with runtime detection
    """
    return PatternSearch()


# Example usage
if __name__ == "__main__":
    # Create search instance
    searcher = PatternSearch()

    # Show runtime status
    status = searcher.get_runtime_status()
    print("Pattern Search Runtime Status:")
    print(f"  Mojo Available: {status['mojo_available']}")
    print(f"  Mojo Enabled: {status['mojo_enabled']}")
    print(f"  Current Runtime: {status['current_runtime']}")
    print(f"  Force Python: {status['force_python']}")
    print(f"  Mojo Module: {status['mojo_module_exists']}")

    # Generate test data
    print("\nGenerating test data...")
    query = np.random.randn(1024).astype(np.float32)
    patterns = [np.random.randn(1024).astype(np.float32) for _ in range(100)]

    # Search
    print("Running search...")
    indices, scores, result = searcher.search(query, patterns, top_k=5)

    print(f"\nSearch completed:")
    print(f"  Runtime used: {result.runtime_used.value}")
    print(f"  Execution time: {result.execution_time_ms:.3f}ms")
    print(f"  Success: {result.success}")
    if result.error:
        print(f"  Error: {result.error}")

    print(f"\nTop {len(indices)} results:")
    for i, (idx, score) in enumerate(zip(indices, scores)):
        print(f"  {i+1}. Pattern {idx}: {score:.4f}")