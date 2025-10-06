{
  description = "Mojo-accelerated pattern search (13.1x speedup)";

  inputs = {
    nixpkgs.url = "github:meta-introspector/nixpkgs?ref=feature/CRQ-016-nixify";
    flake-utils.url = "github:numtide/flake-utils";
    mojo-runtime = {
      url = "path:../mojo-runtime";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, mojo-runtime }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        mojoPath = mojo-runtime.lib.mojoPath system;

        # Pre-built library (compiled outside Nix due to 1,371x slowdown in sandbox)
        # Use absolute path to force Nix to copy the .so into its store
        prebuiltLib = /home/m0xu/1-projects/synapse/.synapse/neo4j/libpattern_search.so;

        libpattern_search = pkgs.stdenv.mkDerivation {
          pname = "libpattern_search";
          version = "0.1.0";

          # Source: Mojo source file only
          src = ../../../.synapse/neo4j;

          buildInputs = [
            mojo-runtime.packages.${system}.default
          ];

          # NOTE: Mojo compilation exhibits 1,371x slowdown in Nix sandbox due to
          # LLVM syscall overhead. We package pre-built artifacts instead.
          # See: nix/flakes/mojo-pattern-search/README.md for workflow details

          unpackPhase = ''
            runHook preUnpack

            # Copy source directory
            cp -r $src source-tmp
            chmod -R u+w source-tmp

            # Copy pre-built .so file into source
            cp ${prebuiltLib} source-tmp/libpattern_search.so
            chmod u+w source-tmp/libpattern_search.so

            # Set source root
            export sourceRoot=$PWD/source-tmp
            cd $sourceRoot

            runHook postUnpack
          '';

          buildPhase = ''
            echo "Validating pre-built Mojo library..."

            # Check if pre-built library exists
            if [ ! -f libpattern_search.so ]; then
              echo "ERROR: Pre-built libpattern_search.so not found in source"
              echo ""
              echo "Build it first with:"
              echo "  cd ${../../../.synapse/neo4j}"
              echo "  mojo build --emit=shared-lib pattern_search_mojo.mojo -o libpattern_search.so"
              echo ""
              echo "Expected location: .synapse/neo4j/libpattern_search.so"
              exit 1
            fi

            echo "✅ Found pre-built library: libpattern_search.so"

            # Verify it's a valid ELF shared library
            file libpattern_search.so | grep "ELF.*shared object" || {
              echo "ERROR: libpattern_search.so is not a valid ELF shared library"
              exit 1
            }
            echo "✅ Valid ELF shared object"

            # Verify FFI exports
            ${pkgs.binutils}/bin/nm -D libpattern_search.so | grep pattern_search_ffi || {
              echo "ERROR: FFI export 'pattern_search_ffi' not found!"
              echo "Library may not be compiled correctly."
              exit 1
            }
            echo "✅ FFI exports verified: pattern_search_ffi found"
          '';

          installPhase = ''
            mkdir -p $out/lib
            cp libpattern_search.so $out/lib/

            echo "Installed to: $out/lib/libpattern_search.so"
          '';

          meta = {
            description = "SIMD-optimized pattern search for Synapse Pattern Map";
            performance = "13.1x speedup over Python baseline (0.62ms vs 8.12ms)";
            homepage = "https://github.com/yourusername/synapse-system";
          };
        };

      in {
        packages = {
          default = libpattern_search;
          libpattern_search = libpattern_search;
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            mojo-runtime.packages.${system}.default
            pkgs.python312
            pkgs.binutils  # For nm to check exports
          ];

          shellHook = ''
            echo "🔍 Pattern Search Development Environment"
            echo "Mojo: ${mojoPath}"
            echo ""
            echo "Commands:"
            echo "  make build      - Compile pattern_search_mojo.mojo"
            echo "  make verify     - Check FFI exports"
            echo "  make test       - Run integration tests"
            echo ""
            echo "Source: .synapse/neo4j/pattern_search_mojo.mojo"
            echo "Output: libpattern_search.so"

            # Set library path for Python testing
            export MOJO_LIB_PATH="$(pwd)/.synapse/neo4j"
          '';
        };
      });
}
