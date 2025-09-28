"""
Workflow Tools - Template management and execution optimization

Implements workflow pattern library and execution graph optimization.
"""

from typing import Dict, List, Any, Optional, Tuple


async def load_workflow_template(template_name: str) -> Dict[str, Any]:
    """
    Load predefined workflow template.

    Args:
        template_name: Name of workflow template

    Returns:
        Dict with workflow definition
    """
    templates = {
        "feature": {
            "name": "feature_implementation",
            "description": "Complete feature development pipeline",
            "sequence": ["@architect", "@dev", "@test", "@hound", "@4Q", "@docs"],
            "parallel_streams": [
                ["@architect", "@docs"],  # Design and documentation can be parallel
                ["@dev", "@test"]         # Development and test writing can overlap
            ],
            "dependencies": {
                "@dev": ["@architect"],
                "@test": ["@dev"],
                "@hound": ["@dev"],
                "@4Q": ["@hound"],
                "@docs": []  # Can start early
            },
            "estimated_duration": 45,  # minutes
            "complexity_factors": ["feature_scope", "integration_complexity", "testing_requirements"]
        },

        "bugfix": {
            "name": "bug_resolution",
            "description": "Fast bug diagnosis and repair",
            "sequence": ["@test", "@dev", "@test", "@git"],
            "parallel_streams": [],  # Sequential for reliability
            "dependencies": {
                "@dev": ["@test"],
                "@git": ["@test"]
            },
            "estimated_duration": 20,  # minutes
            "complexity_factors": ["bug_severity", "root_cause_depth", "test_coverage"]
        },

        "refactor": {
            "name": "code_refactoring",
            "description": "Quality-focused code improvement",
            "sequence": ["@test", "@dev", "@hound", "@4Q"],
            "parallel_streams": [
                ["@hound", "@4Q"]  # Quality review and compression can be parallel
            ],
            "dependencies": {
                "@dev": ["@test"],
                "@hound": ["@dev"],
                "@4Q": ["@dev"]
            },
            "estimated_duration": 35,  # minutes
            "complexity_factors": ["code_complexity", "abstraction_opportunities", "quality_targets"]
        },

        "architecture": {
            "name": "system_architecture",
            "description": "High-level system design and planning",
            "sequence": ["@architect", "@security", "@devops", "@docs"],
            "parallel_streams": [
                ["@security", "@devops"]  # Security and infrastructure can be parallel
            ],
            "dependencies": {
                "@security": ["@architect"],
                "@devops": ["@architect"],
                "@docs": ["@architect"]
            },
            "estimated_duration": 60,  # minutes
            "complexity_factors": ["system_scale", "security_requirements", "deployment_complexity"]
        },

        "quality_audit": {
            "name": "comprehensive_quality_audit",
            "description": "Deep code quality assessment and improvement",
            "sequence": ["@hound", "@4Q", "@test", "@security"],
            "parallel_streams": [
                ["@hound", "@security"],  # Code quality and security can be parallel
                ["@4Q", "@test"]          # Compression and testing can overlap
            ],
            "dependencies": {
                "@4Q": ["@hound"],
                "@test": ["@4Q"]
            },
            "estimated_duration": 50,  # minutes
            "complexity_factors": ["codebase_size", "quality_standards", "security_requirements"]
        }
    }

    return templates.get(template_name, templates["feature"])


async def create_custom_workflow(agents: List[str], dependencies: Dict[str, List[str]] = None) -> Dict[str, Any]:
    """
    Create custom workflow from agent list and dependencies.

    Args:
        agents: List of agent names
        dependencies: Optional dependency mapping

    Returns:
        Dict with custom workflow definition
    """
    if dependencies is None:
        # Create simple sequential dependencies
        dependencies = {}
        for i, agent in enumerate(agents):
            if i > 0:
                dependencies[agent] = [agents[i-1]]
            else:
                dependencies[agent] = []

    # Identify parallel opportunities
    parallel_streams = _identify_parallel_opportunities(agents, dependencies)

    # Estimate duration
    estimated_duration = len(agents) * 15  # 15 minutes per agent baseline

    return {
        "name": "custom_workflow",
        "description": f"Custom workflow with {len(agents)} agents",
        "sequence": agents,
        "parallel_streams": parallel_streams,
        "dependencies": dependencies,
        "estimated_duration": estimated_duration,
        "complexity_factors": ["agent_coordination", "custom_requirements"]
    }


async def optimize_execution_graph(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimize workflow execution graph for maximum parallel efficiency.

    Args:
        workflow: Workflow definition

    Returns:
        Dict with optimized execution plan
    """
    sequence = workflow.get("sequence", [])
    dependencies = workflow.get("dependencies", {})

    # Calculate execution levels (topological sort)
    execution_levels = _calculate_execution_levels(sequence, dependencies)

    # Optimize resource allocation
    resource_plan = _optimize_resource_allocation(execution_levels)

    # Calculate efficiency metrics
    efficiency_metrics = _calculate_efficiency_metrics(sequence, execution_levels)

    return {
        "original_sequence": sequence,
        "execution_levels": execution_levels,
        "resource_plan": resource_plan,
        "efficiency_metrics": efficiency_metrics,
        "optimizations_applied": _identify_optimizations(workflow, execution_levels)
    }


async def calculate_workflow_efficiency(workflow: Dict[str, Any], execution_results: Dict[str, Any] = None) -> Dict[str, float]:
    """
    Calculate workflow efficiency metrics.

    Args:
        workflow: Workflow definition
        execution_results: Optional actual execution results

    Returns:
        Dict with efficiency metrics
    """
    sequence = workflow.get("sequence", [])
    parallel_streams = workflow.get("parallel_streams", [])
    estimated_duration = workflow.get("estimated_duration", 0)

    # Calculate theoretical efficiency
    total_agents = len(sequence)
    max_parallel = max(len(stream) for stream in parallel_streams) if parallel_streams else 1
    theoretical_efficiency = min(1.0, max_parallel / total_agents) if total_agents > 0 else 0

    # Calculate actual efficiency if execution results available
    actual_efficiency = theoretical_efficiency
    if execution_results:
        actual_duration = execution_results.get("total_execution_time", estimated_duration)
        if actual_duration > 0 and estimated_duration > 0:
            time_efficiency = min(1.0, estimated_duration / actual_duration)
            actual_efficiency = (theoretical_efficiency + time_efficiency) / 2

    return {
        "theoretical_efficiency": theoretical_efficiency,
        "actual_efficiency": actual_efficiency,
        "parallelism_factor": max_parallel / total_agents if total_agents > 0 else 0,
        "coordination_overhead": 1 - actual_efficiency,
        "optimization_potential": max(0, 1 - theoretical_efficiency)
    }


# Helper functions

def _identify_parallel_opportunities(agents: List[str], dependencies: Dict[str, List[str]]) -> List[List[str]]:
    """Identify which agents can run in parallel."""
    parallel_streams = []
    remaining_agents = set(agents)

    while remaining_agents:
        # Find agents with no unresolved dependencies
        parallel_batch = []
        for agent in remaining_agents:
            agent_deps = dependencies.get(agent, [])
            if all(dep not in remaining_agents for dep in agent_deps):
                parallel_batch.append(agent)

        if parallel_batch:
            parallel_streams.append(parallel_batch)
            remaining_agents -= set(parallel_batch)
        else:
            # Circular dependency - break it
            break

    return parallel_streams


def _calculate_execution_levels(agents: List[str], dependencies: Dict[str, List[str]]) -> List[List[str]]:
    """Calculate execution levels using topological sort."""
    levels = []
    remaining = set(agents)

    while remaining:
        # Find agents with no dependencies in remaining set
        level = []
        for agent in list(remaining):
            deps = dependencies.get(agent, [])
            if not any(dep in remaining for dep in deps):
                level.append(agent)

        if not level:
            # Circular dependency detected
            level = list(remaining)  # Add all remaining to break cycle

        levels.append(level)
        remaining -= set(level)

    return levels


def _optimize_resource_allocation(execution_levels: List[List[str]]) -> Dict[str, Any]:
    """Optimize resource allocation across execution levels."""
    max_parallel_agents = max(len(level) for level in execution_levels) if execution_levels else 1

    return {
        "max_concurrent_agents": min(max_parallel_agents, 5),  # System limit
        "resource_distribution": "balanced",
        "memory_allocation": f"{max_parallel_agents * 512}MB",  # 512MB per agent
        "cpu_allocation": f"{max_parallel_agents * 20}%",      # 20% CPU per agent
        "recommended_timeout": max(300, max_parallel_agents * 60)  # Scale timeout with complexity
    }


def _calculate_efficiency_metrics(sequence: List[str], levels: List[List[str]]) -> Dict[str, float]:
    """Calculate various efficiency metrics."""
    total_agents = len(sequence)
    total_levels = len(levels)
    max_parallel = max(len(level) for level in levels) if levels else 1

    # Parallelism efficiency: how well we utilize parallel execution
    parallelism_efficiency = max_parallel / total_agents if total_agents > 0 else 0

    # Level efficiency: how balanced the levels are
    level_sizes = [len(level) for level in levels]
    avg_level_size = sum(level_sizes) / len(level_sizes) if level_sizes else 0
    level_efficiency = 1 - (max(level_sizes) - avg_level_size) / max(level_sizes) if max(level_sizes) > 0 else 1

    # Dependency efficiency: fewer levels is better
    dependency_efficiency = 1 / total_levels if total_levels > 0 else 1

    return {
        "parallelism_efficiency": parallelism_efficiency,
        "level_efficiency": level_efficiency,
        "dependency_efficiency": dependency_efficiency,
        "overall_efficiency": (parallelism_efficiency + level_efficiency + dependency_efficiency) / 3
    }


def _identify_optimizations(workflow: Dict[str, Any], execution_levels: List[List[str]]) -> List[str]:
    """Identify optimizations applied to workflow."""
    optimizations = []

    # Check if we achieved parallelism
    if any(len(level) > 1 for level in execution_levels):
        optimizations.append("parallel_execution_enabled")

    # Check if we reduced dependency chains
    original_sequence = workflow.get("sequence", [])
    if len(execution_levels) < len(original_sequence):
        optimizations.append("dependency_chain_reduced")

    # Check for resource optimization
    max_parallel = max(len(level) for level in execution_levels) if execution_levels else 1
    if max_parallel <= 5:  # System resource limit
        optimizations.append("resource_allocation_optimized")

    return optimizations


async def validate_workflow_template(template: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate workflow template for consistency and feasibility.

    Args:
        template: Workflow template to validate

    Returns:
        Dict with validation results
    """
    validation_results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "suggestions": []
    }

    # Check required fields
    required_fields = ["name", "sequence", "dependencies"]
    for field in required_fields:
        if field not in template:
            validation_results["errors"].append(f"Missing required field: {field}")
            validation_results["valid"] = False

    if not validation_results["valid"]:
        return validation_results

    # Validate sequence and dependencies consistency
    sequence = set(template["sequence"])
    dependencies = template["dependencies"]

    # Check all dependencies reference agents in sequence
    for agent, deps in dependencies.items():
        if agent not in sequence:
            validation_results["errors"].append(f"Agent {agent} in dependencies but not in sequence")
            validation_results["valid"] = False

        for dep in deps:
            if dep not in sequence:
                validation_results["errors"].append(f"Dependency {dep} not found in sequence")
                validation_results["valid"] = False

    # Check for circular dependencies
    if _has_circular_dependencies(dependencies):
        validation_results["errors"].append("Circular dependencies detected")
        validation_results["valid"] = False

    # Performance warnings
    if len(template["sequence"]) > 10:
        validation_results["warnings"].append("Large workflow may have coordination overhead")

    # Optimization suggestions
    levels = _calculate_execution_levels(template["sequence"], dependencies)
    if len(levels) == len(template["sequence"]):
        validation_results["suggestions"].append("Consider adding parallel execution opportunities")

    return validation_results


def _has_circular_dependencies(dependencies: Dict[str, List[str]]) -> bool:
    """Check if dependency graph has circular dependencies."""
    visited = set()
    rec_stack = set()

    def has_cycle(node):
        visited.add(node)
        rec_stack.add(node)

        for neighbor in dependencies.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True

        rec_stack.remove(node)
        return False

    for node in dependencies:
        if node not in visited:
            if has_cycle(node):
                return True

    return False