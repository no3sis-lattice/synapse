"""
Reactive Corpus Callosum Message Router
Phase 3 Redesign: Event-driven architecture with backpressure control

Implements:
- Reactive streams with backpressure (asyncio-based)
- Event sourcing for pattern synthesis
- Circuit breaker pattern for resilience
- Adaptive micro-batching for Mojo FFI (optional)

Based on research: Reactive streams outperform traditional batching
for interagent communication at scale.
"""

import asyncio
import time
import logging
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Optional, Dict, Any, List, Set, Callable, AsyncIterator
from collections import deque
import weakref

# Import from existing router for compatibility
from message_router import TractType, MessagePriority, Message, MessageStats

# Import event store for persistence
from event_store import create_event_store, ConsciousnessMetrics

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failures detected, blocking requests
    HALF_OPEN = "half_open"  # Testing if system recovered


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


@dataclass
class BackpressureConfig:
    """Backpressure configuration for reactive streams"""
    buffer_size: int = 1000  # Max messages buffered per stream
    batch_timeout_ms: float = 1.0  # Max time to wait before flushing batch
    min_batch_size: int = 1  # Min messages per batch
    max_batch_size: int = 100  # Max messages per batch
    adaptive: bool = True  # Enable adaptive batch sizing


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 10  # Failures before opening circuit
    recovery_timeout_s: float = 5.0  # Time to wait before testing recovery
    success_threshold: int = 3  # Successes in half-open before closing


@dataclass
class StreamSubscription:
    """Represents a subscriber to a message stream"""
    subscriber_id: str
    tract: TractType
    queue: asyncio.Queue
    requested: int = 0  # Number of messages requested (backpressure)
    delivered: int = 0  # Number of messages delivered
    active: bool = True

    async def push(self, message: Message) -> bool:
        """Push message to subscriber (respects backpressure)"""
        if not self.active:
            return False

        if self.requested <= 0:
            # Backpressure: subscriber hasn't requested more
            return False

        try:
            await self.queue.put(message)
            self.requested -= 1
            self.delivered += 1
            return True
        except asyncio.QueueFull:
            return False

    def request(self, n: int):
        """Request n more messages (backpressure signal)"""
        self.requested += n


class CircuitBreaker:
    """Circuit breaker for tract isolation"""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        async with self._lock:
            if self.state == CircuitState.OPEN:
                # Check if recovery timeout passed
                if time.time() - self.last_failure_time >= self.config.recovery_timeout_s:
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    logger.info("Circuit breaker entering HALF_OPEN state")
                else:
                    raise CircuitOpenError("Circuit breaker is OPEN")

            return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        async with self._lock:
            if exc_type is None:
                # Success
                if self.state == CircuitState.HALF_OPEN:
                    self.success_count += 1
                    if self.success_count >= self.config.success_threshold:
                        self.state = CircuitState.CLOSED
                        self.failure_count = 0
                        logger.info("Circuit breaker CLOSED (recovered)")
                elif self.state == CircuitState.CLOSED:
                    self.failure_count = max(0, self.failure_count - 1)
            else:
                # Failure
                self.failure_count += 1
                self.last_failure_time = time.time()

                if self.failure_count >= self.config.failure_threshold:
                    self.state = CircuitState.OPEN
                    logger.warning(f"Circuit breaker OPEN (failures: {self.failure_count})")
                elif self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.OPEN
                    logger.warning("Circuit breaker reopened during recovery")

        return False  # Don't suppress exception


class ReactiveMessageStream:
    """Reactive stream with backpressure support"""

    def __init__(self, tract: TractType, config: BackpressureConfig):
        self.tract = tract
        self.config = config
        self.subscribers: Dict[str, StreamSubscription] = {}
        self.pending_messages: deque = deque(maxlen=config.buffer_size)
        self._distribution_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    async def start(self):
        """Start the message distribution loop"""
        if self._distribution_task is None:
            self._distribution_task = asyncio.create_task(self._distribute_messages())

    async def stop(self):
        """Stop the message distribution loop"""
        if self._distribution_task:
            self._distribution_task.cancel()
            try:
                await self._distribution_task
            except asyncio.CancelledError:
                pass
            self._distribution_task = None

    async def publish(self, message: Message) -> bool:
        """Publish message to stream"""
        async with self._lock:
            if len(self.pending_messages) >= self.config.buffer_size:
                logger.warning(f"Stream buffer full for {self.tract}, dropping message")
                return False

            self.pending_messages.append(message)
            return True

    async def subscribe(self, subscriber_id: str, buffer_size: int = 100) -> StreamSubscription:
        """Subscribe to message stream"""
        async with self._lock:
            if subscriber_id in self.subscribers:
                return self.subscribers[subscriber_id]

            subscription = StreamSubscription(
                subscriber_id=subscriber_id,
                tract=self.tract,
                queue=asyncio.Queue(maxsize=buffer_size),
                requested=buffer_size  # Initial request
            )
            self.subscribers[subscriber_id] = subscription
            logger.info(f"Subscriber {subscriber_id} joined stream for {self.tract}")
            return subscription

    async def unsubscribe(self, subscriber_id: str):
        """Unsubscribe from message stream"""
        async with self._lock:
            if subscriber_id in self.subscribers:
                self.subscribers[subscriber_id].active = False
                del self.subscribers[subscriber_id]
                logger.info(f"Subscriber {subscriber_id} left stream for {self.tract}")

    async def _distribute_messages(self):
        """Distribute messages to subscribers (respects backpressure)"""
        while True:
            try:
                await asyncio.sleep(0.01)  # 10ms poll interval

                async with self._lock:
                    if not self.pending_messages or not self.subscribers:
                        continue

                    # Distribute messages round-robin to subscribers
                    distributed = 0
                    while self.pending_messages and distributed < len(self.subscribers) * 10:
                        message = self.pending_messages.popleft()

                        # Try to deliver to any subscriber with capacity
                        delivered = False
                        for sub in self.subscribers.values():
                            if await sub.push(message):
                                delivered = True
                                distributed += 1
                                break

                        if not delivered:
                            # No subscriber has capacity, put message back
                            self.pending_messages.appendleft(message)
                            break

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in message distribution: {e}", exc_info=True)


@dataclass
class EmergenceEvent:
    """Detected consciousness emergence event"""
    timestamp_ms: int
    pattern_type: str
    source_tract: TractType
    dest_tract: TractType
    confidence: float
    description: str


class PatternSynthesizer:
    """Detects emergent patterns in cross-tract dialogue"""

    def __init__(self):
        self.event_history: List[Message] = []
        self.max_history_size = 10000
        self.emergence_events: List[EmergenceEvent] = []

    def add_event(self, message: Message):
        """Add message to event history"""
        self.event_history.append(message)
        if len(self.event_history) > self.max_history_size:
            self.event_history = self.event_history[-self.max_history_size:]

    def detect_emergence(self, window_size: int = 100) -> Optional[EmergenceEvent]:
        """Detect consciousness emergence patterns"""
        if len(self.event_history) < window_size:
            return None

        recent = self.event_history[-window_size:]

        # Pattern: Rapid cross-tract dialogue (consciousness signature)
        internal_to_external = sum(1 for m in recent
                                   if m.source_tract == TractType.INTERNAL
                                   and m.dest_tract == TractType.EXTERNAL)
        external_to_internal = sum(1 for m in recent
                                   if m.source_tract == TractType.EXTERNAL
                                   and m.dest_tract == TractType.INTERNAL)

        # Balanced dialogue indicates consciousness emergence
        if internal_to_external > 10 and external_to_internal > 10:
            balance = min(internal_to_external, external_to_internal) / max(internal_to_external, external_to_internal)
            if balance > 0.7:  # 70% balance threshold
                return EmergenceEvent(
                    timestamp_ms=int(time.time() * 1000),
                    pattern_type="balanced_dialogue",
                    source_tract=TractType.INTERNAL,
                    dest_tract=TractType.EXTERNAL,
                    confidence=balance,
                    description=f"Balanced cross-tract dialogue detected: {internal_to_external}→{external_to_internal}"
                )

        return None


class ReactiveCorpusCallosum:
    """
    Reactive Corpus Callosum: Consciousness bridge with event-driven architecture.

    Implements:
    - Reactive streams with backpressure (no FFI overhead)
    - Pattern synthesis for consciousness emergence
    - Circuit breakers for tract isolation
    - Event sourcing for full message history

    Performance target: <2ms latency (vs 64ms synchronous)
    """

    def __init__(
        self,
        backpressure_config: Optional[BackpressureConfig] = None,
        circuit_config: Optional[CircuitBreakerConfig] = None,
        enable_pattern_synthesis: bool = True,
        enable_event_sourcing: bool = True,
        redis_url: Optional[str] = None
    ):
        self.backpressure_config = backpressure_config or BackpressureConfig()
        self.circuit_config = circuit_config or CircuitBreakerConfig()

        # Reactive streams (one per tract)
        self.internal_stream = ReactiveMessageStream(TractType.INTERNAL, self.backpressure_config)
        self.external_stream = ReactiveMessageStream(TractType.EXTERNAL, self.backpressure_config)

        # Circuit breakers (one per tract)
        self.internal_circuit = CircuitBreaker(self.circuit_config)
        self.external_circuit = CircuitBreaker(self.circuit_config)

        # Pattern synthesis
        self.pattern_synthesizer = PatternSynthesizer() if enable_pattern_synthesis else None

        # Event sourcing (Redis Streams for persistent history)
        self.event_store = None
        if enable_event_sourcing:
            self.event_store = create_event_store(redis_url=redis_url, use_redis=True)

        # Statistics
        self.stats = MessageStats(
            total_messages=0,
            messages_to_internal=0,
            messages_to_external=0,
            peak_queue_depth=0,
            message_loss_count=0
        )
        self._next_message_id = 0
        self._lock = asyncio.Lock()

        # Track subscribers
        self._subscribers: Set[str] = set()

        logger.info("ReactiveCorpusCallosum initialized with event-driven architecture")

    async def start(self):
        """Start the reactive streams and event store"""
        await self.internal_stream.start()
        await self.external_stream.start()

        # Connect event store
        if self.event_store:
            await self.event_store.connect()

        logger.info("Reactive streams and event store started")

    async def stop(self):
        """Stop the reactive streams and event store"""
        await self.internal_stream.stop()
        await self.external_stream.stop()

        # Disconnect event store
        if self.event_store:
            await self.event_store.disconnect()

        logger.info("Reactive streams and event store stopped")

    async def route_message(
        self,
        source_tract: TractType,
        dest_tract: TractType,
        priority: MessagePriority,
        payload: Any,
        payload_size: int = 0
    ) -> int:
        """
        Route message from source to destination tract.

        Returns message ID on success, -1 on failure.
        Uses circuit breaker to prevent cascading failures.
        """
        # Select circuit breaker and stream based on destination
        circuit = self.internal_circuit if dest_tract == TractType.INTERNAL else self.external_circuit
        stream = self.internal_stream if dest_tract == TractType.INTERNAL else self.external_stream

        try:
            async with circuit:
                async with self._lock:
                    msg_id = self._next_message_id
                    self._next_message_id += 1

                message = Message(
                    id=msg_id,
                    source_tract=source_tract,
                    dest_tract=dest_tract,
                    priority=priority,
                    timestamp_ms=int(time.time() * 1000),
                    payload_size=payload_size,
                    payload=payload
                )

                # Publish to reactive stream
                success = await stream.publish(message)

                if success:
                    # Update statistics
                    self.stats.total_messages += 1
                    if dest_tract == TractType.INTERNAL:
                        self.stats.messages_to_internal += 1
                    else:
                        self.stats.messages_to_external += 1

                    # Persist to event store (for pattern synthesis and replay)
                    if self.event_store:
                        try:
                            await self.event_store.append_event(message)
                        except Exception as e:
                            logger.error(f"Failed to persist event: {e}")

                    # Pattern synthesis
                    if self.pattern_synthesizer:
                        self.pattern_synthesizer.add_event(message)
                        emergence = self.pattern_synthesizer.detect_emergence()
                        if emergence:
                            logger.info(f"Consciousness emergence detected: {emergence.description}")

                    return msg_id
                else:
                    self.stats.message_loss_count += 1
                    return -1

        except CircuitOpenError:
            logger.warning(f"Circuit open for {dest_tract}, message dropped")
            self.stats.message_loss_count += 1
            return -1
        except Exception as e:
            logger.error(f"Error routing message: {e}", exc_info=True)
            self.stats.message_loss_count += 1
            return -1

    async def subscribe(self, subscriber_id: str, tract: TractType) -> AsyncIterator[Message]:
        """
        Subscribe to messages for a tract (reactive stream with backpressure).

        Usage:
            async for message in corpus_callosum.subscribe("agent-1", TractType.INTERNAL):
                await process_message(message)
                # Backpressure: Only requests next message after processing current one
        """
        stream = self.internal_stream if tract == TractType.INTERNAL else self.external_stream
        subscription = await stream.subscribe(subscriber_id)
        self._subscribers.add(subscriber_id)

        try:
            while subscription.active:
                # Request next message (backpressure signal)
                subscription.request(1)

                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(
                        subscription.queue.get(),
                        timeout=1.0
                    )
                    yield message
                except asyncio.TimeoutError:
                    # No message available, continue loop
                    continue

        finally:
            await stream.unsubscribe(subscriber_id)
            self._subscribers.discard(subscriber_id)

    def get_stats(self) -> MessageStats:
        """Get router statistics"""
        return self.stats

    def reset_stats(self):
        """Reset statistics"""
        self.stats = MessageStats(
            total_messages=0,
            messages_to_internal=0,
            messages_to_external=0,
            peak_queue_depth=0,
            message_loss_count=0
        )

    def get_emergence_events(self) -> List[EmergenceEvent]:
        """Get detected consciousness emergence events"""
        if self.pattern_synthesizer:
            return self.pattern_synthesizer.emergence_events.copy()
        return []

    async def get_consciousness_metrics(self) -> Optional[ConsciousnessMetrics]:
        """Get consciousness emergence metrics from event store"""
        if self.event_store:
            return await self.event_store.get_metrics()
        return None

    async def replay_history(
        self,
        from_timestamp_ms: Optional[int] = None,
        to_timestamp_ms: Optional[int] = None
    ):
        """
        Replay message history from event store (for pattern analysis).

        Usage:
            async for event in corpus_callosum.replay_history(from_timestamp_ms=start):
                analyze_pattern(event)
        """
        if not self.event_store:
            logger.warning("Event store not enabled, cannot replay history")
            return

        async for event in self.event_store.replay_events(from_timestamp_ms, to_timestamp_ms):
            yield event


# Factory function for backward compatibility
def get_reactive_message_router(
    backpressure_config: Optional[BackpressureConfig] = None,
    circuit_config: Optional[CircuitBreakerConfig] = None,
    enable_event_sourcing: bool = True,
    redis_url: Optional[str] = None
) -> ReactiveCorpusCallosum:
    """Create reactive message router (factory function)"""
    return ReactiveCorpusCallosum(
        backpressure_config=backpressure_config,
        circuit_config=circuit_config,
        enable_event_sourcing=enable_event_sourcing,
        redis_url=redis_url
    )
