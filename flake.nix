{
  description = "A lattice of flakes for the Synapse system.";

  inputs = {
    # External dependencies
    nixpkgs.url = "github:meta-introspector/nixpkgs?ref=feature/CRQ-016-nixify";
    flake-utils.url = "github:numtide/flake-utils";

    # Internal toolchain dependencies
    pip2nix = {
      url = "github:meta-introspector/pip2nix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
    };

    # Agent flakes (internal modules) - using GitHub URLs with dir parameter
    base-agent = { url = "github:sub0xdai/synapse-system?dir=nix/flakes/base-agent"; inputs.nixpkgs.follows = "nixpkgs"; };
    architect = { url = "github:sub0xdai/synapse-system?dir=nix/flakes/architect"; inputs.nixpkgs.follows = "nixpkgs"; };
    clarity-judge = { url = "github:sub0xdai/synapse-system?dir=nix/flakes/clarity-judge"; inputs.nixpkgs.follows = "nixpkgs"; };
    code-hound = { url = "github:sub0xdai/synapse-system?dir=nix/flakes/code-hound"; inputs.nixpkgs.follows = "nixpkgs"; };
    devops-engineer = { url = "github:sub0xdai/synapse-system?dir=nix/flakes/devops-engineer"; inputs.nixpkgs.follows = "nixpkgs"; };
    docs-writer = { url = "github:sub0xdai/synapse-system?dir=nix/flakes/docs-writer"; inputs.nixpkgs.follows = "nixpkgs"; };
    file-creator = { url = "github:sub0xdai/synapse-system?dir=nix/flakes/file-creator"; inputs.nixpkgs.follows = "nixpkgs"; };
    git-workflow = { url = "github:sub0xdai/synapse-system?dir=nix/flakes/git-workflow"; inputs.nixpkgs.follows = "nixpkgs"; };
    golang-specialist = { url = "github:sub0xdai/synapse-system?dir=nix/flakes/golang-specialist"; inputs.nixpkgs.follows = "nixpkgs"; };
    python-specialist = { url = "github:sub0xdai/synapse-system?dir=nix/flakes/python-specialist"; inputs.nixpkgs.follows = "nixpkgs"; };
    rust-specialist = { url = "github:sub0xdai/synapse-system?dir=nix/flakes/rust-specialist"; inputs.nixpkgs.follows = "nixpkgs"; };
    security-specialist = { url = "github:sub0xdai/synapse-system?dir=nix/flakes/security-specialist"; inputs.nixpkgs.follows = "nixpkgs"; };
    boss = { url = "github:sub0xdai/synapse-system?dir=nix/flakes/boss"; inputs.nixpkgs.follows = "nixpkgs"; };
    test-runner = { url = "github:sub0xdai/synapse-system?dir=nix/flakes/test-runner"; inputs.nixpkgs.follows = "nixpkgs"; };
    tool-runner = { url = "github:sub0xdai/synapse-system?dir=nix/flakes/tool-runner"; inputs.nixpkgs.follows = "nixpkgs"; };
    typescript-specialist = { url = "github:sub0xdai/synapse-system?dir=nix/flakes/typescript-specialist"; inputs.nixpkgs.follows = "nixpkgs"; };
    ux-designer = { url = "github:sub0xdai/synapse-system?dir=nix/flakes/ux-designer"; inputs.nixpkgs.follows = "nixpkgs"; };
    pneuma = {
      url = "github:sub0xdai/synapse-system?dir=nix/flakes/pneuma";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.base-agent.follows = "base-agent";
    };

    # Mojo components - immutable GitHub references for performance layer
    mojo-runtime = {
      url = "github:sub0xdai/synapse-system?dir=nix/flakes/mojo-runtime";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    mojo-pattern-search = {
      url = "github:sub0xdai/synapse-system?dir=nix/flakes/mojo-pattern-search";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.mojo-runtime.follows = "mojo-runtime";
    };

    mojo-message-router = {
      url = "github:sub0xdai/synapse-system?dir=nix/flakes/mojo-message-router";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.mojo-runtime.follows = "mojo-runtime";
    };

    # Formal verification - immutable GitHub reference for proof system
    lean4-verification = {
      url = "github:sub0xdai/synapse-system?dir=nix/flakes/lean4-verification";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    # Synapse Core - immutable GitHub reference for core orchestration framework
    synapse-core = {
      url = "github:sub0xdai/synapse-system?dir=nix/flakes/synapse-core";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, pip2nix, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };

        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          redis
        ]);

        # Import modular components
        pythonBase = import ./nix/modules/python-base.nix { inherit pkgs system; };
        neo4jTools = import ./nix/modules/neo4j-tools.nix { inherit pkgs system; pythonBase = pythonBase; };
        bossAgent = import ./nix/modules/agents/boss.nix { inherit pkgs system; pythonBase = pythonBase; neo4jTools = neo4jTools; };
        fileCreatorOrchestrator = import ./nix/modules/orchestrators/file-creator.nix { inherit pkgs system; pythonBase = pythonBase; };

      in
      {
        packages = {
          default = pkgs.writeShellScriptBin "synapse-system" ''
            echo "Synapse System - Multi-agent development platform"
            echo "Available agents: boss, architect, code-hound, etc."
            echo "Use 'synapse --help' for CLI commands"
          '';

          inherit (inputs.architect.packages.${system}) architect;
          inherit (inputs.clarity-judge.packages.${system}) clarity-judge;
          inherit (inputs.code-hound.packages.${system}) code-hound;
          inherit (inputs.devops-engineer.packages.${system}) devops-engineer;
          inherit (inputs.docs-writer.packages.${system}) docs-writer;
          inherit (inputs.file-creator.packages.${system}) file-creator;
          inherit (inputs.git-workflow.packages.${system}) git-workflow;
          inherit (inputs.golang-specialist.packages.${system}) golang-specialist;
          inherit (inputs.python-specialist.packages.${system}) python-specialist;
          inherit (inputs.rust-specialist.packages.${system}) rust-specialist;
          inherit (inputs.security-specialist.packages.${system}) security-specialist;
          inherit (inputs.boss.packages.${system}) boss;
          inherit (inputs.test-runner.packages.${system}) test-runner;
          inherit (inputs.tool-runner.packages.${system}) tool-runner;
          inherit (inputs.typescript-specialist.packages.${system}) typescript-specialist;
          inherit (inputs.ux-designer.packages.${system}) ux-designer;
          inherit (inputs.pneuma.packages.${system}) Pneuma;

          # Mojo runtime and libraries
          mojo-runtime = inputs.mojo-runtime.packages.${system}.mojo;
          inherit (inputs.mojo-pattern-search.packages.${system}) libpattern_search;
          inherit (inputs.mojo-message-router.packages.${system}) libmessage_router;

          # Lean4 formal verification
          inherit (inputs.lean4-verification.packages.${system}) lean4-verification;
          lean4-verification-test = inputs.lean4-verification.packages.${system}.lean4-verification-test;
          lean4-verification-docs = inputs.lean4-verification.packages.${system}.lean4-verification-docs;
          lean = inputs.lean4-verification.packages.${system}.lean;

          # Convenience package with all Mojo libraries
          mojo-libraries = pkgs.buildEnv {
            name = "synapse-mojo-libraries";
            paths = [
              inputs.mojo-pattern-search.packages.${system}.libpattern_search
              inputs.mojo-message-router.packages.${system}.libmessage_router
            ];
          };

          # Synapse Core - orchestration framework
          inherit (inputs.synapse-core.packages.${system}) synapse-core;
          synapse-cli = inputs.synapse-core.packages.${system}.synapse-core;

          # Modular packages (from nix/modules/)
          python-base = pythonBase.env;
          synapse-neo4j-tools = neo4jTools.package;
          synapse-boss = bossAgent.package;
          synapse-file-creator = fileCreatorOrchestrator.package;

          # Neo4j individual tools
          synapse-health = neo4jTools.tools.health;
          synapse-search = neo4jTools.tools.search;
          synapse-ingest = neo4jTools.tools.ingest;
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pip2nix.packages.${system}.default
            inputs.mojo-runtime.packages.${system}.default
            inputs.lean4-verification.packages.${system}.lean
            inputs.synapse-core.packages.${system}.synapse-core
          ];
          packages = with pkgs; [
            bashInteractive
            coreutils
            nix
          ];

          shellHook = ''
            echo "🧠 Synapse Development Environment"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "Python: $(python --version)"
            echo "Mojo: $(mojo --version 2>&1 | head -n1 || echo 'Not available')"
            echo "Lean4: $(lean --version 2>&1 | head -n1 || echo 'Not available')"
            echo ""
            echo "Mojo libraries available:"
            echo "  • libpattern_search.so (13.1x speedup)"
            echo "  • libmessage_router.so (cross-tract routing)"
            echo ""
            echo "Formal verification available:"
            echo "  • Lean4 dual-tract proofs (formal/lean4/)"
            echo "  • Corpus Callosum adjunction theorem"
            echo ""
            echo "Synapse Core:"
            echo "  • Template system with JSON Schema validation"
            echo "  • GMP quality gates (bootstrap: 65% coverage)"
            echo "  • CLI: synapse template list|info|validate"
            echo ""
            echo "Commands:"
            echo "  nix build .#synapse-core           - Build core framework"
            echo "  nix build .#mojo-libraries         - Build all Mojo components"
            echo "  nix run .#lean4-verification-test  - Run formal verification"
            echo "  cd formal/lean4 && lake build      - Build Lean4 locally"
            echo "  cd .synapse/neo4j && make          - Build pattern search locally"
            echo "  synapse start                      - Start Neo4j/Redis services"

            # Set library path for Python to find Nix-built libraries
            export MOJO_LIB_PATH="${inputs.mojo-pattern-search.packages.${system}.libpattern_search}/lib:${inputs.mojo-message-router.packages.${system}.libmessage_router}/lib"
          '';
        };

        devShells.mojo-dev = pkgs.mkShell {
          buildInputs = with pkgs; [
            inputs.mojo-runtime.packages.${system}.default
            python312
            python312Packages.ctypes
            gnumake
            binutils
            git
          ];

          shellHook = ''
            echo "🔥 Mojo Development Environment for Synapse"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "Mojo version: $(mojo --version 2>&1 | head -n1)"
            echo ""
            echo "Build commands:"
            echo "  make -C .synapse/corpus_callosum  - Build message router"
            echo "  make -C .synapse/neo4j            - Build pattern search"
            echo "  nm -D <lib.so>                    - Check FFI exports"
            echo ""
            echo "Libraries:"
            echo "  • .synapse/neo4j/libpattern_search.so"
            echo "  • .synapse/corpus_callosum/libmessage_router.so"
          '';
        };

        devShells.lean4-dev = inputs.lean4-verification.devShells.${system}.default;

        defaultPackage = self.devShells.${system}.default;

        # CI/CD checks
        checks = {
          # Existing checks...

          # Add Lean4 verification check
          lean4-verification = inputs.lean4-verification.packages.${system}.lean4-verification-test;
        };
      }
    );
}
