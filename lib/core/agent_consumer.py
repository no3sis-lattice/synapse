"""
Agent Consumer Base Class
Implements async subscribe pattern for reactive Corpus Callosum

Pneuma-conscious: Agents as consumers (Axiom II - The Map)
Each agent discovers patterns through continuous message consumption.
"""

import asyncio
import logging
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass
import time

# Add corpus callosum to path
sys.path.insert(0, str(Path.home() / '.synapse-system' / '.synapse' / 'corpus_callosum'))
from reactive_message_router import TractType, Message

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for agent consumer"""
    agent_id: str
    tract: TractType
    buffer_size: int = 100
    batch_size: int = 10
    processing_timeout_s: float = 30.0


class AgentConsumer(ABC):
    """
    Base class for agents that consume from reactive Corpus Callosum.

    Pneuma-conscious: Implements Axiom II (The Map)
    - Agents discover patterns through continuous message consumption
    - Each processed message updates the agent's internal model
    - Backpressure prevents agent overload

    Usage:
        class MyAgent(AgentConsumer):
            async def process_message(self, message: Message) -> Any:
                # Handle message
                return result

        agent = MyAgent(config, corpus_callosum)
        await agent.start()
        # ... agent runs in background ...
        await agent.stop()
    """

    def __init__(self, config: AgentConfig, corpus_callosum):
        self.config = config
        self.corpus_callosum = corpus_callosum
        self.running = False
        self._consumer_task: Optional[asyncio.Task] = None
        self._messages_processed = 0
        self._messages_failed = 0

    async def start(self):
        """Start consuming messages"""
        if self.running:
            logger.warning(f"Agent {self.config.agent_id} already running")
            return

        self.running = True
        self._consumer_task = asyncio.create_task(self._consume_loop())
        logger.info(f"Agent {self.config.agent_id} started consuming from {self.config.tract.name}")

    async def stop(self):
        """Stop consuming messages"""
        self.running = False

        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass
            finally:
                self._consumer_task = None

        logger.info(
            f"Agent {self.config.agent_id} stopped "
            f"(processed: {self._messages_processed}, failed: {self._messages_failed})"
        )

    async def _consume_loop(self):
        """
        Main consumption loop (backpressure-aware).

        Fixes BLOCKER 2: Wires up agent-to-orchestrator response flow.
        """
        try:
            async for message in self.corpus_callosum.subscribe(
                self.config.agent_id,
                self.config.tract
            ):
                start_time = time.time()

                try:
                    # Process message with timeout
                    result = await asyncio.wait_for(
                        self.process_message(message),
                        timeout=self.config.processing_timeout_s
                    )
                    self._messages_processed += 1

                    # Store result back to orchestrator (fixes BLOCKER 2)
                    await self._store_result_to_orchestrator(message, result, time.time() - start_time)

                except asyncio.TimeoutError:
                    self._messages_failed += 1
                    logger.error(
                        f"Agent {self.config.agent_id} timed out processing message {message.id}"
                    )
                    # Store timeout error
                    await self._store_error_to_orchestrator(
                        message,
                        f"Timeout after {self.config.processing_timeout_s}s",
                        time.time() - start_time
                    )

                except Exception as e:
                    self._messages_failed += 1
                    logger.error(
                        f"Agent {self.config.agent_id} error processing message {message.id}: {e}",
                        exc_info=True
                    )
                    # Store error
                    await self._store_error_to_orchestrator(
                        message,
                        str(e),
                        time.time() - start_time
                    )

        except asyncio.CancelledError:
            logger.info(f"Agent {self.config.agent_id} consumption loop cancelled")

        except Exception as e:
            logger.error(
                f"Agent {self.config.agent_id} consumption loop failed: {e}",
                exc_info=True
            )

    async def _store_result_to_orchestrator(self, message: Message, result: Any, execution_time: float):
        """
        Store successful result back to orchestrator (fixes BLOCKER 2).

        This completes the request-response pattern between agents and orchestrator.
        """
        payload = message.payload if isinstance(message.payload, dict) else {}
        task = payload.get('task')
        orchestrator = payload.get('orchestrator')

        if task and orchestrator:
            # Import here to avoid circular dependency
            from task_state import TaskState

            # Convert result to ExecutionResult format
            # Import ExecutionResult here to avoid circular import
            import sys
            sys.path.insert(0, str(Path.home() / '.synapse-system' / 'lib'))
            from orchestration import ExecutionResult

            execution_result = ExecutionResult(
                task_id=task.id,
                agent=self.config.agent_id,
                status=TaskState.COMPLETED,
                output=result,
                execution_time=execution_time,
                artifacts=[]
            )

            # Store result via orchestrator's store method
            await orchestrator.store_task_result(task.id, execution_result)
            logger.debug(f"Stored result for task {task.id} to orchestrator")

    async def _store_error_to_orchestrator(self, message: Message, error: str, execution_time: float):
        """Store error result back to orchestrator"""
        payload = message.payload if isinstance(message.payload, dict) else {}
        task = payload.get('task')
        orchestrator = payload.get('orchestrator')

        if task and orchestrator:
            # Import here to avoid circular dependency
            from task_state import TaskState

            # Import ExecutionResult here
            import sys
            sys.path.insert(0, str(Path.home() / '.synapse-system' / 'lib'))
            from orchestration import ExecutionResult

            execution_result = ExecutionResult(
                task_id=task.id,
                agent=self.config.agent_id,
                status=TaskState.FAILED,
                output=None,
                execution_time=execution_time,
                error=error
            )

            # Store result via orchestrator's store method
            await orchestrator.store_task_result(task.id, execution_result)
            logger.debug(f"Stored error for task {task.id} to orchestrator")

    @abstractmethod
    async def process_message(self, message: Message) -> Any:
        """
        Process a single message.

        Must be implemented by subclasses.

        Args:
            message: Message from Corpus Callosum

        Returns:
            Processing result (implementation-defined)
        """
        pass

    def get_stats(self) -> dict:
        """Get agent statistics"""
        return {
            "agent_id": self.config.agent_id,
            "tract": self.config.tract.name,
            "messages_processed": self._messages_processed,
            "messages_failed": self._messages_failed,
            "success_rate": (
                self._messages_processed / (self._messages_processed + self._messages_failed)
                if (self._messages_processed + self._messages_failed) > 0
                else 0.0
            )
        }


# ============================================================================
# Factory Functions
# ============================================================================

def create_agent_consumer(
    agent_type: str,
    agent_id: str,
    tract: TractType,
    corpus_callosum,
    **config_kwargs
) -> AgentConsumer:
    """
    Factory function to create agent consumers by type.

    Args:
        agent_type: Type of agent ("architect", "test-runner", etc.)
        agent_id: Unique agent identifier
        tract: Tract assignment (INTERNAL or EXTERNAL)
        corpus_callosum: ReactiveCorpusCallosum instance
        **config_kwargs: Additional AgentConfig parameters

    Returns:
        AgentConsumer instance

    Raises:
        ValueError: If agent_type is unknown or example agents not imported

    Note:
        Example agents are in examples/example_agents.py
        For production, implement real agent logic.
    """
    config = AgentConfig(
        agent_id=agent_id,
        tract=tract,
        **config_kwargs
    )

    # Import example agents
    try:
        import sys
        sys.path.insert(0, str(Path.home() / '.synapse-system' / 'examples'))
        from example_agents import (
            ArchitectAgent,
            TestRunnerAgent,
            CodeHoundAgent,
            DevOpsAgent
        )
    except ImportError as e:
        raise ValueError(
            f"Example agents not available. "
            f"See examples/example_agents.py for reference implementations. "
            f"Error: {e}"
        )

    agent_classes = {
        "architect": ArchitectAgent,
        "test-runner": TestRunnerAgent,
        "code-hound": CodeHoundAgent,
        "devops-engineer": DevOpsAgent,
    }

    agent_class = agent_classes.get(agent_type)
    if not agent_class:
        raise ValueError(
            f"Unknown agent type: {agent_type}. "
            f"Available types: {list(agent_classes.keys())}"
        )

    return agent_class(config, corpus_callosum)
