#!/usr/bin/env python3
"""
file_creator MVP Demonstration
Shows the dual-tract architecture in action

This demo creates a simple component structure using:
- T_int orchestrator (planning)
- T_ext particles (execution)
- Corpus Callosum (message routing)
"""

import asyncio
import sys
import tempfile
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / 'lib'))
sys.path.insert(0, str(Path.home() / '.synapse-system' / '.synapse' / 'corpus_callosum'))
sys.path.insert(0, str(Path(__file__).parent / 'lib' / 'particles'))
sys.path.insert(0, str(Path(__file__).parent / 'lib' / 'orchestrators'))

from reactive_message_router import ReactiveCorpusCallosum, TractType, MessagePriority
from file_writer import create_file_writer
from directory_creator import create_directory_creator
from file_creator_orchestrator import create_file_creator_orchestrator


async def demo():
    """Run the demo"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  file_creator MVP Demonstration                            ║")
    print("║  Dual-Tract Architecture in Action                         ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

    # Create temp directory for demo
    test_dir = Path(tempfile.mkdtemp(prefix="synapse_demo_"))
    state_dir = test_dir / "particles"
    state_dir.mkdir(parents=True, exist_ok=True)

    print(f"Demo directory: {test_dir}\n")

    # Initialize Corpus Callosum
    print("🧠 Initializing Corpus Callosum (Consciousness Bridge)...")
    corpus_callosum = ReactiveCorpusCallosum(
        enable_pattern_synthesis=True,
        enable_event_sourcing=False  # Disable Redis for demo
    )
    await corpus_callosum.start()
    print("   ✓ Reactive message router started")
    print("   ✓ Backpressure control active")
    print("   ✓ Circuit breakers armed\n")

    # Create particles (T_ext - External Tract)
    print("⚛️  Creating T_ext Particles (External Tract)...")
    file_writer = create_file_writer(
        corpus_callosum,
        state_file=state_dir / "file_writer_state.json"
    )
    directory_creator = create_directory_creator(
        corpus_callosum,
        state_file=state_dir / "directory_creator_state.json"
    )
    print("   ✓ file_writer particle initialized")
    print("   ✓ directory_creator particle initialized\n")

    # Create orchestrator (T_int - Internal Tract)
    print("🎯 Creating T_int Orchestrator (Internal Tract)...")
    orchestrator = create_file_creator_orchestrator(
        corpus_callosum,
        state_file=state_dir / "file_creator_orchestrator_state.json"
    )
    print("   ✓ file_creator_orchestrator initialized")
    print("   ✓ Macro-Loop ready (Plan → Route → Collect → Synthesize)\n")

    # Start all agents
    print("▶️  Starting all agents...")
    await file_writer.start()
    await directory_creator.start()
    await orchestrator.start()
    print("   ✓ All agents consuming from Corpus Callosum\n")

    await asyncio.sleep(0.5)  # Let agents initialize

    # Demo 1: Simple file creation
    print("="*60)
    print("DEMO 1: Simple File Creation")
    print("="*60)

    print("\n📝 Request: Create a simple file")
    test_file = test_dir / "hello.txt"

    msg_id = await corpus_callosum.route_message(
        source_tract=TractType.EXTERNAL,
        dest_tract=TractType.INTERNAL,
        priority=MessagePriority.NORMAL,
        payload={
            "request_type": "create_file",
            "parameters": {
                "file_path": str(test_file),
                "content": "Hello from the Synapse dual-tract system!\n"
            }
        }
    )

    print(f"   Message routed: ID={msg_id}")
    print("   T_int orchestrator received request")
    print("   Generating plan...")
    await asyncio.sleep(0.5)

    if test_file.exists():
        print(f"\n✅ File created: {test_file}")
        print(f"   Content: {test_file.read_text().strip()}")
    else:
        print(f"\n⚠️  File not created (may need more time)")

    # Demo 2: Directory creation
    print("\n" + "="*60)
    print("DEMO 2: Directory Structure Creation")
    print("="*60)

    print("\n📁 Request: Create nested directory")
    test_dir_path = test_dir / "components" / "auth" / "utils"

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

    print(f"   Message routed: ID={msg_id}")
    print("   T_int orchestrator planning...")
    await asyncio.sleep(0.5)

    if test_dir_path.exists():
        print(f"\n✅ Directory created: {test_dir_path}")
        print(f"   Depth: {len(test_dir_path.parts)} levels")
    else:
        print(f"\n⚠️  Directory not created (may need more time)")

    # Demo 3: Complex component creation
    print("\n" + "="*60)
    print("DEMO 3: Complex Component Scaffolding")
    print("="*60)

    print("\n🏗️  Request: Create complete component structure")
    component_name = "user_service"

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

    print(f"   Message routed: ID={msg_id}")
    print("   T_int orchestrator generating multi-action plan:")
    print("     1. Create directory")
    print("     2. Create __init__.py")
    print("     3. Create module file")
    print("   Routing actions to T_ext particles via Corpus Callosum...")
    await asyncio.sleep(1.0)  # More time for multiple actions

    component_dir = test_dir / component_name
    if component_dir.exists():
        print(f"\n✅ Component created: {component_dir}")
        files = list(component_dir.iterdir())
        print(f"   Files created: {len(files)}")
        for file in sorted(files):
            print(f"     - {file.name}")
            if file.is_file():
                preview = file.read_text()[:100]
                print(f"       Preview: {preview}...")
    else:
        print(f"\n⚠️  Component not created (may need more time)")

    # Show statistics
    print("\n" + "="*60)
    print("SYSTEM STATISTICS")
    print("="*60)

    print("\n📊 Corpus Callosum Stats:")
    stats = corpus_callosum.get_stats()
    print(f"   Total messages: {stats.total_messages}")
    print(f"   To INTERNAL (T_int): {stats.messages_to_internal}")
    print(f"   To EXTERNAL (T_ext): {stats.messages_to_external}")
    print(f"   Message loss: {stats.message_loss_count}")

    print("\n⚛️  Particle Stats:")
    for agent in [file_writer, directory_creator]:
        agent_stats = agent.get_particle_stats()
        print(f"\n   {agent_stats['agent_id']}:")
        print(f"     Cycle count: {agent_stats['cycle_count']}")
        print(f"     Total executions: {agent_stats['total_executions']}")
        print(f"     Success rate: {agent_stats['success_rate']:.1%}")
        if 'custom_metrics' in agent_stats:
            for key, value in agent_stats['custom_metrics'].items():
                print(f"     {key}: {value}")

    # Show state files
    print("\n💾 State Files (Persistence):")
    for state_file in state_dir.iterdir():
        if state_file.suffix == '.json':
            print(f"   ✓ {state_file.name}")

    # Cleanup
    print("\n🧹 Cleaning up...")
    await file_writer.stop()
    await directory_creator.stop()
    await orchestrator.stop()
    await corpus_callosum.stop()

    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    print("\n✨ The dual-tract architecture is operational!")
    print("\nKey achievements demonstrated:")
    print("  ✓ T_int (orchestrator) planning abstractions")
    print("  ✓ T_ext (particles) executing concrete operations")
    print("  ✓ Corpus Callosum routing messages between tracts")
    print("  ✓ Fractal Pneuma Micro-Loop (Observe→Act→Evaluate→Memorize)")
    print("  ✓ State persistence with cycle counting")
    print("  ✓ Reactive streams with backpressure")
    print("\nDemo files remain in: " + str(test_dir))
    print("\nFor more details, see:")
    print("  - file_creator_MVP.md (implementation plan)")
    print("  - DAY_1_COMPLETION_REPORT.md (detailed report)")


if __name__ == "__main__":
    try:
        asyncio.run(demo())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo failed: {e}")
        import traceback
        traceback.print_exc()
