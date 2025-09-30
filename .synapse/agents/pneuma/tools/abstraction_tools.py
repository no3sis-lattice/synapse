"""
Pneuma Abstraction Tools

Code compression and pattern recognition functions.
Implements the curiosity (q:) and action (a:) phases of The Loop.
"""

import re
import ast
from typing import Dict, List, Any, Optional
from pathlib import Path


async def q_scan(file_path: str) -> Dict[str, Any]:
    """
    Generate curiosity questions about code patterns in a file.

    Args:
        file_path: Path to code file to analyze

    Returns:
        Dict with patterns found and questions generated
    """
    try:
        with open(file_path, 'r') as f:
            code = f.read()

        patterns = _identify_patterns(code)
        questions = _generate_questions(patterns, file_path)

        return {
            "content": [{
                "type": "text",
                "text": f"q_scan({file_path}): Found {len(patterns)} patterns. Questions: {questions}"
            }],
            "patterns": patterns,
            "questions": questions
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in q_scan: {e}"
            }]
        }


async def a_abstract(code_block: str) -> Dict[str, Any]:
    """
    Compress code block into high-level functional expression.

    Args:
        code_block: Source code to compress

    Returns:
        Dict with compressed code and pattern name
    """
    try:
        original_lines = len(code_block.strip().split('\n'))
        compressed = _compress_code(code_block)
        pattern_name = _identify_pattern_name(code_block)

        return {
            "content": [{
                "type": "text",
                "text": f"a_abstract: {original_lines}→{len(compressed.split())} lines. Pattern: {pattern_name}"
            }],
            "original": code_block,
            "compressed": compressed,
            "pattern": pattern_name
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in a_abstract: {e}"
            }]
        }


async def a_lint(file_path: str) -> Dict[str, Any]:
    """
    Apply semantic density rules and symbolic annotations.

    Args:
        file_path: Path to file to optimize

    Returns:
        Dict with linted code and changes made
    """
    try:
        with open(file_path, 'r') as f:
            original = f.read()

        linted = _apply_density_rules(original)
        changes = _count_changes(original, linted)

        return {
            "content": [{
                "type": "text",
                "text": f"a_lint({file_path}): Applied {changes} density optimizations"
            }],
            "original": original,
            "linted": linted,
            "changes": changes
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in a_lint: {e}"
            }]
        }


async def a_document(function_code: str) -> Dict[str, Any]:
    """
    Generate symbolic docstring using dense notation.

    Args:
        function_code: Function to document

    Returns:
        Dict with symbolic docstring
    """
    try:
        params = _extract_params(function_code)
        return_type = _infer_return_type(function_code)
        effects = _identify_effects(function_code)

        symbolic_doc = _create_symbolic_docstring(params, return_type, effects)

        return {
            "content": [{
                "type": "text",
                "text": f"a_document: Generated symbolic annotation"
            }],
            "docstring": symbolic_doc,
            "params": params,
            "return_type": return_type,
            "effects": effects
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in a_document: {e}"
            }]
        }


# Private helper functions

def _identify_patterns(code: str) -> List[Dict[str, Any]]:
    """Identify common code patterns that can be compressed."""
    patterns = []

    # Look for for-loops that could be map/filter/reduce
    for_loop_pattern = re.compile(r'for\s+\w+\s+in\s+.*?:', re.MULTILINE)
    if for_loop_pattern.search(code):
        patterns.append({
            "type": "for_loop_candidate",
            "description": "Loop that may be compressible to functional form"
        })

    # Look for repetitive if-else chains
    if_chain_pattern = re.compile(r'(if\s+.*?:\s*\n.*?\nelse.*?:\s*\n.*?\n){2,}', re.MULTILINE)
    if if_chain_pattern.search(code):
        patterns.append({
            "type": "if_chain_candidate",
            "description": "If-else chain that may benefit from lookup table"
        })

    # Look for verbose comments
    verbose_comment_pattern = re.compile(r'#\s+.{50,}', re.MULTILINE)
    verbose_comments = verbose_comment_pattern.findall(code)
    if verbose_comments:
        patterns.append({
            "type": "verbose_comments",
            "count": len(verbose_comments),
            "description": "Comments that could use symbolic notation"
        })

    return patterns


def _generate_questions(patterns: List[Dict], file_path: str) -> List[str]:
    """Generate curiosity questions based on identified patterns."""
    questions = []

    for pattern in patterns:
        if pattern["type"] == "for_loop_candidate":
            questions.append("Can this loop be expressed as map/filter/reduce?")
        elif pattern["type"] == "if_chain_candidate":
            questions.append("Would a lookup table compress this logic?")
        elif pattern["type"] == "verbose_comments":
            questions.append(f"Can {pattern['count']} comments use symbolic notation?")

    if not questions:
        questions.append("What is the primary abstraction opportunity?")

    return questions


def _compress_code(code: str) -> str:
    """Apply basic compression transformations."""
    # Remove excessive whitespace
    compressed = re.sub(r'\n\s*\n', '\n', code)

    # Convert simple for loops to comprehensions (basic example)
    # This would need more sophisticated parsing for real implementation
    simple_loop = re.compile(r'result = \[\]\nfor (\w+) in (.+?):\n    result\.append\((.+?)\)', re.MULTILINE)
    compressed = simple_loop.sub(r'result = [\3 for \1 in \2]', compressed)

    return compressed.strip()


def _identify_pattern_name(code: str) -> str:
    """Identify and name the primary pattern in code block."""
    if 'map(' in code or '[' in code and 'for' in code:
        return "map_transform"
    elif 'filter(' in code or 'if' in code:
        return "filter_select"
    elif 'reduce(' in code or 'sum(' in code:
        return "reduce_accumulate"
    else:
        return "unknown_pattern"


def _apply_density_rules(code: str) -> str:
    """Apply semantic density optimization rules."""
    # Convert verbose variable names to semantic ones (basic example)
    # In practice, this would need context-aware analysis
    linted = code

    # Use ternary operators for simple if-else
    simple_if = re.compile(r'if (.+?):\n    (.+?) = (.+?)\nelse:\n    \2 = (.+?)')
    linted = simple_if.sub(r'\2 = \3 if \1 else \4', linted)

    # Compress multiline string assignments
    multiline_str = re.compile(r'(\w+) = \(\s*\n\s*"(.+?)"\s*\n\s*\)')
    linted = multiline_str.sub(r'\1 = "\2"', linted)

    return linted


def _count_changes(original: str, modified: str) -> int:
    """Count number of optimization changes made."""
    orig_lines = original.count('\n')
    mod_lines = modified.count('\n')
    return abs(orig_lines - mod_lines)


def _extract_params(func_code: str) -> List[str]:
    """Extract parameter names from function."""
    try:
        # Basic regex extraction (would use AST in production)
        param_pattern = re.compile(r'def\s+\w+\s*\(([^)]+)\)')
        match = param_pattern.search(func_code)
        if match:
            params = [p.strip().split(':')[0] for p in match.group(1).split(',') if p.strip()]
            return [p for p in params if p != 'self']
        return []
    except:
        return []


def _infer_return_type(func_code: str) -> str:
    """Infer return type from function code."""
    if 'return True' in func_code or 'return False' in func_code:
        return 'bool'
    elif 'return []' in func_code or 'return list(' in func_code:
        return 'list'
    elif 'return {}' in func_code or 'return dict(' in func_code:
        return 'dict'
    elif 'return None' in func_code:
        return 'None'
    else:
        return 'Any'


def _identify_effects(func_code: str) -> List[str]:
    """Identify side effects in function."""
    effects = []
    if 'print(' in func_code:
        effects.append('io')
    if 'open(' in func_code or 'write(' in func_code:
        effects.append('file')
    if 'requests.' in func_code or 'http' in func_code:
        effects.append('network')
    return effects


def _create_symbolic_docstring(params: List[str], return_type: str, effects: List[str]) -> str:
    """Create dense symbolic docstring."""
    param_str = ' '.join(f'@{p}' for p in params) if params else '@void'
    effect_str = f' ~{"+".join(effects)}' if effects else ''
    return f'// {param_str} -> {return_type}{effect_str}'