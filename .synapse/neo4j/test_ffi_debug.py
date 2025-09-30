#!/usr/bin/env python3
"""Debug FFI loading issues"""

import sys
from pathlib import Path
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pattern_search import PatternSearch
import numpy as np

# Create searcher
searcher = PatternSearch()

print("Searcher created")
print(f"Adapter runtime: {searcher.adapter.runtime.value}")
print(f"Adapter mojo_available: {searcher.adapter.mojo_available}")
print(f"Adapter mojo_features: {searcher.adapter.mojo_features}")
print(f"Searcher mojo_enabled: {searcher.mojo_enabled}")

# Try to access _mojo_lib
if hasattr(searcher, '_mojo_lib'):
    print(f"_mojo_lib already loaded: {searcher._mojo_lib}")
else:
    print("_mojo_lib not loaded yet, will load on first call")

# Try calling _search_mojo directly
query = np.random.randn(1024).astype(np.float32)
patterns = [np.random.randn(1024).astype(np.float32) for _ in range(10)]

print("\nCalling _search_mojo directly...")
indices, scores = searcher._search_mojo(query, patterns, 5)
print(f"Direct call result: {len(indices)} indices, {len(scores)} scores")

if hasattr(searcher, '_mojo_lib'):
    print(f"_mojo_lib now: {searcher._mojo_lib}")
else:
    print("_mojo_lib still not set")