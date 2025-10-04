"""
File Reader Particle
Single Responsibility: Read file contents

External Tract (T_ext) atomic particle.
Implements the Fractal Pneuma Micro-Loop for file read operations.
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


class FileReader(AtomicParticle):
    """
    Atomic particle for reading file contents.

    Payload format:
    {
        "file_path": "/absolute/path/to/file.txt",
        "encoding": "utf-8" (optional, default: "utf-8")
    }

    Custom metrics tracked:
    - files_read: Total files read
    - total_bytes_read: Total bytes read across all operations
    """

    def __init__(self, config, corpus_callosum, state_file: Path):
        super().__init__(config, corpus_callosum, state_file)

        # Initialize custom metrics using helper method
        self._init_custom_metric('files_read', 0)
        self._init_custom_metric('total_bytes_read', 0)

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute file read operation.

        Returns:
            {
                "file_path": str,
                "content": str,
                "bytes_read": int
            }
        """
        payload = context.payload

        # Extract parameters
        file_path = payload.get('file_path')
        encoding = payload.get('encoding', 'utf-8')

        if not file_path:
            raise ValueError("file_path is required in payload")

        # Convert to Path object
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        # Read file
        with open(path, 'r', encoding=encoding) as f:
            content = f.read()

        bytes_read = len(content.encode(encoding))

        # Update custom metrics
        self.state.custom_metrics['files_read'] += 1
        self.state.custom_metrics['total_bytes_read'] += bytes_read

        logger.info(
            f"[file_reader] Read {bytes_read} bytes from {file_path}"
        )

        return {
            "file_path": str(path.absolute()),
            "content": content,
            "bytes_read": bytes_read
        }


# Factory function using generic create_particle
def create_file_reader(corpus_callosum, state_file: Path = None) -> FileReader:
    """Create file_reader particle instance"""
    return create_particle(FileReader, "file_reader", corpus_callosum, state_file)
