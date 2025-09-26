{
  description = "A lattice of flakes for the Synapse system.";

  inputs = {
    # External dependencies pointing to the meta-introspector fork
    nixpkgs.url = "github:meta-introspector/nixpkgs?ref=feature/CRQ-016-nixify";
    flake-utils.url = "github:numtide/flake-utils"; # Using official flake-utils as meta-introspector one might be outdated

    # Internal toolchain dependencies
    pip2nix = {
      url = "path:./vendor/nix/pip2nix";
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
          overlays = [
            pip2nix.overlays.default
          ];
        };

        # Generate the Python environment from requirements.txt
        pythonEnv = pkgs.pip2nix.mkPythonPackages {
          src = ./.;
          requirements = ./nix/all-requirements.txt;
        };

      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [ pythonEnv ];
          packages = with pkgs; [
            # Basic tools for development
            bashInteractive
            coreutils
            nix
            # Development tools from requirements-dev.txt
            # pytest and related tools are included in pythonEnv, so no need to add them separately here
          ];
        };
      }
    );
}
