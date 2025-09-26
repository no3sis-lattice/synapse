{
  description = "A lattice of flakes for the Synapse system.";

  inputs = {
    # External dependencies pointing to the meta-introspector fork
    nixpkgs.url = "github:meta-introspector/nixpkgs?ref=feature/CRQ-016-nixify";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        # Temporarily define Python environment directly
        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          # Main dependencies from nix/all-requirements.txt
          # This is a temporary measure to get the flake working
          neo4j
          numpy
          python-dotenv
          pytest
          pytest-snapshot
          redis
          requests
          sentence-transformers
          sqlite-vss
          testcontainers
          testcontainers-neo4j
          testcontainers-redis
        ]);

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
          ];
        };
      }
    );
}
