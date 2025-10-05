"""
Event Bus - Phase 5: Event-Driven Observability

Decouples metrics collection from execution through pub-sub pattern.

Pneuma Design:
- Axiom I (Bifurcation): Events compress execution state into symbols
- Axiom II (Map): Event types discovered, not hardcoded
- Axiom III (Emergence): Observer patterns emerge from event streams

Architecture:
- AsyncEventBus: Core pub-sub with backpressure
- EventType: Standard event taxonomy
- Event: Immutable event record with timestamp
- Subscriber: Async event consumer protocol
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Deque, Dict, List, Optional, Protocol, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# Event bus configuration
MAX_EVENT_QUEUE_SIZE = 1000  # Per subscriber max queue depth
EVENT_RETENTION_SECONDS = 3600  # 1 hour event history
MAX_EVENT_HISTORY = 10000  # Max events to retain in memory

# Backpressure configuration
BACKPRESSURE_THRESHOLD = 0.8  # 80% queue capacity triggers warning
SUBSCRIBER_TIMEOUT_SECONDS = 5.0  # Max time for subscriber to process event


# ============================================================================
# EVENT TYPES AND SCHEMAS
# ============================================================================

class EventType(Enum):
    """
    Standard event taxonomy - grows organically based on usage.

    Pneuma Pattern: Event types emerge from system behavior, not prescribed.
    """
    # Particle lifecycle events
    PARTICLE_STARTED = "particle.started"
    PARTICLE_STOPPED = "particle.stopped"
    PARTICLE_FAILED = "particle.failed"

    # Task execution events
    TASK_RECEIVED = "task.received"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"

    # Pattern discovery events (Axiom II)
    PATTERN_DISCOVERED = "pattern.discovered"
    PATTERN_APPLIED = "pattern.applied"

    # MTF ranking events
    MTF_RERANKED = "mtf.reranked"
    MTF_PARTICLE_PROMOTED = "mtf.particle_promoted"
    MTF_PARTICLE_DEMOTED = "mtf.particle_demoted"

    # Circuit breaker events
    CIRCUIT_OPENED = "circuit.opened"
    CIRCUIT_CLOSED = "circuit.closed"
    CIRCUIT_HALF_OPEN = "circuit.half_open"

    # System health events
    METRICS_COLLECTED = "metrics.collected"
    THRESHOLD_EXCEEDED = "threshold.exceeded"
    BACKPRESSURE_DETECTED = "backpressure.detected"

    # Custom domain events (extensible)
    CUSTOM = "custom"


@dataclass(frozen=True)
class Event:
    """
    Immutable event record.

    Pneuma: Maximum context density - event_id is deterministic hash of content.
    """
    event_id: str
    event_type: EventType
    source: str  # Particle ID or system component
    timestamp: float
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize event to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'source': self.source,
            'timestamp': self.timestamp,
            'payload': self.payload,
            'metadata': self.metadata
        }

    @staticmethod
    def create(
        event_type: EventType,
        source: str,
        payload: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'Event':
        """
        Factory method for creating events.

        Generates deterministic event_id from content hash.
        """
        import hashlib
        import json

        # Generate deterministic ID from content
        content = {
            'type': event_type.value,
            'source': source,
            'payload': payload or {},
            'metadata': metadata or {}
        }
        content_str = json.dumps(content, sort_keys=True)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()[:16]

        # Compound ID: timestamp_hash (for ordering + uniqueness)
        timestamp = time.time()
        event_id = f"evt_{int(timestamp)}_{content_hash}"

        return Event(
            event_id=event_id,
            event_type=event_type,
            source=source,
            timestamp=timestamp,
            payload=payload or {},
            metadata=metadata or {}
        )


# ============================================================================
# SUBSCRIBER PROTOCOL
# ============================================================================

class EventSubscriber(Protocol):
    """
    Protocol for event subscribers.

    Subscribers must implement async handle_event method.
    """

    async def handle_event(self, event: Event) -> None:
        """
        Process an event.

        Args:
            event: Event to process

        Raises:
            Exception: If event processing fails (logged, not propagated)
        """
        ...

    def get_subscriber_id(self) -> str:
        """Return unique subscriber ID"""
        ...

    def get_subscribed_event_types(self) -> Set[EventType]:
        """Return set of event types this subscriber cares about"""
        ...


# ============================================================================
# EVENT BUS
# ============================================================================

class AsyncEventBus:
    """
    Async pub-sub event bus with backpressure handling.

    Design:
    - Subscribers register for specific event types
    - Events broadcast to all matching subscribers
    - Per-subscriber queue with backpressure detection
    - Event history for replay/debugging

    Pneuma: The bus is a consciousness conduit - events flow from execution
    to observation, enabling emergent pattern discovery.
    """

    def __init__(self):
        """Initialize event bus"""
        self.subscribers: Dict[str, EventSubscriber] = {}
        self.event_queues: Dict[str, asyncio.Queue] = {}
        self.consumer_tasks: Dict[str, asyncio.Task] = {}

        # Event history (ring buffer)
        self.event_history: Deque[Event] = deque(maxlen=MAX_EVENT_HISTORY)
        self.history_by_type: Dict[EventType, Deque[Event]] = defaultdict(
            lambda: deque(maxlen=1000)
        )

        # Metrics
        self.total_events_published = 0
        self.events_by_type: Dict[EventType, int] = defaultdict(int)
        self.subscriber_processed_count: Dict[str, int] = defaultdict(int)
        self.subscriber_error_count: Dict[str, int] = defaultdict(int)

        # State
        self.running = False
        self._lock = asyncio.Lock()

        logger.info("AsyncEventBus initialized")

    async def subscribe(
        self,
        subscriber: EventSubscriber,
        event_types: Optional[Set[EventType]] = None
    ) -> None:
        """
        Subscribe to events.

        Args:
            subscriber: Object implementing EventSubscriber protocol
            event_types: Set of event types to subscribe to (None = all)
        """
        async with self._lock:
            subscriber_id = subscriber.get_subscriber_id()

            if subscriber_id in self.subscribers:
                logger.warning(f"Subscriber {subscriber_id} already registered, replacing")
                await self.unsubscribe(subscriber_id)

            # Register subscriber
            self.subscribers[subscriber_id] = subscriber
            self.event_queues[subscriber_id] = asyncio.Queue(maxsize=MAX_EVENT_QUEUE_SIZE)

            # Start consumer task
            self.consumer_tasks[subscriber_id] = asyncio.create_task(
                self._consume_events(subscriber_id)
            )

            logger.info(
                f"Subscriber {subscriber_id} registered for "
                f"{len(event_types or subscriber.get_subscribed_event_types())} event types"
            )

    async def unsubscribe(self, subscriber_id: str) -> None:
        """
        Unsubscribe from events.

        Args:
            subscriber_id: ID of subscriber to remove
        """
        async with self._lock:
            if subscriber_id not in self.subscribers:
                logger.warning(f"Subscriber {subscriber_id} not found")
                return

            # Cancel consumer task
            if subscriber_id in self.consumer_tasks:
                self.consumer_tasks[subscriber_id].cancel()
                try:
                    await self.consumer_tasks[subscriber_id]
                except asyncio.CancelledError:
                    pass
                del self.consumer_tasks[subscriber_id]

            # Remove subscriber
            del self.subscribers[subscriber_id]
            del self.event_queues[subscriber_id]

            logger.info(f"Subscriber {subscriber_id} unregistered")

    async def publish(self, event: Event) -> None:
        """
        Publish event to all matching subscribers.

        Args:
            event: Event to publish
        """
        self.total_events_published += 1
        self.events_by_type[event.event_type] += 1

        # Add to history
        await self._add_to_history(event)

        # Broadcast to matching subscribers
        await self._broadcast_to_subscribers(event)

    async def _add_to_history(self, event: Event) -> None:
        """
        Add event to history buffers.

        Args:
            event: Event to add
        """
        self.event_history.append(event)
        self.history_by_type[event.event_type].append(event)

    async def _broadcast_to_subscribers(self, event: Event) -> None:
        """
        Broadcast event to all matching subscribers.

        Args:
            event: Event to broadcast
        """
        delivered = 0
        for subscriber_id, subscriber in list(self.subscribers.items()):
            # Check if subscriber wants this event type
            subscribed_types = subscriber.get_subscribed_event_types()
            if subscribed_types and event.event_type not in subscribed_types:
                continue

            # Try to enqueue event
            queue = self.event_queues.get(subscriber_id)
            if not queue:
                continue

            try:
                # Non-blocking put with backpressure detection
                queue.put_nowait(event)
                delivered += 1

                # Check backpressure
                await self._check_backpressure(subscriber_id, queue)

            except asyncio.QueueFull:
                logger.error(
                    f"Event queue full for subscriber {subscriber_id}, "
                    f"dropping event {event.event_id}"
                )
                self.subscriber_error_count[subscriber_id] += 1

        if delivered == 0:
            logger.debug(f"Event {event.event_id} had no matching subscribers")

    async def _check_backpressure(
        self,
        subscriber_id: str,
        queue: asyncio.Queue
    ) -> None:
        """
        Check and emit backpressure warnings.

        Args:
            subscriber_id: ID of subscriber
            queue: Subscriber's event queue
        """
        if queue.qsize() / MAX_EVENT_QUEUE_SIZE > BACKPRESSURE_THRESHOLD:
            logger.warning(
                f"Backpressure detected for subscriber {subscriber_id}: "
                f"{queue.qsize()}/{MAX_EVENT_QUEUE_SIZE} events queued"
            )
            # Emit backpressure event
            backpressure_event = Event.create(
                EventType.BACKPRESSURE_DETECTED,
                source="event_bus",
                payload={
                    'subscriber_id': subscriber_id,
                    'queue_size': queue.qsize(),
                    'queue_capacity': MAX_EVENT_QUEUE_SIZE
                }
            )
            # Don't recurse - just add to history
            self.event_history.append(backpressure_event)

    async def _consume_events(self, subscriber_id: str) -> None:
        """
        Consumer task for a subscriber.

        Args:
            subscriber_id: ID of subscriber to consume for
        """
        subscriber = self.subscribers[subscriber_id]
        queue = self.event_queues[subscriber_id]

        logger.info(f"Event consumer started for subscriber {subscriber_id}")

        try:
            while True:
                # Get next event
                event = await queue.get()

                # Process event with timeout
                try:
                    await asyncio.wait_for(
                        subscriber.handle_event(event),
                        timeout=SUBSCRIBER_TIMEOUT_SECONDS
                    )
                    self.subscriber_processed_count[subscriber_id] += 1

                except asyncio.TimeoutError:
                    logger.error(
                        f"Subscriber {subscriber_id} timeout processing event {event.event_id}"
                    )
                    self.subscriber_error_count[subscriber_id] += 1

                except (ValueError, TypeError, RuntimeError, AttributeError) as e:
                    logger.error(
                        f"Subscriber {subscriber_id} error processing event {event.event_id}: {e}"
                    )
                    self.subscriber_error_count[subscriber_id] += 1

                finally:
                    queue.task_done()

        except asyncio.CancelledError:
            logger.info(f"Event consumer cancelled for subscriber {subscriber_id}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return {
            'total_events_published': self.total_events_published,
            'events_by_type': {
                event_type.value: count
                for event_type, count in self.events_by_type.items()
            },
            'total_subscribers': len(self.subscribers),
            'subscriber_stats': {
                sub_id: {
                    'processed': self.subscriber_processed_count[sub_id],
                    'errors': self.subscriber_error_count[sub_id],
                    'queue_size': self.event_queues[sub_id].qsize()
                }
                for sub_id in self.subscribers.keys()
            },
            'event_history_size': len(self.event_history)
        }

    def get_event_history(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[Event]:
        """
        Get recent event history.

        Args:
            event_type: Filter by event type (None = all)
            limit: Maximum events to return

        Returns:
            List of recent events (newest first)
        """
        if event_type:
            history = list(self.history_by_type[event_type])
        else:
            history = list(self.event_history)

        # Return newest first
        return history[-limit:][::-1]


# ============================================================================
# GLOBAL EVENT BUS INSTANCE
# ============================================================================

_event_bus: Optional[AsyncEventBus] = None


def get_event_bus() -> AsyncEventBus:
    """
    Get global event bus instance (singleton).

    Returns:
        Global AsyncEventBus instance
    """
    global _event_bus
    if _event_bus is None:
        _event_bus = AsyncEventBus()
    return _event_bus
