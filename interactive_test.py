#!/usr/bin/env python3
"""
Interactive Manual Testing for file_creator MVP
Menu-driven interface for testing each particle individually

Run with: uv run python interactive_test.py
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
from file_reader import create_file_reader
from file_deleter import create_file_deleter
from directory_deleter import create_directory_deleter
from file_mover import create_file_mover
from batch_file_creator import create_batch_file_creator
from template_applier import create_template_applier
from file_creator_orchestrator import create_file_creator_orchestrator


class InteractiveTester:
    """Interactive manual testing interface"""

    def __init__(self):
        self.test_dir = None
        self.state_dir = None
        self.corpus_callosum = None
        self.particles = {}
        self.orchestrator = None

    async def setup(self):
        """Initialize test environment"""
        print("\n🔧 Setting up test environment...")

        # Create temp directory
        self.test_dir = Path(tempfile.mkdtemp(prefix="synapse_interactive_"))
        self.state_dir = self.test_dir / "particles"
        self.state_dir.mkdir(parents=True, exist_ok=True)

        print(f"   Test directory: {self.test_dir}")

        # Initialize Corpus Callosum
        print("   Starting Corpus Callosum...")
        self.corpus_callosum = ReactiveCorpusCallosum(
            enable_pattern_synthesis=True,
            enable_event_sourcing=False
        )
        await self.corpus_callosum.start()

        # Create all particles
        print("   Creating particles...")
        self.particles['file_writer'] = create_file_writer(
            self.corpus_callosum,
            state_file=self.state_dir / "file_writer_state.json"
        )
        self.particles['directory_creator'] = create_directory_creator(
            self.corpus_callosum,
            state_file=self.state_dir / "directory_creator_state.json"
        )
        self.particles['file_reader'] = create_file_reader(
            self.corpus_callosum,
            state_file=self.state_dir / "file_reader_state.json"
        )
        self.particles['file_deleter'] = create_file_deleter(
            self.corpus_callosum,
            state_file=self.state_dir / "file_deleter_state.json"
        )
        self.particles['directory_deleter'] = create_directory_deleter(
            self.corpus_callosum,
            state_file=self.state_dir / "directory_deleter_state.json"
        )
        self.particles['file_mover'] = create_file_mover(
            self.corpus_callosum,
            state_file=self.state_dir / "file_mover_state.json"
        )
        self.particles['batch_file_creator'] = create_batch_file_creator(
            self.corpus_callosum,
            state_file=self.state_dir / "batch_file_creator_state.json"
        )
        self.particles['template_applier'] = create_template_applier(
            self.corpus_callosum,
            state_file=self.state_dir / "template_applier_state.json"
        )

        # Create orchestrator
        print("   Creating orchestrator...")
        self.orchestrator = create_file_creator_orchestrator(
            self.corpus_callosum,
            state_file=self.state_dir / "file_creator_orchestrator_state.json"
        )

        # Start all
        print("   Starting agents...")
        for particle in self.particles.values():
            await particle.start()
        await self.orchestrator.start()

        await asyncio.sleep(0.1)  # Let agents subscribe

        print("✅ Environment ready!\n")

    async def cleanup(self):
        """Cleanup test environment"""
        print("\n🧹 Cleaning up...")

        for particle in self.particles.values():
            await particle.stop()
        await self.orchestrator.stop()
        await self.corpus_callosum.stop()

        print(f"   Test files remain in: {self.test_dir}")
        print("   (Delete manually if needed)")

    async def send_request(self, request_type: str, parameters: dict):
        """Send request to orchestrator"""
        msg_id = await self.corpus_callosum.route_message(
            source_tract=TractType.EXTERNAL,
            dest_tract=TractType.INTERNAL,
            priority=MessagePriority.NORMAL,
            payload={
                "request_type": request_type,
                "parameters": parameters
            }
        )
        print(f"   Message sent: ID={msg_id}")
        await asyncio.sleep(1.0)  # Wait for processing
        return msg_id

    async def test_create_file(self):
        """Test: Create a single file"""
        print("\n" + "="*60)
        print("TEST: Create File")
        print("="*60)

        file_path = input("\nEnter file path (relative to test dir): ").strip()
        content = input("Enter file content: ").strip()

        full_path = self.test_dir / file_path

        await self.send_request("create_file", {
            "file_path": str(full_path),
            "content": content
        })

        if full_path.exists():
            print(f"\n✅ Success: File created at {full_path}")
            print(f"   Content: {full_path.read_text()}")
        else:
            print(f"\n❌ Failed: File not created")

    async def test_create_directory(self):
        """Test: Create directory"""
        print("\n" + "="*60)
        print("TEST: Create Directory")
        print("="*60)

        dir_path = input("\nEnter directory path (relative to test dir): ").strip()

        full_path = self.test_dir / dir_path

        await self.send_request("create_directory", {
            "directory_path": str(full_path),
            "parents": True
        })

        if full_path.exists() and full_path.is_dir():
            print(f"\n✅ Success: Directory created at {full_path}")
        else:
            print(f"\n❌ Failed: Directory not created")

    async def test_read_file(self):
        """Test: Read file"""
        print("\n" + "="*60)
        print("TEST: Read File")
        print("="*60)

        file_path = input("\nEnter file path to read (relative to test dir): ").strip()
        full_path = self.test_dir / file_path

        if not full_path.exists():
            print(f"\n❌ File doesn't exist: {full_path}")
            return

        await self.send_request("read_file", {
            "file_path": str(full_path)
        })

        print(f"\n✅ Read request sent (check logs for result)")

    async def test_delete_file(self):
        """Test: Delete file"""
        print("\n" + "="*60)
        print("TEST: Delete File")
        print("="*60)

        file_path = input("\nEnter file path to delete (relative to test dir): ").strip()
        full_path = self.test_dir / file_path

        if not full_path.exists():
            print(f"\n❌ File doesn't exist: {full_path}")
            return

        await self.send_request("delete_file", {
            "file_path": str(full_path)
        })

        if not full_path.exists():
            print(f"\n✅ Success: File deleted")
        else:
            print(f"\n❌ Failed: File still exists")

    async def test_move_file(self):
        """Test: Move/rename file"""
        print("\n" + "="*60)
        print("TEST: Move/Rename File")
        print("="*60)

        source = input("\nEnter source file path (relative to test dir): ").strip()
        dest = input("Enter destination path: ").strip()

        source_path = self.test_dir / source
        dest_path = self.test_dir / dest

        if not source_path.exists():
            print(f"\n❌ Source file doesn't exist: {source_path}")
            return

        await self.send_request("move_file", {
            "source_path": str(source_path),
            "dest_path": str(dest_path)
        })

        if dest_path.exists() and not source_path.exists():
            print(f"\n✅ Success: File moved to {dest_path}")
        else:
            print(f"\n❌ Failed: File move incomplete")

    async def test_batch_create(self):
        """Test: Batch file creation"""
        print("\n" + "="*60)
        print("TEST: Batch File Creation")
        print("="*60)

        print("\nEnter files (one per line, format: path|content)")
        print("Press Enter on empty line to finish")

        files = []
        while True:
            line = input("> ").strip()
            if not line:
                break

            if '|' not in line:
                print("Invalid format. Use: path|content")
                continue

            path, content = line.split('|', 1)
            files.append({
                "path": str(self.test_dir / path.strip()),
                "content": content.strip()
            })

        if not files:
            print("\n❌ No files specified")
            return

        await self.send_request("batch_create_files", {
            "files": files
        })

        created = sum(1 for f in files if Path(f["path"]).exists())
        print(f"\n✅ Created {created}/{len(files)} files")

    async def show_stats(self):
        """Show system statistics"""
        print("\n" + "="*60)
        print("SYSTEM STATISTICS")
        print("="*60)

        # Corpus Callosum stats
        stats = self.corpus_callosum.get_stats()
        print(f"\n📊 Corpus Callosum:")
        print(f"   Total messages: {stats.total_messages}")
        print(f"   To INTERNAL: {stats.messages_to_internal}")
        print(f"   To EXTERNAL: {stats.messages_to_external}")

        # Particle stats
        print(f"\n⚛️  Particle Statistics:")
        for name, particle in self.particles.items():
            pstats = particle.get_particle_stats()
            print(f"\n   {name}:")
            print(f"      Executions: {pstats['total_executions']}")
            print(f"      Success rate: {pstats['success_rate']:.1%}")
            print(f"      Cycle count: {pstats['cycle_count']}")

    async def list_files(self):
        """List files in test directory"""
        print("\n" + "="*60)
        print("TEST DIRECTORY CONTENTS")
        print("="*60)

        def show_tree(path: Path, prefix: str = ""):
            items = sorted(path.iterdir())
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                connector = "└── " if is_last else "├── "
                print(f"{prefix}{connector}{item.name}")

                if item.is_dir():
                    extension = "    " if is_last else "│   "
                    show_tree(item, prefix + extension)

        print(f"\n{self.test_dir}/")
        show_tree(self.test_dir)

    async def run_menu(self):
        """Main menu loop"""
        await self.setup()

        while True:
            print("\n" + "="*60)
            print("SYNAPSE INTERACTIVE TESTER")
            print("="*60)
            print("\n1. Create File")
            print("2. Create Directory")
            print("3. Read File")
            print("4. Delete File")
            print("5. Move/Rename File")
            print("6. Batch Create Files")
            print("7. Show Statistics")
            print("8. List Test Directory")
            print("9. Exit")

            choice = input("\nSelect option (1-9): ").strip()

            try:
                if choice == '1':
                    await self.test_create_file()
                elif choice == '2':
                    await self.test_create_directory()
                elif choice == '3':
                    await self.test_read_file()
                elif choice == '4':
                    await self.test_delete_file()
                elif choice == '5':
                    await self.test_move_file()
                elif choice == '6':
                    await self.test_batch_create()
                elif choice == '7':
                    await self.show_stats()
                elif choice == '8':
                    await self.list_files()
                elif choice == '9':
                    break
                else:
                    print("\n❌ Invalid choice")

            except KeyboardInterrupt:
                print("\n\nOperation cancelled")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()

        await self.cleanup()


async def main():
    """Entry point"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  Synapse Interactive Tester                                ║")
    print("║  Manual Testing Interface for file_creator MVP            ║")
    print("╚════════════════════════════════════════════════════════════╝")

    tester = InteractiveTester()
    await tester.run_menu()

    print("\n✨ Testing session complete!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
