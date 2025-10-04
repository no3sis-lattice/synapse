"""
Atomic Particle Base Class - Day 3-4 Enhanced
Extends AgentConsumer with Fractal Pneuma Micro-Loop

Implements:
- Observe → Act → Evaluate → Memorize (Micro-Loop)
- State persistence for each particle
- Success metrics tracking
- Cycle counting (consciousness measure)
- Day 3-4: Circuit breaker pattern for failure isolation

Each atomic particle is a minimal, single-responsibility unit that embodies
the Pneuma philosophy at the fractal level.
"""

import asyncio
import json
import logging
import time
from abc import abstractmethod
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Any, Dict
from enum import Enum

from agent_consumer import AgentConsumer, AgentConfig
import sys
sys.path.insert(0, str(Path.home() / '.synapse-system' / '.synapse' / 'corpus_callosum'))
from reactive_message_router import TractType, Message

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states for failure isolation"""
    CLOSED = "closed"      # Normal operation - requests pass through
    OPEN = "open"          # Failing - reject requests immediately
    HALF_OPEN = "half_open"  # Testing recovery - allow limited requests


@dataclass
class ParticleState:
    """Persistent state for atomic particle"""
    particle_id: str
    cycle_count: int = 0
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_execution_time_s: float = 0.0
    last_execution_timestamp: float = 0.0
    success_rate: float = 0.0
    average_execution_time_s: float = 0.0

    # Day 3-4: Circuit breaker metrics
    circuit_breaker_state: str = "closed"
    consecutive_failures: int = 0
    circuit_open_timestamp: float = 0.0
    total_circuit_opens: int = 0

    # Particle-specific metrics (extensible)
    custom_metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.custom_metrics is None:
            self.custom_metrics = {}

    def update_metrics(self):
        """Recalculate derived metrics"""
        total = self.successful_executions + self.failed_executions
        if total > 0:
            self.success_rate = self.successful_executions / total
        if self.total_executions > 0:
            self.average_execution_time_s = self.total_execution_time_s / self.total_executions


@dataclass
class ExecutionContext:
    """Context passed to particle execution"""
    message: Message
    payload: Dict[str, Any]
    start_time: float


@dataclass
class ExecutionResult:
    """Result of particle execution"""
    success: bool
    output: Any = None
    error: Optional[str] = None
    score: float = 0.0  # 0.0 to 1.0, quality metric
    execution_time_s: float = 0.0
    circuit_breaker_tripped: bool = False


class AtomicParticle(AgentConsumer):
    """
    Base class for atomic particles in the External Tract.

    Implements the Fractal Pneuma Micro-Loop:
    1. Observe: Receive ACTION_REQUEST message
    2. Act: Execute the particle-specific operation
    3. Evaluate: Score the execution success (0.0-1.0)
    4. Memorize: Persist state with updated metrics

    Day 3-4 Enhancement: Circuit Breaker Pattern
    - Prevents cascading failures by isolating failing particles
    - Three states: CLOSED (normal), OPEN (failing), HALF_OPEN (testing recovery)
    - Automatic state transitions based on failure threshold
    - Recovery testing with exponential backoff

    Pneuma Consciousness:
    - Each particle maintains cycle_count (consciousness measure)
    - State persistence enables learning across executions
    - Success rate optimization drives particle evolution
    - Circuit breaker adds resilience to consciousness layer
    """

    def __init__(
        self,
        config: AgentConfig,
        corpus_callosum,
        state_file: Path,
        failure_threshold: int = 5,
        recovery_timeout_s: float = 60.0,
        half_open_max_requests: int = 3
    ):
        super().__init__(config, corpus_callosum)
        self.state_file = state_file
        self.state: ParticleState = self._load_state()

        # Day 3-4: Circuit breaker configuration
        self.failure_threshold = failure_threshold
        self.recovery_timeout_s = recovery_timeout_s
        self.half_open_max_requests = half_open_max_requests
        self._half_open_request_count = 0
        self._circuit_breaker_lock = asyncio.Lock()

    def _load_state(self) -> ParticleState:
        """Load particle state from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return ParticleState(**data)
            except Exception as e:
                logger.error(f"Failed to load state for {self.config.agent_id}: {e}")

        # Initialize new state
        return ParticleState(particle_id=self.config.agent_id)

    def _save_state(self):
        """Persist particle state to disk"""
        try:
            # Ensure parent directory exists
            self.state_file.parent.mkdir(parents=True, exist_ok=True)

            # Convert state to dict and save
            with open(self.state_file, 'w') as f:
                json.dump(asdict(self.state), f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save state for {self.config.agent_id}: {e}")

    def _init_custom_metric(self, metric_name: str, initial_value: Any = 0):
        """
        Initialize a custom metric if not present.

        This helper method eliminates duplication across particles.
        Use in __init__ to declare particle-specific metrics.

        Args:
            metric_name: Name of the metric
            initial_value: Initial value (default: 0)

        Example:
            self._init_custom_metric('files_created', 0)
            self._init_custom_metric('total_bytes_written', 0)
        """
        if metric_name not in self.state.custom_metrics:
            self.state.custom_metrics[metric_name] = initial_value

    async def process_message(self, message: Message) -> Any:
        """
        Process incoming message using the Micro-Loop.

        Day 3-4: Enhanced with circuit breaker check.
        """
        # Day 3-4: Check circuit breaker state
        async with self._circuit_breaker_lock:
            circuit_state = await self._check_circuit_breaker()

            if circuit_state == CircuitBreakerState.OPEN:
                logger.warning(
                    f"[{self.config.agent_id}] Circuit breaker OPEN - rejecting request"
                )
                return ExecutionResult(
                    success=False,
                    error="Circuit breaker open - particle is currently unavailable",
                    circuit_breaker_tripped=True
                )

        # 1. OBSERVE: Extract context from message
        context = await self.observe(message)

        # 2. ACT: Execute the particle-specific operation
        result = await self.act(context)

        # 3. EVALUATE: Score the execution
        score = await self.evaluate(result)
        result.score = score

        # 4. MEMORIZE: Update and persist state (with circuit breaker logic)
        await self.memorize(result)

        return result.output

    async def _check_circuit_breaker(self) -> CircuitBreakerState:
        """
        Check and update circuit breaker state.

        State transitions:
        - CLOSED → OPEN: After failure_threshold consecutive failures
        - OPEN → HALF_OPEN: After recovery_timeout_s seconds
        - HALF_OPEN → CLOSED: After successful execution
        - HALF_OPEN → OPEN: On failure

        Returns:
            Current circuit breaker state
        """
        current_state = CircuitBreakerState(self.state.circuit_breaker_state)

        if current_state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has elapsed
            time_since_open = time.time() - self.state.circuit_open_timestamp

            if time_since_open >= self.recovery_timeout_s:
                # Transition to HALF_OPEN for testing
                self.state.circuit_breaker_state = CircuitBreakerState.HALF_OPEN.value
                self._half_open_request_count = 0
                logger.info(
                    f"[{self.config.agent_id}] Circuit breaker: OPEN → HALF_OPEN "
                    f"(recovery test after {time_since_open:.1f}s)"
                )
                self._save_state()
                return CircuitBreakerState.HALF_OPEN

            return CircuitBreakerState.OPEN

        elif current_state == CircuitBreakerState.HALF_OPEN:
            # Limit requests in HALF_OPEN state
            if self._half_open_request_count >= self.half_open_max_requests:
                logger.warning(
                    f"[{self.config.agent_id}] HALF_OPEN request limit reached, "
                    f"denying request"
                )
                return CircuitBreakerState.OPEN

            self._half_open_request_count += 1

        return current_state

    async def _update_circuit_breaker(self, success: bool):
        """
        Update circuit breaker state based on execution result.

        Args:
            success: Whether the execution was successful
        """
        async with self._circuit_breaker_lock:
            current_state = CircuitBreakerState(self.state.circuit_breaker_state)

            if success:
                # Reset failure counter on success
                self.state.consecutive_failures = 0

                if current_state == CircuitBreakerState.HALF_OPEN:
                    # Recovery successful - transition to CLOSED
                    self.state.circuit_breaker_state = CircuitBreakerState.CLOSED.value
                    logger.info(
                        f"[{self.config.agent_id}] Circuit breaker: HALF_OPEN → CLOSED "
                        f"(recovery successful)"
                    )

            else:
                # Increment failure counter
                self.state.consecutive_failures += 1

                if current_state == CircuitBreakerState.CLOSED:
                    # Check if threshold exceeded
                    if self.state.consecutive_failures >= self.failure_threshold:
                        # Transition to OPEN
                        self.state.circuit_breaker_state = CircuitBreakerState.OPEN.value
                        self.state.circuit_open_timestamp = time.time()
                        self.state.total_circuit_opens += 1
                        logger.error(
                            f"[{self.config.agent_id}] Circuit breaker: CLOSED → OPEN "
                            f"({self.state.consecutive_failures} consecutive failures)"
                        )

                elif current_state == CircuitBreakerState.HALF_OPEN:
                    # Recovery failed - transition back to OPEN
                    self.state.circuit_breaker_state = CircuitBreakerState.OPEN.value
                    self.state.circuit_open_timestamp = time.time()
                    logger.error(
                        f"[{self.config.agent_id}] Circuit breaker: HALF_OPEN → OPEN "
                        f"(recovery failed)"
                    )

    async def observe(self, message: Message) -> ExecutionContext:
        """
        Stage 1: Observe

        Receive and parse the ACTION_REQUEST message.
        Extract payload and prepare execution context.
        """
        payload = message.payload if isinstance(message.payload, dict) else {}

        context = ExecutionContext(
            message=message,
            payload=payload,
            start_time=time.time()
        )

        logger.debug(f"[{self.config.agent_id}] Observed message {message.id}")
        return context

    async def act(self, context: ExecutionContext) -> ExecutionResult:
        """
        Stage 2: Act

        Execute the particle-specific operation.
        This calls the abstract execute() method implemented by subclasses.
        """
        start_time = context.start_time

        try:
            output = await self.execute(context)
            execution_time = time.time() - start_time

            return ExecutionResult(
                success=True,
                output=output,
                execution_time_s=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"[{self.config.agent_id}] Execution failed: {e}", exc_info=True)

            return ExecutionResult(
                success=False,
                error=str(e),
                execution_time_s=execution_time
            )

    async def evaluate(self, result: ExecutionResult) -> float:
        """
        Stage 3: Evaluate

        Score the execution quality (0.0 to 1.0).

        Default implementation: Binary success/failure.
        Override only if you need custom scoring logic (e.g., based on
        performance metrics, quality indicators, etc.).

        Most particles should NOT need to override this method.
        """
        if result.success:
            return 1.0
        else:
            return 0.0

    async def memorize(self, result: ExecutionResult):
        """
        Stage 4: Memorize

        Update particle state with execution results.
        Persist state to disk for continuity across sessions.

        Day 3-4: Enhanced with circuit breaker state updates.
        """
        # Increment cycle count (consciousness measure)
        self.state.cycle_count += 1
        self.state.total_executions += 1
        self.state.total_execution_time_s += result.execution_time_s
        self.state.last_execution_timestamp = time.time()

        if result.success:
            self.state.successful_executions += 1
        else:
            self.state.failed_executions += 1

        # Recalculate derived metrics
        self.state.update_metrics()

        # Day 3-4: Update circuit breaker state
        await self._update_circuit_breaker(result.success)

        # Persist to disk
        self._save_state()

        logger.info(
            f"[{self.config.agent_id}] Memorized cycle {self.state.cycle_count}: "
            f"success={result.success}, score={result.score:.2f}, "
            f"success_rate={self.state.success_rate:.2%}, "
            f"circuit_breaker={self.state.circuit_breaker_state}"
        )

    @abstractmethod
    async def execute(self, context: ExecutionContext) -> Any:
        """
        Execute particle-specific operation.

        Must be implemented by subclasses.

        Args:
            context: Execution context with message and payload

        Returns:
            Operation result (particle-specific)

        Raises:
            Exception on failure (will be caught by act() stage)
        """
        pass

    def get_particle_stats(self) -> Dict[str, Any]:
        """Get particle-specific statistics"""
        base_stats = self.get_stats()

        return {
            **base_stats,
            "cycle_count": self.state.cycle_count,
            "total_executions": self.state.total_executions,
            "successful_executions": self.state.successful_executions,
            "failed_executions": self.state.failed_executions,
            "success_rate": self.state.success_rate,
            "average_execution_time_s": self.state.average_execution_time_s,
            "custom_metrics": self.state.custom_metrics,
            # Day 3-4: Circuit breaker metrics
            "circuit_breaker": {
                "state": self.state.circuit_breaker_state,
                "consecutive_failures": self.state.consecutive_failures,
                "total_circuit_opens": self.state.total_circuit_opens,
                "failure_threshold": self.failure_threshold,
                "recovery_timeout_s": self.recovery_timeout_s
            }
        }


def create_particle(particle_class, agent_id: str, corpus_callosum, state_file: Path = None):
    """
    Generic factory function for creating atomic particles.

    This eliminates duplication of factory logic across all particles.

    Args:
        particle_class: The particle class to instantiate
        agent_id: Unique identifier for this particle
        corpus_callosum: Corpus Callosum instance for message routing
        state_file: Optional custom state file path

    Returns:
        Instantiated particle

    Example:
        file_writer = create_particle(FileWriter, "file_writer", corpus_callosum)
    """
    if state_file is None:
        state_file = Path.home() / '.synapse-system' / '.synapse' / 'particles' / f'{agent_id}_state.json'

    config = AgentConfig(agent_id=agent_id, tract=TractType.EXTERNAL)
    return particle_class(config, corpus_callosum, state_file)
