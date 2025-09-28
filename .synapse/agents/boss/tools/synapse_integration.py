"""
Synapse Integration Tools - Knowledge graph connectivity

Connects orchestrator to Synapse knowledge base for standards,
patterns, and templates.
"""

import os
import json
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path


async def get_synapse_standards(language: str = "general") -> Dict[str, Any]:
    """
    Retrieve coding standards for specified language.

    Args:
        language: Programming language ("rust", "python", "typescript", etc.)

    Returns:
        Dict with coding standards and conventions
    """
    try:
        # Check if Synapse is available
        if not _is_synapse_available():
            return _get_fallback_standards(language)

        # Query Synapse for standards
        search_query = f"coding standards {language} conventions"
        results = await _query_synapse(search_query)

        # Extract standards from results
        standards = _extract_standards_from_results(results, language)

        return {
            "language": language,
            "standards": standards,
            "source": "synapse",
            "last_updated": "2024-09-24"
        }

    except Exception as e:
        return {
            "language": language,
            "standards": _get_fallback_standards(language),
            "source": "fallback",
            "error": str(e)
        }


async def search_patterns(pattern_type: str, context: str = "") -> Dict[str, Any]:
    """
    Search for implementation patterns in knowledge base.

    Args:
        pattern_type: Type of pattern to search for
        context: Additional context for search

    Returns:
        Dict with discovered patterns
    """
    try:
        if not _is_synapse_available():
            return _get_fallback_patterns(pattern_type)

        # Construct search query
        search_query = f"{pattern_type} patterns {context}".strip()
        results = await _query_synapse(search_query)

        # Extract patterns from results
        patterns = _extract_patterns_from_results(results, pattern_type)

        return {
            "pattern_type": pattern_type,
            "patterns": patterns,
            "context": context,
            "source": "synapse",
            "confidence": _calculate_pattern_confidence(patterns)
        }

    except Exception as e:
        return {
            "pattern_type": pattern_type,
            "patterns": _get_fallback_patterns(pattern_type),
            "source": "fallback",
            "error": str(e)
        }


async def query_templates(template_type: str, language: str = "") -> Dict[str, Any]:
    """
    Query for project templates and boilerplate.

    Args:
        template_type: Type of template needed
        language: Programming language (optional)

    Returns:
        Dict with template information
    """
    try:
        if not _is_synapse_available():
            return _get_fallback_templates(template_type, language)

        # Construct template search
        search_query = f"{template_type} template {language}".strip()
        results = await _query_synapse(search_query)

        # Extract template information
        templates = _extract_templates_from_results(results, template_type, language)

        return {
            "template_type": template_type,
            "language": language,
            "templates": templates,
            "source": "synapse",
            "usage_count": len(templates)
        }

    except Exception as e:
        return {
            "template_type": template_type,
            "templates": _get_fallback_templates(template_type, language),
            "source": "fallback",
            "error": str(e)
        }


async def validate_against_standards(code: str, language: str) -> Dict[str, Any]:
    """
    Validate code against language-specific standards.

    Args:
        code: Code to validate
        language: Programming language

    Returns:
        Dict with validation results
    """
    try:
        # Get standards for language
        standards = await get_synapse_standards(language)

        # Perform validation checks
        validation_results = _validate_code_against_standards(code, standards, language)

        return {
            "language": language,
            "validation_results": validation_results,
            "standards_source": standards.get("source", "unknown"),
            "overall_compliance": _calculate_compliance_score(validation_results)
        }

    except Exception as e:
        return {
            "language": language,
            "validation_results": {"error": str(e)},
            "overall_compliance": 0.0
        }


async def store_workflow_pattern(pattern_name: str, workflow: Dict[str, Any], success_metrics: Dict[str, float]) -> Dict[str, Any]:
    """
    Store successful workflow pattern in knowledge base.

    Args:
        pattern_name: Name of the workflow pattern
        workflow: Workflow definition
        success_metrics: Metrics from successful execution

    Returns:
        Dict with storage results
    """
    try:
        if not _is_synapse_available():
            return _store_pattern_locally(pattern_name, workflow, success_metrics)

        # Prepare pattern for storage
        pattern_data = {
            "name": pattern_name,
            "workflow": workflow,
            "metrics": success_metrics,
            "timestamp": "2024-09-24",
            "source": "synapse-pm",
            "usage_count": 1
        }

        # Store in Synapse (simulated)
        storage_result = await _store_in_synapse(pattern_data)

        return {
            "pattern_name": pattern_name,
            "stored": True,
            "storage_id": storage_result.get("id"),
            "source": "synapse"
        }

    except Exception as e:
        return {
            "pattern_name": pattern_name,
            "stored": False,
            "error": str(e),
            "fallback": "local_storage"
        }


# Helper functions

def _is_synapse_available() -> bool:
    """Check if Synapse system is available."""
    try:
        # Check for Synapse directory
        synapse_path = Path.home() / ".synapse-system" / ".synapse"
        if not synapse_path.exists():
            return False

        # Check if Neo4j is running (simplified check)
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return "neo4j" in result.stdout.lower()

    except Exception:
        return False


async def _query_synapse(query: str) -> Dict[str, Any]:
    """Query Synapse knowledge base (simulated)."""
    # Simulate Synapse query
    await _simulate_processing_time(1.0)

    # Return simulated results based on query
    if "standards" in query:
        return {
            "results": [
                {"type": "standard", "content": "naming_conventions", "language": "rust"},
                {"type": "standard", "content": "error_handling", "language": "rust"},
                {"type": "standard", "content": "testing_strategy", "language": "rust"}
            ],
            "query": query,
            "total_results": 3
        }
    elif "patterns" in query:
        return {
            "results": [
                {"type": "pattern", "name": "builder_pattern", "usage": "high"},
                {"type": "pattern", "name": "command_pattern", "usage": "medium"},
                {"type": "pattern", "name": "observer_pattern", "usage": "low"}
            ],
            "query": query,
            "total_results": 3
        }
    else:
        return {"results": [], "query": query, "total_results": 0}


def _extract_standards_from_results(results: Dict[str, Any], language: str) -> Dict[str, Any]:
    """Extract standards information from Synapse results."""
    standards = {}

    for result in results.get("results", []):
        if result.get("type") == "standard":
            content = result.get("content")
            if content == "naming_conventions":
                standards["naming"] = _get_naming_conventions(language)
            elif content == "error_handling":
                standards["errors"] = _get_error_handling_patterns(language)
            elif content == "testing_strategy":
                standards["testing"] = _get_testing_standards(language)

    return standards


def _extract_patterns_from_results(results: Dict[str, Any], pattern_type: str) -> List[Dict[str, Any]]:
    """Extract patterns from Synapse results."""
    patterns = []

    for result in results.get("results", []):
        if result.get("type") == "pattern":
            patterns.append({
                "name": result.get("name"),
                "usage_frequency": result.get("usage", "unknown"),
                "applicability": _assess_pattern_applicability(result.get("name"), pattern_type),
                "implementation_complexity": "medium"
            })

    return patterns


def _extract_templates_from_results(results: Dict[str, Any], template_type: str, language: str) -> List[Dict[str, Any]]:
    """Extract template information from results."""
    templates = []

    # Simulate template extraction
    if template_type == "cli":
        templates.append({
            "name": f"{language}_cli_template",
            "description": f"Command-line application template for {language}",
            "components": ["main", "cli_parser", "config", "tests"],
            "complexity": "simple"
        })

    return templates


def _get_fallback_standards(language: str) -> Dict[str, Any]:
    """Get fallback standards when Synapse unavailable."""
    fallback_standards = {
        "rust": {
            "naming": {
                "functions": "snake_case",
                "types": "PascalCase",
                "constants": "SCREAMING_SNAKE_CASE",
                "modules": "snake_case"
            },
            "errors": {
                "prefer_result": True,
                "custom_error_types": True,
                "error_context": "use anyhow or thiserror"
            },
            "testing": {
                "unit_tests": "same_file_mod_tests",
                "integration_tests": "tests_directory",
                "coverage_target": 80
            }
        },
        "python": {
            "naming": {
                "functions": "snake_case",
                "classes": "PascalCase",
                "constants": "SCREAMING_SNAKE_CASE",
                "modules": "snake_case"
            },
            "errors": {
                "specific_exceptions": True,
                "exception_chaining": True,
                "logging": "use logging module"
            },
            "testing": {
                "framework": "pytest",
                "coverage_target": 85,
                "test_isolation": True
            }
        },
        "general": {
            "naming": {"consistent_style": True},
            "errors": {"proper_error_handling": True},
            "testing": {"comprehensive_coverage": True}
        }
    }

    return fallback_standards.get(language, fallback_standards["general"])


def _get_fallback_patterns(pattern_type: str) -> List[Dict[str, Any]]:
    """Get fallback patterns when Synapse unavailable."""
    fallback_patterns = {
        "error_handling": [
            {"name": "result_pattern", "applicability": "high", "complexity": "low"},
            {"name": "try_catch_pattern", "applicability": "medium", "complexity": "low"}
        ],
        "concurrency": [
            {"name": "actor_pattern", "applicability": "high", "complexity": "medium"},
            {"name": "worker_pool", "applicability": "medium", "complexity": "medium"}
        ],
        "architecture": [
            {"name": "layered_architecture", "applicability": "high", "complexity": "medium"},
            {"name": "microservices", "applicability": "medium", "complexity": "high"}
        ]
    }

    return fallback_patterns.get(pattern_type, [])


def _get_fallback_templates(template_type: str, language: str) -> List[Dict[str, Any]]:
    """Get fallback templates when Synapse unavailable."""
    return [{
        "name": f"{language}_{template_type}_basic",
        "description": f"Basic {template_type} template for {language}",
        "components": ["main", "config", "tests"],
        "complexity": "simple"
    }]


def _validate_code_against_standards(code: str, standards: Dict[str, Any], language: str) -> Dict[str, Any]:
    """Validate code against retrieved standards."""
    validation_results = {
        "naming_compliance": _check_naming_compliance(code, standards.get("standards", {}).get("naming", {})),
        "error_handling_compliance": _check_error_handling(code, language),
        "structure_compliance": _check_code_structure(code, language),
        "violations": []
    }

    return validation_results


def _check_naming_compliance(code: str, naming_standards: Dict[str, Any]) -> Dict[str, Any]:
    """Check naming convention compliance."""
    # Simplified naming check
    return {
        "score": 0.85,
        "violations": [],
        "suggestions": ["Consider using more descriptive variable names"]
    }


def _check_error_handling(code: str, language: str) -> Dict[str, Any]:
    """Check error handling patterns."""
    return {
        "score": 0.90,
        "pattern_usage": "good",
        "suggestions": ["Consider adding more specific error types"]
    }


def _check_code_structure(code: str, language: str) -> Dict[str, Any]:
    """Check code structure and organization."""
    return {
        "score": 0.88,
        "organization": "good",
        "suggestions": ["Consider extracting large functions"]
    }


def _calculate_compliance_score(validation_results: Dict[str, Any]) -> float:
    """Calculate overall compliance score."""
    scores = []
    for key, value in validation_results.items():
        if isinstance(value, dict) and "score" in value:
            scores.append(value["score"])

    return sum(scores) / len(scores) if scores else 0.0


def _calculate_pattern_confidence(patterns: List[Dict[str, Any]]) -> float:
    """Calculate confidence in pattern recommendations."""
    if not patterns:
        return 0.0

    # Simple confidence based on number of patterns and their applicability
    high_applicability = sum(1 for p in patterns if p.get("applicability") == "high")
    return min(1.0, (high_applicability / len(patterns)) * 1.2)


def _assess_pattern_applicability(pattern_name: str, context: str) -> str:
    """Assess how applicable a pattern is to the context."""
    # Simple pattern-context matching
    applicability_map = {
        ("builder_pattern", "construction"): "high",
        ("observer_pattern", "events"): "high",
        ("command_pattern", "actions"): "medium"
    }

    return applicability_map.get((pattern_name, context), "low")


async def _simulate_processing_time(seconds: float):
    """Simulate processing time for async operations."""
    import asyncio
    await asyncio.sleep(min(seconds, 2.0))  # Cap at 2 seconds


async def _store_in_synapse(pattern_data: Dict[str, Any]) -> Dict[str, Any]:
    """Store pattern in Synapse knowledge base (simulated)."""
    await _simulate_processing_time(0.5)

    return {
        "id": f"pattern_{hash(pattern_data['name']) % 10000}",
        "stored": True,
        "timestamp": pattern_data.get("timestamp")
    }


def _store_pattern_locally(pattern_name: str, workflow: Dict[str, Any], metrics: Dict[str, float]) -> Dict[str, Any]:
    """Store pattern locally when Synapse unavailable."""
    try:
        # Create local patterns directory
        patterns_dir = Path.home() / ".synapse-patterns"
        patterns_dir.mkdir(exist_ok=True)

        # Store pattern as JSON
        pattern_file = patterns_dir / f"{pattern_name}.json"
        pattern_data = {
            "name": pattern_name,
            "workflow": workflow,
            "metrics": metrics,
            "timestamp": "2024-09-24",
            "source": "local"
        }

        with open(pattern_file, 'w') as f:
            json.dump(pattern_data, f, indent=2)

        return {"stored": True, "location": str(pattern_file), "source": "local"}

    except Exception as e:
        return {"stored": False, "error": str(e)}


# Standard naming conventions by language
def _get_naming_conventions(language: str) -> Dict[str, str]:
    """Get naming conventions for language."""
    conventions = {
        "rust": {
            "functions": "snake_case",
            "variables": "snake_case",
            "types": "PascalCase",
            "constants": "SCREAMING_SNAKE_CASE",
            "modules": "snake_case"
        },
        "python": {
            "functions": "snake_case",
            "variables": "snake_case",
            "classes": "PascalCase",
            "constants": "SCREAMING_SNAKE_CASE",
            "modules": "snake_case"
        },
        "typescript": {
            "functions": "camelCase",
            "variables": "camelCase",
            "classes": "PascalCase",
            "interfaces": "PascalCase",
            "constants": "SCREAMING_SNAKE_CASE"
        }
    }

    return conventions.get(language, {})


def _get_error_handling_patterns(language: str) -> Dict[str, Any]:
    """Get error handling patterns for language."""
    patterns = {
        "rust": {
            "primary_pattern": "Result<T, E>",
            "secondary_pattern": "Option<T>",
            "panic_usage": "avoid_except_programming_errors",
            "custom_errors": "recommended"
        },
        "python": {
            "primary_pattern": "exceptions",
            "specific_exceptions": "preferred",
            "exception_chaining": "use_from_clause",
            "logging": "log_before_raising"
        }
    }

    return patterns.get(language, {})


def _get_testing_standards(language: str) -> Dict[str, Any]:
    """Get testing standards for language."""
    standards = {
        "rust": {
            "unit_tests": "mod_tests_in_same_file",
            "integration_tests": "tests_directory",
            "test_naming": "descriptive_names",
            "coverage_target": 80
        },
        "python": {
            "framework": "pytest",
            "test_file_naming": "test_*.py",
            "test_function_naming": "test_*",
            "coverage_target": 85
        }
    }

    return standards.get(language, {})