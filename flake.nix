{
  description = "A lattice of flakes for the Synapse system.";

  inputs = {
    # External dependencies pointing to the meta-introspector fork
    nixpkgs.url = "github:meta-introspector/nixpkgs?ref=feature/CRQ-016-nixify";
    flake-utils.url = "github:numtide/flake-utils";

    # pip2nix referenced via GitHub
    pip2nix.url = "github:meta-introspector/pip2nix";
  };

  outputs = { self, nixpkgs, flake-utils, pip2nix, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        # Python environment will be imported from a generated file
        pythonPackages = import ./nix/python-packages.nix {
          inherit pkgs;
          pip2nix = pip2nix.packages.${system}.default;
        };
        pythonEnv = pythonPackages.env;

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
            # Add pip2nix tool to devShell for generating python-packages.nix
            pip2nix.packages.${system}.default
          ];
        };
      }
    );
}
