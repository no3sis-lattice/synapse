{
  description = "Mojo-accelerated cross-tract message router";

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

        libmessage_router = pkgs.stdenv.mkDerivation {
          pname = "libmessage_router";
          version = "0.1.0";

          # Source from actual project location (three levels up: nix/flakes/mojo-message-router -> project root)
          src = ../../../.synapse/corpus_callosum;

          buildInputs = [
            mojo-runtime.packages.${system}.default
          ];

          buildPhase = ''
            echo "Building message_router.mojo with Mojo compiler..."
            ${mojoPath} build message_router.mojo -o libmessage_router.so

            echo "Verifying FFI exports..."
            ${pkgs.binutils}/bin/nm -D libmessage_router.so | grep -E '(create_router|destroy_router|route_message_ffi)' || {
              echo "ERROR: Expected FFI exports not found!"
              exit 1
            }
          '';

          installPhase = ''
            mkdir -p $out/lib
            cp libmessage_router.so $out/lib/

            echo "Installed to: $out/lib/libmessage_router.so"
          '';

          meta = {
            description = "SIMD-optimized message router for Corpus Callosum";
            performance = "Target: 100x+ faster than Python ThreadPoolExecutor";
            homepage = "https://github.com/yourusername/synapse-system";
          };
        };

      in {
        packages = {
          default = libmessage_router;
          libmessage_router = libmessage_router;
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            mojo-runtime.packages.${system}.default
            pkgs.python312
            pkgs.binutils
          ];

          shellHook = ''
            echo "📨 Message Router Development Environment"
            echo "Mojo: ${mojoPath}"
            echo ""
            echo "Commands:"
            echo "  make build      - Compile message_router.mojo"
            echo "  make verify     - Check FFI exports"
            echo "  make test       - Run unit tests"
            echo ""
            echo "Source: .synapse/corpus_callosum/message_router.mojo"
            echo "Output: libmessage_router.so"

            export MOJO_LIB_PATH="$(pwd)/.synapse/corpus_callosum"
          '';
        };
      });
}
