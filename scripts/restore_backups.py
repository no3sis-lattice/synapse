#!/usr/bin/env python3
"""Restore agent files from .bak backups"""

from pathlib import Path

base_dir = Path(__file__).parent.parent / ".synapse" / "agents"

for backup_file in base_dir.rglob("*_agent.py.bak"):
    original_file = backup_file.with_suffix('')
    if original_file.exists():
        original_file.write_text(backup_file.read_text())
        print(f"✓ Restored: {original_file.relative_to(base_dir)}")

print("\n✓ All backups restored")
