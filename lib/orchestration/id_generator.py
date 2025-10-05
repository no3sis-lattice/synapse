"""
Deterministic ID Generator

Provides collision-resistant ID generation using compound format:
    {type}_{sequence:06d}_{hash}

Example: plan_000042_a1b2c3d4

Components:
1. Type prefix (e.g., "plan", "pattern", "action")
2. Monotonic sequence number (6 digits, zero-padded)
3. Content hash (first 8 chars of SHA256)

This prevents collisions for identical requests by combining:
- Temporal ordering (sequence)
- Content uniqueness (hash)

Part of Phase 1b: Template System Foundation
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from threading import Lock

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# ID format configuration
SEQUENCE_DIGITS = 6  # Zero-padded sequence number width
HASH_LENGTH = 8      # Number of hash characters to include
HASH_ALGORITHM = "sha256"  # Hash algorithm (sha256, sha1, md5)

# Sequence persistence
DEFAULT_SEQUENCE_FILE = Path.home() / ".synapse-system" / ".synapse" / "id_sequences.json"


@dataclass
class CompoundID:
    """Structured representation of a compound ID"""
    id_type: str
    sequence: int
    content_hash: str
    full_id: str

    @classmethod
    def parse(cls, id_string: str) -> Optional['CompoundID']:
        """
        Parse a compound ID string.

        Args:
            id_string: ID string in format {type}_{seq}_{hash}

        Returns:
            CompoundID object or None if invalid format
        """
        try:
            parts = id_string.split('_')
            if len(parts) < 3:
                return None

            id_type = parts[0]
            sequence = int(parts[1])
            content_hash = '_'.join(parts[2:])  # Handle hashes with underscores

            return cls(
                id_type=id_type,
                sequence=sequence,
                content_hash=content_hash,
                full_id=id_string
            )
        except (ValueError, IndexError):
            return None


class IDGenerator:
    """
    Thread-safe compound ID generator with collision resistance.

    Generates IDs in format: {type}_{sequence:06d}_{hash}

    Features:
    - Monotonic sequence numbers (persisted to disk)
    - Content-based hashing for uniqueness
    - Thread-safe operation
    - Type-specific sequences

    Usage:
        generator = IDGenerator()
        plan_id = generator.generate("plan", plan_data)
        # Returns: "plan_000042_a1b2c3d4"
    """

    def __init__(self, sequence_file: Optional[Path] = None):
        """
        Initialize ID generator.

        Args:
            sequence_file: Path to sequence persistence file
        """
        self.sequence_file = sequence_file or DEFAULT_SEQUENCE_FILE
        self.sequences: Dict[str, int] = {}
        self.lock = Lock()  # Thread safety

        # Load persisted sequences
        self._load_sequences()

    def _load_sequences(self) -> None:
        """Load sequence counters from persistence file"""
        if not self.sequence_file.exists():
            logger.debug(f"Sequence file not found, starting from 0: {self.sequence_file}")
            return

        try:
            with open(self.sequence_file, 'r') as f:
                self.sequences = json.load(f)
            logger.debug(f"Loaded {len(self.sequences)} sequences from {self.sequence_file}")
        except Exception as e:
            logger.error(f"Failed to load sequences: {e}")
            self.sequences = {}

    def _save_sequences(self) -> None:
        """Save sequence counters to persistence file"""
        try:
            # Ensure directory exists
            self.sequence_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.sequence_file, 'w') as f:
                json.dump(self.sequences, f, indent=2)

            logger.debug(f"Saved {len(self.sequences)} sequences to {self.sequence_file}")
        except Exception as e:
            logger.error(f"Failed to save sequences: {e}")

    def _get_next_sequence(self, id_type: str) -> int:
        """
        Get next sequence number for a given type.

        Thread-safe with automatic persistence.

        Args:
            id_type: Type prefix for the sequence

        Returns:
            Next sequence number
        """
        with self.lock:
            # Initialize if not exists
            if id_type not in self.sequences:
                self.sequences[id_type] = 0

            # Increment and get
            self.sequences[id_type] += 1
            sequence = self.sequences[id_type]

            # Persist immediately
            self._save_sequences()

            return sequence

    def _compute_hash(self, content: Any) -> str:
        """
        Compute content hash.

        Args:
            content: Content to hash (will be JSON-serialized if not string)

        Returns:
            First HASH_LENGTH characters of hash
        """
        # Convert to string if needed
        if isinstance(content, str):
            content_str = content
        elif isinstance(content, (dict, list)):
            # JSON serialize for consistent hashing
            content_str = json.dumps(content, sort_keys=True)
        else:
            content_str = str(content)

        # Compute hash
        hasher = hashlib.new(HASH_ALGORITHM)
        hasher.update(content_str.encode('utf-8'))
        full_hash = hasher.hexdigest()

        return full_hash[:HASH_LENGTH]

    def generate(
        self,
        id_type: str,
        content: Optional[Any] = None,
        extra_context: Optional[str] = None
    ) -> str:
        """
        Generate a compound ID.

        Args:
            id_type: Type prefix (e.g., "plan", "pattern", "action")
            content: Content to hash (optional, uses timestamp if None)
            extra_context: Additional context to include in hash

        Returns:
            Compound ID string: {type}_{sequence:06d}_{hash}
        """
        # Get next sequence number
        sequence = self._get_next_sequence(id_type)

        # Compute content hash
        if content is None:
            # Use timestamp as fallback
            import time
            content = {"timestamp": time.time()}

        # Include extra context if provided
        if extra_context:
            if isinstance(content, dict):
                content = {**content, "_context": extra_context}
            else:
                content = {"_content": content, "_context": extra_context}

        content_hash = self._compute_hash(content)

        # Format compound ID
        compound_id = f"{id_type}_{sequence:0{SEQUENCE_DIGITS}d}_{content_hash}"

        logger.debug(f"Generated ID: {compound_id}")
        return compound_id

    def generate_with_metadata(
        self,
        id_type: str,
        content: Optional[Any] = None,
        extra_context: Optional[str] = None
    ) -> CompoundID:
        """
        Generate a compound ID with structured metadata.

        Args:
            id_type: Type prefix
            content: Content to hash
            extra_context: Additional context

        Returns:
            CompoundID object with parsed components
        """
        full_id = self.generate(id_type, content, extra_context)
        parsed = CompoundID.parse(full_id)

        if parsed is None:
            # Fallback (should never happen)
            sequence = self.sequences.get(id_type, 0)
            content_hash = self._compute_hash(content) if content else "unknown"
            parsed = CompoundID(
                id_type=id_type,
                sequence=sequence,
                content_hash=content_hash,
                full_id=full_id
            )

        return parsed

    def reset_sequence(self, id_type: str) -> None:
        """
        Reset sequence counter for a type (use with caution).

        Args:
            id_type: Type to reset
        """
        with self.lock:
            if id_type in self.sequences:
                logger.warning(f"Resetting sequence for type '{id_type}' from {self.sequences[id_type]} to 0")
                self.sequences[id_type] = 0
                self._save_sequences()

    def get_current_sequence(self, id_type: str) -> int:
        """
        Get current sequence number for a type without incrementing.

        Args:
            id_type: Type to query

        Returns:
            Current sequence number
        """
        with self.lock:
            return self.sequences.get(id_type, 0)

    def get_all_sequences(self) -> Dict[str, int]:
        """
        Get all sequence counters.

        Returns:
            Dictionary of type -> sequence
        """
        with self.lock:
            return dict(self.sequences)


# ============================================================================
# GLOBAL INSTANCE (Singleton Pattern)
# ============================================================================

_global_generator: Optional[IDGenerator] = None
_global_lock = Lock()


def get_global_generator() -> IDGenerator:
    """
    Get or create global ID generator instance (singleton).

    Returns:
        Global IDGenerator instance
    """
    global _global_generator

    if _global_generator is None:
        with _global_lock:
            # Double-check pattern
            if _global_generator is None:
                _global_generator = IDGenerator()

    return _global_generator


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def generate_id(
    id_type: str,
    content: Optional[Any] = None,
    extra_context: Optional[str] = None
) -> str:
    """
    Generate a compound ID using global generator.

    Args:
        id_type: Type prefix
        content: Content to hash
        extra_context: Additional context

    Returns:
        Compound ID string
    """
    generator = get_global_generator()
    return generator.generate(id_type, content, extra_context)


def generate_plan_id(plan_data: Dict[str, Any]) -> str:
    """Generate ID for execution plan"""
    return generate_id("plan", plan_data)


def generate_pattern_id(pattern_data: Dict[str, Any]) -> str:
    """Generate ID for discovered pattern"""
    return generate_id("pattern", pattern_data)


def generate_action_id(action_data: Dict[str, Any]) -> str:
    """Generate ID for planned action"""
    return generate_id("action", action_data)


def generate_result_id(result_data: Dict[str, Any]) -> str:
    """Generate ID for execution result"""
    return generate_id("result", result_data)


# ============================================================================
# COLLISION DETECTION
# ============================================================================

class IDCollisionDetector:
    """
    Detects ID collisions (for testing and monitoring).

    Usage:
        detector = IDCollisionDetector()
        if detector.check_collision(new_id):
            # Handle collision
    """

    def __init__(self):
        self.seen_ids: Dict[str, int] = {}  # ID -> count
        self.lock = Lock()

    def check_collision(self, id_string: str) -> bool:
        """
        Check if an ID has been seen before.

        Args:
            id_string: ID to check

        Returns:
            True if collision detected, False otherwise
        """
        with self.lock:
            if id_string in self.seen_ids:
                self.seen_ids[id_string] += 1
                logger.warning(f"ID collision detected: {id_string} (count: {self.seen_ids[id_string]})")
                return True
            else:
                self.seen_ids[id_string] = 1
                return False

    def get_collision_count(self, id_string: str) -> int:
        """Get number of times an ID has been seen"""
        with self.lock:
            return self.seen_ids.get(id_string, 0)

    def get_total_collisions(self) -> int:
        """Get total number of collisions"""
        with self.lock:
            return sum(1 for count in self.seen_ids.values() if count > 1)

    def get_stats(self) -> Dict[str, Any]:
        """Get collision statistics"""
        with self.lock:
            total_ids = len(self.seen_ids)
            collisions = sum(1 for count in self.seen_ids.values() if count > 1)
            max_collision = max(self.seen_ids.values()) if self.seen_ids else 0

            return {
                "total_ids": total_ids,
                "unique_ids": total_ids - collisions,
                "collisions": collisions,
                "max_collision_count": max_collision,
                "collision_rate": collisions / total_ids if total_ids > 0 else 0.0
            }
