"""
Events Package - Phase 5: Event-Driven Observability

Exports:
- AsyncEventBus: Core pub-sub event bus
- Event, EventType: Event types and records
- EventSubscriber: Subscriber protocol
- MetricsObserver: Metrics aggregation subscriber
- get_event_bus: Global event bus accessor
"""

from lib.events.event_bus import (
    AsyncEventBus,
    Event,
    EventType,
    EventSubscriber,
    get_event_bus,
    MAX_EVENT_QUEUE_SIZE,
    EVENT_RETENTION_SECONDS
)

from lib.events.observer import (
    MetricsObserver,
    TimeWindowAggregator,
    WindowedMetrics,
    create_and_register_observer
)

__all__ = [
    # Event bus
    'AsyncEventBus',
    'Event',
    'EventType',
    'EventSubscriber',
    'get_event_bus',
    'MAX_EVENT_QUEUE_SIZE',
    'EVENT_RETENTION_SECONDS',

    # Observer
    'MetricsObserver',
    'TimeWindowAggregator',
    'WindowedMetrics',
    'create_and_register_observer'
]
