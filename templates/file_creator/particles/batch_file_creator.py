"""
Batch File Creator Particle
Single Responsibility: Create multiple files at once

External Tract (T_ext) atomic particle.
Implements the Fractal Pneuma Micro-Loop for batch file creation operations.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List
import sys

# Add lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.core.atomic_particle import AtomicParticle, ExecutionContext, create_particle
sys.path.insert(0, str(Path.home() / '.synapse-system' / '.synapse' / 'corpus_callosum'))
from reactive_message_router import TractType

logger = logging.getLogger(__name__)


class BatchFileCreator(AtomicParticle):
    """
    Atomic particle for creating multiple files in a single operation.

    Payload format:
    {
        "files": [
            {
                "path": "/absolute/path/to/file1.txt",
                "content": "file content",
                "encoding": "utf-8" (optional)
            },
            ...
        ]
    }

    Custom metrics tracked:
    - batches_processed: Total batch operations completed
    - total_files_created: Total files created across all batches
    """

    def __init__(self, config, corpus_callosum, state_file: Path):
        super().__init__(config, corpus_callosum, state_file)

        # Initialize custom metrics using helper method
        self._init_custom_metric('batches_processed', 0)
        self._init_custom_metric('total_files_created', 0)

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute batch file creation operation.

        Returns:
            {
                "files_created": int,
                "results": [
                    {
                        "file_path": str,
                        "bytes_written": int,
                        "success": bool
                    },
                    ...
                ]
            }
        """
        payload = context.payload

        # Extract parameters
        files = payload.get('files', [])

        if not files:
            raise ValueError("files list is required in payload")

        if not isinstance(files, list):
            raise ValueError("files must be a list")

        results = []
        files_created = 0

        for file_spec in files:
            try:
                file_path = file_spec.get('path')
                content = file_spec.get('content', '')
                encoding = file_spec.get('encoding', 'utf-8')

                if not file_path:
                    results.append({
                        "file_path": None,
                        "success": False,
                        "error": "file path is required"
                    })
                    continue

                # Convert to Path object
                path = Path(file_path)

                # Ensure parent directory exists
                path.parent.mkdir(parents=True, exist_ok=True)

                # Write file
                with open(path, 'w', encoding=encoding) as f:
                    f.write(content)

                bytes_written = len(content.encode(encoding))
                files_created += 1

                results.append({
                    "file_path": str(path.absolute()),
                    "bytes_written": bytes_written,
                    "success": True
                })

            except Exception as e:
                logger.error(f"[batch_file_creator] Failed to create file: {e}")
                results.append({
                    "file_path": file_spec.get('path'),
                    "success": False,
                    "error": str(e)
                })

        # Update custom metrics
        self.state.custom_metrics['batches_processed'] += 1
        self.state.custom_metrics['total_files_created'] += files_created

        logger.info(
            f"[batch_file_creator] Created {files_created}/{len(files)} files in batch"
        )

        return {
            "files_created": files_created,
            "total_requested": len(files),
            "results": results
        }

    async def evaluate(self, result) -> float:
        """
        Evaluate batch file creation quality.

        Scoring:
        - 1.0: All files created successfully
        - Proportional: Based on success rate
        - 0.0: Complete failure

        Note: This particle DOES override evaluate() because it has
        meaningful proportional scoring based on batch success rate.
        """
        if result.success:
            output = result.output
            if output and 'files_created' in output and 'total_requested' in output:
                success_rate = output['files_created'] / output['total_requested']
                return success_rate
            return 1.0
        else:
            return 0.0


# Factory function using generic create_particle
def create_batch_file_creator(corpus_callosum, state_file: Path = None) -> BatchFileCreator:
    """Create batch_file_creator particle instance"""
    return create_particle(BatchFileCreator, "batch_file_creator", corpus_callosum, state_file)
