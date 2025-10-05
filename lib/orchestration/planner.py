"""
Execution Planner - Internal Tract (T_int) Planning Logic

Extracted from FileCreatorOrchestrator to maintain Single Responsibility Principle.
This class handles ONLY plan generation, delegating execution to the orchestrator.

Responsibilities:
- Analyze high-level requests
- Generate execution plans with optimal particle selection
- Handle complex multi-particle workflows
- (Future) Integrate with pattern recommendations for optimization
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List

from .id_generator import generate_plan_id, generate_action_id

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# Default Base Paths
# /tmp is used as default for temporary file operations. This is appropriate
# because these are transient operations that don't require persistent storage.
# Production systems should override this with project-specific paths.
DEFAULT_BASE_PATH = "/tmp"

# Priority Levels (0-9 scale)
PRIORITY_NORMAL = 5  # Default priority for most operations
PRIORITY_HIGH = 8    # High priority for critical operations (e.g., directory creation)

# File Operation Defaults
DEFAULT_FILE_CONTENT = ""        # Empty content for new files
DEFAULT_FILE_MODE = "w"          # Write mode (overwrite)
DEFAULT_FILE_ENCODING = "utf-8"  # UTF-8 encoding

# Directory Operation Defaults
DEFAULT_CREATE_PARENTS = True    # Create parent directories by default
DEFAULT_RECURSIVE_DELETE = False # Don't recursively delete by default (safety)

# Template Defaults
DEFAULT_LANGUAGE = "python"  # Default to Python for scaffold_module

# ============================================================================


class ActionType(Enum):
    """Types of actions that can be planned"""
    CREATE_DIRECTORY = "create_directory"
    WRITE_FILE = "write_file"
    READ_FILE = "read_file"
    DELETE_FILE = "delete_file"
    DELETE_DIRECTORY = "delete_directory"
    MOVE_FILE = "move_file"
    BATCH_CREATE_FILES = "batch_create_files"
    APPLY_TEMPLATE = "apply_template"


@dataclass
class PlannedAction:
    """A single planned action in the execution plan"""
    action_id: str  # Deterministic compound ID
    action_type: ActionType
    target_particle: str  # e.g., "file_writer", "directory_creator"
    payload: Dict[str, Any]
    priority: int = PRIORITY_NORMAL  # Use named constant instead of magic number


@dataclass
class ExecutionPlan:
    """A complete execution plan for a request"""
    plan_id: str  # Deterministic compound ID
    actions: List[PlannedAction]
    created_at: float


@dataclass
class OrchestratorRequest:
    """High-level request to be planned"""
    request_type: str  # e.g., "create_component", "scaffold_module"
    parameters: Dict[str, Any]


class ExecutionPlanner:
    """
    Generates execution plans for high-level requests.

    This class embodies the PLANNING aspect of the Internal Tract (T_int).
    It decomposes abstract requests into concrete action sequences.

    Extracted from orchestrator to maintain SRP (Single Responsibility Principle).
    """

    def __init__(self):
        """Initialize the execution planner"""
        self.plans_generated = 0

    def plan(self, request: OrchestratorRequest) -> ExecutionPlan:
        """
        Generate execution plan from high-level request.

        Args:
            request: High-level orchestrator request

        Returns:
            ExecutionPlan with sequence of PlannedActions

        Raises:
            ValueError: If request_type is unknown
        """
        # Generate deterministic plan ID
        plan_data = {
            "request_type": request.request_type,
            "parameters": request.parameters
        }
        plan_id = generate_plan_id(plan_data)

        import time
        plan = ExecutionPlan(
            plan_id=plan_id,
            actions=[],
            created_at=time.time()
        )

        request_type = request.request_type
        params = request.parameters

        logger.info(f"[planner] Planning for request_type='{request_type}', params={params}")

        # ====================================================================
        # SIMPLE SINGLE-PARTICLE OPERATIONS
        # ====================================================================

        if request_type == "create_file":
            action_data = {
                "action_type": "write_file",
                "target_particle": "file_writer",
                "payload": {
                    "file_path": params.get("file_path"),
                    "content": params.get("content", DEFAULT_FILE_CONTENT),
                    "mode": params.get("mode", DEFAULT_FILE_MODE)
                }
            }
            plan.actions.append(PlannedAction(
                action_id=generate_action_id(action_data),
                action_type=ActionType.WRITE_FILE,
                target_particle="file_writer",
                payload={
                    "file_path": params.get("file_path"),
                    "content": params.get("content", DEFAULT_FILE_CONTENT),
                    "mode": params.get("mode", DEFAULT_FILE_MODE)
                }
            ))

        elif request_type == "create_directory":
            action_data = {
                "action_type": "create_directory",
                "target_particle": "directory_creator",
                "payload": {
                    "directory_path": params.get("directory_path"),
                    "parents": params.get("parents", DEFAULT_CREATE_PARENTS)
                }
            }
            plan.actions.append(PlannedAction(
                action_id=generate_action_id(action_data),
                action_type=ActionType.CREATE_DIRECTORY,
                target_particle="directory_creator",
                payload={
                    "directory_path": params.get("directory_path"),
                    "parents": params.get("parents", DEFAULT_CREATE_PARENTS)
                }
            ))

        elif request_type == "read_file":
            action_data = {
                "action_type": "read_file",
                "target_particle": "file_reader",
                "payload": {
                    "file_path": params.get("file_path"),
                    "encoding": params.get("encoding", DEFAULT_FILE_ENCODING)
                }
            }
            plan.actions.append(PlannedAction(
                action_id=generate_action_id(action_data),
                action_type=ActionType.READ_FILE,
                target_particle="file_reader",
                payload={
                    "file_path": params.get("file_path"),
                    "encoding": params.get("encoding", DEFAULT_FILE_ENCODING)
                }
            ))

        elif request_type == "delete_file":
            action_data = {
                "action_type": "delete_file",
                "target_particle": "file_deleter",
                "payload": {
                    "file_path": params.get("file_path")
                }
            }
            plan.actions.append(PlannedAction(
                action_id=generate_action_id(action_data),
                action_type=ActionType.DELETE_FILE,
                target_particle="file_deleter",
                payload={
                    "file_path": params.get("file_path")
                }
            ))

        elif request_type == "delete_directory":
            action_data = {
                "action_type": "delete_directory",
                "target_particle": "directory_deleter",
                "payload": {
                    "directory_path": params.get("directory_path"),
                    "recursive": params.get("recursive", DEFAULT_RECURSIVE_DELETE)
                }
            }
            plan.actions.append(PlannedAction(
                action_id=generate_action_id(action_data),
                action_type=ActionType.DELETE_DIRECTORY,
                target_particle="directory_deleter",
                payload={
                    "directory_path": params.get("directory_path"),
                    "recursive": params.get("recursive", DEFAULT_RECURSIVE_DELETE)
                }
            ))

        elif request_type == "move_file":
            action_data = {
                "action_type": "move_file",
                "target_particle": "file_mover",
                "payload": {
                    "source_path": params.get("source_path"),
                    "dest_path": params.get("dest_path")
                }
            }
            plan.actions.append(PlannedAction(
                action_id=generate_action_id(action_data),
                action_type=ActionType.MOVE_FILE,
                target_particle="file_mover",
                payload={
                    "source_path": params.get("source_path"),
                    "dest_path": params.get("dest_path")
                }
            ))

        elif request_type == "batch_create_files":
            action_data = {
                "action_type": "batch_create_files",
                "target_particle": "batch_file_creator",
                "payload": {
                    "files": params.get("files", [])
                }
            }
            plan.actions.append(PlannedAction(
                action_id=generate_action_id(action_data),
                action_type=ActionType.BATCH_CREATE_FILES,
                target_particle="batch_file_creator",
                payload={
                    "files": params.get("files", [])
                }
            ))

        elif request_type == "apply_template":
            action_data = {
                "action_type": "apply_template",
                "target_particle": "template_applier",
                "payload": {
                    "template_name": params.get("template_name"),
                    "template_content": params.get("template_content"),
                    "output_path": params.get("output_path"),
                    "variables": params.get("variables", {}),
                    "encoding": params.get("encoding", DEFAULT_FILE_ENCODING)
                }
            }
            plan.actions.append(PlannedAction(
                action_id=generate_action_id(action_data),
                action_type=ActionType.APPLY_TEMPLATE,
                target_particle="template_applier",
                payload={
                    "template_name": params.get("template_name"),
                    "template_content": params.get("template_content"),
                    "output_path": params.get("output_path"),
                    "variables": params.get("variables", {}),
                    "encoding": params.get("encoding", DEFAULT_FILE_ENCODING)
                }
            ))

        # ====================================================================
        # COMPLEX MULTI-PARTICLE OPERATIONS
        # ====================================================================

        elif request_type == "create_component":
            component_name = params.get("component_name")
            base_path = params.get("base_path", DEFAULT_BASE_PATH)
            component_path = f"{base_path}/{component_name}"

            # High priority: Create directory first
            dir_action_data = {
                "action_type": "create_directory",
                "target_particle": "directory_creator",
                "payload": {
                    "directory_path": component_path,
                    "parents": DEFAULT_CREATE_PARENTS
                },
                "priority": PRIORITY_HIGH
            }
            plan.actions.append(PlannedAction(
                action_id=generate_action_id(dir_action_data),
                action_type=ActionType.CREATE_DIRECTORY,
                target_particle="directory_creator",
                payload={
                    "directory_path": component_path,
                    "parents": DEFAULT_CREATE_PARENTS
                },
                priority=PRIORITY_HIGH  # Use named constant
            ))

            # Normal priority: Create __init__.py
            init_action_data = {
                "action_type": "write_file",
                "target_particle": "file_writer",
                "payload": {
                    "file_path": f"{component_path}/__init__.py",
                    "content": f'"""\n{component_name} component\n"""\n'
                }
            }
            plan.actions.append(PlannedAction(
                action_id=generate_action_id(init_action_data),
                action_type=ActionType.WRITE_FILE,
                target_particle="file_writer",
                payload={
                    "file_path": f"{component_path}/__init__.py",
                    "content": f'"""\n{component_name} component\n"""\n'
                }
            ))

            # Normal priority: Create main module file
            module_action_data = {
                "action_type": "write_file",
                "target_particle": "file_writer",
                "payload": {
                    "file_path": f"{component_path}/{component_name}.py",
                    "content": f'"""\n{component_name} module\n"""\n\n\nclass {component_name.title()}:\n    pass\n'
                }
            }
            plan.actions.append(PlannedAction(
                action_id=generate_action_id(module_action_data),
                action_type=ActionType.WRITE_FILE,
                target_particle="file_writer",
                payload={
                    "file_path": f"{component_path}/{component_name}.py",
                    "content": f'"""\n{component_name} module\n"""\n\n\nclass {component_name.title()}:\n    pass\n'
                }
            ))

        elif request_type == "scaffold_module":
            module_name = params.get("module_name")
            base_path = params.get("base_path", DEFAULT_BASE_PATH)
            language = params.get("language", DEFAULT_LANGUAGE)

            template_name = "python_module" if language == "python" else "rust_module"

            # Create base directory
            dir_action_data = {
                "action_type": "create_directory",
                "target_particle": "directory_creator",
                "payload": {
                    "directory_path": base_path,
                    "parents": DEFAULT_CREATE_PARENTS
                }
            }
            plan.actions.append(PlannedAction(
                action_id=generate_action_id(dir_action_data),
                action_type=ActionType.CREATE_DIRECTORY,
                target_particle="directory_creator",
                payload={
                    "directory_path": base_path,
                    "parents": DEFAULT_CREATE_PARENTS
                }
            ))

            # Apply template
            template_action_data = {
                "action_type": "apply_template",
                "target_particle": "template_applier",
                "payload": {
                    "template_name": template_name,
                    "output_path": f"{base_path}/{module_name}.py" if language == "python" else f"{base_path}/{module_name}.rs",
                    "variables": {
                        "description": f"{module_name} module",
                        "class_name": module_name.title(),
                        "class_description": f"{module_name.title()} class",
                        "struct_name": module_name.title(),
                        "imports": ""
                    }
                }
            }
            plan.actions.append(PlannedAction(
                action_id=generate_action_id(template_action_data),
                action_type=ActionType.APPLY_TEMPLATE,
                target_particle="template_applier",
                payload={
                    "template_name": template_name,
                    "output_path": f"{base_path}/{module_name}.py" if language == "python" else f"{base_path}/{module_name}.rs",
                    "variables": {
                        "description": f"{module_name} module",
                        "class_name": module_name.title(),
                        "class_description": f"{module_name.title()} class",
                        "struct_name": module_name.title(),
                        "imports": ""
                    }
                }
            ))

        else:
            raise ValueError(f"Unknown request type: {request_type}")

        self.plans_generated += 1
        return plan

    def get_stats(self) -> Dict[str, Any]:
        """Get planner statistics"""
        return {
            "plans_generated": self.plans_generated
        }
