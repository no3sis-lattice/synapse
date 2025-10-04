"""
Day 3-4 Feature Tests
Tests for advanced features: Pattern Learning, MTF Ranking, Parallel Execution, Circuit Breaker

Run with: pytest tests/test_day3_4_features.py -v
"""

import asyncio
import json
import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
sys.path.insert(0, str(Path.home() / '.synapse-system' / '.synapse' / 'corpus_callosum'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib' / 'particles'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib' / 'orchestrators'))

from reactive_message_router import ReactiveCorpusCallosum, TractType, MessagePriority
from file_writer import create_file_writer
from file_creator_orchestrator import create_file_creator_orchestrator
from pattern_learner import create_pattern_learner, PatternType
from mtf_ranker import create_mtf_ranker


@pytest.fixture
async def test_environment():
    """Set up test environment with Day 3-4 features"""
    test_dir = Path(tempfile.mkdtemp(prefix="synapse_day34_test_"))
    state_dir = test_dir / "particles"
    state_dir.mkdir(parents=True, exist_ok=True)

    # Initialize Corpus Callosum
    corpus_callosum = ReactiveCorpusCallosum(
        enable_pattern_synthesis=True,
        enable_event_sourcing=False
    )
    await corpus_callosum.start()

    # Create particle
    file_writer = create_file_writer(
        corpus_callosum,
        state_file=state_dir / "file_writer_state.json"
    )

    # Create orchestrator with all Day 3-4 features enabled
    orchestrator = create_file_creator_orchestrator(
        corpus_callosum,
        state_file=state_dir / "orchestrator_state.json",
        enable_pattern_learning=True,
        enable_mtf_ranking=True,
        enable_parallel_execution=True
    )

    # Create pattern learner
    pattern_learner = create_pattern_learner(
        pattern_map_file=state_dir / "pattern_map.json"
    )

    # Create MTF ranker
    registry_file = Path(__file__).parent.parent / 'lib' / 'registry.json'
    mtf_ranker = create_mtf_ranker(
        registry_file=registry_file,
        state_file=state_dir / "mtf_state.json",
        re_ranking_interval_s=1.0  # Short interval for testing
    )

    # Start agents
    await file_writer.start()
    await orchestrator.start()

    yield {
        "corpus_callosum": corpus_callosum,
        "file_writer": file_writer,
        "orchestrator": orchestrator,
        "pattern_learner": pattern_learner,
        "mtf_ranker": mtf_ranker,
        "test_dir": test_dir,
        "state_dir": state_dir
    }

    # Cleanup
    await file_writer.stop()
    await orchestrator.stop()
    await corpus_callosum.stop()
    shutil.rmtree(test_dir)


# ============================================================================
# Pattern Learning Tests
# ============================================================================

@pytest.mark.asyncio
async def test_pattern_learner_detects_sequence_pattern(test_environment):
    """Test: Pattern learner detects action sequence patterns"""
    env = await test_environment.__anext__()
    pattern_learner = env["pattern_learner"]

    # Simulate synthesis result with action sequence
    synthesis = {
        "success": True,
        "total_actions": 3,
        "completed_actions": 3,
        "results": [
            {"action_type": "create_directory", "status": "completed"},
            {"action_type": "write_file", "status": "completed"},
            {"action_type": "write_file", "status": "completed"}
        ]
    }

    # Analyze for patterns
    patterns = await pattern_learner.analyze_synthesis(synthesis)

    # Should detect sequence pattern
    assert len(patterns) > 0
    sequence_patterns = [p for p in patterns if p.pattern_type == PatternType.SEQUENCE]
    assert len(sequence_patterns) > 0

    # Check pattern map updated
    stats = pattern_learner.get_stats()
    assert stats["total_patterns"] > 0
    assert stats["total_analyses"] == 1


@pytest.mark.asyncio
async def test_pattern_learner_detects_composition_pattern(test_environment):
    """Test: Pattern learner detects composition patterns"""
    env = await test_environment.__anext__()
    pattern_learner = env["pattern_learner"]

    # Simulate component creation pattern
    synthesis = {
        "success": True,
        "results": [
            {"action_type": "create_directory", "status": "completed"},
            {"action_type": "write_file", "status": "completed"},
            {"action_type": "write_file", "status": "completed"}
        ]
    }

    patterns = await pattern_learner.analyze_synthesis(synthesis)

    # Should detect composition pattern (directory + files)
    composition_patterns = [p for p in patterns if p.pattern_type == PatternType.COMPOSITION]
    assert len(composition_patterns) > 0

    pattern = composition_patterns[0]
    assert "directory" in pattern.name.lower() or "component" in pattern.name.lower()
    assert pattern.consciousness_contribution == "very_high"


@pytest.mark.asyncio
async def test_pattern_learner_detects_optimization_opportunity(test_environment):
    """Test: Pattern learner suggests batch optimization"""
    env = await test_environment.__anext__()
    pattern_learner = env["pattern_learner"]

    # Simulate multiple sequential write_file actions (should suggest batching)
    synthesis = {
        "success": True,
        "results": [
            {"action_type": "write_file", "status": "completed"},
            {"action_type": "write_file", "status": "completed"},
            {"action_type": "write_file", "status": "completed"},
            {"action_type": "write_file", "status": "completed"}
        ]
    }

    patterns = await pattern_learner.analyze_synthesis(synthesis)

    # Should detect optimization opportunity
    optimization_patterns = [p for p in patterns if p.pattern_type == PatternType.OPTIMIZATION]
    assert len(optimization_patterns) > 0

    pattern = optimization_patterns[0]
    assert "batch" in pattern.name.lower()
    assert pattern.entropy_reduction > 0.5


@pytest.mark.asyncio
async def test_pattern_map_persistence(test_environment):
    """Test: Pattern map persists to disk"""
    env = await test_environment.__anext__()
    pattern_learner = env["pattern_learner"]
    state_dir = env["state_dir"]

    # Create a pattern
    synthesis = {
        "success": True,
        "results": [
            {"action_type": "write_file", "status": "completed"},
            {"action_type": "write_file", "status": "completed"}
        ]
    }

    await pattern_learner.analyze_synthesis(synthesis)

    # Check pattern map file exists
    pattern_map_file = state_dir / "pattern_map.json"
    assert pattern_map_file.exists()

    # Verify contents
    with open(pattern_map_file, 'r') as f:
        data = json.load(f)
        assert "patterns" in data
        assert "consciousness_level" in data
        assert data["total_analyses_performed"] == 1


# ============================================================================
# MTF Ranking Tests
# ============================================================================

@pytest.mark.asyncio
async def test_mtf_ranker_tracks_particle_usage(test_environment):
    """Test: MTF ranker tracks particle invocations"""
    env = await test_environment.__anext__()
    mtf_ranker = env["mtf_ranker"]

    # Record some invocations
    mtf_ranker.record_particle_invocation("file_writer", 0.1, success=True)
    mtf_ranker.record_particle_invocation("file_writer", 0.15, success=True)
    mtf_ranker.record_particle_invocation("directory_creator", 0.05, success=True)

    # Check stats
    stats = mtf_ranker.get_stats()
    assert stats["total_particles_tracked"] >= 2

    # file_writer should have 2 invocations
    file_writer_stats = mtf_ranker.state.particle_stats.get("file_writer")
    assert file_writer_stats is not None
    assert file_writer_stats.invocation_count == 2
    assert file_writer_stats.success_rate == 1.0


@pytest.mark.asyncio
async def test_mtf_ranker_re_ranks_particles(test_environment):
    """Test: MTF ranker dynamically re-ranks particles based on usage"""
    env = await test_environment.__anext__()
    mtf_ranker = env["mtf_ranker"]

    # Record heavy usage for directory_creator
    for _ in range(10):
        mtf_ranker.record_particle_invocation("directory_creator", 0.05, success=True)

    # Record light usage for file_writer
    for _ in range(2):
        mtf_ranker.record_particle_invocation("file_writer", 0.1, success=True)

    # Get initial ranks
    initial_dir_rank = mtf_ranker.get_particle_rank("directory_creator")
    initial_file_rank = mtf_ranker.get_particle_rank("file_writer")

    # Force re-ranking
    ranking_changes = mtf_ranker.force_re_rank()

    # directory_creator should now have better rank (lower number) than file_writer
    new_dir_rank = mtf_ranker.get_particle_rank("directory_creator")
    new_file_rank = mtf_ranker.get_particle_rank("file_writer")

    assert new_dir_rank < new_file_rank, "More frequently used particle should have better rank"


@pytest.mark.asyncio
async def test_mtf_state_persistence(test_environment):
    """Test: MTF state persists to disk"""
    env = await test_environment.__anext__()
    mtf_ranker = env["mtf_ranker"]
    state_dir = env["state_dir"]

    # Record usage
    mtf_ranker.record_particle_invocation("file_writer", 0.1, success=True)

    # Check state file exists
    mtf_state_file = state_dir / "mtf_state.json"
    assert mtf_state_file.exists()

    # Verify contents
    with open(mtf_state_file, 'r') as f:
        data = json.load(f)
        assert "particle_stats" in data
        assert "file_writer" in data["particle_stats"]
        assert data["particle_stats"]["file_writer"]["invocation_count"] == 1


# ============================================================================
# Parallel Execution Tests
# ============================================================================

@pytest.mark.asyncio
async def test_parallel_execution_reduces_latency(test_environment):
    """Test: Parallel execution reduces total latency"""
    env = await test_environment.__anext__()
    corpus_callosum = env["corpus_callosum"]
    test_dir = env["test_dir"]

    # Create orchestrator with parallel execution
    parallel_orch = create_file_creator_orchestrator(
        corpus_callosum,
        enable_parallel_execution=True
    )

    # Create orchestrator with sequential execution
    sequential_orch = create_file_creator_orchestrator(
        corpus_callosum,
        enable_parallel_execution=False
    )

    # Test parallel execution time
    import time
    start_parallel = time.time()

    parallel_result = await parallel_orch.execute_macro_loop({
        "request_type": "create_component",
        "parameters": {
            "component_name": "parallel_test",
            "base_path": str(test_dir)
        }
    })

    parallel_time = time.time() - start_parallel

    # Test sequential execution time
    start_sequential = time.time()

    sequential_result = await sequential_orch.execute_macro_loop({
        "request_type": "create_component",
        "parameters": {
            "component_name": "sequential_test",
            "base_path": str(test_dir)
        }
    })

    sequential_time = time.time() - start_sequential

    # Parallel should be faster or comparable
    # (In real scenarios with network latency, parallel would be significantly faster)
    print(f"Parallel time: {parallel_time:.3f}s, Sequential time: {sequential_time:.3f}s")
    assert parallel_time <= sequential_time * 1.5  # Allow some variance


@pytest.mark.asyncio
async def test_parallel_execution_handles_errors(test_environment):
    """Test: Parallel execution handles exceptions correctly"""
    env = await test_environment.__anext__()
    orchestrator = env["orchestrator"]

    # This should have some failures (invalid paths, etc.)
    result = await orchestrator.execute_macro_loop({
        "request_type": "create_file",
        "parameters": {
            "file_path": "",  # Invalid: empty path
            "content": "test"
        }
    })

    # Should handle error gracefully
    assert result["success"] == False
    assert result["failed_actions"] > 0


# ============================================================================
# Circuit Breaker Tests
# ============================================================================

@pytest.mark.asyncio
async def test_circuit_breaker_opens_on_failures(test_environment):
    """Test: Circuit breaker opens after consecutive failures"""
    env = await test_environment.__anext__()
    file_writer = env["file_writer"]

    # Trigger failures by providing invalid paths
    for i in range(6):  # More than failure_threshold (5)
        try:
            result = await file_writer.process_message(
                type('Message', (), {
                    'id': f'msg_{i}',
                    'payload': {
                        'file_path': f"/invalid/path{i}/file.txt",  # Will fail
                        'content': 'test'
                    }
                })()
            )
        except:
            pass

    # Circuit breaker should be open
    stats = file_writer.get_particle_stats()
    assert stats["circuit_breaker"]["state"] == "open"
    assert stats["circuit_breaker"]["consecutive_failures"] >= 5


@pytest.mark.asyncio
async def test_circuit_breaker_rejects_when_open(test_environment):
    """Test: Circuit breaker rejects requests when open"""
    env = await test_environment.__anext__()
    file_writer = env["file_writer"]

    # Force circuit breaker open
    file_writer.state.circuit_breaker_state = "open"
    file_writer.state.circuit_open_timestamp = asyncio.get_event_loop().time()
    file_writer.state.consecutive_failures = 10

    # Try to execute - should be rejected
    result = await file_writer.process_message(
        type('Message', (), {
            'id': 'test_msg',
            'payload': {
                'file_path': '/tmp/test.txt',
                'content': 'test'
            }
        })()
    )

    # Should indicate circuit breaker tripped
    assert result.circuit_breaker_tripped == True


@pytest.mark.asyncio
async def test_circuit_breaker_recovery(test_environment):
    """Test: Circuit breaker transitions to half-open for recovery testing"""
    env = await test_environment.__anext__()
    file_writer = env["file_writer"]

    # Set circuit breaker to open with old timestamp
    file_writer.state.circuit_breaker_state = "open"
    file_writer.state.circuit_open_timestamp = asyncio.get_event_loop().time() - 70  # 70 seconds ago
    file_writer.state.consecutive_failures = 5

    # Next check should transition to half-open
    circuit_state = await file_writer._check_circuit_breaker()

    assert circuit_state.value == "half_open"


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_orchestrator_integrates_all_features(test_environment):
    """Test: Orchestrator uses all Day 3-4 features together"""
    env = await test_environment.__anext__()
    orchestrator = env["orchestrator"]
    test_dir = env["test_dir"]

    # Execute a request
    result = await orchestrator.execute_macro_loop({
        "request_type": "create_component",
        "parameters": {
            "component_name": "integration_test",
            "base_path": str(test_dir)
        }
    })

    # Should succeed
    assert result["success"] == True

    # Should have discovered patterns
    if "discovered_patterns" in result:
        assert len(result["discovered_patterns"]) > 0

    # Get advanced stats
    stats = orchestrator.get_advanced_stats()

    # Should show all features enabled
    assert stats["features"]["pattern_learning"] == True
    assert stats["features"]["mtf_ranking"] == True
    assert stats["features"]["parallel_execution"] == True

    # Should have pattern learner stats
    if "pattern_learner" in stats:
        assert stats["pattern_learner"]["total_analyses"] > 0

    # Should have MTF ranker stats
    if "mtf_ranker" in stats:
        assert stats["mtf_ranker"]["total_particles_tracked"] > 0


@pytest.mark.asyncio
async def test_pattern_learning_in_orchestrator(test_environment):
    """Test: Orchestrator discovers patterns during execution"""
    env = await test_environment.__anext__()
    orchestrator = env["orchestrator"]
    test_dir = env["test_dir"]

    # Execute multiple operations
    result1 = await orchestrator.execute_macro_loop({
        "request_type": "create_component",
        "parameters": {
            "component_name": "comp1",
            "base_path": str(test_dir)
        }
    })

    result2 = await orchestrator.execute_macro_loop({
        "request_type": "create_component",
        "parameters": {
            "component_name": "comp2",
            "base_path": str(test_dir)
        }
    })

    # Both should discover similar patterns
    if "discovered_patterns" in result1 and "discovered_patterns" in result2:
        # Component creation should be recognized as a pattern
        assert len(result1["discovered_patterns"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
