"""
Runtime Adapter - Dual Runtime Infrastructure for Mojo/Python
Phase 2 Week 4: Production deployment with gradual rollout and metrics
"""

import os
import subprocess
import time
import random
import logging
from typing import Any, Callable, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class Runtime(Enum):
    """Available runtime engines"""
    MOJO = "mojo"
    PYTHON = "python"


@dataclass
class RuntimeResult:
    """Result from runtime execution"""
    success: bool
    runtime_used: Runtime
    result: Any
    execution_time_ms: float
    error: Optional[str] = None


class RuntimeAdapter:
    """
    Dual runtime selector with automatic fallback.

    Implements Axiom I (Bifurcation): Collapse complexity into single interface.
    Pattern: Mojo execution with Python safety net.
    """

    def __init__(self):
        self.mojo_available = self._check_mojo()
        self.runtime = Runtime.MOJO if self.mojo_available else Runtime.PYTHON

        # Feature flags from environment
        self.force_python = os.getenv("SYNAPSE_FORCE_PYTHON", "0") == "1"
        self.mojo_features = self._load_mojo_features()

        if self.force_python:
            self.runtime = Runtime.PYTHON

        # Initialize metrics collector
        self.metrics = self._init_metrics()

    def _check_mojo(self) -> bool:
        """Check if Mojo runtime is available"""
        try:
            result = subprocess.run(
                ['mojo', '--version'],
                capture_output=True,
                timeout=2,
                text=True
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _load_mojo_features(self) -> dict[str, bool]:
        """Load Mojo feature flags from config"""
        try:
            from config import MOJO_FEATURES
            return MOJO_FEATURES.copy()
        except ImportError:
            # Fallback to disabled if config not available
            return {
                'pattern_search': False,
                'message_router': False,
                'vector_engine': False,
            }

    def _get_rollout_percentage(self, task_name: str) -> int:
        """Get rollout percentage for gradual deployment"""
        try:
            from config import get_rollout_percentage
            return get_rollout_percentage(task_name)
        except ImportError:
            # Default to 100% if config not available
            return 100

    def _init_metrics(self):
        """Initialize metrics collector with Redis if available"""
        try:
            from mojo_metrics import get_metrics_collector
            # Try to get Redis client
            try:
                import redis
                redis_client = redis.Redis(
                    host=os.getenv('REDIS_HOST', 'localhost'),
                    port=int(os.getenv('REDIS_PORT', '6379')),
                    db=int(os.getenv('REDIS_DB', '0')),
                    decode_responses=True
                )
                # Test connection
                redis_client.ping()
                return get_metrics_collector(redis_client)
            except Exception as e:
                logger.warning(f"Redis not available for metrics: {e}. Using in-memory storage.")
                return get_metrics_collector(None)
        except ImportError:
            logger.warning("Metrics module not available. Metrics collection disabled.")
            return None

    def execute_task(
        self,
        task_name: str,
        python_impl: Callable,
        mojo_impl: Optional[Callable] = None,
        **kwargs
    ) -> RuntimeResult:
        """
        Execute task with dual runtime support.

        Args:
            task_name: Name of the task (for feature flag lookup)
            python_impl: Python implementation function
            mojo_impl: Optional Mojo implementation function
            **kwargs: Arguments passed to implementation

        Returns:
            RuntimeResult with execution details
        """
        start_time = time.time()

        # Check rollout percentage (gradual rollout)
        rollout_percentage = self._get_rollout_percentage(task_name)
        rollout_sample = random.random() * 100  # 0-100

        # Determine runtime
        use_mojo = (
            self.runtime == Runtime.MOJO
            and mojo_impl is not None
            and self.mojo_features.get(task_name, False)
            and not self.force_python
            and rollout_sample <= rollout_percentage  # Gradual rollout gate
        )

        # Execute
        try:
            if use_mojo:
                result = self._execute_mojo(mojo_impl, **kwargs)
                runtime_used = Runtime.MOJO
            else:
                result = self._execute_python(python_impl, **kwargs)
                runtime_used = Runtime.PYTHON

            execution_time = (time.time() - start_time) * 1000  # ms

            # Record metrics
            if self.metrics:
                self.metrics.record_execution(
                    component=task_name,
                    runtime=runtime_used,
                    latency_ms=execution_time,
                    error=None
                )

            return RuntimeResult(
                success=True,
                runtime_used=runtime_used,
                result=result,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            # Automatic fallback on Mojo error
            if use_mojo:
                logger.warning(f"Mojo execution failed for {task_name}, falling back to Python: {e}")
                try:
                    result = self._execute_python(python_impl, **kwargs)
                    execution_time = (time.time() - start_time) * 1000

                    # Record fallback metrics
                    if self.metrics:
                        self.metrics.record_execution(
                            component=task_name,
                            runtime=Runtime.PYTHON,
                            latency_ms=execution_time,
                            error=f"Mojo fallback: {str(e)}"
                        )

                    return RuntimeResult(
                        success=True,
                        runtime_used=Runtime.PYTHON,
                        result=result,
                        execution_time_ms=execution_time,
                        error=f"Mojo failed, used Python fallback: {str(e)}"
                    )
                except Exception as fallback_error:
                    execution_time = (time.time() - start_time) * 1000
                    logger.error(f"Both runtimes failed for {task_name}: Mojo: {e}, Python: {fallback_error}")

                    # Record double failure
                    if self.metrics:
                        self.metrics.record_execution(
                            component=task_name,
                            runtime=Runtime.PYTHON,
                            latency_ms=execution_time,
                            error=f"Both failed: {str(fallback_error)}"
                        )

                    return RuntimeResult(
                        success=False,
                        runtime_used=Runtime.PYTHON,
                        result=None,
                        execution_time_ms=execution_time,
                        error=f"Both runtimes failed. Mojo: {str(e)}, Python: {str(fallback_error)}"
                    )
            else:
                execution_time = (time.time() - start_time) * 1000
                logger.error(f"Python execution failed for {task_name}: {e}")

                # Record Python failure
                if self.metrics:
                    self.metrics.record_execution(
                        component=task_name,
                        runtime=Runtime.PYTHON,
                        latency_ms=execution_time,
                        error=str(e)
                    )

                return RuntimeResult(
                    success=False,
                    runtime_used=runtime_used,
                    result=None,
                    execution_time_ms=execution_time,
                    error=str(e)
                )

    def _execute_python(self, func: Callable, **kwargs) -> Any:
        """Execute Python implementation"""
        return func(**kwargs)

    def _execute_mojo(self, func: Callable, **kwargs) -> Any:
        """Execute Mojo implementation"""
        # Currently wraps Mojo functions via Python bridge
        # Future: Direct Mojo execution via subprocess or FFI
        return func(**kwargs)

    def get_status(self) -> dict:
        """Get runtime adapter status"""
        return {
            'mojo_available': self.mojo_available,
            'current_runtime': self.runtime.value,
            'force_python': self.force_python,
            'mojo_features': self.mojo_features,
        }


# Singleton instance
_adapter = None


def get_runtime_adapter() -> RuntimeAdapter:
    """Get or create RuntimeAdapter singleton"""
    global _adapter
    if _adapter is None:
        _adapter = RuntimeAdapter()
    return _adapter