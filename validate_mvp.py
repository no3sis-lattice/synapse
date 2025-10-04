#!/usr/bin/env python3
"""
Quick validation script for file_creator MVP Day 1
Verifies all components are properly implemented
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

def validate_files():
    """Validate all required files exist"""
    print("=== Validating File Structure ===")

    required_files = [
        "lib/registry.json",
        "lib/atomic_particle.py",
        "lib/particles/file_writer.py",
        "lib/particles/directory_creator.py",
        "lib/orchestrators/file_creator_orchestrator.py",
        "tests/test_file_creator_mvp.py"
    ]

    base = Path(__file__).parent
    missing = []

    for file_path in required_files:
        full_path = base / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            missing.append(file_path)

    return len(missing) == 0


def validate_imports():
    """Validate all modules can be imported"""
    print("\n=== Validating Imports ===")

    try:
        print("Importing atomic_particle...")
        from atomic_particle import AtomicParticle
        print("✓ AtomicParticle")

        print("Importing file_writer...")
        from particles.file_writer import FileWriter, create_file_writer
        print("✓ FileWriter")

        print("Importing directory_creator...")
        from particles.directory_creator import DirectoryCreator, create_directory_creator
        print("✓ DirectoryCreator")

        print("Importing file_creator_orchestrator...")
        from orchestrators.file_creator_orchestrator import FileCreatorOrchestrator, create_file_creator_orchestrator
        print("✓ FileCreatorOrchestrator")

        return True

    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_registry():
    """Validate registry.json structure"""
    print("\n=== Validating Registry ===")

    try:
        import json
        registry_path = Path(__file__).parent / "lib" / "registry.json"

        with open(registry_path, 'r') as f:
            registry = json.load(f)

        # Check required keys
        assert "agents" in registry, "Missing 'agents' key"
        assert "tract_classification" in registry, "Missing 'tract_classification' key"
        assert "compression_mapping" in registry, "Missing 'compression_mapping' key"

        # Check agents
        agents = registry["agents"]
        assert "file_creator_orchestrator" in agents, "Missing orchestrator"
        assert "file_writer" in agents, "Missing file_writer"
        assert "directory_creator" in agents, "Missing directory_creator"

        # Check tract classification
        tracts = registry["tract_classification"]
        assert "INTERNAL" in tracts, "Missing INTERNAL tract"
        assert "EXTERNAL" in tracts, "Missing EXTERNAL tract"
        assert "file_creator_orchestrator" in tracts["INTERNAL"], "Orchestrator not in INTERNAL tract"
        assert "file_writer" in tracts["EXTERNAL"], "file_writer not in EXTERNAL tract"

        # Check compression mapping
        compression = registry["compression_mapping"]
        assert "BWT" in compression, "Missing BWT mapping"
        assert "MTF" in compression, "Missing MTF mapping"
        assert "RLE" in compression, "Missing RLE mapping"
        assert "Huffman" in compression, "Missing Huffman mapping"

        print("✓ Registry structure valid")
        print(f"  - {len(agents)} agents registered")
        print(f"  - {len(tracts['INTERNAL'])} INTERNAL agents")
        print(f"  - {len(tracts['EXTERNAL'])} EXTERNAL agents")

        return True

    except Exception as e:
        print(f"✗ Registry validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validations"""
    print("╔════════════════════════════════════════════════════╗")
    print("║  file_creator MVP Day 1 Validation                 ║")
    print("╚════════════════════════════════════════════════════╝\n")

    results = []

    results.append(("File Structure", validate_files()))
    results.append(("Registry", validate_registry()))
    results.append(("Imports", validate_imports()))

    print("\n" + "="*50)
    print("VALIDATION SUMMARY")
    print("="*50)

    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False

    print("="*50)

    if all_passed:
        print("\n✅ All validations passed! MVP Day 1 implementation complete.")
        print("\nNext steps:")
        print("  1. Run integration tests: pytest tests/test_file_creator_mvp.py -v")
        print("  2. Review file_creator_MVP.md for implementation status")
        print("  3. Begin Day 2: Validation & Expansion")
        return 0
    else:
        print("\n❌ Some validations failed. Please fix errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
