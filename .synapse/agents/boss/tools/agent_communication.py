"""
Agent Communication Tools - Inter-agent messaging and coordination

Implements dense context passing and multi-agent coordination protocols
for the Synapse ecosystem.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class AgentCommunicator:
    """
    Dense inter-agent communication protocol.
    Handles context compression, message routing, and response synthesis.
    """

    def __init__(self):
        self.active_agents = {}
        self.communication_log = []
        self.timeout_default = 300  # 5 minutes
        self.context_compression_ratio = 0.8

    async def query_agent(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query specific agent with dense context.

        Args:
            agent_name: Target agent (e.g., "@rust-specialist")
            context: Compressed context payload

        Returns:
            Dict with agent response and metadata
        """
        try:
            start_time = time.time()

            # Compress context for efficient transmission
            compressed_context = self._compress_context(context)

            # Format agent query
            query = self._format_agent_query(agent_name, compressed_context)

            # Log communication
            comm_id = self._log_communication(agent_name, "query", compressed_context)

            # Execute agent query (simulated for now)
            response = await self._execute_agent_query(agent_name, query)

            # Log response
            execution_time = time.time() - start_time
            self._log_response(comm_id, response, execution_time)

            return {
                "agent": agent_name,
                "response": response,
                "execution_time": execution_time,
                "context_compression": len(str(compressed_context)) / len(str(context)),
                "communication_id": comm_id
            }

        except Exception as e:
            return {
                "agent": agent_name,
                "error": f"Communication failed: {e}",
                "fallback_available": True
            }

    async def broadcast_to_agents(self, agent_list: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Broadcast context to multiple agents simultaneously.

        Args:
            agent_list: List of agent names
            context: Shared context payload

        Returns:
            Dict with all agent responses
        """
        try:
            # Create tasks for parallel execution
            tasks = []
            for agent in agent_list:
                task = asyncio.create_task(self.query_agent(agent, context))
                tasks.append((agent, task))

            # Execute all queries in parallel
            results = {}
            for agent, task in tasks:
                try:
                    result = await asyncio.wait_for(task, timeout=self.timeout_default)
                    results[agent] = result
                except asyncio.TimeoutError:
                    results[agent] = {
                        "agent": agent,
                        "error": "Timeout",
                        "timeout_duration": self.timeout_default
                    }

            return {
                "broadcast_results": results,
                "successful_responses": len([r for r in results.values() if "error" not in r]),
                "failed_responses": len([r for r in results.values() if "error" in r]),
                "total_execution_time": max([r.get("execution_time", 0) for r in results.values()])
            }

        except Exception as e:
            return {"error": f"Broadcast failed: {e}"}

    async def coordinate_parallel_execution(self, agent_tasks: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Coordinate parallel execution with dependency management.

        Args:
            agent_tasks: Dict mapping agents to their task contexts

        Returns:
            Dict with coordinated execution results
        """
        try:
            coordination_id = f"coord_{int(time.time())}"
            results = {}

            # Phase 1: Launch parallel tasks
            running_tasks = {}
            for agent, task_context in agent_tasks.items():
                task = asyncio.create_task(self.query_agent(agent, task_context))
                running_tasks[agent] = {
                    "task": task,
                    "context": task_context,
                    "start_time": time.time()
                }

            # Phase 2: Monitor and collect results
            while running_tasks:
                # Wait for any task to complete
                done_tasks = []
                for agent, task_info in running_tasks.items():
                    if task_info["task"].done():
                        try:
                            result = await task_info["task"]
                            results[agent] = result
                            done_tasks.append(agent)
                        except Exception as e:
                            results[agent] = {"error": str(e)}
                            done_tasks.append(agent)

                # Remove completed tasks
                for agent in done_tasks:
                    del running_tasks[agent]

                # Brief pause to prevent busy waiting
                if running_tasks:
                    await asyncio.sleep(0.1)

            return {
                "coordination_id": coordination_id,
                "results": results,
                "agents_coordinated": len(agent_tasks),
                "successful": len([r for r in results.values() if "error" not in r]),
                "failed": len([r for r in results.values() if "error" in r])
            }

        except Exception as e:
            return {"error": f"Coordination failed: {e}"}

    async def synthesize_multi_agent_results(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize results from multiple agents into coherent output.

        Args:
            agent_results: Results from coordinated agents

        Returns:
            Dict with synthesized output
        """
        try:
            successful_results = {k: v for k, v in agent_results.items()
                                if "error" not in v}

            # Extract deliverables
            deliverables = {}
            for agent, result in successful_results.items():
                agent_deliverables = result.get("response", {}).get("deliverables", [])
                if agent_deliverables:
                    deliverables[agent] = agent_deliverables

            # Create synthesis
            synthesis = {
                "primary_deliverable": self._identify_primary_deliverable(deliverables),
                "supporting_artifacts": self._collect_supporting_artifacts(deliverables),
                "agent_contributions": self._summarize_contributions(successful_results),
                "quality_metrics": self._calculate_synthesis_quality(successful_results),
                "coordination_efficiency": {
                    "agents_used": len(successful_results),
                    "success_rate": len(successful_results) / len(agent_results) if agent_results else 0,
                    "avg_response_time": self._calculate_avg_response_time(successful_results)
                }
            }

            return synthesis

        except Exception as e:
            return {"error": f"Synthesis failed: {e}"}

    def get_communication_log(self) -> List[Dict[str, Any]]:
        """Get communication history for analysis."""
        return self.communication_log

    def clear_communication_log(self):
        """Clear communication history."""
        self.communication_log = []

    # Private helper methods

    def _compress_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply context compression using Pneuma principles."""
        compressed = {}

        # Extract essential context
        if "task" in context:
            compressed["task"] = self._compress_task_description(context["task"])

        if "requirements" in context:
            compressed["req"] = context["requirements"][:5]  # Limit to top 5

        if "context" in context:
            compressed["ctx"] = self._extract_key_context(context["context"])

        if "standards" in context:
            compressed["std"] = context["standards"]

        if "dependencies" in context:
            compressed["deps"] = context["dependencies"]

        return compressed

    def _compress_task_description(self, task: str) -> str:
        """Compress task description to essential information."""
        # Simple compression - take first sentence and key phrases
        sentences = task.split('. ')
        compressed = sentences[0] if sentences else task

        # Limit length
        if len(compressed) > 200:
            compressed = compressed[:200] + "..."

        return compressed

    def _extract_key_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key context elements."""
        key_context = {}

        # Priority context keys
        priority_keys = ["language", "framework", "architecture", "constraints", "goals"]

        for key in priority_keys:
            if key in context:
                key_context[key] = context[key]

        return key_context

    def _format_agent_query(self, agent_name: str, context: Dict[str, Any]) -> str:
        """Format compressed context into agent query."""
        query_parts = [f"{agent_name} requested task:"]

        if "task" in context:
            query_parts.append(f"Task: {context['task']}")

        if "req" in context:
            query_parts.append(f"Requirements: {', '.join(context['req'])}")

        if "ctx" in context:
            ctx_items = [f"{k}: {v}" for k, v in context["ctx"].items()]
            query_parts.append(f"Context: {', '.join(ctx_items)}")

        if "deps" in context:
            query_parts.append(f"Dependencies: {', '.join(context['deps'])}")

        return "\n".join(query_parts)

    def _log_communication(self, agent: str, message_type: str, context: Dict[str, Any]) -> str:
        """Log communication event."""
        comm_id = f"{agent}_{int(time.time())}"

        log_entry = {
            "id": comm_id,
            "timestamp": time.time(),
            "agent": agent,
            "type": message_type,
            "context_size": len(str(context)),
            "context_keys": list(context.keys())
        }

        self.communication_log.append(log_entry)
        return comm_id

    def _log_response(self, comm_id: str, response: Dict[str, Any], execution_time: float):
        """Log response to communication."""
        # Find original log entry and update
        for entry in self.communication_log:
            if entry["id"] == comm_id:
                entry["response_received"] = True
                entry["execution_time"] = execution_time
                entry["response_size"] = len(str(response))
                break

    async def _execute_agent_query(self, agent_name: str, query: str) -> Dict[str, Any]:
        """
        Execute agent query (simplified simulation).

        In full implementation, this would:
        1. Route to actual agent process
        2. Handle model selection (Opus/Sonnet/Haiku)
        3. Process agent-specific tools
        4. Return structured response
        """
        # Simulate agent processing time
        processing_time = 2 + (len(query) / 100)  # Base + complexity factor
        await asyncio.sleep(min(processing_time, 10))  # Cap at 10 seconds

        # Generate simulated response
        response = {
            "agent": agent_name,
            "status": "completed",
            "deliverables": [
                f"{agent_name} analysis completed",
                f"Generated solution for query"
            ],
            "confidence": 0.85,
            "recommendations": ["Follow-up task needed", "Consider optimization"],
            "execution_details": {
                "model_used": "claude-3-opus" if "specialist" in agent_name else "claude-3-sonnet",
                "tools_invoked": ["analyze", "generate", "validate"],
                "processing_time": processing_time
            }
        }

        return response

    def _identify_primary_deliverable(self, deliverables: Dict[str, List[str]]) -> Optional[str]:
        """Identify primary deliverable from agent results."""
        if not deliverables:
            return None

        # Simple heuristic - longest deliverable list indicates primary contributor
        primary_agent = max(deliverables.keys(), key=lambda k: len(deliverables[k]))
        primary_deliverables = deliverables[primary_agent]

        return primary_deliverables[0] if primary_deliverables else None

    def _collect_supporting_artifacts(self, deliverables: Dict[str, List[str]]) -> List[str]:
        """Collect supporting artifacts from all agents."""
        all_artifacts = []
        for agent_deliverables in deliverables.values():
            all_artifacts.extend(agent_deliverables[1:])  # Skip primary deliverable

        return all_artifacts

    def _summarize_contributions(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Summarize each agent's contribution."""
        contributions = {}

        for agent, result in results.items():
            if "response" in result:
                deliverables = result["response"].get("deliverables", [])
                contributions[agent] = f"Provided {len(deliverables)} deliverables"
            else:
                contributions[agent] = "Provided analysis"

        return contributions

    def _calculate_synthesis_quality(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality metrics for synthesis."""
        total_confidence = sum(
            result.get("response", {}).get("confidence", 0.5)
            for result in results.values()
        )
        avg_confidence = total_confidence / len(results) if results else 0

        return {
            "average_confidence": avg_confidence,
            "completeness": len(results) / max(1, len(results)),  # All agents responded
            "consistency": 0.8  # Placeholder - would analyze response consistency
        }

    def _calculate_avg_response_time(self, results: Dict[str, Any]) -> float:
        """Calculate average response time."""
        response_times = [
            result.get("execution_time", 0)
            for result in results.values()
        ]

        return sum(response_times) / len(response_times) if response_times else 0


# Standalone communication functions

async def query_clarity_judge(original_code: str, transformed_code: str) -> Dict[str, Any]:
    """
    Query clarity judge agent for readability assessment.

    Args:
        original_code: Original code before transformation
        transformed_code: Code after transformation

    Returns:
        Dict with clarity assessment
    """
    communicator = AgentCommunicator()

    context = {
        "task": "Assess readability impact of code transformation",
        "original": original_code,
        "transformed": transformed_code,
        "metrics_required": ["readability_score", "complexity_change", "maintainability_impact"]
    }

    return await communicator.query_agent("@clarity-judge", context)


async def coordinate_language_specialists(task: str, languages: List[str]) -> Dict[str, Any]:
    """
    Coordinate multiple language specialists for polyglot projects.

    Args:
        task: Task description
        languages: List of programming languages involved

    Returns:
        Dict with coordinated results from all language specialists
    """
    communicator = AgentCommunicator()

    # Create agent tasks for each language
    agent_tasks = {}
    for lang in languages:
        agent_name = f"@{lang}-specialist"
        agent_tasks[agent_name] = {
            "task": task,
            "language": lang,
            "context": {"project_type": "polyglot"},
            "requirements": ["language_specific_analysis", "cross_language_compatibility"]
        }

    return await communicator.coordinate_parallel_execution(agent_tasks)


async def orchestrate_feature_workflow(feature_description: str) -> Dict[str, Any]:
    """
    Orchestrate complete feature implementation workflow.

    Args:
        feature_description: Description of feature to implement

    Returns:
        Dict with complete workflow results
    """
    communicator = AgentCommunicator()

    # Define workflow sequence
    workflow_agents = {
        "@architect": {
            "task": f"Design architecture for: {feature_description}",
            "deliverables": ["architecture_design", "component_specifications"]
        },
        "@rust-specialist": {
            "task": f"Implement feature: {feature_description}",
            "dependencies": ["@architect"],
            "deliverables": ["implementation", "unit_tests"]
        },
        "@test-runner": {
            "task": f"Test feature: {feature_description}",
            "dependencies": ["@rust-specialist"],
            "deliverables": ["test_results", "coverage_report"]
        },
        "@docs-writer": {
            "task": f"Document feature: {feature_description}",
            "dependencies": ["@rust-specialist"],
            "deliverables": ["documentation", "usage_examples"]
        }
    }

    return await communicator.coordinate_parallel_execution(workflow_agents)