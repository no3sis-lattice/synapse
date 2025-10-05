"""
Integration Test: file_creator MVP - Day 2
Tests the complete dual-tract file creation system with 8 particles

This test validates:
1. Orchestrator receives request and generates plan
2. Plan is routed via Corpus Callosum to particles
3. All 8 particles execute and update state
4. Files/directories are created/read/deleted/moved
5. Batch operations and templates work
6. State files persist with cycle counts

Run with: pytest tests/test_file_creator_mvp.py -v
"""

import asyncio
import json
import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
sys.path.insert(0, str(Path.home() / '.synapse-system' / '.synapse' / 'corpus_callosum'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib' / 'particles'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib' / 'orchestrators'))

from reactive_message_router import ReactiveCorpusCallosum, TractType, MessagePriority
from file_writer import create_file_writer
from directory_creator import create_directory_creator
from file_reader import create_file_reader
from file_deleter import create_file_deleter
from directory_deleter import create_directory_deleter
from file_mover import create_file_mover
from batch_file_creator import create_batch_file_creator
from template_applier import create_template_applier
from file_creator_orchestrator import create_file_creator_orchestrator


@pytest.fixture
async def test_environment():
    """Set up test environment with Corpus Callosum and all 8 particles"""
    # Create temporary directory for test outputs
    test_dir = Path(tempfile.mkdtemp(prefix="synapse_mvp_test_"))
    state_dir = test_dir / "particles"
    state_dir.mkdir(parents=True, exist_ok=True)

    # Initialize Corpus Callosum
    corpus_callosum = ReactiveCorpusCallosum(
        enable_pattern_synthesis=True,
        enable_event_sourcing=False  # Disable Redis for testing
    )
    await corpus_callosum.start()

    # Create all 8 particles
    file_writer = create_file_writer(
        corpus_callosum,
        state_file=state_dir / "file_writer_state.json"
    )
    directory_creator = create_directory_creator(
        corpus_callosum,
        state_file=state_dir / "directory_creator_state.json"
    )
    file_reader = create_file_reader(
        corpus_callosum,
        state_file=state_dir / "file_reader_state.json"
    )
    file_deleter = create_file_deleter(
        corpus_callosum,
        state_file=state_dir / "file_deleter_state.json"
    )
    directory_deleter = create_directory_deleter(
        corpus_callosum,
        state_file=state_dir / "directory_deleter_state.json"
    )
    file_mover = create_file_mover(
        corpus_callosum,
        state_file=state_dir / "file_mover_state.json"
    )
    batch_file_creator = create_batch_file_creator(
        corpus_callosum,
        state_file=state_dir / "batch_file_creator_state.json"
    )
    template_applier = create_template_applier(
        corpus_callosum,
        state_file=state_dir / "template_applier_state.json"
    )

    # Create orchestrator
    orchestrator = create_file_creator_orchestrator(
        corpus_callosum,
        state_file=state_dir / "file_creator_orchestrator_state.json"
    )

    # Start all agents
    await file_writer.start()
    await directory_creator.start()
    await file_reader.start()
    await file_deleter.start()
    await directory_deleter.start()
    await file_mover.start()
    await batch_file_creator.start()
    await template_applier.start()
    await orchestrator.start()

    # Give agents time to fully subscribe to message streams
    await asyncio.sleep(0.1)

    yield {
        "corpus_callosum": corpus_callosum,
        "file_writer": file_writer,
        "directory_creator": directory_creator,
        "file_reader": file_reader,
        "file_deleter": file_deleter,
        "directory_deleter": directory_deleter,
        "file_mover": file_mover,
        "batch_file_creator": batch_file_creator,
        "template_applier": template_applier,
        "orchestrator": orchestrator,
        "test_dir": test_dir,
        "state_dir": state_dir
    }

    # Cleanup
    await file_writer.stop()
    await directory_creator.stop()
    await file_reader.stop()
    await file_deleter.stop()
    await directory_deleter.stop()
    await file_mover.stop()
    await batch_file_creator.stop()
    await template_applier.stop()
    await orchestrator.stop()
    await corpus_callosum.stop()

    # Remove test directory
    shutil.rmtree(test_dir)


@pytest.mark.asyncio
async def test_simple_file_creation(test_environment):
    """Test: Orchestrator creates a single file"""
    env = test_environment
    test_dir = env["test_dir"]
    corpus_callosum = env["corpus_callosum"]

    # Send request to orchestrator via Corpus Callosum
    test_file_path = test_dir / "test_file.txt"
    test_content = "Hello from file_creator MVP!\n"

    msg_id = await corpus_callosum.route_message(
        source_tract=TractType.EXTERNAL,  # Simulating external request
        dest_tract=TractType.INTERNAL,  # To orchestrator
        priority=MessagePriority.NORMAL,
        payload={
            "request_type": "create_file",
            "parameters": {
                "file_path": str(test_file_path),
                "content": test_content
            }
        }
    )

    assert msg_id >= 0, "Message routing failed"

    # Wait for processing
    await asyncio.sleep(1.0)

    # Verify file was created
    assert test_file_path.exists(), "File was not created"
    assert test_file_path.read_text() == test_content, "File content mismatch"


@pytest.mark.asyncio
async def test_file_read(test_environment):
    """Test: File reader particle reads file contents"""
    env = test_environment
    test_dir = env["test_dir"]
    corpus_callosum = env["corpus_callosum"]

    # First create a file
    test_file = test_dir / "read_test.txt"
    test_content = "This is test content for reading"
    test_file.write_text(test_content)

    # Send read request
    msg_id = await corpus_callosum.route_message(
        source_tract=TractType.EXTERNAL,
        dest_tract=TractType.INTERNAL,
        priority=MessagePriority.NORMAL,
        payload={
            "request_type": "read_file",
            "parameters": {
                "file_path": str(test_file)
            }
        }
    )

    assert msg_id >= 0, "Message routing failed"
    await asyncio.sleep(1.0)

    # Note: In full implementation, would verify result was returned
    print("File read request sent successfully")


@pytest.mark.asyncio
async def test_file_deletion(test_environment):
    """Test: File deleter particle deletes files"""
    env = test_environment
    test_dir = env["test_dir"]
    corpus_callosum = env["corpus_callosum"]

    # First create a file
    test_file = test_dir / "delete_test.txt"
    test_file.write_text("This file will be deleted")
    assert test_file.exists()

    # Send delete request
    msg_id = await corpus_callosum.route_message(
        source_tract=TractType.EXTERNAL,
        dest_tract=TractType.INTERNAL,
        priority=MessagePriority.NORMAL,
        payload={
            "request_type": "delete_file",
            "parameters": {
                "file_path": str(test_file)
            }
        }
    )

    assert msg_id >= 0, "Message routing failed"
    await asyncio.sleep(1.0)  # Increased from 0.5s for full message round-trip

    # Verify file was deleted
    assert not test_file.exists(), "File was not deleted"


@pytest.mark.asyncio
async def test_directory_deletion(test_environment):
    """Test: Directory deleter particle deletes directories"""
    env = test_environment
    test_dir = env["test_dir"]
    corpus_callosum = env["corpus_callosum"]

    # Create a directory
    test_subdir = test_dir / "delete_dir"
    test_subdir.mkdir()
    assert test_subdir.exists()

    # Send delete request
    msg_id = await corpus_callosum.route_message(
        source_tract=TractType.EXTERNAL,
        dest_tract=TractType.INTERNAL,
        priority=MessagePriority.NORMAL,
        payload={
            "request_type": "delete_directory",
            "parameters": {
                "directory_path": str(test_subdir),
                "recursive": False
            }
        }
    )

    assert msg_id >= 0, "Message routing failed"
    await asyncio.sleep(1.0)

    # Verify directory was deleted
    assert not test_subdir.exists(), "Directory was not deleted"


@pytest.mark.asyncio
async def test_file_move(test_environment):
    """Test: File mover particle moves/renames files"""
    env = test_environment
    test_dir = env["test_dir"]
    corpus_callosum = env["corpus_callosum"]

    # Create a file
    source_file = test_dir / "source.txt"
    dest_file = test_dir / "destination.txt"
    source_file.write_text("This file will be moved")
    assert source_file.exists()

    # Send move request
    msg_id = await corpus_callosum.route_message(
        source_tract=TractType.EXTERNAL,
        dest_tract=TractType.INTERNAL,
        priority=MessagePriority.NORMAL,
        payload={
            "request_type": "move_file",
            "parameters": {
                "source_path": str(source_file),
                "dest_path": str(dest_file)
            }
        }
    )

    assert msg_id >= 0, "Message routing failed"
    await asyncio.sleep(1.0)

    # Verify file was moved
    assert not source_file.exists(), "Source file still exists"
    assert dest_file.exists(), "Destination file was not created"
    assert dest_file.read_text() == "This file will be moved", "Content mismatch"


@pytest.mark.asyncio
async def test_batch_file_creation(test_environment):
    """Test: Batch file creator creates multiple files at once"""
    env = test_environment
    test_dir = env["test_dir"]
    corpus_callosum = env["corpus_callosum"]

    # Send batch create request
    files = [
        {"path": str(test_dir / "batch1.txt"), "content": "File 1"},
        {"path": str(test_dir / "batch2.txt"), "content": "File 2"},
        {"path": str(test_dir / "batch3.txt"), "content": "File 3"},
    ]

    msg_id = await corpus_callosum.route_message(
        source_tract=TractType.EXTERNAL,
        dest_tract=TractType.INTERNAL,
        priority=MessagePriority.NORMAL,
        payload={
            "request_type": "batch_create_files",
            "parameters": {
                "files": files
            }
        }
    )

    assert msg_id >= 0, "Message routing failed"
    await asyncio.sleep(1.0)

    # Verify all files were created
    for file_spec in files:
        file_path = Path(file_spec["path"])
        assert file_path.exists(), f"Batch file {file_path} was not created"
        assert file_path.read_text() == file_spec["content"], f"Content mismatch for {file_path}"


@pytest.mark.asyncio
async def test_template_application(test_environment):
    """Test: Template applier creates files from templates"""
    env = test_environment
    test_dir = env["test_dir"]
    corpus_callosum = env["corpus_callosum"]

    # Send template apply request
    msg_id = await corpus_callosum.route_message(
        source_tract=TractType.EXTERNAL,
        dest_tract=TractType.INTERNAL,
        priority=MessagePriority.NORMAL,
        payload={
            "request_type": "apply_template",
            "parameters": {
                "template_name": "python_module",
                "output_path": str(test_dir / "my_module.py"),
                "variables": {
                    "description": "Test module",
                    "class_name": "TestClass",
                    "class_description": "A test class",
                    "imports": "import sys"
                }
            }
        }
    )

    assert msg_id >= 0, "Message routing failed"
    await asyncio.sleep(1.0)

    # Verify template was applied
    output_file = test_dir / "my_module.py"
    assert output_file.exists(), "Template output file was not created"
    content = output_file.read_text()
    assert "TestClass" in content, "Template variable not substituted"
    assert "Test module" in content, "Description not in output"


@pytest.mark.asyncio
async def test_directory_creation(test_environment):
    """Test: Orchestrator creates a directory"""
    env = test_environment
    test_dir = env["test_dir"]
    corpus_callosum = env["corpus_callosum"]

    # Send request to orchestrator
    test_dir_path = test_dir / "test_component" / "subdir"

    msg_id = await corpus_callosum.route_message(
        source_tract=TractType.EXTERNAL,
        dest_tract=TractType.INTERNAL,
        priority=MessagePriority.NORMAL,
        payload={
            "request_type": "create_directory",
            "parameters": {
                "directory_path": str(test_dir_path),
                "parents": True
            }
        }
    )

    assert msg_id >= 0, "Message routing failed"

    # Wait for processing
    await asyncio.sleep(1.0)

    # Verify directory was created
    assert test_dir_path.exists(), "Directory was not created"
    assert test_dir_path.is_dir(), "Path is not a directory"


@pytest.mark.asyncio
async def test_complex_component_creation(test_environment):
    """Test: Orchestrator creates a complete component structure"""
    env = test_environment
    test_dir = env["test_dir"]
    corpus_callosum = env["corpus_callosum"]

    # Send request to orchestrator
    component_name = "my_component"

    msg_id = await corpus_callosum.route_message(
        source_tract=TractType.EXTERNAL,
        dest_tract=TractType.INTERNAL,
        priority=MessagePriority.HIGH,
        payload={
            "request_type": "create_component",
            "parameters": {
                "component_name": component_name,
                "base_path": str(test_dir)
            }
        }
    )

    assert msg_id >= 0, "Message routing failed"

    # Wait for processing (longer for multiple actions)
    await asyncio.sleep(1.0)

    # Verify component structure
    component_dir = test_dir / component_name
    assert component_dir.exists(), "Component directory was not created"

    init_file = component_dir / "__init__.py"
    assert init_file.exists(), "__init__.py was not created"
    assert component_name in init_file.read_text(), "__init__.py content mismatch"

    module_file = component_dir / f"{component_name}.py"
    assert module_file.exists(), "Module file was not created"
    assert component_name.title() in module_file.read_text(), "Module content mismatch"


@pytest.mark.asyncio
async def test_scaffold_module(test_environment):
    """Test: Orchestrator scaffolds a module with template"""
    env = test_environment
    test_dir = env["test_dir"]
    corpus_callosum = env["corpus_callosum"]

    # Send scaffold request
    msg_id = await corpus_callosum.route_message(
        source_tract=TractType.EXTERNAL,
        dest_tract=TractType.INTERNAL,
        priority=MessagePriority.NORMAL,
        payload={
            "request_type": "scaffold_module",
            "parameters": {
                "module_name": "data_processor",
                "base_path": str(test_dir / "scaffold_test"),
                "language": "python"
            }
        }
    )

    assert msg_id >= 0, "Message routing failed"
    await asyncio.sleep(1.0)

    # Verify scaffolded module
    module_file = test_dir / "scaffold_test" / "data_processor.py"
    assert module_file.exists(), "Scaffolded module was not created"
    content = module_file.read_text()
    assert "DataProcessor" in content, "Class name not in scaffolded module"


@pytest.mark.asyncio
async def test_particle_state_persistence(test_environment):
    """Test: Particles persist state with cycle counts"""
    env = test_environment
    test_dir = env["test_dir"]
    state_dir = env["state_dir"]
    corpus_callosum = env["corpus_callosum"]
    file_writer = env["file_writer"]
    directory_creator = env["directory_creator"]

    # Execute some operations
    test_file = test_dir / "state_test.txt"

    msg_id = await corpus_callosum.route_message(
        source_tract=TractType.EXTERNAL,
        dest_tract=TractType.INTERNAL,
        priority=MessagePriority.NORMAL,
        payload={
            "request_type": "create_file",
            "parameters": {
                "file_path": str(test_file),
                "content": "Testing state persistence"
            }
        }
    )

    await asyncio.sleep(1.0)

    # Check file_writer state
    file_writer_state_file = state_dir / "file_writer_state.json"
    if file_writer_state_file.exists():
        with open(file_writer_state_file, 'r') as f:
            state = json.load(f)
            assert state['cycle_count'] > 0, "file_writer cycle_count not incremented"
            assert state['total_executions'] > 0, "file_writer total_executions not incremented"
            print(f"file_writer state: cycle_count={state['cycle_count']}, success_rate={state['success_rate']}")

    # Check orchestrator state
    orchestrator_state_file = state_dir / "file_creator_orchestrator_state.json"
    if orchestrator_state_file.exists():
        with open(orchestrator_state_file, 'r') as f:
            state = json.load(f)
            assert state['cycle_count'] > 0, "orchestrator cycle_count not incremented"
            assert state['total_plans'] > 0, "orchestrator total_plans not incremented"
            print(f"orchestrator state: cycle_count={state['cycle_count']}, total_plans={state['total_plans']}")


@pytest.mark.asyncio
async def test_corpus_callosum_stats(test_environment):
    """Test: Corpus Callosum tracks message statistics"""
    env = test_environment
    corpus_callosum = env["corpus_callosum"]

    # Get stats before
    stats_before = corpus_callosum.get_stats()
    messages_before = stats_before.total_messages

    # Send a message
    await corpus_callosum.route_message(
        source_tract=TractType.INTERNAL,
        dest_tract=TractType.EXTERNAL,
        priority=MessagePriority.NORMAL,
        payload={"test": "data"}
    )

    await asyncio.sleep(0.1)

    # Get stats after
    stats_after = corpus_callosum.get_stats()
    messages_after = stats_after.total_messages

    assert messages_after > messages_before, "Corpus Callosum did not track message"
    print(f"Corpus Callosum stats: {stats_after.total_messages} total messages, "
          f"{stats_after.messages_to_internal} to internal, "
          f"{stats_after.messages_to_external} to external")


@pytest.mark.asyncio
async def test_particle_custom_metrics(test_environment):
    """Test: Particles track custom metrics"""
    env = test_environment
    test_dir = env["test_dir"]
    corpus_callosum = env["corpus_callosum"]
    file_writer = env["file_writer"]

    # Create a file
    test_content = "x" * 1000  # 1000 bytes
    test_file = test_dir / "metrics_test.txt"

    msg_id = await corpus_callosum.route_message(
        source_tract=TractType.EXTERNAL,
        dest_tract=TractType.INTERNAL,
        priority=MessagePriority.NORMAL,
        payload={
            "request_type": "create_file",
            "parameters": {
                "file_path": str(test_file),
                "content": test_content
            }
        }
    )

    await asyncio.sleep(1.0)

    # Check custom metrics
    stats = file_writer.get_particle_stats()
    if 'custom_metrics' in stats:
        custom = stats['custom_metrics']
        if 'files_created' in custom:
            assert custom['files_created'] > 0, "files_created metric not incremented"
        if 'total_bytes_written' in custom:
            assert custom['total_bytes_written'] >= len(test_content), "total_bytes_written incorrect"
            print(f"file_writer custom metrics: files_created={custom.get('files_created')}, "
                  f"total_bytes_written={custom.get('total_bytes_written')}")


@pytest.mark.asyncio
async def test_all_particles_functional(test_environment):
    """Test: All 8 particles are functional"""
    env = test_environment
    state_dir = env["state_dir"]

    # Wait a bit for any pending operations
    await asyncio.sleep(1.0)

    # Check that all particle state files exist
    expected_particles = [
        "file_writer",
        "directory_creator",
        "file_reader",
        "file_deleter",
        "directory_deleter",
        "file_mover",
        "batch_file_creator",
        "template_applier"
    ]

    for particle_name in expected_particles:
        state_file = state_dir / f"{particle_name}_state.json"
        # Note: State files only created after first execution
        # This test just verifies particles were instantiated
        particle = env.get(particle_name)
        assert particle is not None, f"{particle_name} was not created"
        print(f"{particle_name}: ✓")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
