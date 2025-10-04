"""
File Mover Particle
Single Responsibility: Move/rename files

External Tract (T_ext) atomic particle.
Implements the Fractal Pneuma Micro-Loop for file move/rename operations.
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


class FileMover(AtomicParticle):
    """
    Atomic particle for moving/renaming files.

    Payload format:
    {
        "source_path": "/absolute/path/to/source.txt",
        "dest_path": "/absolute/path/to/destination.txt"
    }

    Custom metrics tracked:
    - files_moved: Total files moved/renamed
    """

    def __init__(self, config, corpus_callosum, state_file: Path):
        super().__init__(config, corpus_callosum, state_file)

        # Initialize custom metrics using helper method
        self._init_custom_metric('files_moved', 0)

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute file move/rename operation.

        Returns:
            {
                "source_path": str,
                "dest_path": str,
                "moved": bool
            }
        """
        payload = context.payload

        # Extract parameters
        source_path = payload.get('source_path')
        dest_path = payload.get('dest_path')

        if not source_path:
            raise ValueError("source_path is required in payload")
        if not dest_path:
            raise ValueError("dest_path is required in payload")

        # Convert to Path objects
        source = Path(source_path)
        dest = Path(dest_path)

        # Check if source exists
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        if not source.is_file():
            raise ValueError(f"Source path is not a file: {source_path}")

        # Ensure destination parent directory exists
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Move/rename file
        source.rename(dest)

        # Update custom metrics
        self.state.custom_metrics['files_moved'] += 1

        logger.info(
            f"[file_mover] Moved file from {source_path} to {dest_path}"
        )

        return {
            "source_path": str(source.absolute()),
            "dest_path": str(dest.absolute()),
            "moved": True
        }


# Factory function using generic create_particle
def create_file_mover(corpus_callosum, state_file: Path = None) -> FileMover:
    """Create file_mover particle instance"""
    return create_particle(FileMover, "file_mover", corpus_callosum, state_file)
