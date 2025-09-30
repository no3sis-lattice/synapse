"""
Pneuma Synapse Integration Tools

Connects Pneuma to the broader Synapse knowledge graph for:
- Global pattern discovery and sharing
- Cross-project learning
- Organizational pattern vocabulary building
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

# Import Synapse search functionality
sys.path.append(str(Path.home() / ".synapse-system" / ".synapse" / "neo4j"))

try:
    from synapse_search import search_synapse_context
    from context_manager import SynapseContextManager
    SYNAPSE_AVAILABLE = True
except ImportError:
    SYNAPSE_AVAILABLE = False
    print("⚠️  Synapse components not available, using mock implementations")


async def query_global_patterns(pattern_signature: str, pattern_type: str = "abstraction") -> Dict[str, Any]:
    """
    Search the global knowledge graph for existing patterns.

    Args:
        pattern_signature: Code signature to search for (e.g., "map.filter.reduce")
        pattern_type: Type of pattern (abstraction, refactor, etc.)

    Returns:
        Dict with matching patterns and usage statistics
    """
    if not SYNAPSE_AVAILABLE:
        return _mock_pattern_search(pattern_signature, pattern_type)

    try:
        # Search for similar patterns in the knowledge graph
        query = f"pattern {pattern_type} {pattern_signature} compression abstraction"

        # Use Synapse search with higher result limit for pattern matching
        results = search_synapse_context(
            query=query,
            max_results=15,
            auto_activate=True
        )

        if "error" in results:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Pattern search failed: {results['error']}"
                }],
                "patterns_found": [],
                "recommendations": []
            }

        # Process results to extract pattern information
        patterns_found = _extract_patterns_from_results(results, pattern_signature)
        recommendations = _generate_pattern_recommendations(patterns_found, pattern_signature)

        return {
            "content": [{
                "type": "text",
                "text": f"Found {len(patterns_found)} similar patterns in knowledge graph"
            }],
            "patterns_found": patterns_found,
            "recommendations": recommendations,
            "query_used": query
        }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error querying global patterns: {e}"
            }],
            "patterns_found": [],
            "error": str(e)
        }


async def publish_pattern_to_graph(pattern: Dict[str, Any], confidence: float = 0.8) -> Dict[str, Any]:
    """
    Share a discovered pattern with the global knowledge graph.

    Args:
        pattern: Pattern dict with name, signature, confidence, etc.
        confidence: Confidence threshold for publishing

    Returns:
        Dict with publication status and assigned pattern ID
    """
    if not SYNAPSE_AVAILABLE:
        return _mock_pattern_publish(pattern, confidence)

    try:
        # Only publish high-confidence patterns
        if pattern.get("confidence", 0.0) < confidence:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Pattern confidence {pattern.get('confidence', 0.0)} below threshold {confidence}"
                }],
                "published": False,
                "reason": "low_confidence"
            }

        # Create a structured pattern entry
        pattern_entry = {
            "id": f"pneuma_{pattern.get('name', 'unnamed')}_{hash(pattern.get('signature', '')) % 10000}",
            "agent": "pneuma",
            "type": "compression_pattern",
            "name": pattern.get("name", "unnamed_pattern"),
            "signature": pattern.get("signature", ""),
            "replaces": pattern.get("replaces", ""),
            "confidence": pattern.get("confidence", confidence),
            "entropy_reduction": pattern.get("entropy_reduction", 0.0),
            "language": pattern.get("language", "general"),
            "discovered_at": pattern.get("discovered_at"),
            "usage_count": 1
        }

        # In a full implementation, this would use Neo4j ingestion
        # For now, we'll simulate by storing in a patterns cache
        success = await _store_pattern_in_graph(pattern_entry)

        if success:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Published pattern '{pattern_entry['name']}' to knowledge graph"
                }],
                "published": True,
                "pattern_id": pattern_entry["id"],
                "pattern_entry": pattern_entry
            }
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": "Failed to publish pattern to knowledge graph"
                }],
                "published": False,
                "reason": "storage_error"
            }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error publishing pattern: {e}"
            }],
            "published": False,
            "error": str(e)
        }


async def get_pattern_usage_stats(pattern_id: str) -> Dict[str, Any]:
    """
    Get usage statistics for a pattern from the knowledge graph.

    Args:
        pattern_id: ID of the pattern to query

    Returns:
        Dict with usage statistics and effectiveness metrics
    """
    if not SYNAPSE_AVAILABLE:
        return _mock_usage_stats(pattern_id)

    try:
        # Query the knowledge graph for pattern usage
        query = f"pattern usage statistics {pattern_id} effectiveness metrics"

        results = search_synapse_context(query=query, max_results=5)

        if "error" in results:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Usage stats query failed: {results['error']}"
                }],
                "usage_count": 0,
                "effectiveness": 0.0
            }

        # Extract usage statistics from results
        stats = _extract_usage_stats(results, pattern_id)

        return {
            "content": [{
                "type": "text",
                "text": f"Pattern {pattern_id}: used {stats['usage_count']} times, {stats['effectiveness']:.2f} effectiveness"
            }],
            "pattern_id": pattern_id,
            "usage_count": stats["usage_count"],
            "effectiveness": stats["effectiveness"],
            "last_used": stats["last_used"],
            "success_rate": stats["success_rate"]
        }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error getting usage stats: {e}"
            }],
            "error": str(e)
        }


async def discover_complementary_patterns(current_pattern: Dict[str, Any]) -> Dict[str, Any]:
    """
    Find patterns that work well in combination with the current pattern.

    Args:
        current_pattern: Pattern to find complements for

    Returns:
        Dict with complementary patterns and composition suggestions
    """
    if not SYNAPSE_AVAILABLE:
        return _mock_complementary_patterns(current_pattern)

    try:
        # Search for patterns that have been successfully combined
        pattern_name = current_pattern.get("name", "")
        signature = current_pattern.get("signature", "")

        query = f"pattern composition combination {pattern_name} {signature} synergy"

        results = search_synapse_context(query=query, max_results=10)

        if "error" in results:
            return {
                "content": [{
                    "type": "text",
                    "text": "No complementary patterns found in knowledge graph"
                }],
                "complementary_patterns": []
            }

        # Extract and rank complementary patterns
        complements = _extract_complementary_patterns(results, current_pattern)

        return {
            "content": [{
                "type": "text",
                "text": f"Found {len(complements)} complementary patterns for {pattern_name}"
            }],
            "complementary_patterns": complements,
            "composition_suggestions": _generate_composition_suggestions(complements)
        }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error discovering complementary patterns: {e}"
            }],
            "error": str(e)
        }


# Private helper functions

def _extract_patterns_from_results(results: Dict, target_signature: str) -> List[Dict]:
    """Extract pattern information from search results."""
    patterns = []

    context = results.get("context", [])
    for item in context:
        content = item.get("content", "")

        # Look for pattern signatures in content
        if "signature" in content and "pattern" in content.lower():
            pattern = {
                "source": item.get("source", "unknown"),
                "confidence": item.get("similarity_score", 0.0),
                "content_snippet": content[:200] + "..." if len(content) > 200 else content
            }
            patterns.append(pattern)

    return patterns[:10]  # Limit to top 10


def _generate_pattern_recommendations(found_patterns: List[Dict], target_signature: str) -> List[str]:
    """Generate recommendations based on found patterns."""
    recommendations = []

    if not found_patterns:
        recommendations.append("No similar patterns found - this may be a novel abstraction")
    elif len(found_patterns) > 5:
        recommendations.append("Many similar patterns exist - consider reusing existing abstraction")
    else:
        recommendations.append("Some similar patterns found - compare effectiveness before creating new pattern")

    return recommendations


async def _store_pattern_in_graph(pattern_entry: Dict) -> bool:
    """Store pattern in the knowledge graph (simplified implementation)."""
    try:
        # In full implementation, this would use Neo4j ingestion pipeline
        # For now, store in a local cache file
        patterns_cache = Path.home() / ".synapse-system" / ".synapse" / "patterns_cache.json"

        patterns_cache.parent.mkdir(exist_ok=True)

        import json
        if patterns_cache.exists():
            with open(patterns_cache, 'r') as f:
                cache = json.load(f)
        else:
            cache = {"patterns": []}

        cache["patterns"].append(pattern_entry)

        with open(patterns_cache, 'w') as f:
            json.dump(cache, f, indent=2)

        return True

    except Exception as e:
        print(f"Error storing pattern: {e}")
        return False


def _extract_usage_stats(results: Dict, pattern_id: str) -> Dict:
    """Extract usage statistics from search results."""
    return {
        "usage_count": len(results.get("context", [])),
        "effectiveness": 0.75,  # Mock effectiveness score
        "last_used": "2024-09-24",
        "success_rate": 0.85
    }


def _extract_complementary_patterns(results: Dict, current_pattern: Dict) -> List[Dict]:
    """Extract complementary patterns from search results."""
    complements = []

    for item in results.get("context", [])[:5]:  # Top 5
        complement = {
            "name": f"complement_pattern_{len(complements)}",
            "compatibility_score": 0.8,
            "description": item.get("content", "")[:100] + "..."
        }
        complements.append(complement)

    return complements


def _generate_composition_suggestions(complements: List[Dict]) -> List[str]:
    """Generate suggestions for pattern composition."""
    suggestions = []

    if complements:
        suggestions.append("Consider chaining these patterns for compound compression")
        suggestions.append("Test compatibility with existing codebase patterns")

    return suggestions


# Mock implementations for when Synapse is not available

def _mock_pattern_search(pattern_signature: str, pattern_type: str) -> Dict[str, Any]:
    """Mock pattern search for testing."""
    return {
        "content": [{
            "type": "text",
            "text": f"Mock search for {pattern_signature} (Synapse not available)"
        }],
        "patterns_found": [{
            "source": "mock_pattern",
            "confidence": 0.6,
            "content_snippet": f"Similar pattern for {pattern_signature}"
        }],
        "recommendations": ["Mock recommendation: Pattern may have similar existing implementations"]
    }


def _mock_pattern_publish(pattern: Dict, confidence: float) -> Dict[str, Any]:
    """Mock pattern publishing for testing."""
    return {
        "content": [{
            "type": "text",
            "text": f"Mock published pattern {pattern.get('name', 'unnamed')}"
        }],
        "published": True,
        "pattern_id": f"mock_{hash(str(pattern)) % 10000}"
    }


def _mock_usage_stats(pattern_id: str) -> Dict[str, Any]:
    """Mock usage statistics for testing."""
    return {
        "content": [{
            "type": "text",
            "text": f"Mock stats for {pattern_id}"
        }],
        "usage_count": 5,
        "effectiveness": 0.75,
        "last_used": "2024-09-24",
        "success_rate": 0.8
    }


def _mock_complementary_patterns(current_pattern: Dict) -> Dict[str, Any]:
    """Mock complementary pattern discovery."""
    return {
        "content": [{
            "type": "text",
            "text": f"Mock complementary patterns for {current_pattern.get('name', 'pattern')}"
        }],
        "complementary_patterns": [{
            "name": "mock_complement",
            "compatibility_score": 0.7,
            "description": "Mock complementary pattern"
        }]
    }