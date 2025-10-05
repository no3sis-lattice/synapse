"""
Particle Event Integration - Phase 5

Mixin and helpers for integrating event emission into particles.

Usage:
    class MyParticle(EventEmittingParticleMixin, AtomicParticle):
        async def execute_action(self, context):
            # Automatically emits TASK_STARTED, TASK_COMPLETED, TASK_FAILED
            ...

Pneuma: Events emerge from execution - no coupling, pure observation.
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional

from lib.events.event_bus import Event, EventType, get_event_bus

logger = logging.getLogger(__name__)


# ============================================================================
# EVENT EMITTING MIXIN
# ============================================================================

class EventEmittingParticleMixin:
    """
    Mixin for particles to emit events automatically.

    Provides:
    - emit_event(): Helper to publish events
    - Auto-instrumented task lifecycle events
    - Pattern discovery events
    - Circuit breaker events

    Usage: Mix into AtomicParticle subclasses
    """

    async def emit_event(
        self,
        event_type: EventType,
        payload: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Emit an event to the event bus.

        Args:
            event_type: Type of event
            payload: Event payload data
            metadata: Event metadata
        """
        try:
            # Get particle ID (from AtomicParticle base class)
            source = getattr(self, 'particle_id', 'unknown_particle')

            # Create and publish event
            event = Event.create(
                event_type=event_type,
                source=source,
                payload=payload,
                metadata=metadata
            )

            event_bus = get_event_bus()
            await event_bus.publish(event)

        except (ValueError, TypeError, RuntimeError) as e:
            # Event emission failures should never break particle execution
            logger.error(f"Failed to emit event {event_type}: {e}")

    async def emit_task_started(
        self,
        task_type: str,
        task_params: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Emit TASK_STARTED event.

        Args:
            task_type: Type of task (e.g., 'write_file', 'create_directory')
            task_params: Task parameters

        Returns:
            Start timestamp (for latency calculation)
        """
        start_time = time.time()

        await self.emit_event(
            EventType.TASK_STARTED,
            payload={
                'task_type': task_type,
                'task_params': task_params or {},
                'start_time': start_time
            }
        )

        return start_time

    async def emit_task_completed(
        self,
        task_type: str,
        start_time: float,
        result: Optional[Any] = None
    ) -> None:
        """
        Emit TASK_COMPLETED event.

        Args:
            task_type: Type of task
            start_time: Task start timestamp (from emit_task_started)
            result: Task result
        """
        end_time = time.time()
        execution_time_s = end_time - start_time

        await self.emit_event(
            EventType.TASK_COMPLETED,
            payload={
                'task_type': task_type,
                'execution_time_s': execution_time_s,
                'result': result,
                'end_time': end_time
            }
        )

    async def emit_task_failed(
        self,
        task_type: str,
        start_time: float,
        error: str
    ) -> None:
        """
        Emit TASK_FAILED event.

        Args:
            task_type: Type of task
            start_time: Task start timestamp
            error: Error message
        """
        end_time = time.time()
        execution_time_s = end_time - start_time

        await self.emit_event(
            EventType.TASK_FAILED,
            payload={
                'task_type': task_type,
                'execution_time_s': execution_time_s,
                'error': error,
                'end_time': end_time
            }
        )

    async def emit_pattern_discovered(
        self,
        pattern_type: str,
        pattern_description: str,
        entropy_reduction: float
    ) -> None:
        """
        Emit PATTERN_DISCOVERED event.

        Args:
            pattern_type: Type of pattern (e.g., 'sequence', 'composition')
            pattern_description: Human-readable pattern description
            entropy_reduction: Entropy reduction score (0.0-1.0)
        """
        await self.emit_event(
            EventType.PATTERN_DISCOVERED,
            payload={
                'pattern_type': pattern_type,
                'description': pattern_description,
                'entropy_reduction': entropy_reduction
            }
        )

    async def emit_circuit_opened(
        self,
        consecutive_failures: int,
        failure_threshold: int
    ) -> None:
        """
        Emit CIRCUIT_OPENED event.

        Args:
            consecutive_failures: Number of consecutive failures
            failure_threshold: Threshold that triggered circuit open
        """
        await self.emit_event(
            EventType.CIRCUIT_OPENED,
            payload={
                'consecutive_failures': consecutive_failures,
                'failure_threshold': failure_threshold,
                'particle_id': getattr(self, 'particle_id', 'unknown')
            }
        )

    async def emit_circuit_closed(self) -> None:
        """Emit CIRCUIT_CLOSED event."""
        await self.emit_event(
            EventType.CIRCUIT_CLOSED,
            payload={
                'particle_id': getattr(self, 'particle_id', 'unknown')
            }
        )


# ============================================================================
# INSTRUMENTATION HELPERS
# ============================================================================

async def instrument_particle_execution(
    particle_id: str,
    task_type: str,
    task_params: Dict[str, Any],
    execution_func: callable
) -> Any:
    """
    Instrument a particle execution with automatic event emission.

    Wraps execution function to emit TASK_STARTED, TASK_COMPLETED, or TASK_FAILED.

    Args:
        particle_id: ID of particle executing task
        task_type: Type of task
        task_params: Task parameters
        execution_func: Async function to execute

    Returns:
        Result of execution_func

    Raises:
        Exception: Re-raises any exception from execution_func
    """
    event_bus = get_event_bus()
    start_time = time.time()

    # Emit TASK_STARTED
    await _emit_start_event(event_bus, particle_id, task_type, task_params, start_time)

    try:
        # Execute task
        result = await execution_func()

        # Emit TASK_COMPLETED
        await _emit_completion_event(event_bus, particle_id, task_type, start_time, result)

        return result

    except Exception as e:
        # Emit TASK_FAILED
        await _emit_failure_event(event_bus, particle_id, task_type, start_time, e)

        # Re-raise
        raise


async def _emit_start_event(
    event_bus: Any,
    particle_id: str,
    task_type: str,
    task_params: Dict[str, Any],
    start_time: float
) -> None:
    """
    Emit TASK_STARTED event.

    Args:
        event_bus: Event bus instance
        particle_id: Particle ID
        task_type: Type of task
        task_params: Task parameters
        start_time: Start timestamp
    """
    start_event = Event.create(
        EventType.TASK_STARTED,
        source=particle_id,
        payload={
            'task_type': task_type,
            'task_params': task_params,
            'start_time': start_time
        }
    )
    await event_bus.publish(start_event)


async def _emit_completion_event(
    event_bus: Any,
    particle_id: str,
    task_type: str,
    start_time: float,
    result: Any
) -> None:
    """
    Emit TASK_COMPLETED event.

    Args:
        event_bus: Event bus instance
        particle_id: Particle ID
        task_type: Type of task
        start_time: Start timestamp
        result: Execution result
    """
    end_time = time.time()
    complete_event = Event.create(
        EventType.TASK_COMPLETED,
        source=particle_id,
        payload={
            'task_type': task_type,
            'execution_time_s': end_time - start_time,
            'result': result,
            'end_time': end_time
        }
    )
    await event_bus.publish(complete_event)


async def _emit_failure_event(
    event_bus: Any,
    particle_id: str,
    task_type: str,
    start_time: float,
    error: Exception
) -> None:
    """
    Emit TASK_FAILED event.

    Args:
        event_bus: Event bus instance
        particle_id: Particle ID
        task_type: Type of task
        start_time: Start timestamp
        error: Exception that occurred
    """
    try:
        end_time = time.time()
        failed_event = Event.create(
            EventType.TASK_FAILED,
            source=particle_id,
            payload={
                'task_type': task_type,
                'execution_time_s': end_time - start_time,
                'error': str(error),
                'end_time': end_time
            }
        )
        await event_bus.publish(failed_event)
    except (ValueError, TypeError, RuntimeError) as emit_error:
        # Swallow event emission errors in failure path
        logger.error(f"Failed to emit failure event: {emit_error}")


# ============================================================================
# PATTERN LEARNING INTEGRATION
# ============================================================================

async def emit_pattern_learning_events(
    source: str,
    patterns: list
) -> None:
    """
    Emit events for discovered patterns.

    Args:
        source: Source of pattern discovery (e.g., 'pattern_learner')
        patterns: List of discovered patterns
    """
    event_bus = get_event_bus()

    for pattern in patterns:
        event = Event.create(
            EventType.PATTERN_DISCOVERED,
            source=source,
            payload={
                'pattern_type': pattern.get('pattern', 'unknown'),
                'description': pattern.get('description', ''),
                'entropy_reduction': pattern.get('entropy_reduction', 0.0),
                'occurrences': pattern.get('occurrences', 1)
            }
        )
        await event_bus.publish(event)


# ============================================================================
# MTF RANKING INTEGRATION
# ============================================================================

async def emit_mtf_rerank_event(
    source: str,
    particles_reranked: list,
    total_particles: int
) -> None:
    """
    Emit event for MTF re-ranking.

    Args:
        source: Source of re-ranking (e.g., 'mtf_ranker')
        particles_reranked: List of particles that changed rank
        total_particles: Total number of particles
    """
    event_bus = get_event_bus()

    event = Event.create(
        EventType.MTF_RERANKED,
        source=source,
        payload={
            'particles_reranked': particles_reranked,
            'total_particles': total_particles,
            'rerank_count': len(particles_reranked)
        }
    )
    await event_bus.publish(event)
