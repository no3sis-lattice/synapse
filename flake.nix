{
  description = "A lattice of flakes for the Synapse system.";

  inputs = {
    # External dependencies pointing to the meta-introspector fork
    nixpkgs.url = "github:meta-introspector/nixpkgs?ref=feature/CRQ-016-nixify";
    flake-utils.url = "github:numtide/flake-utils";

    # pip2nix referenced via GitHub
    pip2nix.url = "github:meta-introspector/pip2nix";
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

        # Generate the Python environment from all-requirements.txt
        pythonEnv = pkgs.pip2nix.mkPythonPackages {
          src = ./.;
          requirements = ./nix/all-requirements.txt;
        };

      in
      {
        packages = {
          # No agent packages exposed directly here yet, will be done via nix/modules
        };

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
