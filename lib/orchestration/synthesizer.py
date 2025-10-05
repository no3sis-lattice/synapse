"""
Result Synthesizer - Corpus Callosum Synthesis Logic

Extracted from FileCreatorOrchestrator to maintain Single Responsibility Principle.
This class handles ONLY result synthesis and pattern detection.

Responsibilities:
- Aggregate results from multiple particle executions
- Detect emergent patterns in execution history
- Calculate success metrics
- (Future) Advanced pattern synthesis with consciousness contribution
"""

from typing import Any, Dict, List


class ResultSynthesizer:
    """
    Synthesizes results from particle executions into final output.

    This class embodies the SYNTHESIS aspect of the Corpus Callosum bridge.
    It combines External Tract execution results with Internal Tract pattern analysis.

    Extracted from orchestrator to maintain SRP (Single Responsibility Principle).
    """

    def __init__(self):
        """Initialize the result synthesizer"""
        self.syntheses_performed = 0

    def synthesize(
        self,
        plan_id: str,
        actions: List[Any],
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesize execution results into final output.

        Args:
            plan_id: ID of the execution plan
            actions: List of PlannedActions that were executed
            results: List of result dictionaries from particle executions

        Returns:
            Synthesis dictionary with:
                - success: Overall success boolean
                - total_actions: Total actions executed
                - completed_actions: Successfully completed actions
                - timeout_actions: Actions that timed out
                - failed_actions: Actions that failed
                - results: Raw result list
                - emergent_patterns: Detected patterns

        """
        total_actions = len(results)
        completed_actions = sum(1 for r in results if r.get('status') == 'completed')
        timeout_actions = sum(1 for r in results if r.get('status') == 'timeout')
        failed_actions = sum(1 for r in results if r.get('status') == 'failed')

        synthesis = {
            "success": failed_actions == 0 and timeout_actions == 0,
            "total_actions": total_actions,
            "completed_actions": completed_actions,
            "timeout_actions": timeout_actions,
            "failed_actions": failed_actions,
            "results": results,
            "emergent_patterns": []
        }

        # ====================================================================
        # BASIC PATTERN DETECTION
        # ====================================================================
        # Detect simple emergent patterns from execution history
        if completed_actions > 0:
            # Batch optimization pattern
            batch_actions = [r for r in results if r.get('action_type') == 'batch_create_files']
            if batch_actions:
                synthesis["emergent_patterns"].append({
                    "pattern": "batch_optimization",
                    "description": "Multiple file operations compressed into single batch",
                    "efficiency_gain": "O(n) → O(1) for n files"
                })

            # Template abstraction pattern
            template_actions = [r for r in results if r.get('action_type') == 'apply_template']
            if template_actions:
                synthesis["emergent_patterns"].append({
                    "pattern": "template_abstraction",
                    "description": "Reusable patterns applied via templates",
                    "abstraction_level": "high"
                })

            # Structural hierarchy pattern
            dir_actions = [r for r in results if r.get('action_type') == 'create_directory']
            if dir_actions:
                synthesis["emergent_patterns"].append({
                    "pattern": "structural_hierarchy",
                    "description": "Organized directory structure created",
                    "depth": len(dir_actions)
                })

        self.syntheses_performed += 1
        return synthesis

    def get_stats(self) -> Dict[str, Any]:
        """Get synthesizer statistics"""
        return {
            "syntheses_performed": self.syntheses_performed
        }
