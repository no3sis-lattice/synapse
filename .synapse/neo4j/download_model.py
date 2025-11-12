#!/usr/bin/env python3
"""
Download and cache BGE-M3 model for Synapse
============================================

Downloads the BAAI/bge-m3 sentence transformer model (~2GB) and caches it
locally for faster loading in production.

DRY Principle: Checks HuggingFace cache first to avoid duplication.

Usage:
    python download_model.py [--model-path PATH]
"""

import os
import sys
import argparse
from pathlib import Path
from sentence_transformers import SentenceTransformer

DEFAULT_MODEL_PATH = "../data/models/bge-m3"


def find_hf_cache_model():
    """Find BGE-M3 model in HuggingFace cache"""
    hf_cache = Path.home() / ".cache" / "huggingface" / "hub" / "models--BAAI--bge-m3"

    if hf_cache.exists():
        # Find the snapshots directory with model files
        snapshots_dir = hf_cache / "snapshots"
        if snapshots_dir.exists():
            # Get the latest snapshot (most recent directory)
            snapshots = sorted(snapshots_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
            if snapshots:
                return snapshots[0]
    return None


def get_model_size(path: Path) -> float:
    """Calculate total size of model in MB"""
    if not path.exists():
        return 0.0
    if path.is_file():
        return path.stat().st_size / (1024 * 1024)
    return sum(f.stat().st_size for f in path.rglob('*') if f.is_file()) / (1024 * 1024)


def download_model(model_path: str = DEFAULT_MODEL_PATH):
    """Download and cache BGE-M3 model (DRY: checks HuggingFace cache first)"""
    script_dir = Path(__file__).parent
    target_path = (script_dir / model_path).resolve()

    # Check if target already exists
    if target_path.exists():
        size_mb = get_model_size(target_path)
        print(f"✓ BGE-M3 model already exists at {target_path}")
        print(f"  Size: {size_mb:.1f} MB")
        return True

    # Check HuggingFace cache first (DRY principle)
    hf_model_path = find_hf_cache_model()
    if hf_model_path:
        size_mb = get_model_size(hf_model_path)
        print(f"✓ Found BGE-M3 in HuggingFace cache ({size_mb:.1f} MB)")
        print(f"  Cache location: {hf_model_path}")
        print(f"  Creating symlink to avoid duplication (DRY)...")

        # Create parent directory for symlink
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Create symlink instead of copying
        try:
            target_path.symlink_to(hf_model_path)
            print(f"✓ Symlink created: {target_path} -> {hf_model_path}")
            return True
        except OSError as e:
            print(f"⚠ Failed to create symlink: {e}")
            print(f"  Falling back to copy...")

    # If cache not found or symlink failed, download normally
    print(f"Downloading BGE-M3 model to: {target_path}")
    print("This may take several minutes (~2GB download)...")

    # Download model (this will use HuggingFace cache automatically)
    model = SentenceTransformer('BAAI/bge-m3')

    # Create target directory
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Save model
    model.save(str(target_path))

    # Verify
    if target_path.exists():
        size_mb = get_model_size(target_path)
        print(f"✓ BGE-M3 model downloaded successfully ({size_mb:.1f} MB)")
        print(f"  Location: {target_path}")
        return True
    else:
        print(f"✗ Model download failed", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Download BGE-M3 model for Synapse")
    parser.add_argument(
        "--model-path",
        default=DEFAULT_MODEL_PATH,
        help=f"Path to save model (default: {DEFAULT_MODEL_PATH})"
    )

    args = parser.parse_args()

    success = download_model(args.model_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
