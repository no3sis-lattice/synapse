# Mojo Runtime Flake

Nix flake providing the Mojo SDK runtime for Synapse System.

## Overview

This flake packages the Mojo programming language compiler and runtime, making it available for use in other Synapse Nix flakes and development environments.

**Version**: 0.25.7
**Source**: Local Mojo installation (`.venv/bin/mojo`)
**Future**: Will migrate to fetching from Modular servers

## Usage

### Build the Runtime

```bash
# From project root
nix build .#mojo-runtime

# From this directory
nix build
```

### Enter Development Shell

```bash
# From project root
nix develop .#mojo-runtime

# From this directory
nix develop
```

The development shell provides:
- `mojo` command in PATH
- Mojo compiler version 0.25.7+
- All required runtime dependencies

### Use in Other Flakes

```nix
{
  inputs = {
    mojo-runtime = {
      url = "path:../mojo-runtime";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, mojo-runtime }:
    let
      mojoPath = mojo-runtime.lib.mojoPath;
    in {
      # Use mojoPath in build phases
      packages.default = pkgs.stdenv.mkDerivation {
        buildPhase = ''
          ${mojoPath} build myfile.mojo -o output
        '';
      };
    };
}
```

## Exposed Outputs

### Packages

- `packages.default` - Mojo runtime derivation
- `packages.mojo` - Alias for default

### Library

- `lib.mojoPath` - Path to mojo compiler (use in dependent flakes)

### Development Shells

- `devShells.default` - Shell with mojo command available

## Implementation Details

### Current Source Strategy

**Phase 1** (Current): Uses existing local Mojo installation
- Source: `/home/m0xu/.synapse-system/.venv/bin/mojo`
- Reason: Fast iteration, no external dependencies
- Limitation: Not fully reproducible (requires local Mojo install)

**Phase 2** (Future): Fetch from Modular servers
- Will use `pkgs.fetchurl` to download SDK
- URL: `https://dl.modular.com/mojo/v25.6/mojo-sdk-linux-x86_64.tar.gz`
- Enables fully reproducible builds

### Build Process

1. Copy mojo binary from local installation
2. Apply `autoPatchelfHook` to fix dynamic library paths
3. Install to `$out/bin/mojo`
4. Expose path via `lib.mojoPath`

### Dependencies

The flake handles Mojo's dynamic library requirements:
- `stdenv.cc.cc.lib` - C++ standard library
- `zlib` - Compression library
- `autoPatchelfHook` - Automatic ELF path patching

## Testing

### Verify Build

```bash
nix build
ls -lh result/bin/mojo  # Should show mojo binary
```

### Verify Runtime

```bash
nix develop
mojo --version  # Should show 0.25.7 or higher
```

### Test Compilation

```bash
nix develop

# Create test file
echo 'fn main(): print("Hello from Nix!")' > test.mojo

# Compile and run
mojo run test.mojo
# Expected output: Hello from Nix!
```

## Troubleshooting

### Issue: "mojo: command not found"

**Cause**: Mojo not in PATH
**Solution**: Ensure you're in `nix develop` shell

### Issue: "cannot execute binary file"

**Cause**: Architecture mismatch or ELF patching failed
**Solution**: Check that you're on x86_64-linux and autoPatchelfHook ran

### Issue: Build fails with "source does not exist"

**Cause**: Local Mojo installation not found at expected path
**Solution**:
1. Verify Mojo installed: `ls /home/m0xu/.synapse-system/.venv/bin/mojo`
2. If missing, install Mojo: `curl -s https://get.modular.com | sh -`
3. Update `src` path in flake.nix if installed elsewhere

## Supported Platforms

- ✅ `x86_64-linux` - Fully supported
- ⏳ `aarch64-linux` - Planned (Mojo supports ARM64)
- ❌ `x86_64-darwin` - Not supported (Mojo SDK not available)
- ❌ `aarch64-darwin` - Not supported (Mojo SDK not available)

## Integration with Synapse

This flake is used by:
- `mojo-pattern-search` - Pattern search library compilation
- `mojo-message-router` - Message router library compilation
- Root `flake.nix` - Mojo development shell

## Upgrade Path

To upgrade Mojo version:

1. Install new Mojo version locally: `modular install mojo@<version>`
2. Update `mojoVersion` in `flake.nix`
3. Rebuild: `nix build --rebuild`
4. Test: `nix develop` and verify `mojo --version`
5. Update dependent flakes if API changes

## References

- Mojo Documentation: https://docs.modular.com/mojo/
- Modular SDK: https://www.modular.com/max/install
- Nix Flakes: https://nixos.wiki/wiki/Flakes
- Synapse Mojo Migration: `../../MOJO_MIGRATION.md`

## License

Mojo is proprietary software from Modular Inc. This Nix flake simply packages the binary for use in Synapse System.

## Maintainer Notes

- Keep `mojoVersion` in sync with actual Mojo installation
- Monitor Modular releases for new versions
- Test compatibility with all dependent flakes before upgrading
- Document breaking changes in CHANGELOG.md
