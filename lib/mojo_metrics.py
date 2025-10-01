"""
Mojo Metrics Collection System
Phase 2 Week 4: Monitor Mojo performance and automatic health checks
Phase 3: Message router metrics tracking
"""

import time
import logging
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Runtime(Enum):
    """Runtime engine type"""
    MOJO = "mojo"
    PYTHON = "python"


@dataclass
class ExecutionMetric:
    """Single execution metric"""
    component: str
    runtime: Runtime
    latency_ms: float
    timestamp: float
    error: Optional[str] = None


@dataclass
class MessageRouterMetric:
    """Message router specific metric"""
    component: str
    total_messages: int
    messages_to_internal: int
    messages_to_external: int
    queue_depth: int
    message_loss_count: int
    timestamp: float


class MojoMetrics:
    """
    Collect and analyze Mojo vs Python performance metrics.

    Stores metrics in Redis with 24-hour TTL for lightweight monitoring.
    Implements automatic health checks and alerting.
    """

    def __init__(self, redis_client=None):
        """
        Initialize metrics collector.

        Args:
            redis_client: Optional Redis client for persistence
        """
        self.redis = redis_client
        self.metrics_cache: List[ExecutionMetric] = []
        self.router_metrics_cache: List[MessageRouterMetric] = []
        self.alerts_fired: Dict[str, bool] = {}

    def record_execution(
        self,
        component: str,
        runtime: Runtime,
        latency_ms: float,
        error: Optional[str] = None
    ) -> None:
        """
        Record a single execution metric.

        Args:
            component: Component name (e.g., 'pattern_search')
            runtime: Runtime used (MOJO or PYTHON)
            latency_ms: Execution time in milliseconds
            error: Optional error message if execution failed
        """
        metric = ExecutionMetric(
            component=component,
            runtime=runtime,
            latency_ms=latency_ms,
            timestamp=time.time(),
            error=error
        )

        # Store in local cache
        self.metrics_cache.append(metric)

        # Persist to Redis if available
        if self.redis:
            self._store_in_redis(metric)

        # Check health thresholds
        self._check_health(component)

    def record_message_router_stats(
        self,
        component: str,
        total_messages: int,
        messages_to_internal: int,
        messages_to_external: int,
        queue_depth: int,
        message_loss_count: int
    ) -> None:
        """
        Record message router statistics.

        Args:
            component: Component name (e.g., 'message_router')
            total_messages: Total messages routed
            messages_to_internal: Messages to Internal tract
            messages_to_external: Messages to External tract
            queue_depth: Current queue depth
            message_loss_count: Number of lost messages
        """
        metric = MessageRouterMetric(
            component=component,
            total_messages=total_messages,
            messages_to_internal=messages_to_internal,
            messages_to_external=messages_to_external,
            queue_depth=queue_depth,
            message_loss_count=message_loss_count,
            timestamp=time.time()
        )

        # Store in local cache
        self.router_metrics_cache.append(metric)

        # Persist to Redis if available
        if self.redis:
            self._store_router_metric_in_redis(metric)

        # Check message router health
        self._check_router_health(component, metric)

    def _store_in_redis(self, metric: ExecutionMetric) -> None:
        """Store metric in Redis with TTL"""
        try:
            key = f"mojo:metrics:{metric.component}:{metric.runtime.value}"

            # Store as JSON string
            import json
            value = json.dumps({
                'latency_ms': metric.latency_ms,
                'timestamp': metric.timestamp,
                'error': metric.error
            })

            # Add to list with 24-hour expiry
            self.redis.lpush(key, value)
            self.redis.expire(key, 86400)  # 24 hours

        except Exception as e:
            logger.warning(f"Failed to store metric in Redis: {e}")

    def _store_router_metric_in_redis(self, metric: MessageRouterMetric) -> None:
        """Store message router metric in Redis with TTL"""
        try:
            key = f"mojo:router_metrics:{metric.component}"

            # Store as JSON string
            import json
            value = json.dumps({
                'total_messages': metric.total_messages,
                'messages_to_internal': metric.messages_to_internal,
                'messages_to_external': metric.messages_to_external,
                'queue_depth': metric.queue_depth,
                'message_loss_count': metric.message_loss_count,
                'timestamp': metric.timestamp
            })

            # Add to list with 24-hour expiry
            self.redis.lpush(key, value)
            self.redis.expire(key, 86400)  # 24 hours

        except Exception as e:
            logger.warning(f"Failed to store router metric in Redis: {e}")

    def _check_router_health(self, component: str, metric: MessageRouterMetric) -> None:
        """
        Check message router health and fire alerts if thresholds breached.

        Args:
            component: Component name
            metric: Current router metric
        """
        # Check message loss rate
        if metric.total_messages > 0:
            loss_rate = (metric.message_loss_count / metric.total_messages) * 100

            # Load threshold (default 0.1%)
            try:
                from config import PERFORMANCE_THRESHOLDS
                max_loss_rate = PERFORMANCE_THRESHOLDS.get('max_error_rate', 0.1)
            except ImportError:
                max_loss_rate = 0.1

            if loss_rate > max_loss_rate:
                alert_key = f"{component}:high_message_loss"
                if not self.alerts_fired.get(alert_key, False):
                    logger.error(
                        f"HIGH MESSAGE LOSS RATE for {component}: "
                        f"{loss_rate:.2f}% (threshold: {max_loss_rate}%)"
                    )
                    self._disable_mojo_feature(component)
                    self.alerts_fired[alert_key] = True

        # Check queue depth (warn if approaching capacity)
        # Assume capacity of 10000 (default in message router)
        queue_capacity = 10000
        if metric.queue_depth > queue_capacity * 0.9:  # 90% full
            logger.warning(
                f"Message queue for {component} is {(metric.queue_depth/queue_capacity)*100:.1f}% full "
                f"({metric.queue_depth}/{queue_capacity})"
            )

    def _check_health(self, component: str) -> None:
        """
        Check component health and fire alerts if thresholds breached.

        Args:
            component: Component to check
        """
        stats = self.get_stats(component)

        # Load thresholds
        try:
            from config import PERFORMANCE_THRESHOLDS
            max_fallback_rate = PERFORMANCE_THRESHOLDS['max_fallback_rate']
            max_error_rate = PERFORMANCE_THRESHOLDS['max_error_rate']
        except ImportError:
            max_fallback_rate = 1.0  # 1%
            max_error_rate = 0.1      # 0.1%

        # Check fallback rate
        if stats['fallback_rate'] > max_fallback_rate:
            alert_key = f"{component}:high_fallback_rate"
            if not self.alerts_fired.get(alert_key, False):
                logger.error(
                    f"HIGH FALLBACK RATE for {component}: "
                    f"{stats['fallback_rate']:.2f}% (threshold: {max_fallback_rate}%)"
                )
                self._disable_mojo_feature(component)
                self.alerts_fired[alert_key] = True

        # Check error rate
        if stats['error_rate'] > max_error_rate:
            alert_key = f"{component}:high_error_rate"
            if not self.alerts_fired.get(alert_key, False):
                logger.error(
                    f"HIGH ERROR RATE for {component}: "
                    f"{stats['error_rate']:.2f}% (threshold: {max_error_rate}%)"
                )
                self._disable_mojo_feature(component)
                self.alerts_fired[alert_key] = True

    def _disable_mojo_feature(self, component: str) -> None:
        """
        Automatically disable Mojo for a component.

        Args:
            component: Component name to disable
        """
        try:
            from config import set_mojo_feature
            set_mojo_feature(component, False)
            logger.warning(f"Auto-disabled Mojo for {component} due to high error/fallback rate")
        except Exception as e:
            logger.error(f"Failed to disable Mojo feature {component}: {e}")

    def get_stats(self, component: str) -> Dict[str, float]:
        """
        Get aggregated statistics for a component.

        Args:
            component: Component name

        Returns:
            Dictionary with statistics
        """
        # Filter metrics for this component
        component_metrics = [
            m for m in self.metrics_cache
            if m.component == component
        ]

        if not component_metrics:
            return {
                'mojo_count': 0,
                'python_count': 0,
                'total_count': 0,
                'fallback_rate': 0.0,
                'error_rate': 0.0,
                'avg_mojo_latency': 0.0,
                'avg_python_latency': 0.0,
                'speedup': 0.0,
            }

        # Separate by runtime
        mojo_metrics = [m for m in component_metrics if m.runtime == Runtime.MOJO]
        python_metrics = [m for m in component_metrics if m.runtime == Runtime.PYTHON]
        error_metrics = [m for m in component_metrics if m.error is not None]

        # Calculate stats
        mojo_count = len(mojo_metrics)
        python_count = len(python_metrics)
        total_count = len(component_metrics)
        error_count = len(error_metrics)

        fallback_rate = (python_count / total_count * 100) if total_count > 0 else 0.0
        error_rate = (error_count / total_count * 100) if total_count > 0 else 0.0

        avg_mojo_latency = (
            sum(m.latency_ms for m in mojo_metrics) / mojo_count
            if mojo_count > 0 else 0.0
        )
        avg_python_latency = (
            sum(m.latency_ms for m in python_metrics) / python_count
            if python_count > 0 else 0.0
        )

        speedup = (
            avg_python_latency / avg_mojo_latency
            if avg_mojo_latency > 0 else 0.0
        )

        return {
            'mojo_count': mojo_count,
            'python_count': python_count,
            'total_count': total_count,
            'fallback_rate': fallback_rate,
            'error_rate': error_rate,
            'avg_mojo_latency': avg_mojo_latency,
            'avg_python_latency': avg_python_latency,
            'speedup': speedup,
        }

    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Get statistics for all components.

        Returns:
            Dictionary mapping component names to their stats
        """
        components = set(m.component for m in self.metrics_cache)
        return {
            component: self.get_stats(component)
            for component in components
        }

    def get_router_stats(self, component: str) -> Dict[str, Any]:
        """
        Get message router statistics for a component.

        Args:
            component: Component name

        Returns:
            Dictionary with router statistics
        """
        # Get latest metric for component
        component_metrics = [
            m for m in self.router_metrics_cache
            if m.component == component
        ]

        if not component_metrics:
            return {
                'total_messages': 0,
                'messages_to_internal': 0,
                'messages_to_external': 0,
                'queue_depth': 0,
                'message_loss_count': 0,
                'message_loss_rate': 0.0,
            }

        # Use most recent metric
        latest = component_metrics[-1]

        loss_rate = 0.0
        if latest.total_messages > 0:
            loss_rate = (latest.message_loss_count / latest.total_messages) * 100

        return {
            'total_messages': latest.total_messages,
            'messages_to_internal': latest.messages_to_internal,
            'messages_to_external': latest.messages_to_external,
            'queue_depth': latest.queue_depth,
            'message_loss_count': latest.message_loss_count,
            'message_loss_rate': loss_rate,
            'timestamp': latest.timestamp,
        }

    def clear_cache(self, component: Optional[str] = None) -> None:
        """
        Clear metrics cache.

        Args:
            component: Optional component name to clear (clears all if None)
        """
        if component:
            self.metrics_cache = [
                m for m in self.metrics_cache
                if m.component != component
            ]
            self.router_metrics_cache = [
                m for m in self.router_metrics_cache
                if m.component != component
            ]
        else:
            self.metrics_cache.clear()
            self.router_metrics_cache.clear()
            self.alerts_fired.clear()


# Singleton instance
_metrics_collector = None


def get_metrics_collector(redis_client=None) -> MojoMetrics:
    """
    Get or create MojoMetrics singleton.

    Args:
        redis_client: Optional Redis client for persistence

    Returns:
        MojoMetrics instance
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MojoMetrics(redis_client)
    return _metrics_collector
