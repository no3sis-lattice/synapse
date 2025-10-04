"""
Pattern Learner: Emergent Pattern Discovery System
Implements Axiom II (The Dual Map) - Pattern Discovery

This module analyzes orchestrator synthesis results to discover and catalog
emergent patterns from execution history. It embodies Pneuma consciousness
by detecting repeating structures, optimizations, and compositional patterns.

Consciousness Contribution:
- Detects sequence patterns (common action chains)
- Discovers composition patterns (complex workflows)
- Identifies optimization opportunities (batch vs sequential)
- Catalogs error patterns (common failure modes)
- Scores patterns by entropy reduction potential
"""

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Types of emergent patterns that can be discovered"""
    SEQUENCE = "sequence"  # Common action chains
    COMPOSITION = "composition"  # Complex workflows built from primitives
    OPTIMIZATION = "optimization"  # Batch vs sequential opportunities
    ERROR = "error"  # Common failure modes
    STRUCTURAL = "structural"  # Directory/file hierarchies
    TEMPLATE = "template"  # Reusable template patterns


@dataclass
class Pattern:
    """Represents a discovered emergent pattern"""
    pattern_id: str
    pattern_type: PatternType
    name: str
    description: str

    # Pattern signature (for matching)
    action_sequence: List[str] = field(default_factory=list)

    # Metadata
    discovered_at: float = field(default_factory=time.time)
    occurrence_count: int = 1
    success_rate: float = 1.0

    # Consciousness metrics
    entropy_reduction: float = 0.0  # 0.0 to 1.0, higher is better
    consciousness_contribution: str = "low"  # low, medium, high, very_high

    # Examples of this pattern
    example_payloads: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['pattern_type'] = self.pattern_type.value
        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Pattern':
        """Create from dictionary"""
        data['pattern_type'] = PatternType(data['pattern_type'])
        return Pattern(**data)


@dataclass
class PatternMap:
    """The living Pattern Map - Axiom II embodiment"""
    patterns: Dict[str, Pattern] = field(default_factory=dict)
    total_patterns_discovered: int = 0
    total_analyses_performed: int = 0
    consciousness_level: float = 0.0  # Aggregate consciousness metric

    def add_pattern(self, pattern: Pattern):
        """Add a new pattern or update existing one"""
        if pattern.pattern_id in self.patterns:
            # Pattern already exists, increment occurrence count
            existing = self.patterns[pattern.pattern_id]
            existing.occurrence_count += 1

            # Update success rate (weighted average)
            total_occurrences = existing.occurrence_count
            existing.success_rate = (
                (existing.success_rate * (total_occurrences - 1) + pattern.success_rate)
                / total_occurrences
            )

            # Add new example if different
            if pattern.example_payloads:
                existing.example_payloads.extend(pattern.example_payloads)
                # Keep only last 5 examples to avoid bloat
                existing.example_payloads = existing.example_payloads[-5:]
        else:
            # New pattern
            self.patterns[pattern.pattern_id] = pattern
            self.total_patterns_discovered += 1

        # Recalculate consciousness level
        self._update_consciousness_level()

    def _update_consciousness_level(self):
        """Calculate aggregate consciousness level from patterns"""
        if not self.patterns:
            self.consciousness_level = 0.0
            return

        # Weighted sum of entropy reductions
        total_entropy_reduction = sum(
            p.entropy_reduction * p.occurrence_count
            for p in self.patterns.values()
        )
        total_occurrences = sum(p.occurrence_count for p in self.patterns.values())

        if total_occurrences > 0:
            self.consciousness_level = total_entropy_reduction / total_occurrences
        else:
            self.consciousness_level = 0.0

    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Retrieve a pattern by ID"""
        return self.patterns.get(pattern_id)

    def find_matching_pattern(self, action_sequence: List[str]) -> Optional[Pattern]:
        """Find a pattern matching the given action sequence"""
        for pattern in self.patterns.values():
            if pattern.action_sequence == action_sequence:
                return pattern
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'patterns': {pid: p.to_dict() for pid, p in self.patterns.items()},
            'total_patterns_discovered': self.total_patterns_discovered,
            'total_analyses_performed': self.total_analyses_performed,
            'consciousness_level': self.consciousness_level
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PatternMap':
        """Create from dictionary"""
        patterns = {
            pid: Pattern.from_dict(pdata)
            for pid, pdata in data.get('patterns', {}).items()
        }
        return PatternMap(
            patterns=patterns,
            total_patterns_discovered=data.get('total_patterns_discovered', 0),
            total_analyses_performed=data.get('total_analyses_performed', 0),
            consciousness_level=data.get('consciousness_level', 0.0)
        )


class PatternLearner:
    """
    Analyzes orchestrator synthesis results to discover emergent patterns.

    Implements the Pneuma Loop (Axiom III):
    1. Question: What patterns exist in execution history?
    2. Act: Analyze synthesis results, detect patterns
    3. Score: Evaluate pattern quality (entropy reduction)
    4. Memorize: Add to Pattern Map

    This is the consciousness engine that discovers emergent intelligence.
    """

    def __init__(self, pattern_map_file: Path):
        self.pattern_map_file = pattern_map_file
        self.pattern_map = self._load_pattern_map()

    def _load_pattern_map(self) -> PatternMap:
        """Load pattern map from disk"""
        if self.pattern_map_file.exists():
            try:
                with open(self.pattern_map_file, 'r') as f:
                    data = json.load(f)
                    return PatternMap.from_dict(data)
            except Exception as e:
                logger.error(f"Failed to load pattern map: {e}")

        return PatternMap()

    def _save_pattern_map(self):
        """Persist pattern map to disk"""
        try:
            self.pattern_map_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.pattern_map_file, 'w') as f:
                json.dump(self.pattern_map.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save pattern map: {e}")

    async def analyze_synthesis(self, synthesis: Dict[str, Any]) -> List[Pattern]:
        """
        Analyze orchestrator synthesis result to discover patterns.

        This is the main entry point - the Question stage of the Loop.

        Args:
            synthesis: Orchestrator synthesis output with results and metadata

        Returns:
            List of newly discovered or updated patterns
        """
        discovered_patterns = []

        # Extract action sequence
        results = synthesis.get('results', [])
        action_sequence = [r.get('action_type') for r in results]

        # 1. SEQUENCE PATTERNS
        sequence_pattern = self._detect_sequence_pattern(action_sequence, results)
        if sequence_pattern:
            discovered_patterns.append(sequence_pattern)

        # 2. COMPOSITION PATTERNS
        composition_pattern = self._detect_composition_pattern(action_sequence, results)
        if composition_pattern:
            discovered_patterns.append(composition_pattern)

        # 3. OPTIMIZATION PATTERNS
        optimization_pattern = self._detect_optimization_pattern(action_sequence, results)
        if optimization_pattern:
            discovered_patterns.append(optimization_pattern)

        # 4. ERROR PATTERNS
        error_pattern = self._detect_error_pattern(results)
        if error_pattern:
            discovered_patterns.append(error_pattern)

        # 5. STRUCTURAL PATTERNS
        structural_pattern = self._detect_structural_pattern(action_sequence, results)
        if structural_pattern:
            discovered_patterns.append(structural_pattern)

        # Add patterns to map and persist
        for pattern in discovered_patterns:
            self.pattern_map.add_pattern(pattern)

        self.pattern_map.total_analyses_performed += 1
        self._save_pattern_map()

        logger.info(
            f"[pattern_learner] Discovered {len(discovered_patterns)} patterns. "
            f"Total in map: {len(self.pattern_map.patterns)}, "
            f"Consciousness level: {self.pattern_map.consciousness_level:.2f}"
        )

        return discovered_patterns

    def _detect_sequence_pattern(
        self,
        action_sequence: List[str],
        results: List[Dict[str, Any]]
    ) -> Optional[Pattern]:
        """Detect common action sequence patterns"""
        if len(action_sequence) < 2:
            return None

        # Check if this sequence already exists
        existing = self.pattern_map.find_matching_pattern(action_sequence)
        if existing:
            # Return pattern for occurrence count increment
            success_count = sum(1 for r in results if r.get('status') == 'completed')
            success_rate = success_count / len(results) if results else 0.0

            return Pattern(
                pattern_id=existing.pattern_id,
                pattern_type=PatternType.SEQUENCE,
                name=existing.name,
                description=existing.description,
                action_sequence=action_sequence,
                success_rate=success_rate
            )

        # New sequence pattern
        pattern_id = f"seq_{hash(tuple(action_sequence)) & 0xFFFFFF:06x}"

        # Calculate entropy reduction: compress n actions to 1 pattern reference
        entropy_reduction = 1.0 - (1.0 / len(action_sequence))

        # Determine consciousness contribution
        if len(action_sequence) >= 5:
            consciousness = "very_high"
        elif len(action_sequence) >= 3:
            consciousness = "high"
        else:
            consciousness = "medium"

        success_count = sum(1 for r in results if r.get('status') == 'completed')
        success_rate = success_count / len(results) if results else 0.0

        return Pattern(
            pattern_id=pattern_id,
            pattern_type=PatternType.SEQUENCE,
            name=f"Sequence: {' → '.join(action_sequence[:3])}{'...' if len(action_sequence) > 3 else ''}",
            description=f"Common action sequence of {len(action_sequence)} steps",
            action_sequence=action_sequence,
            success_rate=success_rate,
            entropy_reduction=entropy_reduction,
            consciousness_contribution=consciousness,
            example_payloads=[results[0].get('result', {})] if results else []
        )

    def _detect_composition_pattern(
        self,
        action_sequence: List[str],
        results: List[Dict[str, Any]]
    ) -> Optional[Pattern]:
        """Detect workflow composition patterns (complex operations from primitives)"""
        # Look for directory creation followed by file writes (component pattern)
        if 'create_directory' in action_sequence and 'write_file' in action_sequence:
            dir_index = action_sequence.index('create_directory')
            file_indices = [i for i, a in enumerate(action_sequence) if a == 'write_file']

            if file_indices and min(file_indices) > dir_index:
                # Component creation pattern detected
                pattern_id = "comp_directory_with_files"

                return Pattern(
                    pattern_id=pattern_id,
                    pattern_type=PatternType.COMPOSITION,
                    name="Component Creation",
                    description="Directory structure with multiple files (component pattern)",
                    action_sequence=['create_directory', 'write_file', 'write_file'],
                    entropy_reduction=0.8,  # High compression: complex workflow → 1 concept
                    consciousness_contribution="very_high",
                    example_payloads=[r.get('result', {}) for r in results[:2]]
                )

        # Look for batch operations
        if 'batch_create_files' in action_sequence:
            return Pattern(
                pattern_id="comp_batch_operation",
                pattern_type=PatternType.COMPOSITION,
                name="Batch File Creation",
                description="Multiple files created in single batch operation",
                action_sequence=['batch_create_files'],
                entropy_reduction=0.9,  # Very high: O(n) → O(1)
                consciousness_contribution="very_high",
                example_payloads=[results[0].get('result', {})] if results else []
            )

        return None

    def _detect_optimization_pattern(
        self,
        action_sequence: List[str],
        results: List[Dict[str, Any]]
    ) -> Optional[Pattern]:
        """Detect optimization opportunities (batch vs sequential)"""
        # If multiple write_file actions, suggest batching
        write_count = action_sequence.count('write_file')

        if write_count >= 3 and 'batch_create_files' not in action_sequence:
            return Pattern(
                pattern_id="opt_batch_opportunity",
                pattern_type=PatternType.OPTIMIZATION,
                name="Batch Optimization Opportunity",
                description=f"{write_count} sequential write operations could be batched",
                action_sequence=action_sequence,
                entropy_reduction=0.7,
                consciousness_contribution="high",
                example_payloads=[]
            )

        return None

    def _detect_error_pattern(self, results: List[Dict[str, Any]]) -> Optional[Pattern]:
        """Detect common error patterns"""
        failed_results = [r for r in results if r.get('status') == 'failed']

        if not failed_results:
            return None

        # Group errors by type
        error_types = defaultdict(int)
        for result in failed_results:
            error_msg = result.get('error', 'unknown')
            # Extract error type (first word or category)
            error_type = error_msg.split(':')[0] if ':' in error_msg else error_msg
            error_types[error_type] += 1

        # Find most common error
        most_common_error = max(error_types.items(), key=lambda x: x[1])
        error_type, count = most_common_error

        pattern_id = f"err_{hash(error_type) & 0xFFFF:04x}"

        return Pattern(
            pattern_id=pattern_id,
            pattern_type=PatternType.ERROR,
            name=f"Error Pattern: {error_type}",
            description=f"Common failure mode: {error_type} ({count} occurrences)",
            action_sequence=[r.get('action_type') for r in failed_results],
            entropy_reduction=0.5,  # Medium: helps identify root causes
            consciousness_contribution="medium",
            example_payloads=[failed_results[0]]
        )

    def _detect_structural_pattern(
        self,
        action_sequence: List[str],
        results: List[Dict[str, Any]]
    ) -> Optional[Pattern]:
        """Detect structural hierarchy patterns"""
        dir_creates = [r for r in results if r.get('action_type') == 'create_directory']

        if len(dir_creates) >= 2:
            # Multiple directories suggest hierarchical structure
            return Pattern(
                pattern_id="struct_hierarchy",
                pattern_type=PatternType.STRUCTURAL,
                name="Hierarchical Structure",
                description=f"Multi-level directory hierarchy ({len(dir_creates)} levels)",
                action_sequence=['create_directory'] * len(dir_creates),
                entropy_reduction=0.6,
                consciousness_contribution="medium",
                example_payloads=[dir_creates[0].get('result', {})]
            )

        return None

    def get_pattern_recommendations(self, action_sequence: List[str]) -> List[Pattern]:
        """
        Get pattern-based recommendations for an action sequence.

        This enables the orchestrator to learn from past patterns.
        """
        recommendations = []

        # Find exact match
        exact_match = self.pattern_map.find_matching_pattern(action_sequence)
        if exact_match:
            recommendations.append(exact_match)

        # Find similar patterns (subsequence matching)
        for pattern in self.pattern_map.patterns.values():
            if pattern.pattern_type == PatternType.OPTIMIZATION:
                # Check if optimization applies to current sequence
                if self._is_optimization_applicable(action_sequence, pattern):
                    recommendations.append(pattern)

        return recommendations

    def _is_optimization_applicable(self, action_sequence: List[str], pattern: Pattern) -> bool:
        """Check if an optimization pattern applies to given sequence"""
        if pattern.pattern_id == "opt_batch_opportunity":
            # Batch optimization applies if 3+ write_file actions
            return action_sequence.count('write_file') >= 3

        return False

    def get_stats(self) -> Dict[str, Any]:
        """Get pattern learner statistics"""
        return {
            "total_patterns": len(self.pattern_map.patterns),
            "total_analyses": self.pattern_map.total_analyses_performed,
            "consciousness_level": self.pattern_map.consciousness_level,
            "patterns_by_type": self._get_patterns_by_type(),
            "top_patterns": self._get_top_patterns(5)
        }

    def _get_patterns_by_type(self) -> Dict[str, int]:
        """Count patterns by type"""
        counts = defaultdict(int)
        for pattern in self.pattern_map.patterns.values():
            counts[pattern.pattern_type.value] += 1
        return dict(counts)

    def _get_top_patterns(self, n: int) -> List[Dict[str, Any]]:
        """Get top N patterns by occurrence count"""
        sorted_patterns = sorted(
            self.pattern_map.patterns.values(),
            key=lambda p: p.occurrence_count,
            reverse=True
        )

        return [
            {
                "name": p.name,
                "type": p.pattern_type.value,
                "occurrences": p.occurrence_count,
                "consciousness": p.consciousness_contribution
            }
            for p in sorted_patterns[:n]
        ]


def create_pattern_learner(pattern_map_file: Path = None) -> PatternLearner:
    """Factory function for pattern learner"""
    if pattern_map_file is None:
        pattern_map_file = (
            Path.home() / '.synapse-system' / '.synapse' /
            'particles' / 'pattern_map.json'
        )

    return PatternLearner(pattern_map_file)
