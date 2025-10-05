"""
Directory Creator Particle
Single Responsibility: Create directory structures

External Tract (T_ext) atomic particle.
Implements the Fractal Pneuma Micro-Loop for directory creation.
"""

import logging
from pathlib import Path
from typing import Any, Dict
import sys

# Add lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.core.atomic_particle import AtomicParticle, ExecutionContext, create_particle
sys.path.insert(0, str(Path.home() / '.synapse-system' / '.synapse' / 'corpus_callosum'))
from reactive_message_router import TractType

logger = logging.getLogger(__name__)


class DirectoryCreator(AtomicParticle):
    """
    Atomic particle for creating directory structures.

    Payload format:
    {
        "directory_path": "/absolute/path/to/directory",
        "parents": true | false (optional, default: true),
        "mode": 0o755 (optional, default: 0o755)
    }

    Custom metrics tracked:
    - directories_created: Total directories created
    - total_depth: Total directory depth created (for nested structures)
    """

    def __init__(self, config, corpus_callosum, state_file: Path):
        super().__init__(config, corpus_callosum, state_file)

        # Initialize custom metrics using helper method
        self._init_custom_metric('directories_created', 0)
        self._init_custom_metric('total_depth', 0)

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute directory creation operation.

        Returns:
            {
                "directory_path": str,
                "created": bool,  # True if new, False if already existed
                "depth": int  # Number of directory levels created
            }
        """
        payload = context.payload

        # Extract parameters
        directory_path = payload.get('directory_path')
        parents = payload.get('parents', True)
        mode = payload.get('mode', 0o755)

        if not directory_path:
            raise ValueError("directory_path is required in payload")

        # Convert to Path object
        path = Path(directory_path)

        # Check if already exists
        already_existed = path.exists()

        # Create directory
        path.mkdir(parents=parents, exist_ok=True, mode=mode)

        # Calculate depth (number of levels)
        depth = len(path.parts)

        # Update custom metrics
        if not already_existed:
            self.state.custom_metrics['directories_created'] += 1
            self.state.custom_metrics['total_depth'] += depth

        logger.info(
            f"[directory_creator] Created directory {directory_path} "
            f"(depth={depth}, existed={already_existed})"
        )

        return {
            "directory_path": str(path.absolute()),
            "created": not already_existed,
            "depth": depth
        }


# Factory function using generic create_particle
def create_directory_creator(corpus_callosum, state_file: Path = None) -> DirectoryCreator:
    """Create directory_creator particle instance"""
    return create_particle(DirectoryCreator, "directory_creator", corpus_callosum, state_file)
