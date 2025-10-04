#!/usr/bin/env python3
"""
Unit tests for ResultSynthesizer - Corpus Callosum Synthesis Logic

Tests coverage:
- Synthesis with various result combinations
- Success calculation (all completed, some failed, some timeout)
- Emergent pattern detection (batch, template, structural)
- Synthesis statistics
- Edge cases and error scenarios
"""

import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

import pytest
from synthesizer import ResultSynthesizer
from planner import ActionType, PlannedAction


class TestResultSynthesizer:
    """Test suite for ResultSynthesizer"""

    def setup_method(self):
        """Setup fresh synthesizer for each test"""
        self.synthesizer = ResultSynthesizer()

    # ========================================================================
    # SUCCESS CALCULATION TESTS
    # ========================================================================

    def test_all_completed_success(self):
        """Test synthesis when all actions completed successfully"""
        plan_id = "test_plan_1"
        actions = [
            PlannedAction(
                action_type=ActionType.WRITE_FILE,
                target_particle="file_writer",
                payload={"file_path": "/tmp/test.txt"}
            )
        ]
        results = [
            {
                "status": "completed",
                "action_type": "write_file",
                "result": {"file_created": "/tmp/test.txt"}
            }
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        assert synthesis["success"] is True
        assert synthesis["total_actions"] == 1
        assert synthesis["completed_actions"] == 1
        assert synthesis["timeout_actions"] == 0
        assert synthesis["failed_actions"] == 0

    def test_multiple_completed_success(self):
        """Test synthesis with multiple completed actions"""
        plan_id = "test_plan_2"
        actions = []
        results = [
            {"status": "completed", "action_type": "create_directory"},
            {"status": "completed", "action_type": "write_file"},
            {"status": "completed", "action_type": "write_file"}
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        assert synthesis["success"] is True
        assert synthesis["total_actions"] == 3
        assert synthesis["completed_actions"] == 3
        assert synthesis["timeout_actions"] == 0
        assert synthesis["failed_actions"] == 0

    def test_some_failed(self):
        """Test synthesis when some actions failed"""
        plan_id = "test_plan_3"
        actions = []
        results = [
            {"status": "completed", "action_type": "write_file"},
            {"status": "failed", "action_type": "write_file", "error": "Permission denied"},
            {"status": "completed", "action_type": "write_file"}
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        assert synthesis["success"] is False  # Any failure = overall failure
        assert synthesis["total_actions"] == 3
        assert synthesis["completed_actions"] == 2
        assert synthesis["timeout_actions"] == 0
        assert synthesis["failed_actions"] == 1

    def test_some_timeout(self):
        """Test synthesis when some actions timed out"""
        plan_id = "test_plan_4"
        actions = []
        results = [
            {"status": "completed", "action_type": "write_file"},
            {"status": "timeout", "action_type": "write_file"},
            {"status": "completed", "action_type": "write_file"}
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        assert synthesis["success"] is False  # Any timeout = overall failure
        assert synthesis["total_actions"] == 3
        assert synthesis["completed_actions"] == 2
        assert synthesis["timeout_actions"] == 1
        assert synthesis["failed_actions"] == 0

    def test_mixed_failed_and_timeout(self):
        """Test synthesis with both failures and timeouts"""
        plan_id = "test_plan_5"
        actions = []
        results = [
            {"status": "completed", "action_type": "write_file"},
            {"status": "failed", "action_type": "write_file"},
            {"status": "timeout", "action_type": "write_file"},
            {"status": "completed", "action_type": "write_file"}
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        assert synthesis["success"] is False
        assert synthesis["total_actions"] == 4
        assert synthesis["completed_actions"] == 2
        assert synthesis["timeout_actions"] == 1
        assert synthesis["failed_actions"] == 1

    def test_all_failed(self):
        """Test synthesis when all actions failed"""
        plan_id = "test_plan_6"
        actions = []
        results = [
            {"status": "failed", "action_type": "write_file"},
            {"status": "failed", "action_type": "write_file"}
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        assert synthesis["success"] is False
        assert synthesis["total_actions"] == 2
        assert synthesis["completed_actions"] == 0
        assert synthesis["timeout_actions"] == 0
        assert synthesis["failed_actions"] == 2

    # ========================================================================
    # EMERGENT PATTERN DETECTION TESTS
    # ========================================================================

    def test_batch_optimization_pattern(self):
        """Test detection of batch optimization pattern"""
        plan_id = "test_plan_batch"
        actions = []
        results = [
            {
                "status": "completed",
                "action_type": "batch_create_files",
                "result": {"files_created": 5}
            }
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        # Should detect batch optimization pattern
        assert len(synthesis["emergent_patterns"]) > 0
        batch_pattern = synthesis["emergent_patterns"][0]
        assert batch_pattern["pattern"] == "batch_optimization"
        assert "batch" in batch_pattern["description"].lower()
        assert "O(n) → O(1)" in batch_pattern["efficiency_gain"]

    def test_template_abstraction_pattern(self):
        """Test detection of template abstraction pattern"""
        plan_id = "test_plan_template"
        actions = []
        results = [
            {
                "status": "completed",
                "action_type": "apply_template",
                "result": {"template_applied": "python_module"}
            }
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        # Should detect template pattern
        assert len(synthesis["emergent_patterns"]) > 0
        template_pattern = synthesis["emergent_patterns"][0]
        assert template_pattern["pattern"] == "template_abstraction"
        assert "template" in template_pattern["description"].lower()
        assert template_pattern["abstraction_level"] == "high"

    def test_structural_hierarchy_pattern(self):
        """Test detection of structural hierarchy pattern"""
        plan_id = "test_plan_structure"
        actions = []
        results = [
            {"status": "completed", "action_type": "create_directory"},
            {"status": "completed", "action_type": "create_directory"},
            {"status": "completed", "action_type": "create_directory"}
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        # Should detect structural hierarchy pattern
        patterns = synthesis["emergent_patterns"]
        structural_patterns = [p for p in patterns if p["pattern"] == "structural_hierarchy"]
        assert len(structural_patterns) > 0

        structural_pattern = structural_patterns[0]
        assert "hierarchy" in structural_pattern["description"].lower()
        assert structural_pattern["depth"] == 3

    def test_multiple_patterns_detected(self):
        """Test detection of multiple patterns in same synthesis"""
        plan_id = "test_plan_multi"
        actions = []
        results = [
            {"status": "completed", "action_type": "create_directory"},
            {"status": "completed", "action_type": "create_directory"},
            {"status": "completed", "action_type": "batch_create_files"},
            {"status": "completed", "action_type": "apply_template"}
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        # Should detect multiple patterns
        patterns = synthesis["emergent_patterns"]
        assert len(patterns) >= 3  # batch, template, structural

        pattern_types = {p["pattern"] for p in patterns}
        assert "batch_optimization" in pattern_types
        assert "template_abstraction" in pattern_types
        assert "structural_hierarchy" in pattern_types

    def test_no_patterns_for_simple_operations(self):
        """Test that simple single operations don't trigger pattern detection"""
        plan_id = "test_plan_simple"
        actions = []
        results = [
            {"status": "completed", "action_type": "write_file"}
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        # Single write_file shouldn't trigger any patterns
        assert len(synthesis["emergent_patterns"]) == 0

    def test_no_patterns_when_all_failed(self):
        """Test that failed operations don't trigger pattern detection"""
        plan_id = "test_plan_failed"
        actions = []
        results = [
            {"status": "failed", "action_type": "batch_create_files"},
            {"status": "failed", "action_type": "apply_template"}
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        # No completed actions = no patterns
        assert len(synthesis["emergent_patterns"]) == 0

    # ========================================================================
    # RESULTS AGGREGATION TESTS
    # ========================================================================

    def test_results_preserved_in_synthesis(self):
        """Test that raw results are preserved in synthesis"""
        plan_id = "test_plan_results"
        actions = []
        results = [
            {"status": "completed", "action_type": "write_file", "result": {"file": "a.txt"}},
            {"status": "completed", "action_type": "write_file", "result": {"file": "b.txt"}}
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        assert synthesis["results"] == results
        assert len(synthesis["results"]) == 2

    def test_empty_results(self):
        """Test synthesis with empty results list"""
        plan_id = "test_plan_empty"
        actions = []
        results = []

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        assert synthesis["success"] is True  # No failures = success
        assert synthesis["total_actions"] == 0
        assert synthesis["completed_actions"] == 0
        assert synthesis["timeout_actions"] == 0
        assert synthesis["failed_actions"] == 0
        assert synthesis["emergent_patterns"] == []

    # ========================================================================
    # STATISTICS TESTS
    # ========================================================================

    def test_syntheses_counter_increments(self):
        """Test that syntheses_performed counter increments"""
        assert self.synthesizer.syntheses_performed == 0

        plan_id = "test_plan_stats"
        actions = []
        results = [{"status": "completed", "action_type": "write_file"}]

        self.synthesizer.synthesize(plan_id, actions, results)
        assert self.synthesizer.syntheses_performed == 1

        self.synthesizer.synthesize(plan_id, actions, results)
        assert self.synthesizer.syntheses_performed == 2

    def test_get_stats(self):
        """Test get_stats() returns correct statistics"""
        # Perform several syntheses
        for i in range(5):
            self.synthesizer.synthesize(
                f"test_plan_{i}",
                [],
                [{"status": "completed", "action_type": "write_file"}]
            )

        stats = self.synthesizer.get_stats()

        assert stats["syntheses_performed"] == 5

    # ========================================================================
    # EDGE CASES
    # ========================================================================

    def test_unknown_status_ignored(self):
        """Test that unknown status values are ignored in counting"""
        plan_id = "test_plan_unknown"
        actions = []
        results = [
            {"status": "completed", "action_type": "write_file"},
            {"status": "unknown_status", "action_type": "write_file"},
            {"status": "completed", "action_type": "write_file"}
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        # Unknown status shouldn't be counted
        assert synthesis["total_actions"] == 3
        assert synthesis["completed_actions"] == 2
        assert synthesis["timeout_actions"] == 0
        assert synthesis["failed_actions"] == 0
        # Success because no explicit failures or timeouts
        assert synthesis["success"] is True

    def test_missing_status_field(self):
        """Test handling of results without status field"""
        plan_id = "test_plan_no_status"
        actions = []
        results = [
            {"action_type": "write_file"},  # Missing status
            {"status": "completed", "action_type": "write_file"}
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        # Should handle gracefully
        assert synthesis["total_actions"] == 2
        assert synthesis["completed_actions"] == 1

    def test_missing_action_type_field(self):
        """Test handling of results without action_type field"""
        plan_id = "test_plan_no_action_type"
        actions = []
        results = [
            {"status": "completed"},  # Missing action_type
            {"status": "completed", "action_type": "write_file"}
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        # Should handle gracefully
        assert synthesis["total_actions"] == 2
        assert synthesis["completed_actions"] == 2

    def test_complex_result_data(self):
        """Test synthesis with complex nested result data"""
        plan_id = "test_plan_complex"
        actions = []
        results = [
            {
                "status": "completed",
                "action_type": "write_file",
                "result": {
                    "file_path": "/tmp/test.txt",
                    "bytes_written": 1024,
                    "metadata": {
                        "encoding": "utf-8",
                        "timestamp": 1234567890
                    }
                }
            }
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        # Complex data should be preserved
        assert synthesis["results"][0]["result"]["metadata"]["encoding"] == "utf-8"

    def test_single_directory_no_hierarchy_pattern(self):
        """Test that single directory doesn't trigger hierarchy pattern"""
        plan_id = "test_plan_single_dir"
        actions = []
        results = [
            {"status": "completed", "action_type": "create_directory"}
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        # Single directory shouldn't trigger hierarchy pattern (needs >= 2)
        structural_patterns = [
            p for p in synthesis["emergent_patterns"]
            if p["pattern"] == "structural_hierarchy"
        ]
        assert len(structural_patterns) == 0

    def test_synthesis_with_all_pattern_types(self):
        """Test comprehensive synthesis with all pattern types"""
        plan_id = "test_plan_comprehensive"
        actions = []
        results = [
            {"status": "completed", "action_type": "create_directory"},
            {"status": "completed", "action_type": "create_directory"},
            {"status": "completed", "action_type": "batch_create_files"},
            {"status": "completed", "action_type": "apply_template"}
        ]

        synthesis = self.synthesizer.synthesize(plan_id, actions, results)

        assert synthesis["success"] is True
        assert synthesis["total_actions"] == 4
        assert synthesis["completed_actions"] == 4

        # Should detect all three pattern types
        assert len(synthesis["emergent_patterns"]) == 3

        pattern_names = {p["pattern"] for p in synthesis["emergent_patterns"]}
        assert pattern_names == {
            "batch_optimization",
            "template_abstraction",
            "structural_hierarchy"
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
