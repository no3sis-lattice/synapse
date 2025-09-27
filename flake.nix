{
  description = "A lattice of flakes for the Synapse system.";

  inputs = {
    # External dependencies pointing to the meta-introspector fork
    nixpkgs.url = "github:meta-introspector/nixpkgs?ref=feature/CRQ-016-nixify";
    flake-utils.url = "github:meta-introspector/flake-utils?ref=feature/CRQ-016-nixify";

    # pip2nix referenced via GitHub
    pip2nix.url = "github:meta-introspector/pip2nix?ref=master";

    # Agent flakes
    AGENT1.url = "path:./nix/flakes/4QZero";
    ARCHITECT.url = "path:./nix/flakes/architect";
    base-agent.url = "path:./nix/flakes/base-agent";
  };

  outputs = { self, nixpkgs, flake-utils, pip2nix, AGENT1, ARCHITECT, base-agent, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

      in
      {
        packages = rec {
          AGENT1-agent = (import AGENT1 {
            inherit self nixpkgs flake-utils;
            synapse-system = self; # Pass self as synapse-system
            base-agent = base-agent; # Pass base-agent flake
          }).packages.${system}.default;
          ARCHITECT-agent = (import ARCHITECT {
            inherit self nixpkgs flake-utils;
            synapse-system = self; # Pass self as synapse-system
            base-agent = base-agent; # Pass base-agent flake
          }).packages.${system}.default;
          # No agent packages exposed directly here yet, will be done via nix/modules
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            base-agent.pythonEnv.${system}
            pip2nix.packages.${system}.default
          ];
          packages = with pkgs; [
            bashInteractive
            coreutils
            nix
          ];
        };
      }
    );
}

