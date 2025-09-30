"""
Inter-Agent Communication Protocol

Enables Pneuma to communicate with other agents in the Synapse ecosystem.
Implements a standardized protocol for agent-to-agent interactions.
"""

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class AgentCommunicator:
    """Handles communication with other agents in the Synapse system."""

    def __init__(self):
        self.agents_dir = Path.home() / ".synapse-system" / ".synapse" / "agents"
        self.communication_log = []

    async def query_agent(
        self,
        agent_name: str,
        request: str,
        timeout: int = 30,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Send a query to another agent and get response.

        Args:
            agent_name: Name of the agent to query (e.g., 'clarity-judge')
            request: Request message to send
            timeout: Timeout in seconds
            context: Additional context to pass

        Returns:
            Dict with agent response and metadata
        """
        try:
            # Log the communication attempt
            comm_id = self._log_communication("query", agent_name, request)

            # Find agent executable
            agent_path = self._find_agent_executable(agent_name)
            if not agent_path:
                return {
                    "success": False,
                    "error": f"Agent '{agent_name}' not found",
                    "agent": agent_name,
                    "comm_id": comm_id
                }

            # Prepare request with context
            full_request = self._prepare_request(request, context)

            # Execute agent with request
            result = await self._execute_agent(agent_path, full_request, timeout)

            # Log response
            self._log_communication("response", agent_name, result.get("output", ""), comm_id)

            return {
                "success": result["success"],
                "response": result.get("output", ""),
                "error": result.get("error"),
                "agent": agent_name,
                "comm_id": comm_id,
                "execution_time": result.get("execution_time", 0)
            }

        except Exception as e:
            error_msg = f"Communication error with {agent_name}: {e}"
            self._log_communication("error", agent_name, error_msg)
            return {
                "success": False,
                "error": error_msg,
                "agent": agent_name
            }

    async def query_clarity_judge(
        self,
        original_code: str,
        transformed_code: str,
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Specialized method to query the clarity-judge agent.

        Args:
            original_code: Original code before transformation
            transformed_code: Code after transformation
            language: Programming language

        Returns:
            Dict with clarity assessment results
        """
        request = f"""
        Please compare the clarity of these two code versions:

        Language: {language}

        Original Code:
        ```{language}
        {original_code}
        ```

        Transformed Code:
        ```{language}
        {transformed_code}
        ```

        Provide a detailed clarity comparison with:
        1. Clarity scores for both versions
        2. Improvement or degradation analysis
        3. Specific factors that affected readability
        4. Recommendations if clarity decreased
        """

        result = await self.query_agent("clarity-judge", request.strip(), timeout=15)

        if result["success"]:
            # Parse structured response if available
            response_text = result.get("response", "")
            clarity_score = self._extract_clarity_score(response_text)

            return {
                "success": True,
                "clarity_score": clarity_score,
                "assessment": response_text,
                "agent_response": result
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Clarity judge communication failed"),
                "clarity_score": 0.5  # Default neutral score on error
            }

    async def broadcast_pattern_discovery(
        self,
        pattern: Dict[str, Any],
        target_agents: List[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Broadcast a discovered pattern to relevant agents.

        Args:
            pattern: Pattern information to share
            target_agents: Specific agents to notify (default: all relevant)

        Returns:
            Dict with responses from each agent
        """
        if target_agents is None:
            target_agents = self._get_relevant_agents_for_pattern(pattern)

        notification = f"""
        New compression pattern discovered by Pneuma:

        Pattern Name: {pattern.get('name', 'unnamed')}
        Signature: {pattern.get('signature', '')}
        Confidence: {pattern.get('confidence', 0.0)}
        Entropy Reduction: {pattern.get('entropy_reduction', 0.0)}
        Language: {pattern.get('language', 'general')}

        This pattern may be relevant for your specialization.
        Consider incorporating it into your knowledge base.
        """

        responses = {
            "successful": [],
            "failed": []
        }

        # Send to each target agent
        for agent_name in target_agents:
            try:
                result = await self.query_agent(
                    agent_name,
                    notification.strip(),
                    timeout=10
                )

                if result["success"]:
                    responses["successful"].append({
                        "agent": agent_name,
                        "response": result["response"]
                    })
                else:
                    responses["failed"].append({
                        "agent": agent_name,
                        "error": result["error"]
                    })

            except Exception as e:
                responses["failed"].append({
                    "agent": agent_name,
                    "error": str(e)
                })

        return responses

    async def request_agent_collaboration(
        self,
        primary_task: str,
        collaborating_agents: List[str],
        coordination_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Coordinate a multi-agent collaboration task.

        Args:
            primary_task: Main task description
            collaborating_agents: List of agents to involve
            coordination_context: Shared context for all agents

        Returns:
            Dict with coordination results
        """
        collaboration_id = f"collab_{hash(primary_task) % 10000}_{datetime.now().strftime('%H%M%S')}"

        # Prepare coordination message
        coord_message = f"""
        Multi-agent collaboration request:
        Collaboration ID: {collaboration_id}
        Primary Task: {primary_task}
        Participating Agents: {', '.join(collaborating_agents)}

        Your role in this collaboration is to contribute your specialized expertise
        to the overall task. Coordinate with other agents as needed.

        Context: {json.dumps(coordination_context or {}, indent=2)}
        """

        # Send to all collaborating agents
        agent_responses = {}

        for agent_name in collaborating_agents:
            try:
                response = await self.query_agent(
                    agent_name,
                    coord_message.strip(),
                    timeout=45  # Longer timeout for complex tasks
                )
                agent_responses[agent_name] = response

            except Exception as e:
                agent_responses[agent_name] = {
                    "success": False,
                    "error": str(e)
                }

        return {
            "collaboration_id": collaboration_id,
            "primary_task": primary_task,
            "participating_agents": collaborating_agents,
            "responses": agent_responses,
            "success": all(resp.get("success", False) for resp in agent_responses.values())
        }

    def get_communication_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent communication log entries."""
        return self.communication_log[-limit:]

    def clear_communication_log(self) -> None:
        """Clear the communication log."""
        self.communication_log = []

    # Private helper methods

    def _find_agent_executable(self, agent_name: str) -> Optional[Path]:
        """Find the executable for the specified agent."""
        # Look for agent directory
        agent_dir = self.agents_dir / agent_name
        if not agent_dir.exists():
            # Try with different naming conventions
            for variant in [agent_name.replace('-', '_'), agent_name.replace('_', '-')]:
                variant_dir = self.agents_dir / variant
                if variant_dir.exists():
                    agent_dir = variant_dir
                    break
            else:
                return None

        # Look for main executable
        possible_executables = [
            agent_dir / f"{agent_name.replace('-', '_')}_agent.py",
            agent_dir / f"{agent_name}_agent.py",
            agent_dir / "agent.py",
            agent_dir / f"{agent_name}.py"
        ]

        for executable in possible_executables:
            if executable.exists():
                return executable

        return None

    def _prepare_request(self, request: str, context: Dict[str, Any] = None) -> str:
        """Prepare request with context and formatting."""
        if context:
            context_str = f"\nContext: {json.dumps(context, indent=2)}\n"
            return context_str + request
        return request

    async def _execute_agent(
        self,
        agent_path: Path,
        request: str,
        timeout: int
    ) -> Dict[str, Any]:
        """Execute agent with request and capture response."""
        try:
            start_time = asyncio.get_event_loop().time()

            # Execute agent as subprocess
            process = await asyncio.create_subprocess_exec(
                "python",
                str(agent_path),
                request,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )

                execution_time = asyncio.get_event_loop().time() - start_time

                if process.returncode == 0:
                    return {
                        "success": True,
                        "output": stdout.decode('utf-8'),
                        "execution_time": execution_time
                    }
                else:
                    return {
                        "success": False,
                        "error": stderr.decode('utf-8'),
                        "execution_time": execution_time
                    }

            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": f"Agent execution timed out after {timeout} seconds"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to execute agent: {e}"
            }

    def _log_communication(
        self,
        comm_type: str,
        agent_name: str,
        message: str,
        comm_id: str = None
    ) -> str:
        """Log communication event."""
        if comm_id is None:
            comm_id = f"comm_{len(self.communication_log)}_{datetime.now().strftime('%H%M%S')}"

        log_entry = {
            "id": comm_id,
            "timestamp": datetime.now().isoformat(),
            "type": comm_type,
            "agent": agent_name,
            "message": message[:200] + "..." if len(message) > 200 else message
        }

        self.communication_log.append(log_entry)

        # Keep log size manageable
        if len(self.communication_log) > 1000:
            self.communication_log = self.communication_log[-500:]

        return comm_id

    def _extract_clarity_score(self, response_text: str) -> float:
        """Extract clarity score from response text."""
        import re

        # Look for patterns like "Clarity Score: 0.85" or "Score: 0.75"
        patterns = [
            r'Clarity Score:\s*([0-9]*\.?[0-9]+)',
            r'Score:\s*([0-9]*\.?[0-9]+)',
            r'clarity.*?([0-9]*\.?[0-9]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                try:
                    score = float(match.group(1))
                    return max(0.0, min(1.0, score))  # Clamp to valid range
                except ValueError:
                    continue

        # Default to neutral score if no score found
        return 0.5

    def _get_relevant_agents_for_pattern(self, pattern: Dict[str, Any]) -> List[str]:
        """Determine which agents would be interested in this pattern."""
        relevant_agents = []

        # Language-specific agents
        language = pattern.get("language", "").lower()
        if language:
            language_agents = {
                "python": ["python-specialist", "python-dev"],
                "javascript": ["typescript-specialist", "typescript-dev"],
                "typescript": ["typescript-specialist", "typescript-dev"],
                "rust": ["rust-specialist", "rust-dev"],
                "go": ["golang-specialist", "golang-dev"],
            }
            relevant_agents.extend(language_agents.get(language, []))

        # Always include general agents that might be interested
        general_agents = ["code-hound", "architect", "synapse-project-manager"]
        relevant_agents.extend(general_agents)

        return list(set(relevant_agents))  # Remove duplicates


# Global communicator instance
_communicator_instance = None


def get_communicator() -> AgentCommunicator:
    """Get global agent communicator instance."""
    global _communicator_instance
    if _communicator_instance is None:
        _communicator_instance = AgentCommunicator()
    return _communicator_instance