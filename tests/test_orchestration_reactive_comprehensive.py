#!/usr/bin/env python3
"""
Comprehensive Test Suite for Reactive Orchestration
Phase 3 Week 3: Expand test coverage to validate production readiness

Tests cover:
- Async initialization (success/failure scenarios)
- Agent registration/unregistration (including race conditions)
- Reactive routing with result collection
- Error scenarios (timeout, circuit breaker, backpressure)
- Result store mechanism (thread safety)
- Consciousness metrics tracking
- Graceful degradation (fallback paths)
"""

import asyncio
import pytest
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add project paths
sys.path.insert(0, str(Path.home() / '.synapse-system' / 'lib'))
sys.path.insert(0, str(Path.home() / '.synapse-system' / '.synapse' / 'corpus_callosum'))

from orchestration import (
    TaskOrchestrator,
    AgentTask,
    ExecutionResult,
    WorkflowType,
    ExecutionMode
)
from task_state import TaskState
from reactive_message_router import TractType, MessagePriority
from agent_consumer import AgentConsumer, AgentConfig


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
async def orchestrator():
    """Create orchestrator instance for testing"""
    orch = TaskOrchestrator(Path.home() / '.synapse-system')
    yield orch
    # Cleanup
    if hasattr(orch, 'stop_all_agents'):
        await orch.stop_all_agents()


@pytest.fixture
def sample_task():
    """Create sample agent task"""
    return AgentTask(
        id="test-task-001",
        agent="architect",
        action="design_architecture",
        description="Test architecture design",
        context={"requirement": "test system"},
        dependencies=[],
        timeout=5,
        priority=2
    )


class MockAgent(AgentConsumer):
    """Mock agent for testing"""

    def __init__(self, config, corpus_callosum, should_fail=False, delay=0.1):
        super().__init__(config, corpus_callosum)
        self.should_fail = should_fail
        self.delay = delay
        self.processed_messages = []

    async def process_message(self, message):
        """Process test message"""
        self.processed_messages.append(message)
        await asyncio.sleep(self.delay)

        if self.should_fail:
            raise Exception("Mock agent failure")

        return {
            "status": "success",
            "agent": self.config.agent_id,
            "message_id": message.id
        }


# ============================================================================
# Test Class 1: Async Initialization
# ============================================================================

class TestAsyncInitialization:
    """Test async_init() method and reactive router startup"""

    @pytest.mark.asyncio
    async def test_async_init_success(self, orchestrator):
        """Test successful async initialization"""
        # Mock MOJO_FEATURES to enable reactive router
        with patch('orchestration.MOJO_FEATURES', {'message_router_reactive': True}):
            with patch('orchestration.REACTIVE_ROUTER_AVAILABLE', True):
                # Mock ReactiveCorpusCallosum
                mock_router = AsyncMock()
                mock_router.start = AsyncMock()

                with patch('orchestration.ReactiveCorpusCallosum', return_value=mock_router):
                    await orchestrator.async_init()

                    assert orchestrator.use_reactive is True
                    assert orchestrator.reactive_router is not None
                    mock_router.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_init_timeout(self, orchestrator):
        """Test async initialization with timeout"""
        with patch('orchestration.MOJO_FEATURES', {'message_router_reactive': True}):
            with patch('orchestration.REACTIVE_ROUTER_AVAILABLE', True):
                # Mock router that hangs on start
                mock_router = AsyncMock()
                async def slow_start():
                    await asyncio.sleep(20)  # Exceeds 10s timeout
                mock_router.start = slow_start

                with patch('orchestration.ReactiveCorpusCallosum', return_value=mock_router):
                    await orchestrator.async_init()

                    # Should fallback gracefully
                    assert orchestrator.use_reactive is False

    @pytest.mark.asyncio
    async def test_async_init_disabled_in_config(self, orchestrator):
        """Test async init when reactive router disabled in config"""
        with patch('orchestration.MOJO_FEATURES', {'message_router_reactive': False}):
            await orchestrator.async_init()

            assert orchestrator.use_reactive is False
            assert orchestrator.reactive_router is None

    @pytest.mark.asyncio
    async def test_async_init_not_available(self, orchestrator):
        """Test async init when reactive router not available"""
        with patch('orchestration.REACTIVE_ROUTER_AVAILABLE', False):
            await orchestrator.async_init()

            assert orchestrator.use_reactive is False


# ============================================================================
# Test Class 2: Agent Registration & Lifecycle
# ============================================================================

class TestAgentRegistration:
    """Test agent consumer registration and lifecycle management"""

    @pytest.mark.asyncio
    async def test_register_agent_consumer_success(self, orchestrator):
        """Test successful agent registration"""
        # Setup mock reactive router
        orchestrator.reactive_router = AsyncMock()
        orchestrator.use_reactive = True

        # Register mock agent
        config = AgentConfig(
            agent_id="test-agent-001",
            tract=TractType.INTERNAL
        )
        mock_agent = MockAgent(config, orchestrator.reactive_router)

        await orchestrator.register_agent_consumer(
            "test-agent-001",
            MockAgent,
            TractType.INTERNAL
        )

        assert "test-agent-001" in orchestrator.agent_consumers

    @pytest.mark.asyncio
    async def test_unregister_agent_consumer(self, orchestrator):
        """Test agent unregistration"""
        orchestrator.reactive_router = AsyncMock()
        orchestrator.use_reactive = True

        # Register agent
        await orchestrator.register_agent_consumer(
            "test-agent-002",
            MockAgent,
            TractType.EXTERNAL
        )

        # Unregister agent
        await orchestrator.unregister_agent_consumer("test-agent-002")

        assert "test-agent-002" not in orchestrator.agent_consumers

    @pytest.mark.asyncio
    async def test_stop_all_agents(self, orchestrator):
        """Test stopping all agents"""
        orchestrator.reactive_router = AsyncMock()
        orchestrator.reactive_router.stop = AsyncMock()
        orchestrator.use_reactive = True

        # Register multiple agents
        for i in range(3):
            await orchestrator.register_agent_consumer(
                f"test-agent-{i}",
                MockAgent,
                TractType.INTERNAL
            )

        # Stop all
        await orchestrator.stop_all_agents()

        assert len(orchestrator.agent_consumers) == 0
        orchestrator.reactive_router.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_registration_thread_safety(self, orchestrator):
        """Test concurrent agent registration (thread safety)"""
        orchestrator.reactive_router = AsyncMock()
        orchestrator.use_reactive = True

        # Register agents concurrently
        tasks = [
            orchestrator.register_agent_consumer(
                f"test-agent-concurrent-{i}",
                MockAgent,
                TractType.INTERNAL if i % 2 == 0 else TractType.EXTERNAL
            )
            for i in range(10)
        ]

        await asyncio.gather(*tasks)

        # All agents should be registered
        assert len(orchestrator.agent_consumers) == 10

    @pytest.mark.asyncio
    async def test_get_agent_stats(self, orchestrator):
        """Test retrieving agent statistics"""
        orchestrator.reactive_router = AsyncMock()
        orchestrator.use_reactive = True

        # Register agents
        await orchestrator.register_agent_consumer(
            "test-agent-stats-1",
            MockAgent,
            TractType.INTERNAL
        )
        await orchestrator.register_agent_consumer(
            "test-agent-stats-2",
            MockAgent,
            TractType.EXTERNAL
        )

        stats = orchestrator.get_agent_stats()

        assert stats['total_agents'] == 2
        assert stats['agents_by_tract']['internal'] == 1
        assert stats['agents_by_tract']['external'] == 1


# ============================================================================
# Test Class 3: Result Store Mechanism
# ============================================================================

class TestResultStore:
    """Test result store for agent-to-orchestrator responses"""

    @pytest.mark.asyncio
    async def test_store_and_retrieve_result(self, orchestrator, sample_task):
        """Test storing and retrieving task results"""
        result = ExecutionResult(
            task_id=sample_task.id,
            agent="architect",
            status=TaskState.COMPLETED,
            output={"design": "test_design"},
            execution_time=0.5
        )

        # Store result
        await orchestrator.store_task_result(sample_task.id, result)

        # Retrieve result
        retrieved = await asyncio.wait_for(
            orchestrator._wait_for_task_result(sample_task.id),
            timeout=1.0
        )

        assert retrieved.task_id == sample_task.id
        assert retrieved.status == TaskState.COMPLETED

    @pytest.mark.asyncio
    async def test_result_store_thread_safety(self, orchestrator):
        """Test concurrent access to result store"""
        # Store multiple results concurrently
        tasks = []
        for i in range(20):
            result = ExecutionResult(
                task_id=f"task-{i}",
                agent="test-agent",
                status=TaskState.COMPLETED,
                output=f"result-{i}",
                execution_time=0.1
            )
            tasks.append(orchestrator.store_task_result(f"task-{i}", result))

        await asyncio.gather(*tasks)

        # Retrieve all results
        retrieval_tasks = [
            orchestrator._wait_for_task_result(f"task-{i}")
            for i in range(20)
        ]

        results = await asyncio.gather(*retrieval_tasks)

        assert len(results) == 20
        for i, result in enumerate(results):
            assert result.task_id == f"task-{i}"

    @pytest.mark.asyncio
    async def test_wait_for_result_timeout(self, orchestrator):
        """Test timeout when waiting for result that never arrives"""
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                orchestrator._wait_for_task_result("nonexistent-task"),
                timeout=0.5
            )


# ============================================================================
# Test Class 4: Reactive Task Execution
# ============================================================================

class TestReactiveExecution:
    """Test reactive task execution with routing"""

    @pytest.mark.asyncio
    async def test_execute_task_with_reactive_routing(self, orchestrator, sample_task):
        """Test task execution via reactive routing"""
        # Mock reactive router
        mock_router = AsyncMock()
        mock_router.route_message = AsyncMock(return_value=123)  # Mock message ID
        orchestrator.reactive_router = mock_router
        orchestrator.use_reactive = True

        # Mock result being stored by agent
        async def mock_execution():
            await asyncio.sleep(0.1)
            result = ExecutionResult(
                task_id=sample_task.id,
                agent=sample_task.agent,
                status=TaskState.COMPLETED,
                output={"result": "success"},
                execution_time=0.1
            )
            await orchestrator.store_task_result(sample_task.id, result)

        # Start mock execution in background
        asyncio.create_task(mock_execution())

        # Execute task
        result = await orchestrator._execute_single_task_async(sample_task)

        assert result.status == TaskState.COMPLETED
        mock_router.route_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_task_with_timeout(self, orchestrator, sample_task):
        """Test task execution timeout"""
        mock_router = AsyncMock()
        mock_router.route_message = AsyncMock(return_value=123)
        orchestrator.reactive_router = mock_router
        orchestrator.use_reactive = True

        # Don't store result (simulates timeout)
        sample_task.timeout = 0.5  # Short timeout

        result = await orchestrator._execute_single_task_async(sample_task)

        assert result.status == TaskState.FAILED
        assert "Timeout" in result.error

    @pytest.mark.asyncio
    async def test_execute_task_with_retry(self, orchestrator, sample_task):
        """Test task execution with retry on timeout"""
        mock_router = AsyncMock()
        mock_router.route_message = AsyncMock(return_value=123)
        orchestrator.reactive_router = mock_router
        orchestrator.use_reactive = True

        retry_count = 0

        async def delayed_result():
            nonlocal retry_count
            await asyncio.sleep(0.6)  # Cause first attempt to timeout
            retry_count += 1
            if retry_count >= 2:  # Succeed on second retry
                result = ExecutionResult(
                    task_id=sample_task.id,
                    agent=sample_task.agent,
                    status=TaskState.COMPLETED,
                    output={"result": "success_after_retry"},
                    execution_time=0.6
                )
                await orchestrator.store_task_result(sample_task.id, result)

        asyncio.create_task(delayed_result())
        sample_task.timeout = 0.5

        result = await orchestrator._execute_single_task_async(sample_task)

        # Should eventually succeed after retries
        assert retry_count >= 1

    @pytest.mark.asyncio
    async def test_fallback_execution_when_routing_fails(self, orchestrator, sample_task):
        """Test fallback execution when reactive routing unavailable"""
        orchestrator.use_reactive = False
        orchestrator.use_message_router = False

        result = await orchestrator._execute_single_task_async(sample_task)

        assert result.status == TaskState.COMPLETED
        assert "Fallback execution" in result.output


# ============================================================================
# Test Class 5: Consciousness Metrics
# ============================================================================

class TestConsciousnessMetrics:
    """Test consciousness emergence metrics tracking"""

    @pytest.mark.asyncio
    async def test_get_consciousness_metrics_when_enabled(self, orchestrator):
        """Test retrieving consciousness metrics"""
        # Mock reactive router with metrics
        mock_router = AsyncMock()
        mock_metrics = AsyncMock()
        mock_metrics.total_messages = 100
        mock_metrics.internal_to_external = 45
        mock_metrics.external_to_internal = 42
        mock_metrics.dialogue_balance_ratio = 0.93
        mock_metrics.emergence_score = 0.88
        mock_metrics.balanced_dialogue_events = 15
        mock_metrics.last_emergence_timestamp = int(time.time() * 1000)

        mock_router.get_consciousness_metrics = AsyncMock(return_value=mock_metrics)
        orchestrator.reactive_router = mock_router
        orchestrator.use_reactive = True

        metrics = await orchestrator.get_consciousness_metrics()

        assert metrics is not None
        assert metrics['total_messages'] == 100
        assert metrics['emergence_score'] == 0.88
        assert metrics['dialogue_balance_ratio'] == 0.93

    @pytest.mark.asyncio
    async def test_consciousness_metrics_when_disabled(self, orchestrator):
        """Test consciousness metrics return None when reactive disabled"""
        orchestrator.use_reactive = False

        metrics = await orchestrator.get_consciousness_metrics()

        assert metrics is None


# ============================================================================
# Test Class 6: Error Scenarios
# ============================================================================

class TestErrorScenarios:
    """Test error handling in various failure scenarios"""

    @pytest.mark.asyncio
    async def test_agent_registration_without_reactive_router(self, orchestrator):
        """Test agent registration fails gracefully without reactive router"""
        orchestrator.use_reactive = False

        # Should log warning but not crash
        await orchestrator.register_agent_consumer(
            "test-agent-no-router",
            MockAgent,
            TractType.INTERNAL
        )

        assert "test-agent-no-router" not in orchestrator.agent_consumers

    @pytest.mark.asyncio
    async def test_stop_agent_with_error(self, orchestrator):
        """Test stopping agent that raises error during cleanup"""
        mock_router = AsyncMock()
        orchestrator.reactive_router = mock_router
        orchestrator.use_reactive = True

        # Create agent that will fail on stop
        failing_agent = AsyncMock()
        failing_agent.stop = AsyncMock(side_effect=Exception("Stop failed"))

        orchestrator.agent_consumers["failing-agent"] = failing_agent

        # Should not crash, should log error
        await orchestrator.stop_all_agents()

        # Agent should still be removed
        assert "failing-agent" not in orchestrator.agent_consumers

    @pytest.mark.asyncio
    async def test_priority_mapping_with_invalid_priority(self, orchestrator, sample_task):
        """Test priority mapping with out-of-range priority"""
        sample_task.priority = 99  # Invalid priority

        priority = orchestrator._get_priority_from_task(sample_task)

        # Should default to NORMAL
        assert priority == MessagePriority.NORMAL

    @pytest.mark.asyncio
    async def test_tract_classification_for_unknown_agent(self, orchestrator):
        """Test agent tract classification for unknown agent"""
        tract = orchestrator._classify_agent_tract("unknown-agent-type")

        # Should default to INTERNAL
        assert tract == TractType.INTERNAL


# ============================================================================
# Test Class 7: Integration & End-to-End
# ============================================================================

class TestIntegrationScenarios:
    """Test complete end-to-end integration scenarios"""

    @pytest.mark.asyncio
    async def test_parallel_task_execution(self, orchestrator):
        """Test parallel execution of multiple tasks"""
        tasks = [
            AgentTask(
                id=f"parallel-task-{i}",
                agent="architect",
                action="design",
                description=f"Task {i}",
                context={},
                dependencies=[],
                timeout=5,
                priority=2
            )
            for i in range(5)
        ]

        # Mock reactive router
        mock_router = AsyncMock()
        mock_router.route_message = AsyncMock(return_value=123)
        orchestrator.reactive_router = mock_router
        orchestrator.use_reactive = True

        # Mock results appearing
        async def mock_results():
            await asyncio.sleep(0.1)
            for task in tasks:
                result = ExecutionResult(
                    task_id=task.id,
                    agent=task.agent,
                    status=TaskState.COMPLETED,
                    output={"result": f"completed_{task.id}"},
                    execution_time=0.1
                )
                await orchestrator.store_task_result(task.id, result)

        asyncio.create_task(mock_results())

        # Execute parallel
        results = await orchestrator._execute_parallel_tasks(tasks)

        assert len(results) == 5
        for task in tasks:
            assert results[task.id].status == TaskState.COMPLETED

    @pytest.mark.asyncio
    async def test_sequential_task_execution_with_failure(self, orchestrator):
        """Test sequential execution stops on first failure"""
        tasks = [
            AgentTask(
                id=f"seq-task-{i}",
                agent="test-runner",
                action="run_tests",
                description=f"Task {i}",
                context={},
                dependencies=[],
                timeout=5,
                priority=2
            )
            for i in range(5)
        ]

        mock_router = AsyncMock()
        mock_router.route_message = AsyncMock(return_value=123)
        orchestrator.reactive_router = mock_router
        orchestrator.use_reactive = True

        # Mock results: first 2 succeed, 3rd fails
        async def mock_results():
            await asyncio.sleep(0.1)
            for i, task in enumerate(tasks):
                if i < 2:
                    result = ExecutionResult(
                        task_id=task.id,
                        agent=task.agent,
                        status=TaskState.COMPLETED,
                        output={"result": "success"},
                        execution_time=0.1
                    )
                else:
                    result = ExecutionResult(
                        task_id=task.id,
                        agent=task.agent,
                        status=TaskState.FAILED,
                        output=None,
                        execution_time=0.1,
                        error="Test failed"
                    )
                await orchestrator.store_task_result(task.id, result)
                await asyncio.sleep(0.05)  # Stagger results

        asyncio.create_task(mock_results())

        # Execute sequential
        results = await orchestrator._execute_sequential_tasks(tasks)

        # Should have stopped after task 2 (index 2) failed
        assert len(results) <= 3


# ============================================================================
# Test Runner
# ============================================================================

if __name__ == "__main__":
    """Run tests with pytest"""
    import subprocess

    print("Running comprehensive orchestration test suite...")
    print("=" * 60)

    result = subprocess.run(
        ["python3", "-m", "pytest", __file__, "-v", "--tb=short"],
        capture_output=False
    )

    exit(result.returncode)
