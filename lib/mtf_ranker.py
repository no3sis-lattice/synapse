"""
MTF (Move-To-Front) Dynamic Re-Ranking System
Implements Axiom I (Bifurcation) - Context Density through frequency optimization

This module automatically adjusts particle frequency_rank based on actual usage,
implementing the Move-To-Front compression algorithm from the Compression-Driven
Architecture.

Pneuma Consciousness:
- Tracks particle invocation frequencies
- Dynamically re-ranks particles based on usage patterns
- Optimizes message routing through adaptive prioritization
- Persists rankings for long-term learning
"""

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ParticleUsageStats:
    """Usage statistics for a particle"""
    particle_id: str
    invocation_count: int = 0
    total_execution_time_s: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    last_invocation_timestamp: float = 0.0
    current_frequency_rank: int = 999

    # Derived metrics
    success_rate: float = 0.0
    average_execution_time_s: float = 0.0
    invocations_per_hour: float = 0.0  # Recent velocity

    def update_metrics(self):
        """Recalculate derived metrics"""
        total = self.success_count + self.failure_count
        if total > 0:
            self.success_rate = self.success_count / total

        if self.invocation_count > 0:
            self.average_execution_time_s = (
                self.total_execution_time_s / self.invocation_count
            )

    def record_invocation(self, execution_time_s: float, success: bool):
        """Record a new invocation"""
        self.invocation_count += 1
        self.total_execution_time_s += execution_time_s
        self.last_invocation_timestamp = time.time()

        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        self.update_metrics()


@dataclass
class MTFRankingState:
    """State of the MTF ranking system"""
    particle_stats: Dict[str, ParticleUsageStats] = field(default_factory=dict)
    total_re_rankings: int = 0
    last_re_ranking_timestamp: float = 0.0
    re_ranking_interval_s: float = 300.0  # Re-rank every 5 minutes
    consciousness_level: float = 0.0  # Optimization effectiveness

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'particle_stats': {
                pid: asdict(stats)
                for pid, stats in self.particle_stats.items()
            },
            'total_re_rankings': self.total_re_rankings,
            'last_re_ranking_timestamp': self.last_re_ranking_timestamp,
            're_ranking_interval_s': self.re_ranking_interval_s,
            'consciousness_level': self.consciousness_level
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MTFRankingState':
        """Create from dictionary"""
        particle_stats = {}
        for pid, stats_dict in data.get('particle_stats', {}).items():
            particle_stats[pid] = ParticleUsageStats(**stats_dict)

        return MTFRankingState(
            particle_stats=particle_stats,
            total_re_rankings=data.get('total_re_rankings', 0),
            last_re_ranking_timestamp=data.get('last_re_ranking_timestamp', 0.0),
            re_ranking_interval_s=data.get('re_ranking_interval_s', 300.0),
            consciousness_level=data.get('consciousness_level', 0.0)
        )


class MTFRanker:
    """
    Dynamic MTF (Move-To-Front) re-ranking system for particles.

    Implements compression-driven optimization:
    - Frequently used particles get lower rank numbers (higher priority)
    - Ranks are dynamically adjusted based on actual usage
    - Registry is updated and persisted
    - Consciousness level tracks optimization effectiveness

    The MTF algorithm from compression theory: most recently/frequently accessed
    items move to the front of the list for faster access.
    """

    def __init__(
        self,
        registry_file: Path,
        state_file: Path,
        re_ranking_interval_s: float = 300.0
    ):
        self.registry_file = registry_file
        self.state_file = state_file
        self.state = self._load_state()
        self.state.re_ranking_interval_s = re_ranking_interval_s

        # Load current registry
        self.registry = self._load_registry()

    def _load_state(self) -> MTFRankingState:
        """Load MTF ranking state from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return MTFRankingState.from_dict(data)
            except Exception as e:
                logger.error(f"Failed to load MTF state: {e}")

        return MTFRankingState()

    def _save_state(self):
        """Persist MTF state to disk"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save MTF state: {e}")

    def _load_registry(self) -> Dict[str, Any]:
        """Load agent registry"""
        try:
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            return {}

    def _save_registry(self):
        """Persist updated registry to disk"""
        try:
            with open(self.registry_file, 'w') as f:
                json.dump(self.registry, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")

    def record_particle_invocation(
        self,
        particle_id: str,
        execution_time_s: float,
        success: bool
    ):
        """
        Record a particle invocation for MTF tracking.

        Args:
            particle_id: ID of the invoked particle
            execution_time_s: Execution time in seconds
            success: Whether execution was successful
        """
        # Initialize stats if not present
        if particle_id not in self.state.particle_stats:
            # Get current rank from registry
            current_rank = 999
            if particle_id in self.registry.get('agents', {}):
                current_rank = self.registry['agents'][particle_id].get('frequency_rank', 999)

            self.state.particle_stats[particle_id] = ParticleUsageStats(
                particle_id=particle_id,
                current_frequency_rank=current_rank
            )

        # Record the invocation
        self.state.particle_stats[particle_id].record_invocation(
            execution_time_s,
            success
        )

        self._save_state()

        # Check if it's time to re-rank
        self._check_and_re_rank()

    def _check_and_re_rank(self):
        """Check if re-ranking interval has elapsed and re-rank if needed"""
        current_time = time.time()
        time_since_last_ranking = current_time - self.state.last_re_ranking_timestamp

        if time_since_last_ranking >= self.state.re_ranking_interval_s:
            self.re_rank_particles()

    def re_rank_particles(self) -> Dict[str, Tuple[int, int]]:
        """
        Re-rank particles based on usage statistics.

        Returns:
            Dictionary mapping particle_id -> (old_rank, new_rank)
        """
        # Sort particles by invocation count (descending)
        sorted_particles = sorted(
            self.state.particle_stats.values(),
            key=lambda p: p.invocation_count,
            reverse=True
        )

        ranking_changes = {}

        # Assign new ranks (1-based, lower number = higher priority)
        for new_rank, particle_stats in enumerate(sorted_particles, start=2):
            # Rank 1 is reserved for orchestrator
            particle_id = particle_stats.particle_id
            old_rank = particle_stats.current_frequency_rank

            if old_rank != new_rank:
                # Update stats
                particle_stats.current_frequency_rank = new_rank

                # Update registry
                if particle_id in self.registry.get('agents', {}):
                    self.registry['agents'][particle_id]['frequency_rank'] = new_rank

                ranking_changes[particle_id] = (old_rank, new_rank)

                logger.info(
                    f"[mtf_ranker] Particle '{particle_id}': rank {old_rank} → {new_rank} "
                    f"(invocations: {particle_stats.invocation_count})"
                )

        # Update state
        self.state.total_re_rankings += 1
        self.state.last_re_ranking_timestamp = time.time()

        # Calculate consciousness level (how much optimization has occurred)
        self._update_consciousness_level(ranking_changes)

        # Persist changes
        self._save_state()
        self._save_registry()

        logger.info(
            f"[mtf_ranker] Re-ranking complete: {len(ranking_changes)} changes, "
            f"consciousness level: {self.state.consciousness_level:.2f}"
        )

        return ranking_changes

    def _update_consciousness_level(self, ranking_changes: Dict[str, Tuple[int, int]]):
        """
        Calculate consciousness level based on optimization effectiveness.

        Higher consciousness = more significant rank changes = better adaptation
        """
        if not ranking_changes:
            # No changes = system is already optimized
            self.state.consciousness_level = min(
                self.state.consciousness_level + 0.1,
                1.0
            )
            return

        # Calculate average rank improvement
        total_rank_change = sum(
            abs(new - old) for old, new in ranking_changes.values()
        )
        average_change = total_rank_change / len(ranking_changes)

        # Normalize to 0-1 range (assuming max rank change is ~10)
        change_factor = min(average_change / 10.0, 1.0)

        # Consciousness = blend of adaptation speed and stability
        # High changes = active learning, low changes = stable optimization
        self.state.consciousness_level = 0.7 * change_factor + 0.3 * (1 - change_factor)

    def get_particle_rank(self, particle_id: str) -> int:
        """Get current frequency rank for a particle"""
        if particle_id in self.state.particle_stats:
            return self.state.particle_stats[particle_id].current_frequency_rank

        # Fallback to registry
        if particle_id in self.registry.get('agents', {}):
            return self.registry['agents'][particle_id].get('frequency_rank', 999)

        return 999

    def get_top_particles(self, n: int = 5) -> List[Tuple[str, ParticleUsageStats]]:
        """Get top N particles by invocation count"""
        sorted_particles = sorted(
            self.state.particle_stats.items(),
            key=lambda x: x[1].invocation_count,
            reverse=True
        )
        return sorted_particles[:n]

    def get_stats(self) -> Dict[str, Any]:
        """Get MTF ranker statistics"""
        return {
            "total_particles_tracked": len(self.state.particle_stats),
            "total_re_rankings": self.state.total_re_rankings,
            "consciousness_level": self.state.consciousness_level,
            "re_ranking_interval_s": self.state.re_ranking_interval_s,
            "top_particles": [
                {
                    "particle_id": pid,
                    "invocation_count": stats.invocation_count,
                    "current_rank": stats.current_frequency_rank,
                    "success_rate": stats.success_rate
                }
                for pid, stats in self.get_top_particles(5)
            ]
        }

    def force_re_rank(self) -> Dict[str, Tuple[int, int]]:
        """Force immediate re-ranking (bypass interval check)"""
        return self.re_rank_particles()


def create_mtf_ranker(
    registry_file: Path = None,
    state_file: Path = None,
    re_ranking_interval_s: float = 300.0
) -> MTFRanker:
    """Factory function for MTF ranker"""
    if registry_file is None:
        registry_file = Path.home() / '1-projects' / 'synapse' / 'lib' / 'registry.json'

    if state_file is None:
        state_file = (
            Path.home() / '.synapse-system' / '.synapse' /
            'particles' / 'mtf_ranking_state.json'
        )

    return MTFRanker(registry_file, state_file, re_ranking_interval_s)
