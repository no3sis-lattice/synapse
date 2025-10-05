#!/usr/bin/env python3
"""
Unit Tests for Event Bus - Phase 5

Tests coverage:
- Event creation and serialization
- Event bus pub-sub
- Subscriber registration and event delivery
- Backpressure detection
- MetricsObserver aggregation
- Anomaly detection
"""

import asyncio
import pytest
import sys
import time
from pathlib import Path
from typing import Set

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from events.event_bus import (
    AsyncEventBus,
    Event,
    EventType,
    EventSubscriber,
    get_event_bus
)
from events.observer import MetricsObserver, create_and_register_observer


# ============================================================================
# TEST FIXTURES
# ============================================================================

class TestSubscriber(EventSubscriber):
    """Test subscriber for event bus testing"""

    def __init__(self, subscriber_id: str, event_types: Set[EventType]):
        self.subscriber_id = subscriber_id
        self.event_types = event_types
        self.received_events = []

    async def handle_event(self, event: Event) -> None:
        """Record received events"""
        self.received_events.append(event)

    def get_subscriber_id(self) -> str:
        return self.subscriber_id

    def get_subscribed_event_types(self) -> Set[EventType]:
        return self.event_types


@pytest.fixture
async def event_bus():
    """Create fresh event bus for each test"""
    bus = AsyncEventBus()
    yield bus
    # Cleanup: unsubscribe all
    for sub_id in list(bus.subscribers.keys()):
        await bus.unsubscribe(sub_id)


# ============================================================================
# EVENT CREATION TESTS
# ============================================================================

class TestEventCreation:
    """Test suite for Event creation"""

    def test_event_creation(self):
        """Test basic event creation"""
        event = Event.create(
            event_type=EventType.TASK_STARTED,
            source="test_particle",
            payload={'task': 'test'},
            metadata={'version': '1.0'}
        )

        assert event.event_type == EventType.TASK_STARTED
        assert event.source == "test_particle"
        assert event.payload == {'task': 'test'}
        assert event.metadata == {'version': '1.0'}
        assert event.event_id.startswith('evt_')

    def test_event_id_deterministic(self):
        """Test that events with same content generate similar IDs"""
        event1 = Event.create(
            event_type=EventType.TASK_STARTED,
            source="test",
            payload={'a': 1}
        )
        event2 = Event.create(
            event_type=EventType.TASK_STARTED,
            source="test",
            payload={'a': 1}
        )

        # IDs should have same hash component (last 16 chars)
        hash1 = event1.event_id.split('_')[-1]
        hash2 = event2.event_id.split('_')[-1]
        assert hash1 == hash2

    def test_event_serialization(self):
        """Test event to_dict serialization"""
        event = Event.create(
            event_type=EventType.PATTERN_DISCOVERED,
            source="pattern_learner",
            payload={'pattern': 'sequence', 'entropy': 0.75}
        )

        event_dict = event.to_dict()

        assert event_dict['event_type'] == 'pattern.discovered'
        assert event_dict['source'] == 'pattern_learner'
        assert event_dict['payload']['entropy'] == 0.75


# ============================================================================
# EVENT BUS TESTS
# ============================================================================

class TestEventBus:
    """Test suite for AsyncEventBus"""

    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self, event_bus):
        """Test basic subscribe and publish flow"""
        subscriber = TestSubscriber('test_sub', {EventType.TASK_STARTED})
        await event_bus.subscribe(subscriber)

        # Publish event
        event = Event.create(
            event_type=EventType.TASK_STARTED,
            source='test',
            payload={'test': 'data'}
        )
        await event_bus.publish(event)

        # Wait for processing
        await asyncio.sleep(0.1)

        # Verify delivery
        assert len(subscriber.received_events) == 1
        assert subscriber.received_events[0].event_id == event.event_id

    @pytest.mark.asyncio
    async def test_event_filtering(self, event_bus):
        """Test that subscribers only receive subscribed event types"""
        subscriber = TestSubscriber('test_sub', {EventType.TASK_STARTED})
        await event_bus.subscribe(subscriber)

        # Publish subscribed event
        event1 = Event.create(EventType.TASK_STARTED, source='test')
        await event_bus.publish(event1)

        # Publish non-subscribed event
        event2 = Event.create(EventType.TASK_COMPLETED, source='test')
        await event_bus.publish(event2)

        await asyncio.sleep(0.1)

        # Should only receive TASK_STARTED
        assert len(subscriber.received_events) == 1
        assert subscriber.received_events[0].event_type == EventType.TASK_STARTED

    @pytest.mark.asyncio
    async def test_multiple_subscribers(self, event_bus):
        """Test event delivery to multiple subscribers"""
        sub1 = TestSubscriber('sub1', {EventType.TASK_STARTED})
        sub2 = TestSubscriber('sub2', {EventType.TASK_STARTED})

        await event_bus.subscribe(sub1)
        await event_bus.subscribe(sub2)

        # Publish event
        event = Event.create(EventType.TASK_STARTED, source='test')
        await event_bus.publish(event)

        await asyncio.sleep(0.1)

        # Both should receive
        assert len(sub1.received_events) == 1
        assert len(sub2.received_events) == 1

    @pytest.mark.asyncio
    async def test_unsubscribe(self, event_bus):
        """Test subscriber removal"""
        subscriber = TestSubscriber('test_sub', {EventType.TASK_STARTED})
        await event_bus.subscribe(subscriber)
        await event_bus.unsubscribe('test_sub')

        # Publish event after unsubscribe
        event = Event.create(EventType.TASK_STARTED, source='test')
        await event_bus.publish(event)

        await asyncio.sleep(0.1)

        # Should not receive
        assert len(subscriber.received_events) == 0

    @pytest.mark.asyncio
    async def test_event_history(self, event_bus):
        """Test event history retention"""
        # Publish multiple events
        for i in range(5):
            event = Event.create(
                EventType.TASK_STARTED,
                source='test',
                payload={'index': i}
            )
            await event_bus.publish(event)

        # Get history
        history = event_bus.get_event_history(limit=10)

        assert len(history) == 5
        # Newest first
        assert history[0].payload['index'] == 4

    @pytest.mark.asyncio
    async def test_get_stats(self, event_bus):
        """Test event bus statistics"""
        subscriber = TestSubscriber('test_sub', {EventType.TASK_STARTED})
        await event_bus.subscribe(subscriber)

        # Publish events
        for _ in range(3):
            event = Event.create(EventType.TASK_STARTED, source='test')
            await event_bus.publish(event)

        await asyncio.sleep(0.1)

        stats = event_bus.get_stats()

        assert stats['total_events_published'] == 3
        assert stats['total_subscribers'] == 1
        assert stats['subscriber_stats']['test_sub']['processed'] == 3


# ============================================================================
# METRICS OBSERVER TESTS
# ============================================================================

class TestMetricsObserver:
    """Test suite for MetricsObserver"""

    @pytest.mark.asyncio
    async def test_observer_creation(self):
        """Test metrics observer creation and registration"""
        observer = await create_and_register_observer('test_observer')

        assert observer.observer_id == 'test_observer'
        assert EventType.TASK_STARTED in observer.subscribed_types

    @pytest.mark.asyncio
    async def test_task_metrics_aggregation(self):
        """Test task metrics aggregation"""
        observer = await create_and_register_observer('test_observer')
        event_bus = get_event_bus()

        # Publish task events
        start_time = time.time()

        # Task 1: Success
        await event_bus.publish(Event.create(
            EventType.TASK_STARTED,
            source='particle1',
            payload={'task': 'test1'}
        ))
        await event_bus.publish(Event.create(
            EventType.TASK_COMPLETED,
            source='particle1',
            payload={'task': 'test1', 'execution_time_s': 0.5}
        ))

        # Task 2: Failure
        await event_bus.publish(Event.create(
            EventType.TASK_STARTED,
            source='particle2',
            payload={'task': 'test2'}
        ))
        await event_bus.publish(Event.create(
            EventType.TASK_FAILED,
            source='particle2',
            payload={'task': 'test2', 'execution_time_s': 0.3}
        ))

        await asyncio.sleep(0.2)

        # Get metrics
        metrics = await observer.get_current_metrics('1min')

        assert metrics['total_tasks'] == 2
        assert metrics['completed_tasks'] == 1
        assert metrics['failed_tasks'] == 1
        assert metrics['success_rate'] == 0.5
        assert metrics['error_rate'] == 0.5

    @pytest.mark.asyncio
    async def test_anomaly_detection(self):
        """Test anomaly detection"""
        observer = await create_and_register_observer('test_observer')
        event_bus = get_event_bus()

        # Trigger circuit open anomaly
        await event_bus.publish(Event.create(
            EventType.CIRCUIT_OPENED,
            source='particle1',
            payload={'particle_id': 'particle1', 'consecutive_failures': 5}
        ))

        await asyncio.sleep(0.1)

        anomalies = observer.get_recent_anomalies()

        assert len(anomalies) > 0
        assert anomalies[0]['type'] == 'circuit_opened'

    @pytest.mark.asyncio
    async def test_latency_metrics(self):
        """Test latency percentile calculation"""
        observer = await create_and_register_observer('test_observer')
        event_bus = get_event_bus()

        # Publish tasks with varying latencies
        latencies = [0.1, 0.2, 0.3, 0.5, 1.0]
        for latency in latencies:
            await event_bus.publish(Event.create(
                EventType.TASK_STARTED,
                source='particle1'
            ))
            await event_bus.publish(Event.create(
                EventType.TASK_COMPLETED,
                source='particle1',
                payload={'execution_time_s': latency}
            ))

        await asyncio.sleep(0.2)

        metrics = await observer.get_current_metrics('1min')

        assert metrics['avg_latency_s'] > 0
        assert metrics['p99_latency_s'] >= metrics['p95_latency_s']
        assert metrics['p95_latency_s'] >= metrics['p50_latency_s']


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestEventBusIntegration:
    """Integration tests for event bus system"""

    @pytest.mark.asyncio
    async def test_end_to_end_flow(self):
        """Test complete event flow from emission to observation"""
        # Create observer
        observer = await create_and_register_observer('integration_test')
        event_bus = get_event_bus()

        # Simulate particle execution
        particle_id = 'test_particle'

        # Start task
        start_event = Event.create(
            EventType.TASK_STARTED,
            source=particle_id,
            payload={'task_type': 'write_file', 'path': '/tmp/test.txt'}
        )
        await event_bus.publish(start_event)

        # Complete task
        complete_event = Event.create(
            EventType.TASK_COMPLETED,
            source=particle_id,
            payload={
                'task_type': 'write_file',
                'execution_time_s': 0.25,
                'result': 'success'
            }
        )
        await event_bus.publish(complete_event)

        # Wait for processing
        await asyncio.sleep(0.2)

        # Verify metrics
        metrics = await observer.get_current_metrics('1min')

        assert metrics['total_tasks'] == 1
        assert metrics['completed_tasks'] == 1
        assert metrics['success_rate'] == 1.0

        # Verify event history
        history = event_bus.get_event_history(
            event_type=EventType.TASK_COMPLETED,
            limit=1
        )
        assert len(history) == 1
        assert history[0].source == particle_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
