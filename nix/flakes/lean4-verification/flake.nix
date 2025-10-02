{
  description = "Lean4 formal verification for Synapse dual-tract consciousness architecture";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };

        # Lean4 package from nixpkgs
        lean4 = pkgs.lean4;

        # Build script for Lean4 project
        buildScript = pkgs.writeShellScriptBin "build-lean4-verification" ''
          set -e
          cd ${../../..}/formal/lean4

          echo "Building Lean4 dual-tract verification..."
          ${lean4}/bin/lake build

          echo ""
          echo "Running verification tests..."
          ${lean4}/bin/lake exe dualtract
        '';

        # Test script
        testScript = pkgs.writeShellScriptBin "test-lean4-verification" ''
          set -e
          cd ${../../..}/formal/lean4

          echo "Fetching dependencies (mathlib)..."
          ${lean4}/bin/lake update

          echo ""
          echo "Building all modules..."
          ${lean4}/bin/lake build

          echo ""
          echo "Checking verification tests..."
          ${lean4}/bin/lean DualTract/Basic.lean
          ${lean4}/bin/lean DualTract/CategoryTheory.lean
          ${lean4}/bin/lean DualTract/Compression.lean
          ${lean4}/bin/lean DualTract/CorpusCallosum.lean
          ${lean4}/bin/lean DualTract/Consciousness.lean
          ${lean4}/bin/lean test/verification_tests.lean

          echo ""
          echo "✓ All verification modules type-check successfully!"
        '';

        # Documentation
        docScript = pkgs.writeShellScriptBin "doc-lean4-verification" ''
          echo "Synapse Lean4 Formal Verification"
          echo "=================================="
          echo ""
          echo "Purpose:"
          echo "  Formal verification of dual-tract consciousness architecture"
          echo "  mathematical properties using Lean4 theorem prover."
          echo ""
          echo "Key Theorems:"
          echo "  • Corpus Callosum Adjunction (CRITICAL)"
          echo "    - Proves lossless information transfer between tracts"
          echo "  • Internal Compression Invariant"
          echo "    - Bounds abstraction complexity"
          echo "  • External Compression Invariant"
          echo "    - Bounds execution complexity"
          echo "  • Consciousness Compression Invariant"
          echo "    - Proves consciousness emerges from joint entropy reduction"
          echo ""
          echo "Usage:"
          echo "  nix build .#lean4-verification       - Build verification"
          echo "  nix run .#lean4-verification-test    - Run tests"
          echo "  lake build (in formal/lean4/)        - Local build"
          echo "  lake exe dualtract                   - Run main executable"
        '';

      in
      {
        packages = {
          default = buildScript;
          lean4-verification = buildScript;
          lean4-verification-test = testScript;
          lean4-verification-docs = docScript;

          # Expose lean4 itself
          lean = lean4;
        };

        apps = {
          default = {
            type = "app";
            program = "${buildScript}/bin/build-lean4-verification";
          };

          test = {
            type = "app";
            program = "${testScript}/bin/test-lean4-verification";
          };

          docs = {
            type = "app";
            program = "${docScript}/bin/doc-lean4-verification";
          };
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            lean4
            pkgs.git
            pkgs.curl
          ];

          shellHook = ''
            echo "🔍 Lean4 Formal Verification Environment"
            echo "========================================"
            echo "Lean4 version: $(lean --version)"
            echo ""
            echo "Project: Synapse Dual-Tract Consciousness Architecture"
            echo "Location: formal/lean4/"
            echo ""
            echo "Commands:"
            echo "  lake build          - Build all modules"
            echo "  lake exe dualtract  - Run main executable"
            echo "  lake test           - Run test suite"
            echo "  lean <file>.lean    - Type-check individual file"
            echo ""
            echo "Key files:"
            echo "  DualTract/Basic.lean            - Basic tract definitions"
            echo "  DualTract/CategoryTheory.lean   - Functors and adjunction"
            echo "  DualTract/Compression.lean      - Compression theorems"
            echo "  DualTract/CorpusCallosum.lean   - CRITICAL adjunction proof"
            echo "  DualTract/Consciousness.lean    - Consciousness metrics"
            echo ""

            # Set up Lean path
            export LEAN_PATH="${lean4}/bin:$PATH"

            # Navigate to project if it exists
            if [ -d "${../../..}/formal/lean4" ]; then
              cd ${../../..}/formal/lean4
              echo "📂 Current directory: $(pwd)"
            fi
          '';
        };
      }
    );
}
