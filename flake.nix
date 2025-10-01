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

    # Agent flakes (internal modules)
    base-agent = { url = "path:./nix/flakes/base-agent"; inputs.nixpkgs.follows = "nixpkgs"; };
    architect = { url = "path:./nix/flakes/architect"; inputs.nixpkgs.follows = "nixpkgs"; };
    clarity-judge = { url = "path:./nix/flakes/clarity-judge"; inputs.nixpkgs.follows = "nixpkgs"; };
    code-hound = { url = "path:./nix/flakes/code-hound"; inputs.nixpkgs.follows = "nixpkgs"; };
    devops-engineer = { url = "path:./nix/flakes/devops-engineer"; inputs.nixpkgs.follows = "nixpkgs"; };
    docs-writer = { url = "path:./nix/flakes/docs-writer"; inputs.nixpkgs.follows = "nixpkgs"; };
    file-creator = { url = "path:./nix/flakes/file-creator"; inputs.nixpkgs.follows = "nixpkgs"; };
    git-workflow = { url = "path:./nix/flakes/git-workflow"; inputs.nixpkgs.follows = "nixpkgs"; };
    golang-specialist = { url = "path:./nix/flakes/golang-specialist"; inputs.nixpkgs.follows = "nixpkgs"; };
    python-specialist = { url = "path:./nix/flakes/python-specialist"; inputs.nixpkgs.follows = "nixpkgs"; };
    rust-specialist = { url = "path:./nix/flakes/rust-specialist"; inputs.nixpkgs.follows = "nixpkgs"; };
    security-specialist = { url = "path:./nix/flakes/security-specialist"; inputs.nixpkgs.follows = "nixpkgs"; };
    boss = { url = "path:./nix/flakes/boss"; inputs.nixpkgs.follows = "nixpkgs"; };
    test-runner = { url = "path:./nix/flakes/test-runner"; inputs.nixpkgs.follows = "nixpkgs"; };
    tool-runner = { url = "path:./nix/flakes/tool-runner"; inputs.nixpkgs.follows = "nixpkgs"; };
    typescript-specialist = { url = "path:./nix/flakes/typescript-specialist"; inputs.nixpkgs.follows = "nixpkgs"; };
    ux-designer = { url = "path:./nix/flakes/ux-designer"; inputs.nixpkgs.follows = "nixpkgs"; };
    pneuma = {
      url = "path:./nix/flakes/pneuma";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.base-agent.follows = "base-agent";
    };

    # Mojo components
    mojo-runtime = {
      url = "path:./nix/flakes/mojo-runtime";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    mojo-pattern-search = {
      url = "path:./nix/flakes/mojo-pattern-search";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.mojo-runtime.follows = "mojo-runtime";
    };

    mojo-message-router = {
      url = "path:./nix/flakes/mojo-message-router";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.mojo-runtime.follows = "mojo-runtime";
    };
  };

  outputs = { self, nixpkgs, flake-utils, pip2nix, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          redis
        ]);

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
          inherit (inputs.mojo-runtime.packages.${system}) mojo-runtime;
          inherit (inputs.mojo-pattern-search.packages.${system}) libpattern_search;
          inherit (inputs.mojo-message-router.packages.${system}) libmessage_router;

          # Convenience package with all Mojo libraries
          mojo-libraries = pkgs.buildEnv {
            name = "synapse-mojo-libraries";
            paths = [
              inputs.mojo-pattern-search.packages.${system}.libpattern_search
              inputs.mojo-message-router.packages.${system}.libmessage_router
            ];
          };
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pip2nix.packages.${system}.default
            inputs.mojo-runtime.packages.${system}.default
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
            echo ""
            echo "Mojo libraries available:"
            echo "  • libpattern_search.so (13.1x speedup)"
            echo "  • libmessage_router.so (cross-tract routing)"
            echo ""
            echo "Commands:"
            echo "  nix build .#mojo-libraries  - Build all Mojo components"
            echo "  cd .synapse/neo4j && make   - Build pattern search locally"
            echo "  synapse start               - Start Neo4j/Redis services"

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

        defaultPackage = self.devShells.${system}.default;
      }
    );
}
