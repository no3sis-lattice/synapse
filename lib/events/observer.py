"""
Observer - Phase 5: Metrics Aggregation via Event Subscription

Subscribes to event bus and aggregates metrics without coupling to execution.

Pneuma Design:
- Axiom I: Compresses event streams into statistical summaries
- Axiom II: Discovers metric patterns autonomously
- Axiom III: Self-adjusts aggregation windows based on event velocity

Architecture:
- MetricsObserver: Event subscriber that aggregates metrics
- TimeWindowAggregator: Rolling time-window statistics
- PatternDetector: Discovers anomalies in metric streams
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, Set
from enum import Enum

from lib.events.event_bus import (
    Event,
    EventType,
    EventSubscriber,
    get_event_bus
)

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# Aggregation windows (seconds)
WINDOW_1MIN = 60
WINDOW_5MIN = 300
WINDOW_1HOUR = 3600

# Anomaly detection thresholds
ERROR_RATE_THRESHOLD = 0.10  # 10% error rate triggers anomaly
LATENCY_P99_THRESHOLD_S = 5.0  # P99 latency over 5s triggers anomaly
BACKPRESSURE_THRESHOLD = 0.8  # 80% queue capacity triggers anomaly

# Persistence
METRICS_STATE_DIR = Path.home() / ".synapse-system" / ".synapse" / "metrics"


# ============================================================================
# METRIC AGGREGATORS
# ============================================================================

@dataclass
class WindowedMetrics:
    """
    Metrics aggregated over a time window.

    Pneuma: Compresses event stream into statistical summary.
    """
    window_start: float
    window_end: float
    window_size_seconds: int

    # Counters
    total_events: int = 0
    events_by_type: Dict[EventType, int] = field(default_factory=lambda: defaultdict(int))

    # Task metrics
    tasks_started: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0

    # Timing metrics
    total_execution_time_s: float = 0.0
    latencies: List[float] = field(default_factory=list)

    # Pattern metrics
    patterns_discovered: int = 0
    mtf_reranks: int = 0

    # Error metrics
    circuit_opens: int = 0
    backpressure_events: int = 0

    def compute_derived_metrics(self) -> Dict[str, Any]:
        """Compute derived metrics from raw counters"""
        total_tasks = self.tasks_started
        completed_tasks = self.tasks_completed + self.tasks_failed

        # Success rate
        success_rate = 0.0
        if completed_tasks > 0:
            success_rate = self.tasks_completed / completed_tasks

        # Error rate
        error_rate = 0.0
        if completed_tasks > 0:
            error_rate = self.tasks_failed / completed_tasks

        # Latency percentiles
        p50 = p95 = p99 = 0.0
        avg_latency = 0.0
        if self.latencies:
            sorted_latencies = sorted(self.latencies)
            n = len(sorted_latencies)
            avg_latency = sum(sorted_latencies) / n
            p50 = sorted_latencies[int(n * 0.50)]
            p95 = sorted_latencies[int(n * 0.95)] if n > 1 else sorted_latencies[0]
            p99 = sorted_latencies[int(n * 0.99)] if n > 1 else sorted_latencies[0]

        # Throughput
        window_duration = self.window_end - self.window_start
        throughput = 0.0
        if window_duration > 0:
            throughput = completed_tasks / window_duration

        return {
            'success_rate': success_rate,
            'error_rate': error_rate,
            'avg_latency_s': avg_latency,
            'p50_latency_s': p50,
            'p95_latency_s': p95,
            'p99_latency_s': p99,
            'throughput_per_second': throughput,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': self.tasks_failed
        }


class TimeWindowAggregator:
    """
    Rolling time-window aggregator.

    Maintains multiple time windows (1min, 5min, 1hour) for metric rollup.
    """

    def __init__(self):
        """Initialize aggregator"""
        self.windows = {
            '1min': WindowedMetrics(
                window_start=time.time(),
                window_end=time.time(),
                window_size_seconds=WINDOW_1MIN
            ),
            '5min': WindowedMetrics(
                window_start=time.time(),
                window_end=time.time(),
                window_size_seconds=WINDOW_5MIN
            ),
            '1hour': WindowedMetrics(
                window_start=time.time(),
                window_end=time.time(),
                window_size_seconds=WINDOW_1HOUR
            )
        }
        self._lock = asyncio.Lock()

    async def add_event(self, event: Event) -> None:
        """
        Add event to all active windows.

        Args:
            event: Event to add
        """
        async with self._lock:
            current_time = event.timestamp

            for window_name, window in self.windows.items():
                # Rotate window if expired
                await self._rotate_window_if_expired(window, current_time)

                # Update window counters
                await self._update_window_counters(window, event, current_time)

    async def _rotate_window_if_expired(
        self,
        window: WindowedMetrics,
        current_time: float
    ) -> None:
        """
        Rotate window if it has expired.

        Args:
            window: Window to check
            current_time: Current timestamp
        """
        if current_time - window.window_start > window.window_size_seconds:
            window.window_start = current_time
            window.window_end = current_time
            window.total_events = 0
            window.events_by_type.clear()
            window.tasks_started = 0
            window.tasks_completed = 0
            window.tasks_failed = 0
            window.latencies.clear()
            window.patterns_discovered = 0
            window.mtf_reranks = 0
            window.circuit_opens = 0
            window.backpressure_events = 0

    async def _update_window_counters(
        self,
        window: WindowedMetrics,
        event: Event,
        current_time: float
    ) -> None:
        """
        Update window counters based on event type.

        Args:
            window: Window to update
            event: Event to process
            current_time: Current timestamp
        """
        window.window_end = current_time
        window.total_events += 1
        window.events_by_type[event.event_type] += 1

        # Type-specific aggregation
        if event.event_type == EventType.TASK_STARTED:
            window.tasks_started += 1

        elif event.event_type == EventType.TASK_COMPLETED:
            window.tasks_completed += 1
            # Extract latency if present
            if 'execution_time_s' in event.payload:
                window.latencies.append(event.payload['execution_time_s'])

        elif event.event_type == EventType.TASK_FAILED:
            window.tasks_failed += 1
            if 'execution_time_s' in event.payload:
                window.latencies.append(event.payload['execution_time_s'])

        elif event.event_type == EventType.PATTERN_DISCOVERED:
            window.patterns_discovered += 1

        elif event.event_type == EventType.MTF_RERANKED:
            window.mtf_reranks += 1

        elif event.event_type == EventType.CIRCUIT_OPENED:
            window.circuit_opens += 1

        elif event.event_type == EventType.BACKPRESSURE_DETECTED:
            window.backpressure_events += 1

    async def get_metrics(self, window_name: str = '1min') -> Dict[str, Any]:
        """
        Get aggregated metrics for a time window.

        Args:
            window_name: Window to query ('1min', '5min', '1hour')

        Returns:
            Dictionary of aggregated metrics
        """
        async with self._lock:
            if window_name not in self.windows:
                raise ValueError(f"Unknown window: {window_name}")

            window = self.windows[window_name]
            derived = window.compute_derived_metrics()

            return {
                'window': window_name,
                'window_start': window.window_start,
                'window_end': window.window_end,
                'total_events': window.total_events,
                **derived
            }


# ============================================================================
# METRICS OBSERVER
# ============================================================================

class MetricsObserver(EventSubscriber):
    """
    Observer that subscribes to events and aggregates metrics.

    Implements EventSubscriber protocol for event bus integration.

    Pneuma: Embodies the Observer pattern - consciousness emerges from
    watching execution without interfering with it.
    """

    def __init__(self, observer_id: str = "metrics_observer"):
        """
        Initialize metrics observer.

        Args:
            observer_id: Unique ID for this observer
        """
        self.observer_id = observer_id
        self.aggregator = TimeWindowAggregator()

        # Anomaly detection
        self.anomalies: Deque[Dict[str, Any]] = deque(maxlen=100)

        # Subscription configuration
        self.subscribed_types: Set[EventType] = {
            EventType.TASK_RECEIVED,
            EventType.TASK_STARTED,
            EventType.TASK_COMPLETED,
            EventType.TASK_FAILED,
            EventType.PATTERN_DISCOVERED,
            EventType.MTF_RERANKED,
            EventType.CIRCUIT_OPENED,
            EventType.BACKPRESSURE_DETECTED
        }

        logger.info(f"MetricsObserver {observer_id} initialized")

    async def handle_event(self, event: Event) -> None:
        """
        Process event and update metrics.

        Args:
            event: Event to process
        """
        # Add to aggregator
        await self.aggregator.add_event(event)

        # Detect anomalies
        await self._detect_anomalies(event)

    async def _detect_anomalies(self, event: Event) -> None:
        """
        Detect anomalies in event stream.

        Pneuma: Pattern discovery - finds unexpected behaviors autonomously.

        Args:
            event: Event that may indicate anomaly
        """
        anomaly = None

        # Check for different anomaly types
        if event.event_type == EventType.TASK_FAILED:
            anomaly = await self._check_error_rate_anomaly(event)
        elif event.event_type == EventType.TASK_COMPLETED:
            anomaly = await self._check_latency_anomaly(event)
        elif event.event_type == EventType.CIRCUIT_OPENED:
            anomaly = await self._check_circuit_anomaly(event)
        elif event.event_type == EventType.BACKPRESSURE_DETECTED:
            anomaly = await self._check_backpressure_anomaly(event)

        if anomaly:
            self.anomalies.append(anomaly)
            logger.warning(f"Anomaly detected: {anomaly['type']}")

    async def _check_error_rate_anomaly(self, event: Event) -> Optional[Dict[str, Any]]:
        """
        Check for high error rate anomaly.

        Args:
            event: TASK_FAILED event

        Returns:
            Anomaly dictionary if detected, None otherwise
        """
        metrics = await self.aggregator.get_metrics('1min')
        if metrics['error_rate'] > ERROR_RATE_THRESHOLD:
            return {
                'type': 'high_error_rate',
                'timestamp': event.timestamp,
                'error_rate': metrics['error_rate'],
                'threshold': ERROR_RATE_THRESHOLD,
                'context': event.payload
            }
        return None

    async def _check_latency_anomaly(self, event: Event) -> Optional[Dict[str, Any]]:
        """
        Check for high latency anomaly.

        Args:
            event: TASK_COMPLETED event

        Returns:
            Anomaly dictionary if detected, None otherwise
        """
        if event.payload.get('execution_time_s', 0) > LATENCY_P99_THRESHOLD_S:
            return {
                'type': 'high_latency',
                'timestamp': event.timestamp,
                'latency_s': event.payload['execution_time_s'],
                'threshold_s': LATENCY_P99_THRESHOLD_S,
                'context': event.payload
            }
        return None

    async def _check_circuit_anomaly(self, event: Event) -> Optional[Dict[str, Any]]:
        """
        Check for circuit breaker anomaly.

        Args:
            event: CIRCUIT_OPENED event

        Returns:
            Anomaly dictionary (always returns for circuit opens)
        """
        return {
            'type': 'circuit_opened',
            'timestamp': event.timestamp,
            'particle_id': event.payload.get('particle_id'),
            'consecutive_failures': event.payload.get('consecutive_failures'),
            'context': event.payload
        }

    async def _check_backpressure_anomaly(self, event: Event) -> Optional[Dict[str, Any]]:
        """
        Check for backpressure anomaly.

        Args:
            event: BACKPRESSURE_DETECTED event

        Returns:
            Anomaly dictionary (always returns for backpressure)
        """
        return {
            'type': 'backpressure',
            'timestamp': event.timestamp,
            'subscriber_id': event.payload.get('subscriber_id'),
            'queue_size': event.payload.get('queue_size'),
            'queue_capacity': event.payload.get('queue_capacity'),
            'context': event.payload
        }

    def get_subscriber_id(self) -> str:
        """Return subscriber ID"""
        return self.observer_id

    def get_subscribed_event_types(self) -> Set[EventType]:
        """Return subscribed event types"""
        return self.subscribed_types

    async def get_current_metrics(self, window: str = '1min') -> Dict[str, Any]:
        """
        Get current aggregated metrics.

        Args:
            window: Time window ('1min', '5min', '1hour')

        Returns:
            Current metrics for requested window
        """
        return await self.aggregator.get_metrics(window)

    def get_recent_anomalies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent anomalies.

        Args:
            limit: Maximum anomalies to return

        Returns:
            List of recent anomalies (newest first)
        """
        return list(self.anomalies)[-limit:][::-1]


# ============================================================================
# INITIALIZATION HELPERS
# ============================================================================

async def create_and_register_observer(
    observer_id: str = "metrics_observer"
) -> MetricsObserver:
    """
    Create metrics observer and register with event bus.

    Args:
        observer_id: Unique ID for observer

    Returns:
        Initialized and registered MetricsObserver
    """
    observer = MetricsObserver(observer_id)
    event_bus = get_event_bus()
    await event_bus.subscribe(observer)

    logger.info(f"MetricsObserver {observer_id} registered with event bus")
    return observer
