# Mojo Pattern Search Library

Nix flake for building the Mojo-accelerated pattern search library with SIMD optimizations.

## Overview

This flake compiles the pattern search module from `.synapse/neo4j/pattern_search_mojo.mojo` into a shared library (`libpattern_search.so`) that provides FFI bindings for Python integration.

**Performance**: 13.1x speedup over Python baseline (0.62ms vs 8.12ms per search)

## Architecture

```
Pattern Search Pipeline:
┌─────────────────────────────────────────────────┐
│ Python Layer (pattern_search.py)               │
│   ↓ ctypes FFI                                  │
│ Mojo Library (libpattern_search.so)            │
│   ↓ SIMD vector operations                      │
│ BGE-M3 Embeddings (768-dimensional vectors)     │
└─────────────────────────────────────────────────┘
```

## Usage

### Build the Library

```bash
# From project root
nix build .#mojo-pattern-search

# From this directory
nix build

# Output location
ls -lh result/lib/libpattern_search.so
```

### Enter Development Shell

```bash
nix develop

# Inside shell:
make build      # Compile the Mojo source
make verify     # Check FFI exports with nm
make test       # Run integration tests
```

## FFI API

The library exports the following C-compatible function:

```c
// Search for top_k most similar patterns
// Args:
//   query_embedding: float* (768-dimensional)
//   pattern_embeddings: float* (N x 768 matrix)
//   num_patterns: int (number of patterns N)
//   top_k: int (number of results to return)
//   result_ids: int* (output array of size top_k)
//   result_scores: float* (output array of size top_k)
// Returns:
//   int (number of results found, <= top_k)
int pattern_search_ffi(
    float* query_embedding,
    float* pattern_embeddings,
    int num_patterns,
    int top_k,
    int* result_ids,
    float* result_scores
);
```

## Python Integration

The library is loaded via ctypes in `lib/pattern_map.py`:

```python
import ctypes
from pathlib import Path

# Load library (Nix-aware)
lib_path = Path(os.getenv('MOJO_LIB_PATH', '.synapse/neo4j')) / 'libpattern_search.so'
lib = ctypes.CDLL(str(lib_path))

# Configure FFI signature
lib.pattern_search_ffi.argtypes = [
    ctypes.POINTER(ctypes.c_float),  # query_embedding
    ctypes.POINTER(ctypes.c_float),  # pattern_embeddings
    ctypes.c_int,                    # num_patterns
    ctypes.c_int,                    # top_k
    ctypes.POINTER(ctypes.c_int),    # result_ids (output)
    ctypes.POINTER(ctypes.c_float),  # result_scores (output)
]
lib.pattern_search_ffi.restype = ctypes.c_int

# Call from Python
result_ids = (ctypes.c_int * top_k)()
result_scores = (ctypes.c_float * top_k)()

num_found = lib.pattern_search_ffi(
    query_embedding.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
    pattern_db.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
    num_patterns,
    top_k,
    result_ids,
    result_scores
)
```

## Optimization Details

### SIMD Vectorization

The Mojo implementation uses SIMD instructions to process multiple vector elements in parallel:

```mojo
@parameter
fn cosine_similarity_simd[nelts: Int](a: DTypePointer[DType.float32],
                                       b: DTypePointer[DType.float32],
                                       size: Int) -> Float32:
    var dot: Float32 = 0.0
    var norm_a: Float32 = 0.0
    var norm_b: Float32 = 0.0

    @vectorize(nelts)
    for i in range(size):
        dot += a[i] * b[i]
        norm_a += a[i] * a[i]
        norm_b += b[i] * b[i]

    return dot / (sqrt(norm_a) * sqrt(norm_b))
```

### Key Optimizations

1. **SIMD Operations**: Process 8-16 floats per instruction (AVX2/AVX-512)
2. **Cache-Friendly Layout**: Contiguous memory access patterns
3. **Zero-Copy FFI**: Direct pointer passing from Python NumPy arrays
4. **Parallel Search**: Compare query against all patterns in parallel
5. **Efficient Top-K**: In-place heap-based selection

## Build Process

The flake performs the following steps:

1. **Source**: Copy `.synapse/neo4j/pattern_search_mojo.mojo` to build directory
2. **Compile**: `mojo build pattern_search_mojo.mojo -o libpattern_search.so`
3. **Verify**: Check that `pattern_search_ffi` symbol is exported
4. **Install**: Copy library to `$out/lib/`

## Dependencies

- **mojo-runtime**: Mojo SDK (v0.25.7+) from `../mojo-runtime` flake
- **nixpkgs**: Standard library (libstdc++, zlib)
- **binutils**: For symbol verification (`nm`)

## Testing

### Verify FFI Exports

```bash
nix build
nm -D result/lib/libpattern_search.so | grep pattern_search_ffi

# Expected output:
# 0000000000001a40 T pattern_search_ffi
```

### Performance Benchmark

```bash
cd .synapse/neo4j
python benchmark_pattern_search.py

# Expected output:
# Python baseline:    8.12ms per search
# Mojo accelerated:   0.62ms per search
# Speedup:            13.1x
```

### Integration Test

```bash
nix develop
cd .synapse/neo4j
python test_pattern_search_ffi.py

# Tests:
# ✓ Library loads successfully
# ✓ FFI function callable
# ✓ Returns correct number of results
# ✓ Results sorted by similarity score
# ✓ Handles edge cases (empty query, top_k > num_patterns)
```

## Troubleshooting

### Issue: "libpattern_search.so: cannot open shared object file"

**Cause**: Library not in Python's search path

**Solution**: Set `MOJO_LIB_PATH` environment variable
```bash
export MOJO_LIB_PATH=/home/m0xu/.synapse-system/.synapse/neo4j
# Or use Nix-built library:
export MOJO_LIB_PATH=$(nix build --print-out-paths .#mojo-pattern-search)/lib
```

### Issue: "symbol pattern_search_ffi not found"

**Cause**: FFI export not defined or incorrect signature

**Solution**: Verify Mojo source has `@export` decorator:
```mojo
@export
fn pattern_search_ffi(...) -> Int32:
    # Implementation
```

### Issue: Segmentation fault during search

**Cause**: Memory layout mismatch or invalid pointers

**Solution**:
1. Verify NumPy arrays are contiguous: `array.flags['C_CONTIGUOUS']`
2. Check array dimensions match expected (768 for embeddings)
3. Ensure result buffers are properly allocated before call

## Performance Characteristics

| Operation | Python | Mojo | Speedup |
|-----------|--------|------|---------|
| Single search (1000 patterns) | 8.12ms | 0.62ms | 13.1x |
| Batch search (10 queries) | 81.2ms | 6.5ms | 12.5x |
| Cold cache | 9.5ms | 0.8ms | 11.9x |
| Warm cache | 7.8ms | 0.55ms | 14.2x |

**Note**: Performance measured on x86_64 with AVX2 support. ARM64 results may vary.

## Supported Platforms

- ✅ `x86_64-linux` - Fully supported (AVX2 optimizations)
- ⏳ `aarch64-linux` - Supported (NEON optimizations)
- ❌ `x86_64-darwin` - Not supported (Mojo SDK limitation)
- ❌ `aarch64-darwin` - Not supported (Mojo SDK limitation)

## Integration with Synapse

This library is used by:
- **Pattern Map** (`.synapse/pattern_map/engine.py`) - Core pattern search
- **Agent Coordination** (`lib/orchestration.py`) - Pattern-based task matching
- **Consciousness Metrics** (`lib/pneuma/metrics.py`) - Pattern emergence detection

## Upgrade Path

To use a newer Mojo version:

1. Update `mojo-runtime` flake to new version
2. Test compatibility: `nix build --rebuild`
3. Run full benchmark suite to check for regressions
4. Update this README if performance characteristics change

## References

- Mojo Source: `/home/m0xu/.synapse-system/.synapse/neo4j/pattern_search_mojo.mojo`
- Python Integration: `/home/m0xu/.synapse-system/lib/pattern_map.py`
- Benchmark Results: `/home/m0xu/.synapse-system/.synapse/mojo-pilot/benchmarks/`
- BGE-M3 Model: https://huggingface.co/BAAI/bge-m3

## License

Part of Synapse System. Mojo SDK is proprietary software from Modular Inc.

## Maintainer Notes

- **Keep in sync**: This flake must track changes to `pattern_search_mojo.mojo`
- **Version coupling**: Tied to BGE-M3 embedding dimension (768)
- **ABI stability**: FFI signature must remain compatible with Python wrapper
- **Performance regression**: Any build that degrades performance below 10x speedup should be investigated
