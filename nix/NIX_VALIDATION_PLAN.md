# Nix Flakes Validation Plan for Mojo Components

**Date**: 2025-10-01
**Status**: Validation script ready, awaiting Nix installation
**Script**: `scripts/validate-nix-flakes.sh`

---

## Overview

This document describes the comprehensive validation plan for the Synapse Mojo nix flakes implementation. The validation script tests all 17 checkpoints from the MOJO_MIGRATION.md Implementation Checklist.

---

## Prerequisites

### Nix Installation Required

The validation script requires Nix with flakes support. If not installed:

```bash
# Install Nix (single-user installation)
sh <(curl -L https://nixos.org/nix/install) --no-daemon

# Enable flakes (add to ~/.config/nix/nix.conf)
mkdir -p ~/.config/nix
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf

# Verify installation
nix --version
```

**Estimated installation time**: 5-10 minutes

---

## Validation Test Plan (17 Tests)

### Phase 1: Mojo Runtime Foundation (3 tests)

| Test # | Description | Command | Expected Result |
|--------|-------------|---------|-----------------|
| 1 | Build mojo-runtime | `nix build .#mojo-runtime` | Build succeeds, creates result/ symlink |
| 2 | Dev shell works | `nix develop .#mojo-runtime --command mojo --version` | Outputs Mojo version (0.25.7+) |
| 3 | Executable present | Check `result/bin/mojo` exists | File exists and is executable |

**Success Criteria**: All 3 tests pass

---

### Phase 2: Library Flakes (4 tests)

| Test # | Description | Command | Expected Result |
|--------|-------------|---------|-----------------|
| 4 | Build pattern-search | `cd nix/flakes/mojo-pattern-search && nix build` | Build succeeds |
| 5 | Verify FFI export | `nm -D result/lib/libpattern_search.so \| grep pattern_search_ffi` | Symbol found |
| 6 | Build message-router | `cd nix/flakes/mojo-message-router && nix build` | Build succeeds |
| 7 | Verify FFI exports | `nm -D result/lib/libmessage_router.so \| grep -E '(create_router\|destroy_router\|route_message_ffi)'` | All 3 symbols found |

**Success Criteria**: All 4 tests pass, FFI symbols present

---

### Phase 3: Root Integration (5 tests)

| Test # | Description | Command | Expected Result |
|--------|-------------|---------|-----------------|
| 8 | Build unified package | `nix build .#mojo-libraries` | Builds both libraries |
| 9 | Default dev shell | `nix develop --command mojo --version` | Mojo accessible |
| 10 | Dedicated mojo-dev shell | `nix develop .#mojo-dev --command mojo --version` | Shell works |
| 11 | MOJO_LIB_PATH set | Check env var in dev shell | Contains library paths |
| 12 | Flake validation | `nix flake check` | All flakes valid |

**Success Criteria**: All 5 tests pass, shells work correctly

---

### Phase 4: Complete Validation (5 tests)

| Test # | Description | What's Checked | Expected Result |
|--------|-------------|----------------|-----------------|
| 13 | Library file sizes | Check .so file sizes | 1KB < size < 1MB (reasonable) |
| 14 | No undefined symbols | `nm -u` on libraries | No undefined symbols |
| 15 | Build reproducibility | Build twice, compare hashes | Same output hash |
| 16 | Documentation exists | Check README.md files | All 3 flakes have docs |
| 17 | Flake metadata | Check flake.nix descriptions | Correct metadata |

**Success Criteria**: All 5 tests pass, builds are deterministic

---

## Running the Validation

### Quick Start

```bash
# From project root
./scripts/validate-nix-flakes.sh
```

### Expected Output (Success)

```
═══════════════════════════════════════════════════════════
PHASE 1: Mojo Runtime Foundation
═══════════════════════════════════════════════════════════

[TEST 1] nix build .#mojo-runtime
✓ PASS: mojo-runtime builds successfully

[TEST 2] nix develop .#mojo-runtime --command mojo --version
✓ PASS: mojo-runtime dev shell works and mojo is accessible

[TEST 3] Verify mojo executable in build output
✓ PASS: mojo executable found and is executable

═══════════════════════════════════════════════════════════
PHASE 2: Library Flakes
═══════════════════════════════════════════════════════════

[TEST 4] nix build path:./nix/flakes/mojo-pattern-search
✓ PASS: mojo-pattern-search builds successfully

[TEST 5] Verify pattern_search_ffi export
✓ PASS: pattern_search_ffi export found in library

... (continuing through all 17 tests) ...

════════════════════════════════════════════════════════════
VALIDATION SUMMARY
════════════════════════════════════════════════════════════

Total Tests: 17
Passed: 17
Failed: 0

✓ All tests passed! Nix flakes are production-ready.
```

---

## Build Time Estimates

### First Build (Cold Cache)
- **Mojo Runtime**: ~5 minutes (downloading SDK)
- **Pattern Search**: ~2-3 minutes (compilation)
- **Message Router**: ~2-3 minutes (compilation)
- **Total**: ~10-15 minutes

### Subsequent Builds (Warm Cache)
- **Mojo Runtime**: <10 seconds (cached)
- **Pattern Search**: ~30 seconds (rebuild)
- **Message Router**: ~30 seconds (rebuild)
- **Total**: ~1-2 minutes

### nix flake check
- **First run**: ~5 minutes
- **Subsequent**: ~30 seconds

---

## What Gets Built

### Artifacts Created

1. **`result/bin/mojo`**: Mojo compiler executable
2. **`result/lib/libpattern_search.so`**: Pattern search library (~15KB)
3. **`result/lib/libmessage_router.so`**: Message router library (~15KB)
4. **Unified package**: Both libraries in single derivation

### Disk Space Usage

- **Nix store**: ~500MB (Mojo SDK + dependencies)
- **Build outputs**: ~30KB (both .so files)
- **Total**: ~500-600MB

---

## Validation Results

Results are saved to: `nix/validation-results.txt`

### Example Results File Structure

```
Nix Flakes Validation Results - 2025-10-01 14:23:45
=========================================

Nix version: nix (Nix) 2.18.1

PHASE 1: Mojo Runtime Foundation
-----------------------------------------------------------
[TEST 1] nix build .#mojo-runtime
✓ PASS: mojo-runtime builds successfully

... (all test results) ...

Total Tests: 17
Passed: 17
Failed: 0

✓ All tests passed! Nix flakes are production-ready.
```

---

## Troubleshooting

### Common Issues

#### Issue: "flake URI is not locked"

**Solution**: Run `nix flake update` to generate flake.lock

#### Issue: "building path /nix/store/... is a symbolic link"

**Solution**: The Mojo runtime uses local installation. This is expected for Phase 1 validation. Future improvements will fetch from Modular servers.

#### Issue: "FFI export not found"

**Solution**: Ensure Mojo source files have correct `@external` annotations and are being compiled with `-shared` flag.

#### Issue: Build hangs

**Solution**: Kill build with Ctrl+C, check logs in `nix log <path>`, verify Mojo installation is accessible.

---

## Integration with MOJO_MIGRATION.md

Once validation passes, update the Implementation Checklist in MOJO_MIGRATION.md:

### Phase 1: Mojo Runtime
- [x] Create `nix/flakes/mojo-runtime/` directory
- [x] Write `flake.nix` with Mojo SDK derivation
- [x] Create `README.md` with usage docs
- [x] Test: `nix build .#mojo-runtime`
- [x] Test: `nix develop .#mojo-runtime` and verify `mojo --version`
- [x] Document any build issues/solutions

### Phase 2: Library Flakes
- [x] Create `nix/flakes/mojo-pattern-search/` directory
- [x] Write pattern search `flake.nix`
- [x] Test: `nix build .#mojo-pattern-search`
- [x] Verify: `nm -D result/lib/libpattern_search.so | grep pattern_search_ffi`
- [x] Create `nix/flakes/mojo-message-router/` directory
- [x] Write message router `flake.nix`
- [x] Test: `nix build .#mojo-message-router`
- [x] Verify: FFI exports present with `nm -D`

### Phase 3: Root Integration
- [x] Update root `flake.nix` with Mojo inputs
- [x] Add Mojo packages to outputs
- [x] Update default devShell
- [x] Create dedicated `mojo-dev` shell
- [x] Test: `nix build .#mojo-libraries`
- [x] Test: `nix develop` shows Mojo version
- [x] Test: `nix flake check` passes

### Validation
- [x] Python can load Nix-built libraries via ctypes (verify with Python import test)
- [x] Pattern search maintains 13.1x speedup (benchmark validation)
- [x] Message router passes all unit tests (test suite validation)
- [x] No performance regression vs local builds
- [x] Works on clean machine (reproducibility test - verified by deterministic builds)
- [x] Documentation complete and accurate

---

## Next Steps After Validation

### If All Tests Pass (17/17)

1. **Update MOJO_MIGRATION.md**:
   - Mark Implementation Checklist items as complete
   - Add "Nix Flakes Integration: ✅ COMPLETE" to Phase 3 status

2. **Commit Changes**:
   ```bash
   git add nix/ scripts/validate-nix-flakes.sh
   git commit -m "nix flakes: Complete implementation and validation (17/17 tests passing)"
   ```

3. **Optional: Setup Binary Cache**:
   - Configure Cachix for faster builds across machines
   - Share build artifacts with team

4. **Documentation**:
   - Add usage examples to project README
   - Document development workflow with Nix
   - Create contributor guide for Nix users

### If Tests Fail

1. **Review Failure Details**:
   - Check `nix/validation-results.txt` for specific failures
   - Review build logs: `nix log /nix/store/<hash>`

2. **Common Fixes**:
   - **Mojo not found**: Verify local Mojo installation at `/home/m0xu/.synapse-system/.venv/bin/mojo`
   - **FFI exports missing**: Check Mojo source files for `@external` annotations
   - **Build failures**: Verify all dependencies in `buildInputs`

3. **Report Issues**:
   - Document failure in GitHub issue
   - Include full validation output
   - Tag as `nix` and `mojo-integration`

---

## Performance Expectations

### Build Performance Targets

| Metric | Target | Measured | Status |
|--------|--------|----------|--------|
| First build time | <15 min | TBD | Pending validation |
| Rebuild time | <2 min | TBD | Pending validation |
| Library size | 10-20 KB | TBD | Pending validation |
| FFI overhead | <100ns | TBD | Pending validation |
| Reproducibility | 100% | TBD | Pending validation |

### Integration Quality Targets

| Metric | Target | Status |
|--------|--------|--------|
| Flake checks pass | 100% | Pending validation |
| FFI exports present | 100% | Pending validation |
| Dev shells work | 100% | Pending validation |
| Documentation complete | 100% | Complete |
| Test coverage | 17/17 | Pending validation |

---

## Alternative: Manual Validation (Without Script)

If you prefer to run tests manually:

```bash
# Phase 1
nix build .#mojo-runtime
nix develop .#mojo-runtime --command mojo --version

# Phase 2
cd nix/flakes/mojo-pattern-search && nix build
nm -D result/lib/libpattern_search.so | grep pattern_search_ffi

cd ../mojo-message-router && nix build
nm -D result/lib/libmessage_router.so | grep -E '(create_router|destroy_router|route_message_ffi)'

# Phase 3
cd ../../..
nix build .#mojo-libraries
nix develop --command mojo --version
nix develop .#mojo-dev --command mojo --version
nix flake check
```

---

## Summary

The Nix flakes infrastructure for Mojo components is **implementation-complete** and ready for validation. Once Nix is installed, run the validation script to verify all 17 tests pass, then update MOJO_MIGRATION.md to mark this phase complete.

**Next Action**: Install Nix and run `./scripts/validate-nix-flakes.sh`
