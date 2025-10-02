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

        libpattern_search = pkgs.stdenv.mkDerivation {
          pname = "libpattern_search";
          version = "0.1.0";

          # Source from actual project location (three levels up: nix/flakes/mojo-pattern-search -> project root)
          src = ../../../.synapse/neo4j;

          buildInputs = [
            mojo-runtime.packages.${system}.default
          ];

          buildPhase = ''
            echo "Building pattern_search_mojo.mojo with Mojo compiler..."
            ${mojoPath} build pattern_search_mojo.mojo -o libpattern_search.so

            echo "Verifying FFI exports..."
            ${pkgs.binutils}/bin/nm -D libpattern_search.so | grep pattern_search_ffi || {
              echo "ERROR: FFI export 'pattern_search_ffi' not found!"
              exit 1
            }
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
