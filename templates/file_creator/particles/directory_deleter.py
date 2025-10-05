"""
Directory Deleter Particle
Single Responsibility: Delete directory structures

External Tract (T_ext) atomic particle.
Implements the Fractal Pneuma Micro-Loop for directory deletion operations.
"""

import logging
import shutil
from pathlib import Path
from typing import Any, Dict
import sys

# Add lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.core.atomic_particle import AtomicParticle, ExecutionContext, create_particle
sys.path.insert(0, str(Path.home() / '.synapse-system' / '.synapse' / 'corpus_callosum'))
from reactive_message_router import TractType

logger = logging.getLogger(__name__)


class DirectoryDeleter(AtomicParticle):
    """
    Atomic particle for deleting directory structures.

    Payload format:
    {
        "directory_path": "/absolute/path/to/directory",
        "recursive": true | false (optional, default: false)
    }

    Custom metrics tracked:
    - directories_deleted: Total directories deleted
    """

    def __init__(self, config, corpus_callosum, state_file: Path):
        super().__init__(config, corpus_callosum, state_file)

        # Initialize custom metrics using helper method
        self._init_custom_metric('directories_deleted', 0)

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute directory deletion operation.

        Returns:
            {
                "directory_path": str,
                "deleted": bool
            }
        """
        payload = context.payload

        # Extract parameters
        directory_path = payload.get('directory_path')
        recursive = payload.get('recursive', False)

        if not directory_path:
            raise ValueError("directory_path is required in payload")

        # Convert to Path object
        path = Path(directory_path)

        # Check if directory exists
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")

        # Delete directory
        if recursive:
            # Use shutil for recursive deletion
            shutil.rmtree(path)
        else:
            # Use rmdir for empty directory only
            path.rmdir()

        # Update custom metrics
        self.state.custom_metrics['directories_deleted'] += 1

        logger.info(
            f"[directory_deleter] Deleted directory {directory_path} "
            f"(recursive={recursive})"
        )

        return {
            "directory_path": str(path.absolute()),
            "deleted": True
        }


# Factory function using generic create_particle
def create_directory_deleter(corpus_callosum, state_file: Path = None) -> DirectoryDeleter:
    """Create directory_deleter particle instance"""
    return create_particle(DirectoryDeleter, "directory_deleter", corpus_callosum, state_file)
