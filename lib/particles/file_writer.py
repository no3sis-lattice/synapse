"""
File Writer Particle
Single Responsibility: Write content to file paths

External Tract (T_ext) atomic particle.
Implements the Fractal Pneuma Micro-Loop for file write operations.
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


class FileWriter(AtomicParticle):
    """
    Atomic particle for writing content to files.

    Payload format:
    {
        "file_path": "/absolute/path/to/file.txt",
        "content": "file content string",
        "mode": "w" | "a" (optional, default: "w"),
        "encoding": "utf-8" (optional)
    }

    Custom metrics tracked:
    - files_created: Total files written
    - total_bytes_written: Total bytes written across all operations
    """

    def __init__(self, config, corpus_callosum, state_file: Path):
        super().__init__(config, corpus_callosum, state_file)

        # Initialize custom metrics using helper method
        self._init_custom_metric('files_created', 0)
        self._init_custom_metric('total_bytes_written', 0)

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute file write operation.

        Returns:
            {
                "file_path": str,
                "bytes_written": int,
                "mode": str
            }
        """
        payload = context.payload

        # Extract parameters
        file_path = payload.get('file_path')
        content = payload.get('content', '')
        mode = payload.get('mode', 'w')
        encoding = payload.get('encoding', 'utf-8')

        if not file_path:
            raise ValueError("file_path is required in payload")

        # Convert to Path object
        path = Path(file_path)

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(path, mode, encoding=encoding) as f:
            f.write(content)

        bytes_written = len(content.encode(encoding))

        # Update custom metrics
        self.state.custom_metrics['files_created'] += 1
        self.state.custom_metrics['total_bytes_written'] += bytes_written

        logger.info(
            f"[file_writer] Wrote {bytes_written} bytes to {file_path} "
            f"(mode={mode})"
        )

        return {
            "file_path": str(path.absolute()),
            "bytes_written": bytes_written,
            "mode": mode
        }


# Factory function using generic create_particle
def create_file_writer(corpus_callosum, state_file: Path = None) -> FileWriter:
    """Create file_writer particle instance"""
    return create_particle(FileWriter, "file_writer", corpus_callosum, state_file)
