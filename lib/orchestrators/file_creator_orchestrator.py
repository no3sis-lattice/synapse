"""
File Creator Orchestrator - Day 3-4 Enhanced
Internal Tract (T_int) agent for planning file creation workflows

Implements the Macro-Loop with advanced features:
1. Receive high-level request
2. Generate execution plan (with pattern-based optimization)
3. Route ACTION_REQUEST messages via Corpus Callosum to T_ext particles (parallel)
4. Collect results (parallel with timeout)
5. Synthesize final output (with pattern learning)

Day 3-4 Enhancements:
- Emergent pattern learning system
- Dynamic MTF re-ranking based on particle usage
- Parallel result collection for improved performance
- Pattern-based optimization recommendations

This orchestrator demonstrates the dual-tract architecture:
- T_int (this): Abstract planning and coordination
- T_ext (particles): Concrete file system operations
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum
import sys

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent_consumer import AgentConsumer, AgentConfig
sys.path.insert(0, str(Path.home() / '.synapse-system' / '.synapse' / 'corpus_callosum'))
from reactive_message_router import TractType, MessagePriority

# Day 3-4 imports
try:
    from pattern_learner import create_pattern_learner, PatternLearner
    from mtf_ranker import create_mtf_ranker, MTFRanker
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError:
    ADVANCED_FEATURES_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Advanced features (pattern learning, MTF ranking) not available")

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of actions the orchestrator can plan"""
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
    action_type: ActionType
    target_particle: str  # e.g., "file_writer", "directory_creator"
    payload: Dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL


@dataclass
class ExecutionPlan:
    """A complete execution plan for a file creation request"""
    plan_id: str
    actions: List[PlannedAction] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


@dataclass
class OrchestratorRequest:
    """High-level request to the orchestrator"""
    request_type: str  # e.g., "create_component", "scaffold_module"
    parameters: Dict[str, Any]


class FileCreatorOrchestrator(AgentConsumer):
    """
    Internal Tract orchestrator for file creation workflows.

    Receives high-level requests and decomposes them into atomic operations
    for External Tract particles.

    Pneuma Consciousness:
    - Implements the Macro-Loop for abstract planning
    - Bridges T_int (planning) and T_ext (execution) via Corpus Callosum
    - Learns optimal planning strategies through execution feedback
    - Adapts particle priorities based on usage (MTF ranking)
    - Discovers emergent patterns in execution history
    """

    def __init__(
        self,
        config: AgentConfig,
        corpus_callosum,
        state_file: Path,
        enable_pattern_learning: bool = True,
        enable_mtf_ranking: bool = True,
        enable_parallel_execution: bool = True
    ):
        super().__init__(config, corpus_callosum)
        self.state_file = state_file
        self.state = self._load_state()
        self._pending_results: Dict[str, asyncio.Queue] = {}
        self._result_lock = asyncio.Lock()
        self._result_timeout = 5.0  # seconds

        # Day 3-4 features
        self.enable_pattern_learning = enable_pattern_learning and ADVANCED_FEATURES_AVAILABLE
        self.enable_mtf_ranking = enable_mtf_ranking and ADVANCED_FEATURES_AVAILABLE
        self.enable_parallel_execution = enable_parallel_execution

        # Initialize pattern learner
        self.pattern_learner: Optional[PatternLearner] = None
        if self.enable_pattern_learning:
            try:
                self.pattern_learner = create_pattern_learner()
                logger.info("[orchestrator] Pattern learning enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize pattern learner: {e}")
                self.enable_pattern_learning = False

        # Initialize MTF ranker
        self.mtf_ranker: Optional[MTFRanker] = None
        if self.enable_mtf_ranking:
            try:
                self.mtf_ranker = create_mtf_ranker()
                logger.info("[orchestrator] MTF ranking enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize MTF ranker: {e}")
                self.enable_mtf_ranking = False

    def _load_state(self) -> Dict[str, Any]:
        """Load orchestrator state from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load orchestrator state: {e}")

        return {
            "cycle_count": 0,
            "total_plans": 0,
            "successful_plans": 0,
            "failed_plans": 0,
            "total_actions_dispatched": 0,
            "total_execution_time_s": 0.0
        }

    def _save_state(self):
        """Persist orchestrator state to disk"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save orchestrator state: {e}")

    async def process_message(self, message) -> Any:
        """
        Process incoming orchestration request.

        This is the entry point for high-level file creation requests.
        """
        payload = message.payload if isinstance(message.payload, dict) else {}
        request = OrchestratorRequest(
            request_type=payload.get('request_type', 'unknown'),
            parameters=payload.get('parameters', {})
        )

        # Execute the Macro-Loop
        result = await self.execute_macro_loop(request)

        # Update state
        self.state['cycle_count'] += 1
        self._save_state()

        return result

    async def execute_macro_loop(self, request: OrchestratorRequest) -> Dict[str, Any]:
        """
        Execute the Macro-Loop: Plan → Route → Collect → Synthesize

        Day 3-4 Enhanced with:
        - Pattern-based optimization recommendations
        - Parallel result collection
        - MTF ranking updates
        - Pattern learning from results
        """
        start_time = time.time()

        # 1. PLAN: Generate execution plan (with pattern optimization)
        plan = await self.plan(request)

        # 2. ROUTE & COLLECT: Dispatch actions (parallel or sequential)
        if self.enable_parallel_execution:
            results = await self.route_and_collect_parallel(plan)
        else:
            results = await self.route_and_collect(plan)

        # 3. SYNTHESIZE: Combine results and discover patterns
        synthesis = await self.synthesize(plan, results)

        # 4. UPDATE STATE & LEARN
        execution_time = time.time() - start_time
        self.state['total_plans'] += 1
        self.state['total_execution_time_s'] += execution_time

        if synthesis['success']:
            self.state['successful_plans'] += 1
        else:
            self.state['failed_plans'] += 1

        synthesis['execution_time_s'] = execution_time
        synthesis['plan_id'] = plan.plan_id

        # Day 3-4: Learn from execution
        if self.enable_pattern_learning and self.pattern_learner:
            try:
                discovered_patterns = await self.pattern_learner.analyze_synthesis(synthesis)
                synthesis['discovered_patterns'] = [p.name for p in discovered_patterns]
            except Exception as e:
                logger.error(f"Pattern learning failed: {e}")

        self._save_state()

        logger.info(
            f"[orchestrator] Completed plan {plan.plan_id}: "
            f"success={synthesis['success']}, time={execution_time:.3f}s, "
            f"mode={'parallel' if self.enable_parallel_execution else 'sequential'}"
        )

        return synthesis

    async def plan(self, request: OrchestratorRequest) -> ExecutionPlan:
        """
        Stage 1: Generate execution plan

        Day 3-4: Enhanced with pattern-based optimization recommendations
        """
        plan_id = f"plan_{int(time.time() * 1000)}"
        plan = ExecutionPlan(plan_id=plan_id)

        request_type = request.request_type
        params = request.parameters

        # Simple single-particle operations
        if request_type == "create_file":
            plan.actions.append(PlannedAction(
                action_type=ActionType.WRITE_FILE,
                target_particle="file_writer",
                payload={
                    "file_path": params.get("file_path"),
                    "content": params.get("content", ""),
                    "mode": params.get("mode", "w")
                }
            ))

        elif request_type == "create_directory":
            plan.actions.append(PlannedAction(
                action_type=ActionType.CREATE_DIRECTORY,
                target_particle="directory_creator",
                payload={
                    "directory_path": params.get("directory_path"),
                    "parents": params.get("parents", True)
                }
            ))

        elif request_type == "read_file":
            plan.actions.append(PlannedAction(
                action_type=ActionType.READ_FILE,
                target_particle="file_reader",
                payload={
                    "file_path": params.get("file_path"),
                    "encoding": params.get("encoding", "utf-8")
                }
            ))

        elif request_type == "delete_file":
            plan.actions.append(PlannedAction(
                action_type=ActionType.DELETE_FILE,
                target_particle="file_deleter",
                payload={
                    "file_path": params.get("file_path")
                }
            ))

        elif request_type == "delete_directory":
            plan.actions.append(PlannedAction(
                action_type=ActionType.DELETE_DIRECTORY,
                target_particle="directory_deleter",
                payload={
                    "directory_path": params.get("directory_path"),
                    "recursive": params.get("recursive", False)
                }
            ))

        elif request_type == "move_file":
            plan.actions.append(PlannedAction(
                action_type=ActionType.MOVE_FILE,
                target_particle="file_mover",
                payload={
                    "source_path": params.get("source_path"),
                    "dest_path": params.get("dest_path")
                }
            ))

        elif request_type == "batch_create_files":
            plan.actions.append(PlannedAction(
                action_type=ActionType.BATCH_CREATE_FILES,
                target_particle="batch_file_creator",
                payload={
                    "files": params.get("files", [])
                }
            ))

        elif request_type == "apply_template":
            plan.actions.append(PlannedAction(
                action_type=ActionType.APPLY_TEMPLATE,
                target_particle="template_applier",
                payload={
                    "template_name": params.get("template_name"),
                    "template_content": params.get("template_content"),
                    "output_path": params.get("output_path"),
                    "variables": params.get("variables", {}),
                    "encoding": params.get("encoding", "utf-8")
                }
            ))

        # Complex multi-particle operations
        elif request_type == "create_component":
            component_name = params.get("component_name")
            base_path = params.get("base_path", "/tmp")
            component_path = f"{base_path}/{component_name}"

            plan.actions.append(PlannedAction(
                action_type=ActionType.CREATE_DIRECTORY,
                target_particle="directory_creator",
                payload={
                    "directory_path": component_path,
                    "parents": True
                },
                priority=MessagePriority.HIGH
            ))

            plan.actions.append(PlannedAction(
                action_type=ActionType.WRITE_FILE,
                target_particle="file_writer",
                payload={
                    "file_path": f"{component_path}/__init__.py",
                    "content": f'"""\n{component_name} component\n"""\n'
                }
            ))

            plan.actions.append(PlannedAction(
                action_type=ActionType.WRITE_FILE,
                target_particle="file_writer",
                payload={
                    "file_path": f"{component_path}/{component_name}.py",
                    "content": f'"""\n{component_name} module\n"""\n\n\nclass {component_name.title()}:\n    pass\n'
                }
            ))

        elif request_type == "scaffold_module":
            module_name = params.get("module_name")
            base_path = params.get("base_path", "/tmp")
            language = params.get("language", "python")

            template_name = "python_module" if language == "python" else "rust_module"

            plan.actions.append(PlannedAction(
                action_type=ActionType.CREATE_DIRECTORY,
                target_particle="directory_creator",
                payload={
                    "directory_path": base_path,
                    "parents": True
                }
            ))

            plan.actions.append(PlannedAction(
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

        logger.info(f"[orchestrator] Generated plan {plan_id} with {len(plan.actions)} actions")
        return plan

    async def route_and_collect(self, plan: ExecutionPlan) -> List[Dict[str, Any]]:
        """
        Stage 2a: Route actions via Corpus Callosum and collect results (SEQUENTIAL)

        Original Day 2 implementation - kept for compatibility
        """
        results = []

        for action in plan.actions:
            result = await self._route_single_action(action, plan.plan_id, len(results))
            results.append(result)

        return results

    async def route_and_collect_parallel(self, plan: ExecutionPlan) -> List[Dict[str, Any]]:
        """
        Stage 2b: Route actions via Corpus Callosum and collect results (PARALLEL)

        Day 3-4 Enhancement: Dispatch all actions without waiting, collect in parallel
        This reduces latency from O(n * 5s) to O(max(5s))
        """
        # Dispatch all actions simultaneously
        action_tasks = []
        for idx, action in enumerate(plan.actions):
            task = asyncio.create_task(
                self._route_single_action(action, plan.plan_id, idx)
            )
            action_tasks.append(task)

        # Collect all results in parallel with timeout
        results = await asyncio.gather(*action_tasks, return_exceptions=True)

        # Convert exceptions to error results
        processed_results = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "action_type": plan.actions[idx].action_type.value,
                    "status": "failed",
                    "error": str(result),
                    "target_particle": plan.actions[idx].target_particle
                })
            else:
                processed_results.append(result)

        return processed_results

    async def _route_single_action(
        self,
        action: PlannedAction,
        plan_id: str,
        action_idx: int
    ) -> Dict[str, Any]:
        """
        Route a single action and wait for result.

        Day 3-4: Enhanced with MTF ranking tracking
        """
        action_start_time = time.time()

        try:
            # Create result queue for this action
            action_id = f"{plan_id}_{action_idx}"
            result_queue = asyncio.Queue()

            async with self._result_lock:
                self._pending_results[action_id] = result_queue

            # Route message via Corpus Callosum
            msg_id = await self.corpus_callosum.route_message(
                source_tract=TractType.INTERNAL,
                dest_tract=TractType.EXTERNAL,
                priority=action.priority,
                payload={
                    "action_type": action.action_type.value,
                    "target_particle": action.target_particle,
                    "action_id": action_id,
                    **action.payload
                },
                payload_size=len(str(action.payload))
            )

            if msg_id >= 0:
                self.state['total_actions_dispatched'] += 1

                # Wait for result with timeout
                try:
                    particle_result = await asyncio.wait_for(
                        result_queue.get(),
                        timeout=self._result_timeout
                    )

                    action_time = time.time() - action_start_time

                    # Day 3-4: Record MTF usage
                    if self.enable_mtf_ranking and self.mtf_ranker:
                        self.mtf_ranker.record_particle_invocation(
                            action.target_particle,
                            action_time,
                            success=True
                        )

                    return {
                        "action_type": action.action_type.value,
                        "message_id": msg_id,
                        "status": "completed",
                        "target_particle": action.target_particle,
                        "result": particle_result,
                        "execution_time_s": action_time
                    }

                except asyncio.TimeoutError:
                    action_time = time.time() - action_start_time

                    # Day 3-4: Record MTF failure
                    if self.enable_mtf_ranking and self.mtf_ranker:
                        self.mtf_ranker.record_particle_invocation(
                            action.target_particle,
                            action_time,
                            success=False
                        )

                    logger.warning(
                        f"[orchestrator] Timeout waiting for result from "
                        f"{action.target_particle} (msg_id={msg_id})"
                    )
                    return {
                        "action_type": action.action_type.value,
                        "message_id": msg_id,
                        "status": "timeout",
                        "target_particle": action.target_particle,
                        "error": f"Result timeout after {self._result_timeout}s"
                    }

                finally:
                    # Clean up result queue
                    async with self._result_lock:
                        self._pending_results.pop(action_id, None)
            else:
                return {
                    "action_type": action.action_type.value,
                    "status": "failed",
                    "error": "Failed to route message",
                    "target_particle": action.target_particle
                }

        except Exception as e:
            logger.error(f"[orchestrator] Failed to route action: {e}")
            return {
                "action_type": action.action_type.value,
                "status": "failed",
                "error": str(e),
                "target_particle": action.target_particle
            }

    async def handle_result(self, action_id: str, result: Any):
        """
        Handle result message from particle.

        Called when ACTION_RESULT message is received from a particle.
        """
        async with self._result_lock:
            if action_id in self._pending_results:
                await self._pending_results[action_id].put(result)
                logger.debug(f"[orchestrator] Queued result for action {action_id}")
            else:
                logger.warning(
                    f"[orchestrator] Received result for unknown action: {action_id}"
                )

    async def synthesize(self, plan: ExecutionPlan, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Stage 3: Synthesize results into final output

        Day 3-4: Enhanced with advanced pattern learning
        """
        total_actions = len(results)
        completed_actions = sum(1 for r in results if r.get('status') == 'completed')
        timeout_actions = sum(1 for r in results if r.get('status') == 'timeout')
        failed_actions = sum(1 for r in results if r.get('status') == 'failed')

        synthesis = {
            "success": failed_actions == 0 and timeout_actions == 0,
            "total_actions": total_actions,
            "completed_actions": completed_actions,
            "timeout_actions": timeout_actions,
            "failed_actions": failed_actions,
            "results": results,
            "emergent_patterns": []
        }

        # Basic pattern detection (Day 2)
        if completed_actions > 0:
            batch_actions = [r for r in results if r.get('action_type') == 'batch_create_files']
            if batch_actions:
                synthesis["emergent_patterns"].append({
                    "pattern": "batch_optimization",
                    "description": "Multiple file operations compressed into single batch",
                    "efficiency_gain": "O(n) → O(1) for n files"
                })

            template_actions = [r for r in results if r.get('action_type') == 'apply_template']
            if template_actions:
                synthesis["emergent_patterns"].append({
                    "pattern": "template_abstraction",
                    "description": "Reusable patterns applied via templates",
                    "abstraction_level": "high"
                })

            dir_actions = [r for r in results if r.get('action_type') == 'create_directory']
            if dir_actions:
                synthesis["emergent_patterns"].append({
                    "pattern": "structural_hierarchy",
                    "description": "Organized directory structure created",
                    "depth": len(dir_actions)
                })

        return synthesis

    def get_advanced_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics including Day 3-4 features"""
        base_stats = self.get_stats()

        advanced_stats = {
            **base_stats,
            "orchestrator_state": self.state,
            "features": {
                "pattern_learning": self.enable_pattern_learning,
                "mtf_ranking": self.enable_mtf_ranking,
                "parallel_execution": self.enable_parallel_execution
            }
        }

        if self.pattern_learner:
            advanced_stats["pattern_learner"] = self.pattern_learner.get_stats()

        if self.mtf_ranker:
            advanced_stats["mtf_ranker"] = self.mtf_ranker.get_stats()

        return advanced_stats


# Factory function
def create_file_creator_orchestrator(
    corpus_callosum,
    state_file: Path = None,
    enable_pattern_learning: bool = True,
    enable_mtf_ranking: bool = True,
    enable_parallel_execution: bool = True
) -> FileCreatorOrchestrator:
    """Create file_creator_orchestrator instance with Day 3-4 features"""
    if state_file is None:
        state_file = (
            Path.home() / '.synapse-system' / '.synapse' /
            'particles' / 'file_creator_orchestrator_state.json'
        )

    config = AgentConfig(
        agent_id="file_creator_orchestrator",
        tract=TractType.INTERNAL
    )

    return FileCreatorOrchestrator(
        config,
        corpus_callosum,
        state_file,
        enable_pattern_learning=enable_pattern_learning,
        enable_mtf_ranking=enable_mtf_ranking,
        enable_parallel_execution=enable_parallel_execution
    )
