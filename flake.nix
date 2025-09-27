{
  description = "A lattice of flakes for the Synapse system.";

  inputs = {
    # External dependencies pointing to the meta-introspector fork
    nixpkgs.url = "github:meta-introspector/nixpkgs?ref=feature/CRQ-016-nixify";
    flake-utils.url = "github:numtide/flake-utils";

    # pip2nix referenced via GitHub
    pip2nix.url = "github:meta-introspector/pip2nix?ref=master";

    # Agent flakes
    # synapse-repo.url = "github:meta-introspector/synapse-system?ref=feature/CRQ-001-NixFlakeModularization";
  };

  outputs = { self, nixpkgs, flake-utils, pip2nix, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        # Import the foundational Python environment module
        pythonModule = import ./nix/modules/python-env.nix {
          inherit pkgs;
          pythonPackagesFile = ./nix/python-packages.nix;
        };
        pythonEnv = pythonModule;

      in
      {
        pythonEnv = pythonEnv;

        packages = {
          # No agent packages exposed directly here yet, will be done via nix/modules
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pip2nix.packages.${system}.default
          ];
          packages = with pkgs; [
            # Basic tools for development
            bashInteractive
            coreutils
            nix
          ];
        };
      }
    );
}
