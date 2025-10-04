"""
File Deleter Particle
Single Responsibility: Delete files

External Tract (T_ext) atomic particle.
Implements the Fractal Pneuma Micro-Loop for file deletion operations.
"""

import logging
from pathlib import Path
from typing import Any, Dict
import sys

# Add lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from atomic_particle import AtomicParticle, ExecutionContext, create_particle
sys.path.insert(0, str(Path.home() / '.synapse-system' / '.synapse' / 'corpus_callosum'))
from reactive_message_router import TractType

logger = logging.getLogger(__name__)


class FileDeleter(AtomicParticle):
    """
    Atomic particle for deleting files.

    Payload format:
    {
        "file_path": "/absolute/path/to/file.txt"
    }

    Custom metrics tracked:
    - files_deleted: Total files deleted
    """

    def __init__(self, config, corpus_callosum, state_file: Path):
        super().__init__(config, corpus_callosum, state_file)

        # Initialize custom metrics using helper method
        self._init_custom_metric('files_deleted', 0)

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute file deletion operation.

        Returns:
            {
                "file_path": str,
                "deleted": bool
            }
        """
        payload = context.payload

        # Extract parameters
        file_path = payload.get('file_path')

        if not file_path:
            raise ValueError("file_path is required in payload")

        # Convert to Path object
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        # Delete file
        path.unlink()

        # Update custom metrics
        self.state.custom_metrics['files_deleted'] += 1

        logger.info(
            f"[file_deleter] Deleted file {file_path}"
        )

        return {
            "file_path": str(path.absolute()),
            "deleted": True
        }


# Factory function using generic create_particle
def create_file_deleter(corpus_callosum, state_file: Path = None) -> FileDeleter:
    """Create file_deleter particle instance"""
    return create_particle(FileDeleter, "file_deleter", corpus_callosum, state_file)
