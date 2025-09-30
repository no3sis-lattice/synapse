"""
Runtime Adapter - Dual Runtime Infrastructure for Mojo/Python
Phase 1: Proof-of-Concept with automatic fallback
"""

import os
import subprocess
import time
from typing import Any, Callable, Optional
from enum import Enum
from dataclasses import dataclass


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
        # TODO: Load from lib/config.py once created
        return {
            'pattern_search': False,    # Enable after Phase 2 validation
            'message_router': False,    # Enable after Phase 3 validation
            'vector_engine': False,     # Future phase
        }

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

        # Determine runtime
        use_mojo = (
            self.runtime == Runtime.MOJO
            and mojo_impl is not None
            and self.mojo_features.get(task_name, False)
            and not self.force_python
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

            return RuntimeResult(
                success=True,
                runtime_used=runtime_used,
                result=result,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            # Automatic fallback on Mojo error
            if use_mojo:
                try:
                    result = self._execute_python(python_impl, **kwargs)
                    execution_time = (time.time() - start_time) * 1000

                    return RuntimeResult(
                        success=True,
                        runtime_used=Runtime.PYTHON,
                        result=result,
                        execution_time_ms=execution_time,
                        error=f"Mojo failed, used Python fallback: {str(e)}"
                    )
                except Exception as fallback_error:
                    execution_time = (time.time() - start_time) * 1000
                    return RuntimeResult(
                        success=False,
                        runtime_used=Runtime.PYTHON,
                        result=None,
                        execution_time_ms=execution_time,
                        error=f"Both runtimes failed. Mojo: {str(e)}, Python: {str(fallback_error)}"
                    )
            else:
                execution_time = (time.time() - start_time) * 1000
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