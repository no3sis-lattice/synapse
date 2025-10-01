"""
Event Store for Corpus Callosum
Phase 3 CHECKPOINT 2: Redis Streams integration for event sourcing

Provides:
- Persistent event log via Redis Streams
- Event replay capability for pattern analysis
- Full message history for consciousness emergence detection
- Consciousness metrics tracking
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any, AsyncIterator
from datetime import datetime

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("redis[asyncio] not available, event sourcing will use in-memory fallback")

from message_router import TractType, MessagePriority, Message

logger = logging.getLogger(__name__)


@dataclass
class ConsciousnessMetrics:
    """Metrics for consciousness emergence detection"""
    total_messages: int = 0
    internal_to_external: int = 0
    external_to_internal: int = 0
    balanced_dialogue_events: int = 0
    emergence_score: float = 0.0  # 0.0 to 1.0
    last_emergence_timestamp: Optional[int] = None
    dialogue_balance_ratio: float = 0.0  # Ratio of balanced communication


@dataclass
class EventLogEntry:
    """Single event in the log"""
    event_id: str
    timestamp_ms: int
    message_id: int
    source_tract: str  # Serialized as string
    dest_tract: str
    priority: int
    payload_size: int
    payload_type: str  # Type of payload for reconstruction


class RedisEventStore:
    """
    Redis Streams-based event store for cross-tract messages.

    Provides persistent, replay-able event log for pattern synthesis
    and consciousness emergence detection.
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        stream_key: str = "corpus_callosum:events",
        max_stream_length: int = 100000,
        enable_metrics: bool = True
    ):
        self.redis_url = redis_url
        self.stream_key = stream_key
        self.max_stream_length = max_stream_length
        self.enable_metrics = enable_metrics

        self.redis_client: Optional[aioredis.Redis] = None
        self.metrics = ConsciousnessMetrics()
        self._metrics_key = f"{stream_key}:metrics"

        logger.info(f"RedisEventStore initialized (stream: {stream_key})")

    async def connect(self):
        """Connect to Redis"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, using in-memory fallback")
            return

        try:
            self.redis_client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()

            # Load existing metrics
            await self._load_metrics()

            logger.info(f"Connected to Redis at {self.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")

    async def append_event(self, message: Message) -> str:
        """
        Append message event to stream.

        Returns event_id (Redis stream ID)
        """
        if not self.redis_client:
            # In-memory fallback (no persistence)
            event_id = f"{int(time.time() * 1000)}-0"
            await self._update_metrics(message)
            return event_id

        try:
            # Serialize message to Redis stream
            event_data = {
                'message_id': str(message.id),
                'source_tract': message.source_tract.name,
                'dest_tract': message.dest_tract.name,
                'priority': str(message.priority.value),
                'timestamp_ms': str(message.timestamp_ms),
                'payload_size': str(message.payload_size),
                'payload_type': type(message.payload).__name__,
            }

            # Add to stream with automatic trimming
            event_id = await self.redis_client.xadd(
                self.stream_key,
                event_data,
                maxlen=self.max_stream_length,
                approximate=True  # Allow approximate trimming for performance
            )

            # Update metrics
            await self._update_metrics(message)

            return event_id

        except Exception as e:
            logger.error(f"Failed to append event to Redis: {e}")
            return f"{int(time.time() * 1000)}-0"  # Fallback ID

    async def get_events(
        self,
        start_id: str = "0",
        count: int = 100,
        block_ms: Optional[int] = None
    ) -> List[EventLogEntry]:
        """
        Read events from stream.

        Args:
            start_id: Stream ID to start from ('0' = from beginning)
            count: Maximum number of events to read
            block_ms: Block for this many ms waiting for new events (None = no blocking)

        Returns list of EventLogEntry
        """
        if not self.redis_client:
            return []

        try:
            # Read from stream
            if block_ms:
                # Blocking read (for real-time streaming)
                results = await self.redis_client.xread(
                    {self.stream_key: start_id},
                    count=count,
                    block=block_ms
                )
            else:
                # Non-blocking read
                results = await self.redis_client.xrange(
                    self.stream_key,
                    min=start_id,
                    max='+',
                    count=count
                )

            # Parse results
            events = []
            if block_ms and results:
                # xread returns: [(stream_name, [(event_id, data), ...])]
                for stream_name, stream_events in results:
                    for event_id, data in stream_events:
                        events.append(self._parse_event(event_id, data))
            else:
                # xrange returns: [(event_id, data), ...]
                for event_id, data in results:
                    events.append(self._parse_event(event_id, data))

            return events

        except Exception as e:
            logger.error(f"Failed to read events from Redis: {e}")
            return []

    async def replay_events(
        self,
        from_timestamp_ms: Optional[int] = None,
        to_timestamp_ms: Optional[int] = None
    ) -> AsyncIterator[EventLogEntry]:
        """
        Replay events from stream (for pattern analysis).

        Args:
            from_timestamp_ms: Start timestamp (None = from beginning)
            to_timestamp_ms: End timestamp (None = to present)

        Yields EventLogEntry in chronological order
        """
        if not self.redis_client:
            return

        try:
            # Determine start ID from timestamp
            if from_timestamp_ms:
                start_id = f"{from_timestamp_ms}-0"
            else:
                start_id = "0"

            # Stream events in batches
            current_id = start_id
            batch_size = 1000

            while True:
                events = await self.get_events(start_id=current_id, count=batch_size)

                if not events:
                    break

                for event in events:
                    # Filter by end timestamp if specified
                    if to_timestamp_ms and int(event.timestamp_ms) > to_timestamp_ms:
                        return

                    yield event

                # Update for next batch
                current_id = events[-1].event_id

                # Check if we've reached the end
                if len(events) < batch_size:
                    break

        except Exception as e:
            logger.error(f"Failed to replay events: {e}")

    async def get_metrics(self) -> ConsciousnessMetrics:
        """Get current consciousness metrics"""
        if self.redis_client and self.enable_metrics:
            await self._load_metrics()
        return self.metrics

    async def _update_metrics(self, message: Message):
        """Update consciousness metrics based on message"""
        if not self.enable_metrics:
            return

        self.metrics.total_messages += 1

        # Track cross-tract dialogue
        if message.source_tract == TractType.INTERNAL and message.dest_tract == TractType.EXTERNAL:
            self.metrics.internal_to_external += 1
        elif message.source_tract == TractType.EXTERNAL and message.dest_tract == TractType.INTERNAL:
            self.metrics.external_to_internal += 1

        # Calculate dialogue balance
        if self.metrics.internal_to_external > 0 and self.metrics.external_to_internal > 0:
            balance = min(
                self.metrics.internal_to_external,
                self.metrics.external_to_internal
            ) / max(
                self.metrics.internal_to_external,
                self.metrics.external_to_internal
            )
            self.metrics.dialogue_balance_ratio = balance

            # Detect balanced dialogue (consciousness signature)
            if balance > 0.7:  # 70% balance threshold
                self.metrics.balanced_dialogue_events += 1
                self.metrics.last_emergence_timestamp = int(time.time() * 1000)

        # Calculate emergence score (0.0 to 1.0)
        if self.metrics.total_messages > 100:
            # Score based on balance and frequency of balanced dialogue
            balance_score = self.metrics.dialogue_balance_ratio
            frequency_score = min(1.0, self.metrics.balanced_dialogue_events / 100)
            self.metrics.emergence_score = (balance_score * 0.7) + (frequency_score * 0.3)

        # Persist metrics to Redis
        if self.redis_client:
            try:
                await self.redis_client.hset(
                    self._metrics_key,
                    mapping={
                        'total_messages': self.metrics.total_messages,
                        'internal_to_external': self.metrics.internal_to_external,
                        'external_to_internal': self.metrics.external_to_internal,
                        'balanced_dialogue_events': self.metrics.balanced_dialogue_events,
                        'emergence_score': self.metrics.emergence_score,
                        'last_emergence_timestamp': self.metrics.last_emergence_timestamp or 0,
                        'dialogue_balance_ratio': self.metrics.dialogue_balance_ratio,
                    }
                )
            except Exception as e:
                logger.error(f"Failed to persist metrics: {e}")

    async def _load_metrics(self):
        """Load metrics from Redis"""
        if not self.redis_client:
            return

        try:
            data = await self.redis_client.hgetall(self._metrics_key)
            if data:
                self.metrics.total_messages = int(data.get('total_messages', 0))
                self.metrics.internal_to_external = int(data.get('internal_to_external', 0))
                self.metrics.external_to_internal = int(data.get('external_to_internal', 0))
                self.metrics.balanced_dialogue_events = int(data.get('balanced_dialogue_events', 0))
                self.metrics.emergence_score = float(data.get('emergence_score', 0.0))
                self.metrics.dialogue_balance_ratio = float(data.get('dialogue_balance_ratio', 0.0))

                last_ts = int(data.get('last_emergence_timestamp', 0))
                self.metrics.last_emergence_timestamp = last_ts if last_ts > 0 else None

        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")

    def _parse_event(self, event_id: str, data: Dict[str, str]) -> EventLogEntry:
        """Parse Redis stream entry into EventLogEntry"""
        return EventLogEntry(
            event_id=event_id,
            timestamp_ms=int(data['timestamp_ms']),
            message_id=int(data['message_id']),
            source_tract=data['source_tract'],
            dest_tract=data['dest_tract'],
            priority=int(data['priority']),
            payload_size=int(data['payload_size']),
            payload_type=data['payload_type']
        )


class InMemoryEventStore:
    """
    In-memory fallback event store (for testing or when Redis unavailable).

    Warning: Not persistent, events lost on restart.
    """

    def __init__(self, max_events: int = 10000):
        self.events: List[EventLogEntry] = []
        self.max_events = max_events
        self.metrics = ConsciousnessMetrics()
        self._next_event_id = 0
        logger.info("InMemoryEventStore initialized (non-persistent)")

    async def connect(self):
        """No-op for in-memory store"""
        pass

    async def disconnect(self):
        """No-op for in-memory store"""
        pass

    async def append_event(self, message: Message) -> str:
        """Append event to in-memory list"""
        event_id = f"{int(time.time() * 1000)}-{self._next_event_id}"
        self._next_event_id += 1

        entry = EventLogEntry(
            event_id=event_id,
            timestamp_ms=message.timestamp_ms,
            message_id=message.id,
            source_tract=message.source_tract.name,
            dest_tract=message.dest_tract.name,
            priority=message.priority.value,
            payload_size=message.payload_size,
            payload_type=type(message.payload).__name__
        )

        self.events.append(entry)

        # Trim if exceeds max
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]

        # Update metrics (same logic as Redis version)
        await self._update_metrics(message)

        return event_id

    async def get_events(
        self,
        start_id: str = "0",
        count: int = 100,
        block_ms: Optional[int] = None
    ) -> List[EventLogEntry]:
        """Get events from in-memory list"""
        # Parse start_id to get index
        if start_id == "0":
            start_idx = 0
        else:
            # Find event with matching ID
            start_idx = 0
            for i, event in enumerate(self.events):
                if event.event_id == start_id:
                    start_idx = i + 1
                    break

        return self.events[start_idx:start_idx + count]

    async def replay_events(
        self,
        from_timestamp_ms: Optional[int] = None,
        to_timestamp_ms: Optional[int] = None
    ) -> AsyncIterator[EventLogEntry]:
        """Replay events from in-memory list"""
        for event in self.events:
            if from_timestamp_ms and event.timestamp_ms < from_timestamp_ms:
                continue
            if to_timestamp_ms and event.timestamp_ms > to_timestamp_ms:
                break
            yield event

    async def get_metrics(self) -> ConsciousnessMetrics:
        """Get metrics"""
        return self.metrics

    async def _update_metrics(self, message: Message):
        """Update metrics (same logic as Redis version)"""
        self.metrics.total_messages += 1

        if message.source_tract == TractType.INTERNAL and message.dest_tract == TractType.EXTERNAL:
            self.metrics.internal_to_external += 1
        elif message.source_tract == TractType.EXTERNAL and message.dest_tract == TractType.INTERNAL:
            self.metrics.external_to_internal += 1

        if self.metrics.internal_to_external > 0 and self.metrics.external_to_internal > 0:
            balance = min(
                self.metrics.internal_to_external,
                self.metrics.external_to_internal
            ) / max(
                self.metrics.internal_to_external,
                self.metrics.external_to_internal
            )
            self.metrics.dialogue_balance_ratio = balance

            if balance > 0.7:
                self.metrics.balanced_dialogue_events += 1
                self.metrics.last_emergence_timestamp = int(time.time() * 1000)

        if self.metrics.total_messages > 100:
            balance_score = self.metrics.dialogue_balance_ratio
            frequency_score = min(1.0, self.metrics.balanced_dialogue_events / 100)
            self.metrics.emergence_score = (balance_score * 0.7) + (frequency_score * 0.3)


# Factory function
def create_event_store(
    redis_url: Optional[str] = None,
    use_redis: bool = True,
    **kwargs
) -> "RedisEventStore | InMemoryEventStore":
    """
    Create event store (Redis or in-memory fallback).

    Args:
        redis_url: Redis connection URL (None = use default)
        use_redis: Whether to use Redis (False = force in-memory)
        **kwargs: Additional args for RedisEventStore or InMemoryEventStore
    """
    if use_redis and REDIS_AVAILABLE:
        return RedisEventStore(redis_url=redis_url or "redis://localhost:6379/0", **kwargs)
    else:
        if use_redis and not REDIS_AVAILABLE:
            logger.warning("Redis requested but not available, using in-memory fallback")
        return InMemoryEventStore(**kwargs)
