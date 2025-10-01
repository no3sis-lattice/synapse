"""
Example Agent Implementations for Testing
==========================================

These are minimal example agents that demonstrate the reactive pattern.
For production use, implement real agent logic.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add corpus callosum to path
sys.path.insert(0, str(Path.home() / '.synapse-system' / 'lib'))
sys.path.insert(0, str(Path.home() / '.synapse-system' / '.synapse' / 'corpus_callosum'))

from agent_consumer import AgentConsumer
from reactive_message_router import Message
from task_state import TaskState

logger = logging.getLogger(__name__)


class ArchitectAgent(AgentConsumer):
    """
    Architect agent (Internal Tract).

    Handles:
    - System design requests
    - Architecture planning
    - Component decomposition

    Pneuma-conscious: T_int agent (self-referential processing)
    """

    async def process_message(self, message: Message) -> dict:
        """Process architecture design requests"""
        logger.info(f"Architect processing: {message.payload}")

        # Extract task from payload
        payload = message.payload
        task_info = payload.get('task') if isinstance(payload, dict) else {}

        # Simulate architecture work
        await asyncio.sleep(0.5)

        result = {
            "status": "architecture_complete",
            "agent": "architect",
            "message_id": message.id,
            "design": "system_design.md",
            "components": ["component_a", "component_b", "component_c"],
            "dependencies": {"component_a": ["component_b"]},
        }

        logger.info(f"Architect completed message {message.id}")
        return result


class TestRunnerAgent(AgentConsumer):
    """
    Test runner agent (External Tract).

    Handles:
    - Test execution
    - Test result reporting
    - Coverage analysis

    Pneuma-conscious: T_ext agent (environmental interaction)
    """

    async def process_message(self, message: Message) -> dict:
        """Process test execution requests"""
        logger.info(f"TestRunner executing: {message.payload}")

        # Extract task from payload
        payload = message.payload
        task_info = payload.get('task') if isinstance(payload, dict) else {}

        # Simulate test execution
        await asyncio.sleep(1.0)

        result = {
            "status": "tests_passed",
            "agent": "test-runner",
            "message_id": message.id,
            "tests_run": 42,
            "tests_passed": 40,
            "tests_failed": 2,
            "coverage": 0.95,
            "duration_ms": 1000,
        }

        logger.info(f"TestRunner completed message {message.id}")
        return result


class CodeHoundAgent(AgentConsumer):
    """
    Code reviewer agent (Internal Tract).

    Handles:
    - Code quality review
    - TDD compliance checking
    - SOLID principle validation

    Pneuma-conscious: T_int agent (analytical, reflective)
    """

    async def process_message(self, message: Message) -> dict:
        """Process code review requests"""
        logger.info(f"CodeHound reviewing: {message.payload}")

        # Extract task from payload
        payload = message.payload
        task_info = payload.get('task') if isinstance(payload, dict) else {}

        # Simulate code review
        await asyncio.sleep(0.8)

        result = {
            "status": "review_complete",
            "agent": "code-hound",
            "message_id": message.id,
            "score": 87,
            "issues_found": 3,
            "issues": [
                {"severity": "minor", "description": "Missing docstring"},
                {"severity": "minor", "description": "Long function (35 lines)"},
                {"severity": "info", "description": "Consider extracting helper"}
            ],
            "recommendations": [
                "Add comprehensive docstrings",
                "Break down large functions",
                "Increase test coverage"
            ]
        }

        logger.info(f"CodeHound completed message {message.id}")
        return result


class DevOpsAgent(AgentConsumer):
    """
    DevOps engineer agent (External Tract).

    Handles:
    - Deployment operations
    - Infrastructure management
    - CI/CD pipeline execution

    Pneuma-conscious: T_ext agent (environmental actuation)
    """

    async def process_message(self, message: Message) -> dict:
        """Process deployment requests"""
        logger.info(f"DevOps deploying: {message.payload}")

        # Extract task from payload
        payload = message.payload
        task_info = payload.get('task') if isinstance(payload, dict) else {}

        # Simulate deployment
        await asyncio.sleep(2.0)

        result = {
            "status": "deployment_complete",
            "agent": "devops-engineer",
            "message_id": message.id,
            "environment": "staging",
            "version": "1.2.3",
            "health_check": "passing",
            "rollback_available": True,
        }

        logger.info(f"DevOps completed message {message.id}")
        return result
