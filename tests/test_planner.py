#!/usr/bin/env python3
"""
Unit tests for ExecutionPlanner - Internal Tract Planning Logic

Tests coverage:
- Simple operations (create_file, create_directory, read_file, etc.)
- Complex operations (create_component, scaffold_module)
- Error handling for unknown request types
- Plan generation statistics
- All action types and edge cases
"""

import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

import pytest
from planner import (
    ExecutionPlanner,
    OrchestratorRequest,
    ExecutionPlan,
    PlannedAction,
    ActionType
)


class TestExecutionPlanner:
    """Test suite for ExecutionPlanner"""

    def setup_method(self):
        """Setup fresh planner for each test"""
        self.planner = ExecutionPlanner()

    # ========================================================================
    # SIMPLE OPERATIONS - Single Particle Actions
    # ========================================================================

    def test_create_file_plan(self):
        """Test planning for create_file request"""
        request = OrchestratorRequest(
            request_type="create_file",
            parameters={
                "file_path": "/tmp/test.txt",
                "content": "Hello, World!",
                "mode": "w"
            }
        )

        plan = self.planner.plan(request)

        assert isinstance(plan, ExecutionPlan)
        assert len(plan.actions) == 1
        assert plan.actions[0].action_type == ActionType.WRITE_FILE
        assert plan.actions[0].target_particle == "file_writer"
        assert plan.actions[0].payload["file_path"] == "/tmp/test.txt"
        assert plan.actions[0].payload["content"] == "Hello, World!"
        assert plan.actions[0].payload["mode"] == "w"

    def test_create_file_defaults(self):
        """Test create_file with default parameters"""
        request = OrchestratorRequest(
            request_type="create_file",
            parameters={
                "file_path": "/tmp/test.txt"
                # No content, no mode - should use defaults
            }
        )

        plan = self.planner.plan(request)

        assert plan.actions[0].payload["content"] == ""
        assert plan.actions[0].payload["mode"] == "w"

    def test_create_directory_plan(self):
        """Test planning for create_directory request"""
        request = OrchestratorRequest(
            request_type="create_directory",
            parameters={
                "directory_path": "/tmp/test_dir",
                "parents": True
            }
        )

        plan = self.planner.plan(request)

        assert len(plan.actions) == 1
        assert plan.actions[0].action_type == ActionType.CREATE_DIRECTORY
        assert plan.actions[0].target_particle == "directory_creator"
        assert plan.actions[0].payload["directory_path"] == "/tmp/test_dir"
        assert plan.actions[0].payload["parents"] is True

    def test_read_file_plan(self):
        """Test planning for read_file request"""
        request = OrchestratorRequest(
            request_type="read_file",
            parameters={
                "file_path": "/tmp/test.txt",
                "encoding": "utf-8"
            }
        )

        plan = self.planner.plan(request)

        assert len(plan.actions) == 1
        assert plan.actions[0].action_type == ActionType.READ_FILE
        assert plan.actions[0].target_particle == "file_reader"
        assert plan.actions[0].payload["file_path"] == "/tmp/test.txt"
        assert plan.actions[0].payload["encoding"] == "utf-8"

    def test_delete_file_plan(self):
        """Test planning for delete_file request"""
        request = OrchestratorRequest(
            request_type="delete_file",
            parameters={
                "file_path": "/tmp/test.txt"
            }
        )

        plan = self.planner.plan(request)

        assert len(plan.actions) == 1
        assert plan.actions[0].action_type == ActionType.DELETE_FILE
        assert plan.actions[0].target_particle == "file_deleter"
        assert plan.actions[0].payload["file_path"] == "/tmp/test.txt"

    def test_delete_directory_plan(self):
        """Test planning for delete_directory request"""
        request = OrchestratorRequest(
            request_type="delete_directory",
            parameters={
                "directory_path": "/tmp/test_dir",
                "recursive": False
            }
        )

        plan = self.planner.plan(request)

        assert len(plan.actions) == 1
        assert plan.actions[0].action_type == ActionType.DELETE_DIRECTORY
        assert plan.actions[0].target_particle == "directory_deleter"
        assert plan.actions[0].payload["directory_path"] == "/tmp/test_dir"
        assert plan.actions[0].payload["recursive"] is False

    def test_move_file_plan(self):
        """Test planning for move_file request"""
        request = OrchestratorRequest(
            request_type="move_file",
            parameters={
                "source_path": "/tmp/old.txt",
                "dest_path": "/tmp/new.txt"
            }
        )

        plan = self.planner.plan(request)

        assert len(plan.actions) == 1
        assert plan.actions[0].action_type == ActionType.MOVE_FILE
        assert plan.actions[0].target_particle == "file_mover"
        assert plan.actions[0].payload["source_path"] == "/tmp/old.txt"
        assert plan.actions[0].payload["dest_path"] == "/tmp/new.txt"

    def test_batch_create_files_plan(self):
        """Test planning for batch_create_files request"""
        files = [
            {"path": "/tmp/file1.txt", "content": "File 1"},
            {"path": "/tmp/file2.txt", "content": "File 2"}
        ]

        request = OrchestratorRequest(
            request_type="batch_create_files",
            parameters={
                "files": files
            }
        )

        plan = self.planner.plan(request)

        assert len(plan.actions) == 1
        assert plan.actions[0].action_type == ActionType.BATCH_CREATE_FILES
        assert plan.actions[0].target_particle == "batch_file_creator"
        assert plan.actions[0].payload["files"] == files

    def test_apply_template_plan(self):
        """Test planning for apply_template request"""
        request = OrchestratorRequest(
            request_type="apply_template",
            parameters={
                "template_name": "python_module",
                "template_content": "# {{module_name}}",
                "output_path": "/tmp/module.py",
                "variables": {"module_name": "test_module"},
                "encoding": "utf-8"
            }
        )

        plan = self.planner.plan(request)

        assert len(plan.actions) == 1
        assert plan.actions[0].action_type == ActionType.APPLY_TEMPLATE
        assert plan.actions[0].target_particle == "template_applier"
        assert plan.actions[0].payload["template_name"] == "python_module"
        assert plan.actions[0].payload["output_path"] == "/tmp/module.py"
        assert plan.actions[0].payload["variables"]["module_name"] == "test_module"

    # ========================================================================
    # COMPLEX OPERATIONS - Multi-Particle Workflows
    # ========================================================================

    def test_create_component_plan(self):
        """Test planning for create_component request (complex workflow)"""
        request = OrchestratorRequest(
            request_type="create_component",
            parameters={
                "component_name": "auth",
                "base_path": "/tmp/components"
            }
        )

        plan = self.planner.plan(request)

        # Should have 3 actions: create dir, __init__.py, auth.py
        assert len(plan.actions) == 3

        # Action 1: Create directory (high priority)
        assert plan.actions[0].action_type == ActionType.CREATE_DIRECTORY
        assert plan.actions[0].target_particle == "directory_creator"
        assert plan.actions[0].payload["directory_path"] == "/tmp/components/auth"
        assert plan.actions[0].priority == 8  # High priority

        # Action 2: Create __init__.py
        assert plan.actions[1].action_type == ActionType.WRITE_FILE
        assert plan.actions[1].target_particle == "file_writer"
        assert "/tmp/components/auth/__init__.py" in plan.actions[1].payload["file_path"]
        assert "auth component" in plan.actions[1].payload["content"]

        # Action 3: Create auth.py
        assert plan.actions[2].action_type == ActionType.WRITE_FILE
        assert plan.actions[2].target_particle == "file_writer"
        assert "/tmp/components/auth/auth.py" in plan.actions[2].payload["file_path"]
        assert "class Auth:" in plan.actions[2].payload["content"]

    def test_create_component_default_base_path(self):
        """Test create_component with default base_path"""
        request = OrchestratorRequest(
            request_type="create_component",
            parameters={
                "component_name": "test_component"
                # No base_path - should default to /tmp
            }
        )

        plan = self.planner.plan(request)

        # Should use /tmp as default
        assert "/tmp/test_component" in plan.actions[0].payload["directory_path"]

    def test_scaffold_module_python(self):
        """Test planning for scaffold_module request (Python)"""
        request = OrchestratorRequest(
            request_type="scaffold_module",
            parameters={
                "module_name": "calculator",
                "base_path": "/tmp/modules",
                "language": "python"
            }
        )

        plan = self.planner.plan(request)

        # Should have 2 actions: create dir, apply template
        assert len(plan.actions) == 2

        # Action 1: Create directory
        assert plan.actions[0].action_type == ActionType.CREATE_DIRECTORY
        assert plan.actions[0].payload["directory_path"] == "/tmp/modules"

        # Action 2: Apply Python template
        assert plan.actions[1].action_type == ActionType.APPLY_TEMPLATE
        assert plan.actions[1].payload["template_name"] == "python_module"
        assert plan.actions[1].payload["output_path"] == "/tmp/modules/calculator.py"
        assert plan.actions[1].payload["variables"]["class_name"] == "Calculator"

    def test_scaffold_module_rust(self):
        """Test planning for scaffold_module request (Rust)"""
        request = OrchestratorRequest(
            request_type="scaffold_module",
            parameters={
                "module_name": "parser",
                "base_path": "/tmp/rust",
                "language": "rust"
            }
        )

        plan = self.planner.plan(request)

        assert len(plan.actions) == 2

        # Action 2: Apply Rust template
        assert plan.actions[1].action_type == ActionType.APPLY_TEMPLATE
        assert plan.actions[1].payload["template_name"] == "rust_module"
        assert plan.actions[1].payload["output_path"] == "/tmp/rust/parser.rs"

    def test_scaffold_module_default_language(self):
        """Test scaffold_module with default language (Python)"""
        request = OrchestratorRequest(
            request_type="scaffold_module",
            parameters={
                "module_name": "utils",
                "base_path": "/tmp"
            }
        )

        plan = self.planner.plan(request)

        # Should default to Python
        assert plan.actions[1].payload["template_name"] == "python_module"
        assert plan.actions[1].payload["output_path"].endswith(".py")

    # ========================================================================
    # ERROR HANDLING
    # ========================================================================

    def test_unknown_request_type_raises_error(self):
        """Test that unknown request type raises ValueError"""
        request = OrchestratorRequest(
            request_type="invalid_operation",
            parameters={}
        )

        with pytest.raises(ValueError) as exc_info:
            self.planner.plan(request)

        assert "Unknown request type" in str(exc_info.value)
        assert "invalid_operation" in str(exc_info.value)

    def test_empty_request_type_raises_error(self):
        """Test that empty request type raises ValueError"""
        request = OrchestratorRequest(
            request_type="",
            parameters={}
        )

        with pytest.raises(ValueError) as exc_info:
            self.planner.plan(request)

        assert "Unknown request type" in str(exc_info.value)

    # ========================================================================
    # PLAN METADATA & STATISTICS
    # ========================================================================

    def test_plan_has_unique_id(self):
        """Test that each plan gets a unique ID"""
        request = OrchestratorRequest(
            request_type="create_file",
            parameters={"file_path": "/tmp/test.txt"}
        )

        plan1 = self.planner.plan(request)
        plan2 = self.planner.plan(request)

        assert plan1.plan_id != plan2.plan_id
        assert plan1.plan_id.startswith("plan_")
        assert plan2.plan_id.startswith("plan_")

    def test_plan_has_timestamp(self):
        """Test that plans have creation timestamp"""
        request = OrchestratorRequest(
            request_type="create_file",
            parameters={"file_path": "/tmp/test.txt"}
        )

        import time
        before = time.time()
        plan = self.planner.plan(request)
        after = time.time()

        assert before <= plan.created_at <= after

    def test_stats_increment(self):
        """Test that planner statistics increment correctly"""
        assert self.planner.plans_generated == 0

        request = OrchestratorRequest(
            request_type="create_file",
            parameters={"file_path": "/tmp/test.txt"}
        )

        self.planner.plan(request)
        assert self.planner.plans_generated == 1

        self.planner.plan(request)
        assert self.planner.plans_generated == 2

    def test_get_stats(self):
        """Test get_stats() returns correct statistics"""
        # Generate some plans
        request = OrchestratorRequest(
            request_type="create_file",
            parameters={"file_path": "/tmp/test.txt"}
        )

        for _ in range(5):
            self.planner.plan(request)

        stats = self.planner.get_stats()

        assert stats["plans_generated"] == 5

    # ========================================================================
    # PRIORITY HANDLING
    # ========================================================================

    def test_default_priority(self):
        """Test that actions have default priority of 5"""
        request = OrchestratorRequest(
            request_type="create_file",
            parameters={"file_path": "/tmp/test.txt"}
        )

        plan = self.planner.plan(request)

        assert plan.actions[0].priority == 5

    def test_high_priority_for_directory_in_component(self):
        """Test that directory creation in create_component has high priority"""
        request = OrchestratorRequest(
            request_type="create_component",
            parameters={
                "component_name": "test",
                "base_path": "/tmp"
            }
        )

        plan = self.planner.plan(request)

        # First action (directory creation) should have priority 8
        assert plan.actions[0].action_type == ActionType.CREATE_DIRECTORY
        assert plan.actions[0].priority == 8

        # Other actions should have default priority
        assert plan.actions[1].priority == 5
        assert plan.actions[2].priority == 5

    # ========================================================================
    # EDGE CASES
    # ========================================================================

    def test_missing_parameters_use_defaults(self):
        """Test that missing parameters fall back to sensible defaults"""
        # create_file without content or mode
        request = OrchestratorRequest(
            request_type="create_file",
            parameters={"file_path": "/tmp/test.txt"}
        )

        plan = self.planner.plan(request)

        assert plan.actions[0].payload["content"] == ""
        assert plan.actions[0].payload["mode"] == "w"

        # create_directory without parents
        request = OrchestratorRequest(
            request_type="create_directory",
            parameters={"directory_path": "/tmp/test"}
        )

        plan = self.planner.plan(request)

        assert plan.actions[0].payload["parents"] is True

    def test_empty_batch_files_list(self):
        """Test batch_create_files with empty files list"""
        request = OrchestratorRequest(
            request_type="batch_create_files",
            parameters={}  # No files specified
        )

        plan = self.planner.plan(request)

        # Should still create plan, but with empty files list
        assert plan.actions[0].payload["files"] == []

    def test_none_parameters(self):
        """Test handling of None parameter values"""
        request = OrchestratorRequest(
            request_type="create_file",
            parameters={
                "file_path": None,  # Invalid but shouldn't crash
                "content": None,
                "mode": None
            }
        )

        plan = self.planner.plan(request)

        # Should create plan (validation happens at execution time)
        assert len(plan.actions) == 1
        assert plan.actions[0].payload["file_path"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
