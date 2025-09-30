"""
Pneuma Analysis Tools

Entropy reduction and clarity scoring functions.
Implements the evaluation (s:) phase of The Loop.
"""

import re
import math
from typing import Dict, Any, List, Tuple
from collections import Counter


async def s_score(original_code: str, transformed_code: str, context: Dict = None) -> Dict[str, Any]:
    """
    Score a code transformation based on entropy reduction and clarity.

    Args:
        original_code: The original code before transformation
        transformed_code: The code after transformation
        context: Additional context for scoring

    Returns:
        Dict with score breakdown and final score (0.0 to 1.0)
    """
    try:
        entropy_reduction = calculate_entropy_reduction(original_code, transformed_code)
        clarity_penalty = _calculate_clarity_penalty(original_code, transformed_code)

        # Final score combines entropy reduction with clarity penalty
        final_score = max(0.0, entropy_reduction - clarity_penalty)

        return {
            "content": [{
                "type": "text",
                "text": f"s_score: {final_score:.3f} (entropy: {entropy_reduction:.3f}, clarity: -{clarity_penalty:.3f})"
            }],
            "entropy_reduction": entropy_reduction,
            "clarity_penalty": clarity_penalty,
            "final_score": final_score,
            "metrics": _get_detailed_metrics(original_code, transformed_code)
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in s_score: {e}"
            }]
        }


def calculate_entropy_reduction(original: str, transformed: str) -> float:
    """
    Calculate entropy reduction as the primary metric.

    Returns:
        Float between 0.0 and 1.0 representing compression ratio
    """
    if not original or not transformed:
        return 0.0

    # Basic length-based compression
    len_reduction = 1.0 - (len(transformed.strip()) / len(original.strip()))

    # Line count reduction
    orig_lines = len([line for line in original.split('\n') if line.strip()])
    trans_lines = len([line for line in transformed.split('\n') if line.strip()])
    line_reduction = 1.0 - (trans_lines / orig_lines) if orig_lines > 0 else 0.0

    # Token-based entropy (more sophisticated measure)
    token_reduction = _calculate_token_entropy_reduction(original, transformed)

    # Weighted average of different entropy measures
    return (len_reduction * 0.4) + (line_reduction * 0.3) + (token_reduction * 0.3)


async def analyze_complexity(code: str) -> Dict[str, Any]:
    """
    Analyze code complexity for pattern detection.

    Args:
        code: Source code to analyze

    Returns:
        Dict with complexity metrics and recommendations
    """
    try:
        metrics = {
            "cyclomatic_complexity": _calculate_cyclomatic_complexity(code),
            "nesting_depth": _calculate_nesting_depth(code),
            "function_count": len(re.findall(r'def\s+\w+', code)),
            "line_count": len([line for line in code.split('\n') if line.strip()]),
            "token_diversity": _calculate_token_diversity(code)
        }

        recommendations = _generate_complexity_recommendations(metrics)

        return {
            "content": [{
                "type": "text",
                "text": f"Complexity analysis: CC={metrics['cyclomatic_complexity']}, depth={metrics['nesting_depth']}"
            }],
            "metrics": metrics,
            "recommendations": recommendations
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in analyze_complexity: {e}"
            }]
        }


# Private helper functions

def _calculate_clarity_penalty(original: str, transformed: str) -> float:
    """
    Calculate penalty for reduced clarity.
    Higher penalty means transformation made code less readable.
    """
    penalty = 0.0

    # Penalty for removing meaningful variable names
    orig_vars = set(re.findall(r'\b[a-z_][a-z0-9_]{2,}\b', original.lower()))
    trans_vars = set(re.findall(r'\b[a-z_][a-z0-9_]{2,}\b', transformed.lower()))

    if len(trans_vars) < len(orig_vars) * 0.7:  # Lost more than 30% of variables
        penalty += 0.2

    # Penalty for increasing nesting without clear benefit
    orig_depth = _calculate_nesting_depth(original)
    trans_depth = _calculate_nesting_depth(transformed)

    if trans_depth > orig_depth:
        penalty += 0.1 * (trans_depth - orig_depth)

    # Penalty for removing comments without adding symbolic ones
    orig_comments = len(re.findall(r'#.*', original))
    trans_comments = len(re.findall(r'#.*', transformed))
    trans_symbolic = len(re.findall(r'#\s*@\w+', transformed))  # Symbolic comments

    if trans_comments + trans_symbolic < orig_comments * 0.8:
        penalty += 0.15

    return min(penalty, 0.8)  # Cap penalty at 0.8


def _calculate_token_entropy_reduction(original: str, transformed: str) -> float:
    """Calculate entropy reduction based on token frequency distribution."""
    def get_token_entropy(code: str) -> float:
        tokens = re.findall(r'\b\w+\b', code.lower())
        if not tokens:
            return 0.0

        counter = Counter(tokens)
        total = len(tokens)

        entropy = 0.0
        for count in counter.values():
            prob = count / total
            entropy -= prob * math.log2(prob)

        return entropy

    orig_entropy = get_token_entropy(original)
    trans_entropy = get_token_entropy(transformed)

    if orig_entropy == 0:
        return 0.0

    # Higher entropy reduction means more pattern consolidation
    return max(0.0, 1.0 - (trans_entropy / orig_entropy))


def _get_detailed_metrics(original: str, transformed: str) -> Dict[str, Any]:
    """Get detailed metrics for transformation analysis."""
    return {
        "character_count": {
            "original": len(original),
            "transformed": len(transformed),
            "reduction": len(original) - len(transformed)
        },
        "line_count": {
            "original": len(original.split('\n')),
            "transformed": len(transformed.split('\n')),
            "reduction": len(original.split('\n')) - len(transformed.split('\n'))
        },
        "token_count": {
            "original": len(re.findall(r'\b\w+\b', original)),
            "transformed": len(re.findall(r'\b\w+\b', transformed)),
            "reduction": len(re.findall(r'\b\w+\b', original)) - len(re.findall(r'\b\w+\b', transformed))
        }
    }


def _calculate_cyclomatic_complexity(code: str) -> int:
    """Calculate cyclomatic complexity (simplified)."""
    # Count decision points
    decision_keywords = ['if', 'elif', 'while', 'for', 'and', 'or', 'except']
    complexity = 1  # Base complexity

    for keyword in decision_keywords:
        complexity += len(re.findall(rf'\b{keyword}\b', code))

    return complexity


def _calculate_nesting_depth(code: str) -> int:
    """Calculate maximum nesting depth."""
    lines = code.split('\n')
    max_depth = 0
    current_depth = 0

    for line in lines:
        stripped = line.lstrip()
        if not stripped or stripped.startswith('#'):
            continue

        # Calculate indentation level
        indent_level = (len(line) - len(stripped)) // 4  # Assuming 4-space indents

        if stripped.endswith(':'):
            current_depth = indent_level + 1
            max_depth = max(max_depth, current_depth)
        else:
            current_depth = indent_level

    return max_depth


def _calculate_token_diversity(code: str) -> float:
    """Calculate diversity of tokens (unique tokens / total tokens)."""
    tokens = re.findall(r'\b\w+\b', code.lower())
    if not tokens:
        return 0.0

    unique_tokens = len(set(tokens))
    total_tokens = len(tokens)

    return unique_tokens / total_tokens


def _generate_complexity_recommendations(metrics: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on complexity metrics."""
    recommendations = []

    if metrics["cyclomatic_complexity"] > 10:
        recommendations.append("High cyclomatic complexity - consider function decomposition")

    if metrics["nesting_depth"] > 4:
        recommendations.append("Deep nesting detected - consider early returns or guard clauses")

    if metrics["token_diversity"] < 0.3:
        recommendations.append("Low token diversity - may indicate repetitive patterns")

    if metrics["line_count"] > 50 and metrics["function_count"] < 3:
        recommendations.append("Large single function - consider breaking into smaller functions")

    return recommendations