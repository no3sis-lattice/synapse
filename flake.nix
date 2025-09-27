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
    synapse-project-manager = { url = "path:./nix/flakes/synapse-project-manager"; inputs.nixpkgs.follows = "nixpkgs"; };
    test-runner = { url = "path:./nix/flakes/test-runner"; inputs.nixpkgs.follows = "nixpkgs"; };
    tool-runner = { url = "path:./nix/flakes/tool-runner"; inputs.nixpkgs.follows = "nixpkgs"; };
    typescript-specialist = { url = "path:./nix/flakes/typescript-specialist"; inputs.nixpkgs.follows = "nixpkgs"; };
    ux-designer = { url = "path:./nix/flakes/ux-designer"; inputs.nixpkgs.follows = "nixpkgs"; };
    "4QZero" = { url = "path:./nix/flakes/4QZero"; inputs.nixpkgs.follows = "nixpkgs"; };
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
            echo "Available agents: architect, code-hound, synapse-project-manager, etc."
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
          inherit (inputs.synapse-project-manager.packages.${system}) synapse-project-manager;
          inherit (inputs.test-runner.packages.${system}) test-runner;
          inherit (inputs.tool-runner.packages.${system}) tool-runner;
          inherit (inputs.typescript-specialist.packages.${system}) typescript-specialist;
          inherit (inputs.ux-designer.packages.${system}) ux-designer;
          inherit (inputs."4QZero".packages.${system}) "4QZero";
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pip2nix.packages.${system}.default
          ];
          packages = with pkgs; [
            bashInteractive
            coreutils
            nix
          ];
        };
        
        defaultPackage = self.devShells.${system}.default;
      }
    );
}
