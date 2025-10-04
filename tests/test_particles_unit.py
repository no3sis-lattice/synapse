"""
Unit Tests for Atomic Particles
Tests each particle's execute() method in isolation

Following TDD principles:
- Tests written to verify existing functionality
- Each particle tested independently
- No Corpus Callosum or orchestrator required
- Tests cover success cases, error cases, and edge cases
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock
import sys

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib' / 'particles'))

from atomic_particle import ExecutionContext
from file_writer import FileWriter
from file_reader import FileReader
from directory_creator import DirectoryCreator
from file_deleter import FileDeleter
from directory_deleter import DirectoryDeleter
from file_mover import FileMover
from batch_file_creator import BatchFileCreator
from template_applier import TemplateApplier
from reactive_message_router import TractType, Message
from agent_consumer import AgentConfig


# Fixture: Create temporary directory for tests
@pytest.fixture
def temp_dir():
    """Create a temporary directory for file operations"""
    temp_path = Path(tempfile.mkdtemp(prefix="synapse_unit_test_"))
    yield temp_path
    # Cleanup
    if temp_path.exists():
        shutil.rmtree(temp_path)


# Fixture: Mock Corpus Callosum
@pytest.fixture
def mock_corpus_callosum():
    """Create a mock Corpus Callosum for testing"""
    mock = Mock()
    mock.route_message = Mock(return_value=0)
    return mock


# Fixture: Create mock message
def create_mock_message(payload: dict):
    """Helper to create a mock message"""
    msg = Mock(spec=Message)
    msg.id = 1
    msg.payload = payload
    return msg


# ============================================================
# FILE WRITER TESTS
# ============================================================

@pytest.mark.asyncio
async def test_file_writer_creates_file(temp_dir, mock_corpus_callosum):
    """Test: FileWriter creates a file with content"""
    # Arrange
    state_file = temp_dir / "file_writer_state.json"
    config = AgentConfig(agent_id="file_writer", tract=TractType.EXTERNAL)
    writer = FileWriter(config, mock_corpus_callosum, state_file)

    file_path = temp_dir / "test.txt"
    content = "Hello, World!"

    message = create_mock_message({
        "file_path": str(file_path),
        "content": content
    })

    context = ExecutionContext(
        message=message,
        payload=message.payload,
        start_time=0.0
    )

    # Act
    result = await writer.execute(context)

    # Assert
    assert file_path.exists()
    assert file_path.read_text() == content
    assert result["file_path"] == str(file_path.absolute())
    assert result["bytes_written"] == len(content)
    assert result["mode"] == "w"


@pytest.mark.asyncio
async def test_file_writer_handles_missing_path(temp_dir, mock_corpus_callosum):
    """Test: FileWriter raises error when file_path is missing"""
    state_file = temp_dir / "file_writer_state.json"
    config = AgentConfig(agent_id="file_writer", tract=TractType.EXTERNAL)
    writer = FileWriter(config, mock_corpus_callosum, state_file)

    message = create_mock_message({"content": "test"})
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    with pytest.raises(ValueError, match="file_path is required"):
        await writer.execute(context)


@pytest.mark.asyncio
async def test_file_writer_append_mode(temp_dir, mock_corpus_callosum):
    """Test: FileWriter appends content in append mode"""
    state_file = temp_dir / "file_writer_state.json"
    config = AgentConfig(agent_id="file_writer", tract=TractType.EXTERNAL)
    writer = FileWriter(config, mock_corpus_callosum, state_file)

    file_path = temp_dir / "append_test.txt"
    file_path.write_text("Initial content\n")

    message = create_mock_message({
        "file_path": str(file_path),
        "content": "Appended content",
        "mode": "a"
    })
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    await writer.execute(context)

    content = file_path.read_text()
    assert "Initial content" in content
    assert "Appended content" in content


@pytest.mark.asyncio
async def test_file_writer_creates_parent_directory(temp_dir, mock_corpus_callosum):
    """Test: FileWriter creates parent directories automatically"""
    state_file = temp_dir / "file_writer_state.json"
    config = AgentConfig(agent_id="file_writer", tract=TractType.EXTERNAL)
    writer = FileWriter(config, mock_corpus_callosum, state_file)

    file_path = temp_dir / "nested" / "dir" / "file.txt"

    message = create_mock_message({
        "file_path": str(file_path),
        "content": "test"
    })
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    await writer.execute(context)

    assert file_path.exists()
    assert file_path.parent.exists()


# ============================================================
# FILE READER TESTS
# ============================================================

@pytest.mark.asyncio
async def test_file_reader_reads_file(temp_dir, mock_corpus_callosum):
    """Test: FileReader reads file contents"""
    state_file = temp_dir / "file_reader_state.json"
    config = AgentConfig(agent_id="file_reader", tract=TractType.EXTERNAL)
    reader = FileReader(config, mock_corpus_callosum, state_file)

    file_path = temp_dir / "read_test.txt"
    content = "Test content to read"
    file_path.write_text(content)

    message = create_mock_message({"file_path": str(file_path)})
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    result = await reader.execute(context)

    assert result["content"] == content
    assert result["bytes_read"] == len(content.encode('utf-8'))


@pytest.mark.asyncio
async def test_file_reader_handles_missing_file(temp_dir, mock_corpus_callosum):
    """Test: FileReader raises error when file doesn't exist"""
    state_file = temp_dir / "file_reader_state.json"
    config = AgentConfig(agent_id="file_reader", tract=TractType.EXTERNAL)
    reader = FileReader(config, mock_corpus_callosum, state_file)

    file_path = temp_dir / "nonexistent.txt"

    message = create_mock_message({"file_path": str(file_path)})
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    with pytest.raises(FileNotFoundError):
        await reader.execute(context)


@pytest.mark.asyncio
async def test_file_reader_handles_directory_path(temp_dir, mock_corpus_callosum):
    """Test: FileReader raises error when path is a directory"""
    state_file = temp_dir / "file_reader_state.json"
    config = AgentConfig(agent_id="file_reader", tract=TractType.EXTERNAL)
    reader = FileReader(config, mock_corpus_callosum, state_file)

    dir_path = temp_dir / "testdir"
    dir_path.mkdir()

    message = create_mock_message({"file_path": str(dir_path)})
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    with pytest.raises(ValueError, match="not a file"):
        await reader.execute(context)


# ============================================================
# DIRECTORY CREATOR TESTS
# ============================================================

@pytest.mark.asyncio
async def test_directory_creator_creates_dir(temp_dir, mock_corpus_callosum):
    """Test: DirectoryCreator creates a directory"""
    state_file = temp_dir / "directory_creator_state.json"
    config = AgentConfig(agent_id="directory_creator", tract=TractType.EXTERNAL)
    creator = DirectoryCreator(config, mock_corpus_callosum, state_file)

    dir_path = temp_dir / "new_directory"

    message = create_mock_message({"directory_path": str(dir_path)})
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    result = await creator.execute(context)

    assert dir_path.exists()
    assert dir_path.is_dir()
    assert result["created"] is True


@pytest.mark.asyncio
async def test_directory_creator_creates_nested_dirs(temp_dir, mock_corpus_callosum):
    """Test: DirectoryCreator creates nested directories with parents=True"""
    state_file = temp_dir / "directory_creator_state.json"
    config = AgentConfig(agent_id="directory_creator", tract=TractType.EXTERNAL)
    creator = DirectoryCreator(config, mock_corpus_callosum, state_file)

    dir_path = temp_dir / "level1" / "level2" / "level3"

    message = create_mock_message({
        "directory_path": str(dir_path),
        "parents": True
    })
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    result = await creator.execute(context)

    assert dir_path.exists()
    assert result["depth"] > 0


@pytest.mark.asyncio
async def test_directory_creator_handles_existing_dir(temp_dir, mock_corpus_callosum):
    """Test: DirectoryCreator handles already existing directory"""
    state_file = temp_dir / "directory_creator_state.json"
    config = AgentConfig(agent_id="directory_creator", tract=TractType.EXTERNAL)
    creator = DirectoryCreator(config, mock_corpus_callosum, state_file)

    dir_path = temp_dir / "existing_dir"
    dir_path.mkdir()

    message = create_mock_message({"directory_path": str(dir_path)})
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    result = await creator.execute(context)

    assert dir_path.exists()
    assert result["created"] is False  # Already existed


# ============================================================
# FILE DELETER TESTS
# ============================================================

@pytest.mark.asyncio
async def test_file_deleter_deletes_file(temp_dir, mock_corpus_callosum):
    """Test: FileDeleter deletes a file"""
    state_file = temp_dir / "file_deleter_state.json"
    config = AgentConfig(agent_id="file_deleter", tract=TractType.EXTERNAL)
    deleter = FileDeleter(config, mock_corpus_callosum, state_file)

    file_path = temp_dir / "to_delete.txt"
    file_path.write_text("Delete me")

    message = create_mock_message({"file_path": str(file_path)})
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    await deleter.execute(context)

    assert not file_path.exists()


@pytest.mark.asyncio
async def test_file_deleter_handles_missing_file(temp_dir, mock_corpus_callosum):
    """Test: FileDeleter raises error when file doesn't exist"""
    state_file = temp_dir / "file_deleter_state.json"
    config = AgentConfig(agent_id="file_deleter", tract=TractType.EXTERNAL)
    deleter = FileDeleter(config, mock_corpus_callosum, state_file)

    file_path = temp_dir / "nonexistent.txt"

    message = create_mock_message({"file_path": str(file_path)})
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    with pytest.raises(FileNotFoundError):
        await deleter.execute(context)


# ============================================================
# DIRECTORY DELETER TESTS
# ============================================================

@pytest.mark.asyncio
async def test_directory_deleter_deletes_empty_dir(temp_dir, mock_corpus_callosum):
    """Test: DirectoryDeleter deletes empty directory"""
    state_file = temp_dir / "directory_deleter_state.json"
    config = AgentConfig(agent_id="directory_deleter", tract=TractType.EXTERNAL)
    deleter = DirectoryDeleter(config, mock_corpus_callosum, state_file)

    dir_path = temp_dir / "empty_dir"
    dir_path.mkdir()

    message = create_mock_message({
        "directory_path": str(dir_path),
        "recursive": False
    })
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    await deleter.execute(context)

    assert not dir_path.exists()


@pytest.mark.asyncio
async def test_directory_deleter_deletes_recursively(temp_dir, mock_corpus_callosum):
    """Test: DirectoryDeleter deletes directory recursively"""
    state_file = temp_dir / "directory_deleter_state.json"
    config = AgentConfig(agent_id="directory_deleter", tract=TractType.EXTERNAL)
    deleter = DirectoryDeleter(config, mock_corpus_callosum, state_file)

    dir_path = temp_dir / "recursive_dir"
    dir_path.mkdir()
    (dir_path / "file.txt").write_text("test")

    message = create_mock_message({
        "directory_path": str(dir_path),
        "recursive": True
    })
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    await deleter.execute(context)

    assert not dir_path.exists()


# ============================================================
# FILE MOVER TESTS
# ============================================================

@pytest.mark.asyncio
async def test_file_mover_moves_file(temp_dir, mock_corpus_callosum):
    """Test: FileMover moves a file"""
    state_file = temp_dir / "file_mover_state.json"
    config = AgentConfig(agent_id="file_mover", tract=TractType.EXTERNAL)
    mover = FileMover(config, mock_corpus_callosum, state_file)

    source = temp_dir / "source.txt"
    dest = temp_dir / "destination.txt"
    source.write_text("Move me")

    message = create_mock_message({
        "source_path": str(source),
        "dest_path": str(dest)
    })
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    await mover.execute(context)

    assert not source.exists()
    assert dest.exists()
    assert dest.read_text() == "Move me"


@pytest.mark.asyncio
async def test_file_mover_handles_missing_source(temp_dir, mock_corpus_callosum):
    """Test: FileMover raises error when source doesn't exist"""
    state_file = temp_dir / "file_mover_state.json"
    config = AgentConfig(agent_id="file_mover", tract=TractType.EXTERNAL)
    mover = FileMover(config, mock_corpus_callosum, state_file)

    source = temp_dir / "nonexistent.txt"
    dest = temp_dir / "destination.txt"

    message = create_mock_message({
        "source_path": str(source),
        "dest_path": str(dest)
    })
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    with pytest.raises(FileNotFoundError):
        await mover.execute(context)


# ============================================================
# BATCH FILE CREATOR TESTS
# ============================================================

@pytest.mark.asyncio
async def test_batch_file_creator_creates_multiple_files(temp_dir, mock_corpus_callosum):
    """Test: BatchFileCreator creates multiple files"""
    state_file = temp_dir / "batch_file_creator_state.json"
    config = AgentConfig(agent_id="batch_file_creator", tract=TractType.EXTERNAL)
    creator = BatchFileCreator(config, mock_corpus_callosum, state_file)

    files = [
        {"path": str(temp_dir / "file1.txt"), "content": "Content 1"},
        {"path": str(temp_dir / "file2.txt"), "content": "Content 2"},
        {"path": str(temp_dir / "file3.txt"), "content": "Content 3"},
    ]

    message = create_mock_message({"files": files})
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    result = await creator.execute(context)

    assert result["files_created"] == 3
    assert (temp_dir / "file1.txt").exists()
    assert (temp_dir / "file2.txt").exists()
    assert (temp_dir / "file3.txt").exists()


@pytest.mark.asyncio
async def test_batch_file_creator_handles_partial_failure(temp_dir, mock_corpus_callosum):
    """Test: BatchFileCreator handles partial failures gracefully"""
    state_file = temp_dir / "batch_file_creator_state.json"
    config = AgentConfig(agent_id="batch_file_creator", tract=TractType.EXTERNAL)
    creator = BatchFileCreator(config, mock_corpus_callosum, state_file)

    files = [
        {"path": str(temp_dir / "good1.txt"), "content": "Good"},
        {"path": None, "content": "Bad"},  # Missing path
        {"path": str(temp_dir / "good2.txt"), "content": "Good"},
    ]

    message = create_mock_message({"files": files})
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    result = await creator.execute(context)

    assert result["files_created"] == 2  # Only 2 succeeded
    assert result["total_requested"] == 3


# ============================================================
# TEMPLATE APPLIER TESTS
# ============================================================

@pytest.mark.asyncio
async def test_template_applier_applies_template(temp_dir, mock_corpus_callosum):
    """Test: TemplateApplier applies template with variables"""
    state_file = temp_dir / "template_applier_state.json"
    config = AgentConfig(agent_id="template_applier", tract=TractType.EXTERNAL)
    applier = TemplateApplier(config, mock_corpus_callosum, state_file)

    output_path = temp_dir / "output.py"

    message = create_mock_message({
        "template_name": "python_module",
        "output_path": str(output_path),
        "variables": {
            "description": "Test module",
            "imports": "import sys",
            "class_name": "TestClass",
            "class_description": "A test class"
        }
    })
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    result = await applier.execute(context)

    assert output_path.exists()
    content = output_path.read_text()
    assert "TestClass" in content
    assert "Test module" in content
    assert result["template_used"] == "python_module"


@pytest.mark.asyncio
async def test_template_applier_handles_missing_variables(temp_dir, mock_corpus_callosum):
    """Test: TemplateApplier handles missing variables gracefully"""
    state_file = temp_dir / "template_applier_state.json"
    config = AgentConfig(agent_id="template_applier", tract=TractType.EXTERNAL)
    applier = TemplateApplier(config, mock_corpus_callosum, state_file)

    output_path = temp_dir / "output.txt"

    message = create_mock_message({
        "template_content": "Hello $name, you are $age years old",
        "output_path": str(output_path),
        "variables": {
            "name": "Alice"
            # Missing 'age' variable
        }
    })
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    result = await applier.execute(context)

    assert output_path.exists()
    content = output_path.read_text()
    assert "Alice" in content


# ============================================================
# CUSTOM METRICS TESTS
# ============================================================

@pytest.mark.asyncio
async def test_file_writer_updates_custom_metrics(temp_dir, mock_corpus_callosum):
    """Test: FileWriter updates custom metrics correctly"""
    state_file = temp_dir / "file_writer_state.json"
    config = AgentConfig(agent_id="file_writer", tract=TractType.EXTERNAL)
    writer = FileWriter(config, mock_corpus_callosum, state_file)

    # Initial metrics
    assert writer.state.custom_metrics['files_created'] == 0
    assert writer.state.custom_metrics['total_bytes_written'] == 0

    # Execute operation
    file_path = temp_dir / "metrics_test.txt"
    content = "Test content"
    message = create_mock_message({
        "file_path": str(file_path),
        "content": content
    })
    context = ExecutionContext(message=message, payload=message.payload, start_time=0.0)

    await writer.execute(context)

    # Check metrics updated
    assert writer.state.custom_metrics['files_created'] == 1
    assert writer.state.custom_metrics['total_bytes_written'] == len(content)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
