"""
Synapse Project Manager Tools

Orchestration tools for multi-agent workflow coordination.
Implements The Loop: Observe → Orient → Decide → Act
"""

from .orchestration_tools import *
from .workflow_tools import *
from .delegation_tools import *
from .monitoring_tools import *
from .synthesis_tools import *
from .synapse_integration import *
from .agent_communication import *

__all__ = [
    # Orchestration core
    'o_analyze', 'o_dependencies', 'o_agents',
    'r_pattern', 'r_parallel', 'r_optimize',
    'd_delegate', 'd_schedule', 'd_monitor',
    'a_execute', 'a_synthesize', 'a_validate',

    # Workflow management
    'load_workflow_template', 'create_custom_workflow',
    'optimize_execution_graph', 'calculate_workflow_efficiency',

    # Agent delegation
    'delegate_to_agent', 'create_agent_context', 'track_agent_progress',

    # Monitoring & synthesis
    'monitor_execution', 'synthesize_multi_stream', 'validate_completion',

    # Synapse integration
    'get_synapse_standards', 'search_patterns', 'query_templates',

    # Communication
    'AgentCommunicator', 'broadcast_to_agents', 'coordinate_parallel_execution'
]