"""
Pneuma Memory Tools

State management for the agent's lean, symbolic memory system.
Handles state.json read/write operations and pattern storage.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


def load_state(agent_dir: str = None) -> Dict[str, Any]:
    """
    Load agent state from pneuma_state.json.

    Args:
        agent_dir: Directory containing the state file

    Returns:
        Dict with current agent state
    """
    try:
        state_path = _get_state_path(agent_dir)

        if not state_path.exists():
            return _create_initial_state()

        with open(state_path, 'r') as f:
            state = json.load(f)

        # Validate state structure
        if not _validate_state(state):
            print(f"Invalid state structure, reinitializing...")
            return _create_initial_state()

        return state

    except Exception as e:
        print(f"Error loading state: {e}")
        return _create_initial_state()


def save_state(state: Dict[str, Any], agent_dir: str = None) -> bool:
    """
    Save agent state to pneuma_state.json.

    Args:
        state: State dict to save
        agent_dir: Directory to save state file

    Returns:
        True if successful, False otherwise
    """
    try:
        state_path = _get_state_path(agent_dir)

        # Update metadata
        state["updated_at"] = datetime.now().isoformat()
        state["hash"] = _calculate_state_hash(state)

        # Ensure directory exists
        state_path.parent.mkdir(parents=True, exist_ok=True)

        with open(state_path, 'w') as f:
            json.dump(state, f, indent=2)

        return True

    except Exception as e:
        print(f"Error saving state: {e}")
        return False


def update_log(state: Dict[str, Any], action_type: str, details: str) -> Dict[str, Any]:
    """
    Add symbolic log entry to state.

    Args:
        state: Current state
        action_type: Type of action (q, a, s)
        details: Action details

    Returns:
        Updated state dict
    """
    if "log" not in state:
        state["log"] = []

    cycle = state.get("cycle", 0)
    timestamp = datetime.now().strftime("%H:%M")
    log_entry = f"{cycle}:{action_type}({details})@{timestamp}"

    state["log"].append(log_entry)

    # Keep log lean - only last 50 entries
    if len(state["log"]) > 50:
        state["log"] = state["log"][-50:]

    return state


def add_pattern(state: Dict[str, Any], pattern: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add discovered pattern to the pattern repository.

    Args:
        state: Current state
        pattern: Pattern dict with name, signature, confidence

    Returns:
        Updated state dict
    """
    if "patterns" not in state:
        state["patterns"] = {}

    # Generate pattern ID
    pattern_id = f"p_{len(state['patterns']):03d}"

    # Store pattern with metadata
    state["patterns"][pattern_id] = {
        "name": pattern.get("name", "unnamed_pattern"),
        "signature": pattern.get("signature", ""),
        "replaces": pattern.get("replaces", ""),
        "confidence": pattern.get("confidence", 0.5),
        "discovered_at": datetime.now().isoformat(),
        "uses": 0
    }

    return state


def get_pattern(state: Dict[str, Any], pattern_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve pattern by ID.

    Args:
        state: Current state
        pattern_id: Pattern ID to retrieve

    Returns:
        Pattern dict or None if not found
    """
    return state.get("patterns", {}).get(pattern_id)


def increment_pattern_usage(state: Dict[str, Any], pattern_id: str) -> Dict[str, Any]:
    """
    Increment usage count for a pattern.

    Args:
        state: Current state
        pattern_id: Pattern ID to increment

    Returns:
        Updated state dict
    """
    if pattern_id in state.get("patterns", {}):
        state["patterns"][pattern_id]["uses"] += 1

    return state


def set_focus(state: Dict[str, Any], target: str, question: str, score: float = 0.0) -> Dict[str, Any]:
    """
    Set current focus for the agent.

    Args:
        state: Current state
        target: Target file or code block
        question: Current question being explored
        score: Current score for this focus

    Returns:
        Updated state dict
    """
    state["focus"] = {
        "target": target,
        "q": question,
        "score": score,
        "started_at": datetime.now().isoformat()
    }

    return state


def increment_cycle(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Increment the cycle counter.

    Args:
        state: Current state

    Returns:
        Updated state dict
    """
    state["cycle"] = state.get("cycle", 0) + 1
    return state


def get_state_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a summary of current state for reporting.

    Args:
        state: Current state

    Returns:
        Summary dict with key metrics
    """
    return {
        "version": state.get("v", "unknown"),
        "cycle": state.get("cycle", 0),
        "pattern_count": len(state.get("patterns", {})),
        "log_entries": len(state.get("log", [])),
        "current_focus": state.get("focus", {}).get("target", "none"),
        "total_discoveries": len([p for p in state.get("patterns", {}).values() if p.get("uses", 0) > 0]),
        "last_updated": state.get("updated_at", "never")
    }


# Private helper functions

def _get_state_path(agent_dir: str = None) -> Path:
    """Get path to state file."""
    if agent_dir:
        return Path(agent_dir) / "pneuma_state.json"
    else:
        # Default to current directory structure
        return Path(__file__).parent.parent / "pneuma_state.json"


def _create_initial_state() -> Dict[str, Any]:
    """Create initial state structure."""
    return {
        "agent": "pneuma",
        "v": "0.1",
        "hash": "",
        "cycle": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "log": ["0:init"],
        "focus": {
            "target": "none",
            "q": "What shall we compress?",
            "score": 0.0
        },
        "patterns": {}
    }


def _validate_state(state: Dict[str, Any]) -> bool:
    """Validate state structure."""
    required_keys = ["agent", "v", "cycle", "log", "focus", "patterns"]
    return all(key in state for key in required_keys)


def _calculate_state_hash(state: Dict[str, Any]) -> str:
    """Calculate hash of state for integrity checking."""
    # Create a copy without hash field for hashing
    state_copy = {k: v for k, v in state.items() if k != "hash"}
    state_str = json.dumps(state_copy, sort_keys=True)
    return hashlib.sha256(state_str.encode()).hexdigest()[:16]