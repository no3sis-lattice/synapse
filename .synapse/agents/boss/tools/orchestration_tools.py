"""
Orchestration Tools - Core coordination functions

Implements The Loop phases:
- Observe (o:): Task analysis and dependency mapping
- Orient (r:): Pattern matching and optimization
- Decide (d:): Agent assignment and scheduling
- Act (a:): Execution and validation
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


async def o_analyze(request: str) -> Dict[str, Any]:
    """
    Analyze request and decompose into atomic tasks.

    Args:
        request: User request to analyze

    Returns:
        Dict with task breakdown and complexity analysis
    """
    try:
        # Extract key components from request
        components = _extract_request_components(request)

        # Decompose into atomic tasks
        atomic_tasks = _decompose_to_tasks(request, components)

        # Assess complexity
        complexity_score = _calculate_complexity(atomic_tasks)

        # Identify required capabilities
        capabilities = _identify_required_capabilities(atomic_tasks)

        return {
            "request": request,
            "components": components,
            "tasks": atomic_tasks,
            "complexity": complexity_score,
            "capabilities": capabilities,
            "estimated_duration": sum(t.get("duration", 5) for t in atomic_tasks)
        }

    except Exception as e:
        return {"error": f"Analysis failed: {e}"}


async def o_dependencies(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build dependency graph from task list.

    Args:
        tasks: List of atomic tasks

    Returns:
        Dict with dependency graph and execution waves
    """
    try:
        dependency_graph = {}
        execution_waves = []

        # Build basic dependency relationships
        for i, task in enumerate(tasks):
            task_id = task.get("id", f"task_{i}")
            dependencies = _identify_task_dependencies(task, tasks[:i])
            dependency_graph[task_id] = dependencies

        # Calculate execution waves (topological layers)
        execution_waves = _calculate_execution_waves(dependency_graph)

        # Identify critical path
        critical_path = _find_critical_path(dependency_graph, tasks)

        return {
            "graph": dependency_graph,
            "waves": execution_waves,
            "critical_path": critical_path,
            "parallelism_score": len(execution_waves[0]) if execution_waves else 1
        }

    except Exception as e:
        return {"error": f"Dependency analysis failed: {e}"}


async def o_agents(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Map tasks to appropriate agents based on capabilities.

    Args:
        tasks: List of atomic tasks

    Returns:
        Dict mapping agents to assigned tasks
    """
    try:
        agent_capabilities = _get_agent_capabilities()
        agent_assignments = {}

        for task in tasks:
            best_agent = _match_task_to_agent(task, agent_capabilities)

            if best_agent not in agent_assignments:
                agent_assignments[best_agent] = []

            agent_assignments[best_agent].append({
                "task_id": task.get("id"),
                "description": task.get("description"),
                "complexity": task.get("complexity", 5),
                "requirements": task.get("requirements", [])
            })

        # Calculate load balancing
        load_distribution = {agent: sum(t["complexity"] for t in tasks)
                           for agent, tasks in agent_assignments.items()}

        return {
            "assignments": agent_assignments,
            "load_distribution": load_distribution,
            "agents_required": len(agent_assignments),
            "max_load": max(load_distribution.values()) if load_distribution else 0
        }

    except Exception as e:
        return {"error": f"Agent mapping failed: {e}"}


async def r_pattern(workflow_type: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Match request to workflow pattern template.

    Args:
        workflow_type: Requested pattern ("auto", "feature", "bugfix", etc.)
        analysis: Task analysis results

    Returns:
        Dict with matched pattern and customizations
    """
    try:
        # Load workflow patterns
        patterns = _load_workflow_patterns()

        if workflow_type == "auto":
            # Auto-detect best pattern
            matched_pattern = _auto_detect_pattern(analysis, patterns)
        else:
            matched_pattern = patterns.get(workflow_type, patterns["default"])

        # Customize pattern for specific request
        customized_pattern = _customize_pattern(matched_pattern, analysis)

        return {
            "pattern_name": matched_pattern["name"],
            "base_sequence": matched_pattern["sequence"],
            "customized_sequence": customized_pattern["sequence"],
            "parallel_opportunities": customized_pattern["parallel"],
            "estimated_efficiency": customized_pattern["efficiency"]
        }

    except Exception as e:
        return {"error": f"Pattern matching failed: {e}"}


async def r_parallel(dependency_graph: Dict[str, List[str]]) -> List[List[str]]:
    """
    Identify parallel execution opportunities.

    Args:
        dependency_graph: Task dependency relationships

    Returns:
        List of parallel execution streams
    """
    try:
        parallel_streams = []
        remaining_tasks = set(dependency_graph.keys())

        while remaining_tasks:
            # Find tasks with no unresolved dependencies
            available_tasks = []
            for task in remaining_tasks:
                dependencies = dependency_graph[task]
                if all(dep not in remaining_tasks for dep in dependencies):
                    available_tasks.append(task)

            if not available_tasks:
                # Circular dependency detected
                break

            parallel_streams.append(available_tasks)
            remaining_tasks -= set(available_tasks)

        return parallel_streams

    except Exception as e:
        return []


async def r_optimize(parallel_streams: List[List[str]]) -> Dict[str, Any]:
    """
    Optimize execution sequence for maximum efficiency.

    Args:
        parallel_streams: Parallel execution opportunities

    Returns:
        Dict with optimized execution plan
    """
    try:
        # Calculate optimal resource allocation
        resource_allocation = _optimize_resource_allocation(parallel_streams)

        # Minimize coordination overhead
        coordination_plan = _minimize_coordination_overhead(parallel_streams)

        # Generate execution timeline
        timeline = _generate_execution_timeline(parallel_streams, resource_allocation)

        return {
            "optimized_streams": parallel_streams,
            "resource_allocation": resource_allocation,
            "coordination_plan": coordination_plan,
            "timeline": timeline,
            "efficiency_score": _calculate_efficiency_score(parallel_streams, timeline)
        }

    except Exception as e:
        return {"error": f"Optimization failed: {e}"}


# Helper functions

def _extract_request_components(request: str) -> Dict[str, Any]:
    """Extract key components from user request."""
    components = {
        "action_verbs": re.findall(r'\b(implement|create|fix|refactor|add|build|update)\b', request.lower()),
        "technologies": re.findall(r'\b(rust|python|typescript|javascript|go|java|react|vue)\b', request.lower()),
        "entities": _extract_entities(request),
        "complexity_indicators": _identify_complexity_indicators(request)
    }
    return components


def _decompose_to_tasks(request: str, components: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Decompose request into atomic tasks."""
    tasks = []

    # Basic task patterns based on action verbs
    if "implement" in components.get("action_verbs", []):
        tasks.extend([
            {"id": "design", "description": "Design implementation", "complexity": 7},
            {"id": "code", "description": "Write code", "complexity": 8},
            {"id": "test", "description": "Test implementation", "complexity": 6}
        ])
    elif "fix" in components.get("action_verbs", []):
        tasks.extend([
            {"id": "reproduce", "description": "Reproduce issue", "complexity": 4},
            {"id": "diagnose", "description": "Diagnose root cause", "complexity": 6},
            {"id": "repair", "description": "Implement fix", "complexity": 7}
        ])
    else:
        # Generic task breakdown
        tasks.extend([
            {"id": "analyze", "description": "Analyze requirements", "complexity": 5},
            {"id": "execute", "description": "Execute task", "complexity": 7},
            {"id": "validate", "description": "Validate results", "complexity": 4}
        ])

    return tasks


def _calculate_complexity(tasks: List[Dict[str, Any]]) -> int:
    """Calculate overall complexity score."""
    if not tasks:
        return 1
    return min(10, sum(task.get("complexity", 5) for task in tasks) // len(tasks))


def _identify_required_capabilities(tasks: List[Dict[str, Any]]) -> List[str]:
    """Identify capabilities required for tasks."""
    capabilities = set()

    capability_mapping = {
        "design": "architecture",
        "code": "development",
        "test": "testing",
        "analyze": "analysis",
        "diagnose": "debugging",
        "validate": "quality_assurance"
    }

    for task in tasks:
        task_id = task.get("id", "")
        if task_id in capability_mapping:
            capabilities.add(capability_mapping[task_id])

    return list(capabilities)


def _get_agent_capabilities() -> Dict[str, List[str]]:
    """Get agent capability mappings."""
    return {
        "@architect": ["architecture", "design", "planning"],
        "@rust-specialist": ["development", "rust", "systems"],
        "@python-specialist": ["development", "python", "scripting"],
        "@typescript-specialist": ["development", "typescript", "web"],
        "@test-runner": ["testing", "validation", "quality_assurance"],
        "@code-hound": ["analysis", "quality_assurance", "debugging"],
        "@4QZero": ["optimization", "refactoring", "abstraction"],
        "@docs-writer": ["documentation", "writing"],
        "@git-workflow": ["version_control", "deployment"]
    }


def _match_task_to_agent(task: Dict[str, Any], agent_capabilities: Dict[str, List[str]]) -> str:
    """Match task to best suited agent."""
    task_id = task.get("id", "")

    # Direct task-to-agent mappings
    direct_mappings = {
        "design": "@architect",
        "code": "@rust-specialist",  # Default to rust, could be dynamic
        "test": "@test-runner",
        "analyze": "@code-hound",
        "diagnose": "@code-hound",
        "validate": "@test-runner",
        "document": "@docs-writer"
    }

    return direct_mappings.get(task_id, "@rust-specialist")


def _load_workflow_patterns() -> Dict[str, Any]:
    """Load predefined workflow patterns."""
    return {
        "feature": {
            "name": "feature_implementation",
            "sequence": ["@architect", "@rust-specialist", "@test-runner", "@code-hound", "@4QZero", "@docs-writer"],
            "parallel_opportunities": [["@architect", "@docs-writer"], ["@rust-specialist", "@test-runner"]]
        },
        "bugfix": {
            "name": "bug_fix",
            "sequence": ["@test-runner", "@rust-specialist", "@test-runner", "@git-workflow"],
            "parallel_opportunities": []
        },
        "refactor": {
            "name": "code_refactor",
            "sequence": ["@test-runner", "@rust-specialist", "@code-hound", "@4QZero"],
            "parallel_opportunities": [["@code-hound", "@4QZero"]]
        },
        "default": {
            "name": "general_task",
            "sequence": ["@rust-specialist", "@test-runner"],
            "parallel_opportunities": []
        }
    }


def _auto_detect_pattern(analysis: Dict[str, Any], patterns: Dict[str, Any]) -> Dict[str, Any]:
    """Auto-detect best workflow pattern."""
    components = analysis.get("components", {})

    if "implement" in components.get("action_verbs", []):
        return patterns["feature"]
    elif "fix" in components.get("action_verbs", []):
        return patterns["bugfix"]
    elif "refactor" in components.get("action_verbs", []):
        return patterns["refactor"]
    else:
        return patterns["default"]


def _customize_pattern(pattern: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Customize workflow pattern for specific request."""
    # For now, return pattern as-is
    # In full implementation, would modify based on analysis
    return {
        "sequence": pattern["sequence"],
        "parallel": pattern.get("parallel_opportunities", []),
        "efficiency": 0.8  # Baseline efficiency
    }


# Additional helper functions for full implementation
def _extract_entities(request: str) -> List[str]:
    """Extract named entities from request."""
    # Simple regex-based extraction
    entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', request)
    return entities


def _identify_complexity_indicators(request: str) -> List[str]:
    """Identify complexity indicators in request."""
    indicators = []
    if len(request) > 200:
        indicators.append("long_description")
    if "complex" in request.lower():
        indicators.append("explicit_complexity")
    if "integration" in request.lower():
        indicators.append("integration_required")
    return indicators


def _identify_task_dependencies(task: Dict[str, Any], previous_tasks: List[Dict[str, Any]]) -> List[str]:
    """Identify dependencies for a task."""
    # Simple sequential dependency for now
    if previous_tasks:
        return [previous_tasks[-1].get("id")]
    return []


def _calculate_execution_waves(dependency_graph: Dict[str, List[str]]) -> List[List[str]]:
    """Calculate execution waves from dependency graph."""
    waves = []
    remaining = set(dependency_graph.keys())

    while remaining:
        wave = []
        for task in list(remaining):
            deps = dependency_graph[task]
            if all(dep not in remaining for dep in deps):
                wave.append(task)

        if not wave:
            break

        waves.append(wave)
        remaining -= set(wave)

    return waves


def _find_critical_path(dependency_graph: Dict[str, List[str]], tasks: List[Dict[str, Any]]) -> List[str]:
    """Find critical path through task graph."""
    # Simplified critical path - just return longest sequential path
    paths = []

    def find_path(task_id, current_path):
        current_path = current_path + [task_id]
        dependents = [t for t, deps in dependency_graph.items() if task_id in deps]

        if not dependents:
            paths.append(current_path)
        else:
            for dependent in dependents:
                find_path(dependent, current_path)

    # Start from tasks with no dependencies
    roots = [task for task, deps in dependency_graph.items() if not deps]
    for root in roots:
        find_path(root, [])

    return max(paths, key=len) if paths else []


def _optimize_resource_allocation(streams: List[List[str]]) -> Dict[str, Any]:
    """Optimize resource allocation across streams."""
    return {
        "max_parallel": min(5, max(len(stream) for stream in streams) if streams else 1),
        "load_balancing": "round_robin",
        "resource_limit": 80  # CPU percentage
    }


def _minimize_coordination_overhead(streams: List[List[str]]) -> Dict[str, Any]:
    """Minimize coordination overhead."""
    return {
        "context_sharing": "minimal",
        "sync_points": len(streams) - 1 if streams else 0,
        "communication_pattern": "hub_and_spoke"
    }


def _generate_execution_timeline(streams: List[List[str]], allocation: Dict[str, Any]) -> Dict[str, Any]:
    """Generate execution timeline."""
    return {
        "total_waves": len(streams),
        "estimated_duration": len(streams) * 60,  # 60 seconds per wave
        "parallel_efficiency": allocation.get("max_parallel", 1)
    }


def _calculate_efficiency_score(streams: List[List[str]], timeline: Dict[str, Any]) -> float:
    """Calculate workflow efficiency score."""
    if not streams:
        return 0.0

    total_tasks = sum(len(stream) for stream in streams)
    parallel_efficiency = timeline.get("parallel_efficiency", 1)

    return min(1.0, (total_tasks * parallel_efficiency) / (len(streams) * 10))