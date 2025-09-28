#!/usr/bin/env python3
"""
Synapse Project Manager Agent - Master Network Orchestrator

The neural center of the agent ecosystem, managing complex multi-agent workflows
with maximum coordination density and emergent intelligence.
"""

import asyncio
import json
import yaml
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Import orchestration tools
from tools.orchestration_tools import *
from tools.workflow_tools import *
from tools.delegation_tools import *
from tools.monitoring_tools import *
from tools.synthesis_tools import *
from tools.synapse_integration import *
from tools.agent_communication import *

class SynapseProjectManagerAgent:
    """Master orchestrator for multi-agent workflows."""

    def __init__(self):
        self.agent_dir = Path(__file__).parent
        self.config = self._load_config()
        self.state = self._load_state()
        self.communicator = AgentCommunicator()

    def _load_config(self) -> Dict[str, Any]:
        """Load agent configuration."""
        config_path = self.agent_dir / "synapse_pm_config.yml"
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._default_config()

    def _load_state(self) -> Dict[str, Any]:
        """Load agent symbolic state."""
        state_path = self.agent_dir / "synapse_pm_state.json"
        try:
            with open(state_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._default_state()

    def _save_state(self):
        """Save current state to disk."""
        state_path = self.agent_dir / "synapse_pm_state.json"
        with open(state_path, 'w') as f:
            json.dump(self.state, f, indent=2)

    def _default_config(self) -> Dict[str, Any]:
        """Default configuration when none exists."""
        return {
            "agent": {
                "name": "synapse-project-manager",
                "model_preference": {
                    "primary": "claude-3-opus",
                    "fallback": "claude-3-sonnet",
                    "simple_tasks": "claude-3-haiku"
                }
            },
            "orchestration": {
                "max_parallel_agents": 5,
                "timeout_per_agent": 300,
                "retry_on_failure": True,
                "context_density": 0.8
            },
            "workflows": {
                "feature": ["@architect", "@dev", "@test", "@code-hound", "@4QZero", "@docs-writer", "@git-workflow"],
                "bugfix": ["@test-runner", "@dev", "@test-runner", "@git-workflow"],
                "refactor": ["@test-runner", "@dev", "@test-runner", "@code-hound", "@4QZero"]
            }
        }

    def _default_state(self) -> Dict[str, Any]:
        """Default state when none exists."""
        return {
            "workflows": {},
            "agents": {"available": [], "active": {}, "blocked": []},
            "tasks": {},
            "patterns": [],
            "cycle": 0
        }

    # Core orchestration tools with @tool decorators

    async def orchestrate_workflow(self, request: str, workflow_type: str = "auto") -> Dict[str, Any]:
        """
        Main orchestration entry point. Executes The Loop for complex requests.

        Args:
            request: User request to orchestrate
            workflow_type: Template to use ("auto", "feature", "bugfix", "refactor")

        Returns:
            Dict with orchestration results and agent outputs
        """
        try:
            # The Loop: Observe → Orient → Decide → Act

            # 1. Observe (o:)
            analysis = await self.o_analyze(request)
            dependencies = await self.o_dependencies(analysis["tasks"])
            agent_mapping = await self.o_agents(analysis["tasks"])

            # 2. Orient (r:)
            pattern = await self.r_pattern(workflow_type, analysis)
            parallel_streams = await self.r_parallel(dependencies)
            optimized_sequence = await self.r_optimize(parallel_streams)

            # 3. Decide (d:)
            delegations = await self.d_delegate(optimized_sequence, agent_mapping)
            schedule = await self.d_schedule(optimized_sequence)
            monitoring_plan = await self.d_monitor(delegations)

            # 4. Act (a:)
            execution_results = await self.a_execute(delegations, schedule)
            synthesized_output = await self.a_synthesize(execution_results)
            validation_result = await self.a_validate(synthesized_output)

            # Update state and return results
            workflow_id = f"wf_{len(self.state['workflows']) + 1:03d}"
            self.state["workflows"][workflow_id] = {
                "request": request,
                "pattern": pattern,
                "agents_used": list(agent_mapping.keys()),
                "status": "completed" if validation_result["valid"] else "partial",
                "cycle": self.state["cycle"]
            }
            self.state["cycle"] += 1
            self._save_state()

            return {
                "workflow_id": workflow_id,
                "pattern": pattern,
                "execution_graph": optimized_sequence,
                "agent_results": execution_results,
                "synthesized_output": synthesized_output,
                "validation": validation_result,
                "performance": {
                    "agents_coordinated": len(agent_mapping),
                    "parallel_streams": len(parallel_streams),
                    "total_tasks": len(analysis["tasks"])
                }
            }

        except Exception as e:
            return {
                "error": f"Orchestration failed: {e}",
                "fallback": "Executing simplified workflow"
            }

    async def decompose_task(self, complex_task: str) -> Dict[str, Any]:
        """
        Break complex task into atomic, executable components.

        Args:
            complex_task: High-level task description

        Returns:
            Dict with task graph and dependencies
        """
        try:
            # Use pattern matching to identify task type
            task_patterns = {
                "implement": ["design", "code", "test", "document"],
                "fix": ["reproduce", "diagnose", "repair", "verify"],
                "refactor": ["analyze", "plan", "transform", "validate"],
                "add feature": ["specify", "design", "implement", "integrate", "test"]
            }

            # Extract atomic tasks
            atomic_tasks = []
            task_type = self._identify_task_type(complex_task)

            if task_type in task_patterns:
                for i, subtask in enumerate(task_patterns[task_type]):
                    atomic_tasks.append({
                        "id": f"t_{i+1:03d}",
                        "description": f"{subtask} - {complex_task}",
                        "type": subtask,
                        "complexity": self._estimate_complexity(subtask, complex_task),
                        "agent_required": self._suggest_agent(subtask)
                    })

            # Build dependency graph
            dependencies = self._build_dependencies(atomic_tasks)

            return {
                "original_task": complex_task,
                "task_type": task_type,
                "atomic_tasks": atomic_tasks,
                "dependencies": dependencies,
                "estimated_duration": sum(t["complexity"] for t in atomic_tasks)
            }

        except Exception as e:
            return {"error": f"Task decomposition failed: {e}"}

    async def coordinate_agents(self, agent_tasks: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute inter-agent communication and coordination.

        Args:
            agent_tasks: Mapping of agents to their assigned tasks

        Returns:
            Dict with coordination results
        """
        try:
            coordination_results = {}
            active_agents = []

            for agent_name, task_info in agent_tasks.items():
                # Prepare dense context for agent
                context = {
                    "task": task_info["task"],
                    "context": task_info.get("context", {}),
                    "requirements": task_info.get("requirements", []),
                    "dependencies": task_info.get("dependencies", []),
                    "standards": await get_synapse_standards(task_info.get("language", "general"))
                }

                # Update agent status
                self.state["agents"]["active"][agent_name] = "⊙"
                active_agents.append(agent_name)

                # Execute agent task
                try:
                    result = await self.communicator.query_agent(agent_name, context)
                    self.state["agents"]["active"][agent_name] = "⊗"
                    coordination_results[agent_name] = {
                        "status": "completed",
                        "result": result,
                        "execution_time": result.get("execution_time", 0)
                    }
                except Exception as e:
                    self.state["agents"]["active"][agent_name] = "⊘"
                    coordination_results[agent_name] = {
                        "status": "failed",
                        "error": str(e),
                        "fallback_needed": True
                    }

            self._save_state()

            return {
                "agents_coordinated": len(active_agents),
                "successful": sum(1 for r in coordination_results.values() if r["status"] == "completed"),
                "failed": sum(1 for r in coordination_results.values() if r["status"] == "failed"),
                "results": coordination_results
            }

        except Exception as e:
            return {"error": f"Agent coordination failed: {e}"}

    async def synthesize_results(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge multi-agent outputs into coherent result.

        Args:
            agent_results: Results from coordinated agents

        Returns:
            Dict with synthesized output
        """
        try:
            successful_results = {k: v for k, v in agent_results.items()
                                if v.get("status") == "completed"}

            # Extract deliverables from each agent
            deliverables = {}
            for agent, result in successful_results.items():
                if "deliverables" in result.get("result", {}):
                    deliverables[agent] = result["result"]["deliverables"]

            # Synthesize into final output
            synthesis = {
                "primary_output": self._identify_primary_deliverable(deliverables),
                "supporting_artifacts": self._collect_supporting_artifacts(deliverables),
                "quality_metrics": self._calculate_quality_metrics(successful_results),
                "agent_contributions": {agent: self._summarize_contribution(result)
                                       for agent, result in successful_results.items()},
                "workflow_efficiency": {
                    "agents_used": len(successful_results),
                    "parallel_execution": self._calculate_parallelism(agent_results),
                    "context_density": self._measure_context_density(agent_results)
                }
            }

            return synthesis

        except Exception as e:
            return {"error": f"Result synthesis failed: {e}"}

    async def validate_completion(self, synthesized_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate workflow completion against standards and requirements.

        Args:
            synthesized_result: Synthesized output from agents

        Returns:
            Dict with validation results
        """
        try:
            validation_checks = []

            # Check primary deliverable quality
            if "primary_output" in synthesized_result:
                quality_check = await self._validate_quality(synthesized_result["primary_output"])
                validation_checks.append(quality_check)

            # Validate against synapse standards
            standards_check = await self._validate_standards(synthesized_result)
            validation_checks.append(standards_check)

            # Check completeness
            completeness_check = self._validate_completeness(synthesized_result)
            validation_checks.append(completeness_check)

            overall_valid = all(check.get("valid", False) for check in validation_checks)
            confidence_score = sum(check.get("confidence", 0) for check in validation_checks) / len(validation_checks)

            return {
                "valid": overall_valid,
                "confidence": confidence_score,
                "checks": validation_checks,
                "recommendations": self._generate_recommendations(validation_checks) if not overall_valid else []
            }

        except Exception as e:
            return {"error": f"Validation failed: {e}", "valid": False}

    # Observe phase methods (o:)

    async def o_analyze(self, request: str) -> Dict[str, Any]:
        """Analyze request and decompose into atomic tasks."""
        return await o_analyze(request)

    async def o_dependencies(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build dependency graph from task list."""
        return await o_dependencies(tasks)

    async def o_agents(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Map tasks to appropriate agents."""
        return await o_agents(tasks)

    # Orient phase methods (r:)

    async def r_pattern(self, workflow_type: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Match request to workflow pattern."""
        return await r_pattern(workflow_type, analysis)

    async def r_parallel(self, dependency_graph: Dict[str, List[str]]) -> List[List[str]]:
        """Identify parallel execution opportunities."""
        return await r_parallel(dependency_graph)

    async def r_optimize(self, parallel_streams: List[List[str]]) -> Dict[str, Any]:
        """Optimize execution sequence."""
        return await r_optimize(parallel_streams)

    # Decide phase methods (d:)

    async def d_delegate(self, execution_plan: Dict[str, Any], agent_mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Create delegation plan for agents."""
        delegations = {}

        for agent, tasks in agent_mapping.get("assignments", {}).items():
            delegations[agent] = {
                "tasks": tasks,
                "context": execution_plan,
                "timeout": self.config["orchestration"]["timeout_per_agent"]
            }

        return delegations

    async def d_schedule(self, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Create execution schedule."""
        return {
            "execution_order": execution_plan.get("optimized_streams", []),
            "estimated_duration": sum(15 for _ in execution_plan.get("optimized_streams", [])),
            "resource_allocation": "balanced"
        }

    async def d_monitor(self, delegations: Dict[str, Any]) -> Dict[str, Any]:
        """Create monitoring plan."""
        return {
            "agents_to_monitor": list(delegations.keys()),
            "check_interval": 30,  # seconds
            "timeout_handling": "graceful_degradation"
        }

    # Act phase methods (a:)

    async def a_execute(self, delegations: Dict[str, Any], schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coordinated agent tasks."""
        return await self.coordinate_agents(delegations)

    async def a_synthesize(self, execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize multi-agent results."""
        return await self.synthesize_results(execution_results.get("results", {}))

    async def a_validate(self, synthesized_output: Dict[str, Any]) -> Dict[str, Any]:
        """Validate completion against standards."""
        return await self.validate_completion(synthesized_output)

    # Helper methods

    def _identify_task_type(self, task: str) -> str:
        """Identify task type from description."""
        task_lower = task.lower()
        if any(word in task_lower for word in ["implement", "create", "add", "build"]):
            return "implement"
        elif any(word in task_lower for word in ["fix", "bug", "error", "issue"]):
            return "fix"
        elif any(word in task_lower for word in ["refactor", "optimize", "improve"]):
            return "refactor"
        else:
            return "general"

    def _estimate_complexity(self, subtask: str, context: str) -> int:
        """Estimate task complexity (1-10 scale)."""
        # Simple heuristic based on subtask type
        complexity_map = {
            "design": 8, "implement": 9, "test": 6, "document": 4,
            "reproduce": 3, "diagnose": 7, "repair": 8, "verify": 5,
            "analyze": 6, "plan": 5, "transform": 9, "validate": 4
        }
        return complexity_map.get(subtask, 5)

    def _suggest_agent(self, subtask: str) -> str:
        """Suggest appropriate agent for subtask."""
        agent_mapping = {
            "design": "@architect",
            "implement": "@dev",
            "test": "@test-runner",
            "document": "@docs-writer",
            "reproduce": "@test-runner",
            "diagnose": "@code-hound",
            "repair": "@dev",
            "verify": "@test-runner",
            "analyze": "@code-hound",
            "plan": "@architect",
            "transform": "@4QZero",
            "validate": "@code-hound"
        }
        return agent_mapping.get(subtask, "@dev")

    def _build_dependencies(self, tasks: List[Dict]) -> Dict[str, List[str]]:
        """Build task dependency graph."""
        dependencies = {}
        for i, task in enumerate(tasks):
            task_id = task["id"]
            if i == 0:
                dependencies[task_id] = []  # First task has no dependencies
            else:
                dependencies[task_id] = [tasks[i-1]["id"]]  # Sequential by default
        return dependencies

if __name__ == "__main__":
    agent = SynapseProjectManagerAgent()
    print(f"Synapse Project Manager Agent initialized")
    print(f"Configuration: {agent.config['agent']['name']}")
    print(f"Workflow patterns: {len(agent.config['workflows'])}")
    print(f"Current state cycle: {agent.state['cycle']}")