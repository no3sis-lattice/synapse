#!/usr/bin/env python3
"""
Unit Tests for ID Generator - Phase 1b

Tests coverage:
- Compound ID generation
- Sequence management and persistence
- Content hashing and determinism
- Thread safety
- Collision detection
- ID parsing
- Global instance singleton
- Convenience functions
- Collision resistance under load
"""

import json
import pytest
import sys
import tempfile
import threading
from pathlib import Path
from typing import Set
from concurrent.futures import ThreadPoolExecutor

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from orchestration.id_generator import (
    IDGenerator,
    CompoundID,
    IDCollisionDetector,
    get_global_generator,
    generate_id,
    generate_plan_id,
    generate_pattern_id,
    generate_action_id,
    generate_result_id
)


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def temp_sequence_file(tmp_path):
    """Create temporary sequence file"""
    return tmp_path / "test_sequences.json"


@pytest.fixture
def generator(temp_sequence_file):
    """Create fresh ID generator for each test"""
    return IDGenerator(sequence_file=temp_sequence_file)


# ============================================================================
# COMPOUND ID PARSING TESTS
# ============================================================================

class TestCompoundIDParsing:
    """Test suite for CompoundID parsing"""

    def test_parse_valid_id(self):
        """Test parsing valid compound ID"""
        id_string = "plan_000042_a1b2c3d4"

        compound = CompoundID.parse(id_string)

        assert compound is not None
        assert compound.id_type == "plan"
        assert compound.sequence == 42
        assert compound.content_hash == "a1b2c3d4"
        assert compound.full_id == id_string

    def test_parse_id_with_underscores_in_hash(self):
        """Test parsing ID with underscores in hash"""
        id_string = "pattern_000100_abc_def_123"

        compound = CompoundID.parse(id_string)

        assert compound is not None
        assert compound.id_type == "pattern"
        assert compound.sequence == 100
        assert compound.content_hash == "abc_def_123"

    def test_parse_invalid_id(self):
        """Test parsing invalid ID returns None"""
        invalid_ids = [
            "invalid",
            "only_two_parts",
            "not_a_number_abc_hash"
        ]

        for invalid_id in invalid_ids:
            compound = CompoundID.parse(invalid_id)
            assert compound is None


# ============================================================================
# ID GENERATION TESTS
# ============================================================================

class TestIDGeneration:
    """Test suite for ID generation"""

    def test_generate_basic_id(self, generator):
        """Test basic ID generation"""
        id_string = generator.generate("test", {"data": "value"})

        assert id_string.startswith("test_")
        parts = id_string.split('_')
        assert len(parts) == 3
        assert parts[1].isdigit()
        assert len(parts[2]) == 8  # Hash length

    def test_generate_with_sequence(self, generator):
        """Test sequence increments correctly"""
        id1 = generator.generate("plan", {"a": 1})
        id2 = generator.generate("plan", {"b": 2})
        id3 = generator.generate("plan", {"c": 3})

        # Extract sequences
        seq1 = int(id1.split('_')[1])
        seq2 = int(id2.split('_')[1])
        seq3 = int(id3.split('_')[1])

        assert seq2 == seq1 + 1
        assert seq3 == seq2 + 1

    def test_generate_different_types_separate_sequences(self, generator):
        """Test different ID types have separate sequences"""
        plan_id = generator.generate("plan", {"x": 1})
        pattern_id = generator.generate("pattern", {"y": 2})
        action_id = generator.generate("action", {"z": 3})

        plan_seq = int(plan_id.split('_')[1])
        pattern_seq = int(pattern_id.split('_')[1])
        action_seq = int(action_id.split('_')[1])

        # All should start at 1
        assert plan_seq == 1
        assert pattern_seq == 1
        assert action_seq == 1

    def test_generate_with_extra_context(self, generator):
        """Test ID generation with extra context"""
        id_without = generator.generate("test", {"data": "value"})
        id_with = generator.generate("test", {"data": "value"}, extra_context="extra")

        # Should have different hashes due to context
        hash_without = id_without.split('_')[-1]
        hash_with = id_with.split('_')[-1]

        assert hash_without != hash_with

    def test_generate_with_none_content(self, generator):
        """Test ID generation with None content uses timestamp"""
        id_string = generator.generate("test", content=None)

        assert id_string.startswith("test_")
        # Should still generate valid ID
        compound = CompoundID.parse(id_string)
        assert compound is not None

    def test_generate_with_metadata(self, generator):
        """Test generate_with_metadata returns CompoundID"""
        content = {"task": "compute", "input": [1, 2, 3]}

        compound = generator.generate_with_metadata("action", content)

        assert isinstance(compound, CompoundID)
        assert compound.id_type == "action"
        assert compound.sequence > 0
        assert len(compound.content_hash) == 8
        assert compound.full_id.startswith("action_")


# ============================================================================
# CONTENT HASHING TESTS
# ============================================================================

class TestContentHashing:
    """Test suite for content hashing"""

    def test_hash_deterministic_for_same_content(self, generator):
        """Test hash is deterministic for identical content"""
        content = {"key": "value", "number": 42}

        id1 = generator.generate("test", content)
        id2 = generator.generate("test", content)

        # Different sequences but same hash
        hash1 = id1.split('_')[-1]
        hash2 = id2.split('_')[-1]

        assert hash1 == hash2

    def test_hash_different_for_different_content(self, generator):
        """Test hash changes with content"""
        id1 = generator.generate("test", {"a": 1})
        id2 = generator.generate("test", {"a": 2})

        hash1 = id1.split('_')[-1]
        hash2 = id2.split('_')[-1]

        assert hash1 != hash2

    def test_hash_json_key_order_independent(self, generator):
        """Test hash is same regardless of JSON key order"""
        content1 = {"b": 2, "a": 1, "c": 3}
        content2 = {"a": 1, "c": 3, "b": 2}

        id1 = generator.generate("test", content1)
        id2 = generator.generate("test", content2)

        hash1 = id1.split('_')[-1]
        hash2 = id2.split('_')[-1]

        assert hash1 == hash2


# ============================================================================
# SEQUENCE PERSISTENCE TESTS
# ============================================================================

class TestSequencePersistence:
    """Test suite for sequence persistence"""

    def test_sequences_persist_across_instances(self, temp_sequence_file):
        """Test sequences are persisted and loaded"""
        # Create first generator and generate IDs
        gen1 = IDGenerator(sequence_file=temp_sequence_file)
        id1 = gen1.generate("test", {"a": 1})
        id2 = gen1.generate("test", {"b": 2})

        seq1 = int(id1.split('_')[1])
        seq2 = int(id2.split('_')[1])

        # Create second generator with same file
        gen2 = IDGenerator(sequence_file=temp_sequence_file)
        id3 = gen2.generate("test", {"c": 3})

        seq3 = int(id3.split('_')[1])

        # Sequence should continue from where gen1 left off
        assert seq3 == seq2 + 1

    def test_sequence_file_created(self, temp_sequence_file):
        """Test sequence file is created on first save"""
        assert not temp_sequence_file.exists()

        generator = IDGenerator(sequence_file=temp_sequence_file)
        generator.generate("test", {"a": 1})

        assert temp_sequence_file.exists()

    def test_get_current_sequence(self, generator):
        """Test getting current sequence without incrementing"""
        # Generate a few IDs
        generator.generate("test", {"a": 1})
        generator.generate("test", {"b": 2})

        current = generator.get_current_sequence("test")

        assert current == 2

        # Generate another
        generator.generate("test", {"c": 3})

        assert generator.get_current_sequence("test") == 3

    def test_reset_sequence(self, generator):
        """Test resetting sequence"""
        generator.generate("test", {"a": 1})
        generator.generate("test", {"b": 2})

        assert generator.get_current_sequence("test") == 2

        generator.reset_sequence("test")

        assert generator.get_current_sequence("test") == 0

    def test_get_all_sequences(self, generator):
        """Test getting all sequences"""
        generator.generate("plan", {"a": 1})
        generator.generate("pattern", {"b": 2})
        generator.generate("action", {"c": 3})

        sequences = generator.get_all_sequences()

        assert sequences["plan"] == 1
        assert sequences["pattern"] == 1
        assert sequences["action"] == 1


# ============================================================================
# THREAD SAFETY TESTS
# ============================================================================

class TestThreadSafety:
    """Test suite for thread safety"""

    def test_concurrent_generation_no_duplicates(self, generator):
        """Test concurrent ID generation produces no duplicate sequences"""
        ids_generated = []
        lock = threading.Lock()

        def generate_ids(count):
            for i in range(count):
                id_string = generator.generate("test", {"iteration": i})
                with lock:
                    ids_generated.append(id_string)

        # Run 10 threads generating 10 IDs each
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=generate_ids, args=(10,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Should have 100 unique IDs
        assert len(ids_generated) == 100

        # Extract sequences
        sequences = [int(id_str.split('_')[1]) for id_str in ids_generated]

        # All sequences should be unique
        assert len(set(sequences)) == 100

        # Sequences should be 1-100 (in some order)
        assert set(sequences) == set(range(1, 101))

    def test_concurrent_different_types(self, generator):
        """Test concurrent generation of different ID types"""
        results = {"plan": [], "pattern": [], "action": []}
        lock = threading.Lock()

        def generate_type_ids(id_type, count):
            for i in range(count):
                id_string = generator.generate(id_type, {"i": i})
                with lock:
                    results[id_type].append(id_string)

        threads = []
        for id_type in ["plan", "pattern", "action"]:
            thread = threading.Thread(target=generate_type_ids, args=(id_type, 20))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Each type should have 20 IDs
        assert len(results["plan"]) == 20
        assert len(results["pattern"]) == 20
        assert len(results["action"]) == 20

        # Each type should have sequences 1-20
        for id_type, ids in results.items():
            sequences = [int(id_str.split('_')[1]) for id_str in ids]
            assert set(sequences) == set(range(1, 21))


# ============================================================================
# COLLISION DETECTION TESTS
# ============================================================================

class TestCollisionDetection:
    """Test suite for collision detection"""

    def test_no_collision_on_first_occurrence(self):
        """Test first occurrence is not a collision"""
        detector = IDCollisionDetector()

        collision = detector.check_collision("test_000001_abc12345")

        assert collision is False
        assert detector.get_collision_count("test_000001_abc12345") == 1

    def test_collision_on_duplicate(self):
        """Test collision detected on duplicate ID"""
        detector = IDCollisionDetector()

        detector.check_collision("test_000001_abc12345")
        collision = detector.check_collision("test_000001_abc12345")

        assert collision is True
        assert detector.get_collision_count("test_000001_abc12345") == 2

    def test_collision_stats(self):
        """Test collision statistics"""
        detector = IDCollisionDetector()

        # Generate IDs with some duplicates
        detector.check_collision("id1")
        detector.check_collision("id2")
        detector.check_collision("id1")  # Collision
        detector.check_collision("id3")
        detector.check_collision("id2")  # Collision

        stats = detector.get_stats()

        assert stats["total_ids"] == 3
        assert stats["collisions"] == 2
        assert stats["unique_ids"] == 1
        assert stats["max_collision_count"] == 2

    def test_high_volume_collision_resistance(self, generator):
        """Test collision resistance under high volume"""
        detector = IDCollisionDetector()

        # Generate 1000 IDs with same content (should have different sequences)
        for i in range(1000):
            id_string = generator.generate("test", {"fixed": "content"})
            detector.check_collision(id_string)

        stats = detector.get_stats()

        # Should have no collisions due to sequence numbers
        assert stats["collisions"] == 0
        assert stats["unique_ids"] == 1000


# ============================================================================
# GLOBAL INSTANCE TESTS
# ============================================================================

class TestGlobalInstance:
    """Test suite for global instance singleton"""

    def test_get_global_generator_singleton(self):
        """Test global generator is singleton"""
        gen1 = get_global_generator()
        gen2 = get_global_generator()

        assert gen1 is gen2

    def test_global_generator_persistence(self):
        """Test global generator maintains state"""
        gen = get_global_generator()

        id1 = gen.generate("test", {"a": 1})
        seq1 = int(id1.split('_')[1])

        # Get global again
        gen2 = get_global_generator()
        id2 = gen2.generate("test", {"b": 2})
        seq2 = int(id2.split('_')[1])

        # Sequence should continue
        assert seq2 == seq1 + 1


# ============================================================================
# CONVENIENCE FUNCTIONS TESTS
# ============================================================================

class TestConvenienceFunctions:
    """Test suite for convenience functions"""

    def test_generate_id_function(self):
        """Test generate_id convenience function"""
        id_string = generate_id("custom", {"data": "test"})

        assert id_string.startswith("custom_")
        compound = CompoundID.parse(id_string)
        assert compound is not None

    def test_generate_plan_id(self):
        """Test generate_plan_id function"""
        plan_data = {"goal": "test", "steps": [1, 2, 3]}

        plan_id = generate_plan_id(plan_data)

        assert plan_id.startswith("plan_")
        compound = CompoundID.parse(plan_id)
        assert compound.id_type == "plan"

    def test_generate_pattern_id(self):
        """Test generate_pattern_id function"""
        pattern_data = {"type": "sequence", "entropy": 0.75}

        pattern_id = generate_pattern_id(pattern_data)

        assert pattern_id.startswith("pattern_")
        compound = CompoundID.parse(pattern_id)
        assert compound.id_type == "pattern"

    def test_generate_action_id(self):
        """Test generate_action_id function"""
        action_data = {"operation": "write", "target": "/path/to/file"}

        action_id = generate_action_id(action_data)

        assert action_id.startswith("action_")
        compound = CompoundID.parse(action_id)
        assert compound.id_type == "action"

    def test_generate_result_id(self):
        """Test generate_result_id function"""
        result_data = {"success": True, "output": "completed"}

        result_id = generate_result_id(result_data)

        assert result_id.startswith("result_")
        compound = CompoundID.parse(result_id)
        assert compound.id_type == "result"


# ============================================================================
# COLLISION RESISTANCE STRESS TESTS
# ============================================================================

class TestCollisionResistance:
    """Stress tests for collision resistance"""

    def test_parallel_high_volume_generation(self, generator):
        """Test parallel generation of thousands of IDs"""
        all_ids = []
        lock = threading.Lock()

        def generate_batch(batch_size):
            batch_ids = []
            for i in range(batch_size):
                id_string = generator.generate("stress", {"batch_item": i})
                batch_ids.append(id_string)
            with lock:
                all_ids.extend(batch_ids)

        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(generate_batch, 100) for _ in range(10)]
            for future in futures:
                future.result()

        # Should have 1000 unique IDs
        assert len(all_ids) == 1000
        assert len(set(all_ids)) == 1000

    def test_identical_content_different_sequences(self, generator):
        """Test identical content gets different IDs via sequence"""
        content = {"fixed": "data", "value": 42}

        ids = [generator.generate("test", content) for _ in range(100)]

        # All IDs should be unique
        assert len(set(ids)) == 100

        # All should have same hash but different sequences
        hashes = [id_str.split('_')[-1] for id_str in ids]
        assert len(set(hashes)) == 1  # All same hash

        sequences = [int(id_str.split('_')[1]) for id_str in ids]
        assert len(set(sequences)) == 100  # All different sequences


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test suite for error handling"""

    def test_corrupted_sequence_file_recovery(self, temp_sequence_file):
        """Test recovery from corrupted sequence file"""
        # Write invalid JSON
        with open(temp_sequence_file, 'w') as f:
            f.write("{ invalid json }")

        # Should recover gracefully
        generator = IDGenerator(sequence_file=temp_sequence_file)
        id_string = generator.generate("test", {"a": 1})

        assert id_string.startswith("test_")
        # Sequence should start from 1
        seq = int(id_string.split('_')[1])
        assert seq == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
