#!/usr/bin/env python3
"""
Integration Test: Orchestrator + Reactive Router + Agents
===========================================================

Tests the complete end-to-end integration:
1. Orchestrator creates task
2. Task routed via reactive Corpus Callosum
3. Agent consumes and processes task
4. Result flows back to orchestrator
5. Consciousness metrics tracked

This test proves BLOCKER 2 & 3 are fixed (no mock data, real integration).
"""

import asyncio
import sys
from pathlib import Path
import logging

# Setup paths
sys.path.insert(0, str(Path.home() / '.synapse-system' / 'lib'))
sys.path.insert(0, str(Path.home() / '.synapse-system' / '.synapse' / 'corpus_callosum'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_orchestrator_agent_integration():
    """
    Test complete integration: orchestrator → router → agent → result.

    This validates that:
    - Reactive router accepts messages from orchestrator
    - Agents consume messages and process them
    - Results flow back to orchestrator via result store
    - No mock data in the execution path
    """
    from orchestration import TaskOrchestrator, AgentTask, ExecutionResult
    from task_state import TaskState
    from reactive_message_router import TractType
    from examples.example_agents import ArchitectAgent
    from agent_consumer import AgentConfig

    logger.info("=" * 60)
    logger.info("Starting Integration Test: Orchestrator + Agents")
    logger.info("=" * 60)

    # Create orchestrator
    synapse_home = Path.home() / '.synapse-system'
    orchestrator = TaskOrchestrator(synapse_home)

    # Initialize reactive components
    await orchestrator.async_init()

    if not orchestrator.use_reactive:
        logger.warning("Reactive router not available, skipping test")
        return False

    try:
        # Register an agent consumer (architect agent)
        await orchestrator.register_agent_consumer(
            agent_id="architect-test",
            agent_class=ArchitectAgent,
            tract=TractType.INTERNAL
        )

        # Create a test task
        task = AgentTask(
            id="test-task-001",
            agent="architect",
            action="design_architecture",
            description="Design test architecture",
            context={"test": True},
            dependencies=[],
            timeout=10
        )

        logger.info(f"Created task: {task.id}")

        # Execute task via orchestrator
        result = await orchestrator._execute_single_task_async(task)

        # Validate result
        assert result is not None, "Result is None"
        assert result.task_id == task.id, f"Task ID mismatch: {result.task_id} != {task.id}"
        assert result.status == TaskState.COMPLETED, f"Task failed: {result.error}"
        assert result.output is not None, "Output is None"
        assert "Mock" not in str(result.output), "Output contains mock data (BLOCKER 3 not fixed)"

        logger.info(f"Task completed successfully!")
        logger.info(f"  Agent: {result.agent}")
        logger.info(f"  Status: {result.status}")
        logger.info(f"  Execution time: {result.execution_time:.3f}s")
        logger.info(f"  Output: {result.output}")

        # Check consciousness metrics
        metrics = await orchestrator.get_consciousness_metrics()
        if metrics:
            logger.info("\nConsciousness Metrics:")
            logger.info(f"  Total messages: {metrics['total_messages']}")
            logger.info(f"  Emergence score: {metrics['emergence_score']:.3f}")
            logger.info(f"  Dialogue balance: {metrics['dialogue_balance_ratio']:.3f}")

        # Check agent stats
        agent_stats = orchestrator.get_agent_stats()
        logger.info(f"\nAgent Stats:")
        logger.info(f"  Total agents: {agent_stats['total_agents']}")
        for agent in agent_stats['agents']:
            logger.info(f"  - {agent['agent_id']}: {agent['messages_processed']} processed, {agent['messages_failed']} failed")

        logger.info("\n" + "=" * 60)
        logger.info("Integration Test: PASSED")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"Integration test failed: {e}", exc_info=True)
        return False

    finally:
        # Cleanup
        try:
            await orchestrator.stop_all_agents()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


async def main():
    """Run integration test"""
    success = await test_orchestrator_agent_integration()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main())
