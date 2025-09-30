"""
Integration tests for Pattern Search with Dual Runtime

Tests:
1. Python fallback functionality
2. RuntimeAdapter integration
3. Feature flag behavior
4. Performance validation
5. Error handling and fallback
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".synapse" / "neo4j"))
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from pattern_search import PatternSearch, create_pattern_search
from runtime_adapter import Runtime
from config import MOJO_FEATURES


class TestPatternSearchIntegration:
    """Integration tests for pattern search system."""

    @pytest.fixture
    def searcher(self):
        """Create PatternSearch instance for testing."""
        return create_pattern_search()

    @pytest.fixture
    def test_data(self):
        """Generate test vectors."""
        np.random.seed(42)
        query = np.random.randn(1024).astype(np.float32)
        patterns = [
            np.random.randn(1024).astype(np.float32)
            for _ in range(100)
        ]
        return query, patterns

    def test_pattern_search_initialization(self, searcher):
        """Test that PatternSearch initializes correctly."""
        assert searcher is not None
        assert searcher.adapter is not None
        assert hasattr(searcher, 'mojo_enabled')

    def test_runtime_status(self, searcher):
        """Test runtime status reporting."""
        status = searcher.get_runtime_status()

        assert 'mojo_available' in status
        assert 'mojo_enabled' in status
        assert 'current_runtime' in status
        assert 'force_python' in status
        assert 'mojo_module_exists' in status

        assert isinstance(status['mojo_available'], bool)
        assert isinstance(status['mojo_enabled'], bool)
        assert status['current_runtime'] in ['mojo', 'python']

    def test_python_search_basic(self, searcher, test_data):
        """Test basic search functionality with Python backend."""
        query, patterns = test_data

        indices, scores, result = searcher.search(query, patterns, top_k=5)

        # Validate results
        assert len(indices) == 5
        assert len(scores) == 5
        assert result.success is True
        assert result.runtime_used in [Runtime.PYTHON, Runtime.MOJO]
        assert result.execution_time_ms > 0

        # Validate scores are sorted descending
        assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1))

        # Validate scores are in valid range
        assert all(-1.0 <= score <= 1.0 for score in scores)

    def test_top_k_parameter(self, searcher, test_data):
        """Test that top_k parameter works correctly."""
        query, patterns = test_data

        for k in [1, 5, 10, 20]:
            indices, scores, result = searcher.search(query, patterns, top_k=k)

            assert len(indices) == min(k, len(patterns))
            assert len(scores) == min(k, len(patterns))
            assert result.success is True

    def test_empty_patterns(self, searcher):
        """Test behavior with empty pattern list."""
        query = np.random.randn(1024).astype(np.float32)
        patterns = []

        indices, scores, result = searcher.search(query, patterns, top_k=5)

        assert len(indices) == 0
        assert len(scores) == 0
        assert result.success is True

    def test_single_pattern(self, searcher):
        """Test search with single pattern."""
        query = np.random.randn(1024).astype(np.float32)
        patterns = [np.random.randn(1024).astype(np.float32)]

        indices, scores, result = searcher.search(query, patterns, top_k=5)

        assert len(indices) == 1
        assert len(scores) == 1
        assert indices[0] == 0
        assert result.success is True

    def test_identical_vectors(self, searcher):
        """Test search with identical query and pattern."""
        query = np.random.randn(1024).astype(np.float32)
        patterns = [query.copy()]  # Identical vector

        indices, scores, result = searcher.search(query, patterns, top_k=1)

        assert len(indices) == 1
        assert len(scores) == 1
        # Cosine similarity should be very close to 1.0 for identical vectors
        assert scores[0] > 0.99
        assert result.success is True

    def test_zero_vectors(self, searcher):
        """Test handling of zero vectors."""
        query = np.zeros(1024, dtype=np.float32)
        patterns = [np.random.randn(1024).astype(np.float32)]

        indices, scores, result = searcher.search(query, patterns, top_k=1)

        # Should handle gracefully (cosine similarity = 0 for zero vectors)
        assert result.success is True
        assert len(indices) == 1
        assert scores[0] == 0.0

    def test_performance_baseline(self, searcher, test_data):
        """Test that search completes within reasonable time."""
        query, patterns = test_data

        indices, scores, result = searcher.search(query, patterns, top_k=10)

        # Should complete in under 100ms for 100 patterns (generous limit)
        assert result.execution_time_ms < 100.0
        assert result.success is True

    def test_large_pattern_set(self, searcher):
        """Test search with larger pattern database."""
        np.random.seed(42)
        query = np.random.randn(1024).astype(np.float32)
        patterns = [
            np.random.randn(1024).astype(np.float32)
            for _ in range(1000)
        ]

        indices, scores, result = searcher.search(query, patterns, top_k=10)

        assert len(indices) == 10
        assert len(scores) == 10
        assert result.success is True

        # With Mojo: should be < 2ms, with Python: should be < 50ms
        if result.runtime_used == Runtime.MOJO:
            assert result.execution_time_ms < 10.0  # Generous for first run
        else:
            assert result.execution_time_ms < 50.0

    def test_runtime_adapter_integration(self, searcher):
        """Test RuntimeAdapter integration."""
        adapter = searcher.adapter

        assert adapter is not None
        assert hasattr(adapter, 'runtime')
        assert hasattr(adapter, 'mojo_available')
        assert hasattr(adapter, 'force_python')

    def test_feature_flag_disabled(self, searcher):
        """Test that feature flag controls Mojo usage."""
        # Check current feature flag state
        original_state = MOJO_FEATURES.get('pattern_search', False)

        # Feature should be disabled by default (Phase 2 Week 2)
        assert original_state is False
        assert searcher.mojo_enabled is False

    def test_consistent_results(self, searcher, test_data):
        """Test that multiple searches return consistent results."""
        query, patterns = test_data

        # Run search twice
        indices1, scores1, _ = searcher.search(query, patterns, top_k=5)
        indices2, scores2, _ = searcher.search(query, patterns, top_k=5)

        # Results should be identical
        assert indices1 == indices2
        np.testing.assert_array_almost_equal(scores1, scores2, decimal=5)


class TestPatternSearchFactory:
    """Test factory function."""

    def test_create_pattern_search(self):
        """Test factory creates valid instance."""
        searcher = create_pattern_search()

        assert searcher is not None
        assert isinstance(searcher, PatternSearch)
        assert searcher.adapter is not None


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])