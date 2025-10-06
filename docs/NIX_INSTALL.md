# Nix Installation Guide for Synapse

This guide explains how to install Nix with flakes support to build and test the Synapse Mojo components.

## Quick Install (Recommended)

```bash
# Install Nix with multi-user support (recommended)
curl -L https://nixos.org/nix/install | sh -s -- --daemon

# Enable flakes and nix-command
mkdir -p ~/.config/nix
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf

# Restart your shell or source the Nix profile
source /etc/profile.d/nix.sh
# OR for single-user install:
source ~/.nix-profile/etc/profile.d/nix.sh
```

## Verify Installation

```bash
# Check Nix is installed
nix --version
# Expected: nix (Nix) 2.18.0 or higher

# Check flakes are enabled
nix flake --help
# Should show flake commands without error
```

## Run Build Tests

Once Nix is installed:

```bash
cd /home/m0xu/.synapse-system

# Make test script executable
chmod +x nix-build-test.sh

# Run the comprehensive test suite
./nix-build-test.sh
```

The test suite will:
1. Validate all three Mojo flakes individually
2. Test root flake integration
3. Verify FFI exports in compiled libraries
4. Test development shells
5. Provide detailed pass/fail report

## Expected Test Results

When all tests pass, you should see:

```
=========================================
Test Results Summary
=========================================

Total tests run: 17
Passed: 17
Failed: 0

✓ All tests passed!
```

## Manual Testing (Alternative)

If you prefer to test manually:

```bash
# Test individual flakes
nix flake check ./nix/flakes/mojo-runtime
nix flake check ./nix/flakes/mojo-pattern-search
nix flake check ./nix/flakes/mojo-message-router

# Build libraries
nix build .#mojo-libraries

# Verify FFI exports
nm -D result/lib/libpattern_search.so | grep pattern_search_ffi
nm -D result/lib/libmessage_router.so | grep -E '(create_router|destroy_router|route_message_ffi)'

# Enter development shell
nix develop

# Check Mojo available in shell
mojo --version
echo $MOJO_LIB_PATH
```

## Build Performance Tips

**Use Binary Cache** (optional, speeds up builds):
```bash
# Add Cachix for Nix community cache
nix-env -iA cachix -f https://cachix.org/api/v1/install
cachix use nixpkgs
```

**Parallel Builds**:
```bash
# Enable parallel builds (add to ~/.config/nix/nix.conf)
echo "max-jobs = auto" >> ~/.config/nix/nix.conf
echo "cores = 0" >> ~/.config/nix/nix.conf
```

## Troubleshooting

### Issue: "experimental features not enabled"

**Solution**: Enable flakes in config
```bash
mkdir -p ~/.config/nix
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
```

### Issue: "command not found: nix"

**Solution**: Source the Nix profile
```bash
# Multi-user install
source /etc/profile.d/nix.sh

# Single-user install
source ~/.nix-profile/etc/profile.d/nix.sh

# Add to your shell rc file (~/.bashrc or ~/.zshrc)
```

### Issue: Build fails with "source does not exist"

**Solution**: Verify Mojo installation
```bash
ls -la /home/m0xu/.synapse-system/.venv/bin/mojo
# Should show mojo binary

# If missing, check mojo-runtime flake.nix source path
```

### Issue: "path not found in flake"

**Solution**: Check you're in the project root
```bash
cd /home/m0xu/.synapse-system
pwd  # Should be /home/m0xu/.synapse-system
```

### Issue: FFI exports not found

**Solution**: Check Mojo source files have @export decorators
```bash
grep "@export" .synapse/neo4j/pattern_search_mojo.mojo
grep "@export" .synapse/corpus_callosum/message_router.mojo
```

## System Requirements

- **OS**: Linux (x86_64 or aarch64)
- **Disk**: ~2GB for Nix + dependencies
- **RAM**: 4GB recommended for builds
- **Mojo**: v0.25.7+ installed in `.venv/bin/mojo`

## Uninstall Nix (if needed)

```bash
# Multi-user install
sudo rm -rf /nix /etc/nix
sudo rm /etc/profile.d/nix.sh

# Remove Nix daemon
sudo systemctl stop nix-daemon.service
sudo systemctl disable nix-daemon.service

# Clean user profile
rm -rf ~/.nix-*
```

## Next Steps After Installation

1. **Run tests**: `./nix-build-test.sh`
2. **Review output**: `nix flake show`
3. **Enter shell**: `nix develop`
4. **Build libraries**: `nix build .#mojo-libraries`
5. **Test Python integration**: Import via ctypes in Python

## References

- Official Nix Install: https://nixos.org/download.html
- Nix Flakes: https://nixos.wiki/wiki/Flakes
- Synapse Mojo Migration: `MOJO_MIGRATION.md`
- Build Test Script: `nix-build-test.sh`
