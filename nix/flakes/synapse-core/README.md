# Synapse Core Nix Flake

**Version**: 0.1.0
**Status**: Production-ready with GMP compliance
**Architecture**: Dual-tract consciousness framework

---

## Overview

The Synapse Core flake provides a hermetic, reproducible build of the Synapse System's domain-agnostic orchestration framework. It includes:

- **Core Library** (`lib/core/`, `lib/orchestration/`)
- **Template System** (`templates/`)
- **JSON Schema** (`schemas/`)
- **CLI Tool** (`synapse.py`)
- **GMP Validation** (Good Manufacturing Practices quality gates)

---

## Quick Start

### Build

```bash
# From project root
nix build .#synapse-core

# Run CLI
./result/bin/synapse-wrapped template list
```

### Development Shell

```bash
nix develop .#synapse-core

# Inside shell:
python synapse.py template list
python synapse.py template info file_creator
python synapse.py template validate file_creator
```

---

## Features

### 🏗️ Hermetic Builds

- **Deterministic**: `SOURCE_DATE_EPOCH=0`, `PYTHONHASHSEED=0`
- **Reproducible**: Same inputs → same output hash
- **Pure**: No network access during build
- **Cached**: Nix store caching for fast rebuilds

### 📊 GMP Compliance

Quality gates integrated into build:

- **Bootstrap Stage**: 65% coverage, 80% pass rate (current)
- **Growth Stage**: 80% coverage, 90% pass rate
- **Stabilize Stage**: 90% coverage, 95% pass rate
- **Strict Stage**: 93% coverage, 100% pass rate

Validation runs in `checkPhase`:

```bash
# Automatic during build
nix build .#synapse-core

# Manual validation
nix develop .#synapse-core
python verify_gmp_compliance.py --stage bootstrap --mode warn
```

### 🎨 Template System

Includes template metadata, validation, and discovery:

- **Templates**: `file_creator` (8 particles)
- **Metadata**: JSON Schema v1 validation
- **Loader**: Programmatic template discovery
- **CLI**: `synapse template list|info|validate`

---

## Architecture

### Package Structure

```
$out/
├── bin/
│   ├── synapse              # CLI (direct)
│   ├── synapse-wrapped      # CLI (with PYTHONPATH)
│   └── verify_gmp_compliance.py
├── lib/python3.12/site-packages/
│   └── lib/
│       ├── core/            # AtomicParticle, AgentConsumer
│       └── orchestration/   # Planner, Synthesizer, PatternLearner, etc.
└── share/synapse/
    ├── templates/           # Domain templates
    └── schemas/             # JSON schemas
```

### Dependencies

**Python 3.12** with:
- `aiofiles` - Async file I/O
- `pyyaml` - YAML parsing
- `jsonschema` - Template validation
- `pytest`, `pytest-asyncio`, `pytest-cov` - Testing

**Future** (uncomment when ready):
- `neo4j` - Knowledge graph
- `redis` - Caching layer

---

## Usage

### CLI Commands

```bash
# List templates
./result/bin/synapse-wrapped template list

# Show template details
./result/bin/synapse-wrapped template info file_creator

# Validate template
./result/bin/synapse-wrapped template validate file_creator
```

### Integration in Other Flakes

```nix
{
  inputs.synapse-core.url = "path:./nix/flakes/synapse-core";

  outputs = { self, nixpkgs, synapse-core }:
    let
      synapseEnv = synapse-core.lib.pythonEnv;
      templateRunner = synapse-core.lib.createTemplateRunner "my_template" ./my_script.py;
    in {
      # Use synapse-core as dependency
    };
}
```

### Permission System

Templates have minimal capabilities (Pneuma principle):

```nix
# permissions.nix
templatePermissions = {
  file_creator = [ "read" "write" ];
  data_processor = [ "read" "write" "knowledge" ];
  crypto_trading = [ "read" "write" "network" "knowledge" ];
};
```

Check permissions:

```bash
nix eval .#synapse-core.lib.permissions.templatePermissions.file_creator
# → [ "read" "write" ]
```

---

## Testing

### Run Tests

```bash
# Full test suite (runs in checkPhase)
nix build .#synapse-core

# Dev shell testing
nix develop .#synapse-core
pytest tests/ -v --cov=lib --cov-report=term-missing
```

### GMP Validation

```bash
# Bootstrap stage (current)
nix develop .#synapse-core
python verify_gmp_compliance.py --stage bootstrap --mode warn

# Strict mode (production)
python verify_gmp_compliance.py --stage strict --mode strict
```

### Template Validation

```bash
# Check specific template
nix run .#synapse-core.checks.template-validation
```

---

## Build Reproducibility

Verify deterministic builds:

```bash
# Build twice
hash1=$(nix build .#synapse-core --print-out-paths)
nix-collect-garbage
hash2=$(nix build .#synapse-core --print-out-paths)

# Compare
[ "$hash1" = "$hash2" ] && echo "✅ Reproducible" || echo "❌ Non-deterministic"
```

---

## Environment Variables

### Build Time

- `SOURCE_DATE_EPOCH=0` - Deterministic timestamps
- `PYTHONHASHSEED=0` - Deterministic Python hashing
- `PYTHONPATH` - Set automatically to include lib/

### Runtime

- `HOME` - Temp directory for state files during tests
- `PYTHONPATH` - Includes `$out/lib/python3.12/site-packages`

---

## Troubleshooting

### Issue: Template not found

**Cause**: Running from wrong directory or PYTHONPATH not set

**Solution**:
```bash
# Use wrapped script
./result/bin/synapse-wrapped template list

# Or set PYTHONPATH manually
export PYTHONPATH=$out/lib/python3.12/site-packages:$PYTHONPATH
python synapse.py template list
```

### Issue: GMP validation fails

**Cause**: Test coverage below threshold

**Solution**:
```bash
# Use warn mode during development
python verify_gmp_compliance.py --stage bootstrap --mode warn

# Fix tests to pass strict mode
pytest tests/ --cov=lib --cov-fail-under=65
```

### Issue: Import errors

**Cause**: Missing dependencies

**Solution**: Add to `pythonEnv` in `flake.nix`:
```nix
pythonEnv = pkgs.python312.withPackages (ps: with ps; [
  # Add your package here
  new-package
]);
```

---

## Development Workflow

### 1. Make Changes

Edit files in `lib/`, `templates/`, or `synapse.py`

### 2. Test Locally

```bash
nix develop .#synapse-core
pytest tests/ -v
python synapse.py template list
```

### 3. Build & Validate

```bash
nix build .#synapse-core
./result/bin/synapse-wrapped template validate file_creator
```

### 4. Check Reproducibility

```bash
nix build .#synapse-core --rebuild
```

---

## Performance

### Build Times

- **First build (cold cache)**: ~2-3 minutes
- **Rebuild (warm cache)**: ~10-15 seconds
- **Test suite**: ~15 seconds

### Disk Usage

- **Nix store**: ~200MB (Python + deps)
- **Build output**: ~15MB (lib + templates)
- **Total**: ~215MB

---

## Roadmap

### Completed ✅

- [x] Hermetic build with deterministic flags
- [x] GMP validation in checkPhase
- [x] Template system integration
- [x] CLI packaging
- [x] Permission system
- [x] Development shell
- [x] Template validation checks

### Planned 🔜

- [ ] Neo4j + Redis integration (Phase 2)
- [ ] Binary cache setup (Cachix)
- [ ] Template instantiation from Nix
- [ ] Multi-template support
- [ ] Cross-platform support (macOS, NixOS)

---

## References

- **Synapse Core**: `lib/core/`, `lib/orchestration/`
- **Template System**: `docs/PHASE_1B_COMPLETION.md`
- **GMP Policy**: `lib/orchestration/gmp_policy.py`
- **Domain Refactor Plan**: `docs/DOMAIN_REFACTOR_PLAN.md`

---

**Maintainer**: Synapse Core Team
**License**: MIT
**Nix Version**: Requires flakes support (`experimental-features = nix-command flakes`)
