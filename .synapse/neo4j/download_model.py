#!/usr/bin/env python3
"""
Download and cache BGE-M3 model for Synapse
============================================

Downloads the BAAI/bge-m3 sentence transformer model (~2GB) and caches it
locally for faster loading in production.

Usage:
    python download_model.py [--model-path PATH]
"""

import sys
import argparse
from pathlib import Path
from sentence_transformers import SentenceTransformer

DEFAULT_MODEL_PATH = "../data/models/bge-m3"


def download_model(model_path: str = DEFAULT_MODEL_PATH):
    """Download and cache BGE-M3 model"""
    # Resolve relative path from script location
    script_dir = Path(__file__).parent
    target_path = (script_dir / model_path).resolve()

    print(f"Downloading BGE-M3 model to: {target_path}")
    print("This may take several minutes (~2GB download)...")

    # Download model
    model = SentenceTransformer('BAAI/bge-m3')

    # Create target directory
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Save model
    model.save(str(target_path))

    # Verify
    if target_path.exists():
        size_mb = sum(f.stat().st_size for f in target_path.rglob('*')) / (1024 * 1024)
        print(f"✓ BGE-M3 model downloaded successfully ({size_mb:.1f} MB)")
        print(f"Location: {target_path}")
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
