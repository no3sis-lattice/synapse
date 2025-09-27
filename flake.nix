{
  description = "A lattice of flakes for the Synapse system.";

  inputs = {
    # External dependencies pointing to the meta-introspector fork
    nixpkgs.url = "github:meta-introspector/nixpkgs?ref=feature/CRQ-016-nixify";
    flake-utils.url = "github:meta-introspector/flake-utils?ref=feature/CRQ-016-nixify";

    # pip2nix referenced via GitHub
    pip2nix.url = "github:meta-introspector/pip2nix?ref=master";

    # Agent flakes
    #AGENT1.url = "github:meta-introspector/synapse-system?dir=nix/flakes/4QZero&ref=feature/base-agent-flake";
    Agent4QZero.url = "path:./nix/flakes/4QZero";
    ARCHITECT.url = "path:./nix/flakes/architect";
    #ARCHITECT.url = "github:meta-introspector/synapse-system?dir=nix/flakes/architect&ref=feature/base-agent-flake";
    #base-agent.url = "github:meta-introspector/synapse-system?dir=nix/flakes/base-agent&ref=feature/base-agent-flake";
    #base-agent.url = "path:./nix/flakes/base-agent";
  };

  outputs = { self, nixpkgs, flake-utils, pip2nix, Agent4QZero, ARCHITECT
            #, base-agent
            , ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        pythonModule = import ./nix/modules/python-env.nix;
        pythonPackagesFile = ./nix/python-packages.nix;

        # Configure base-agent with pythonModule and pythonPackagesFile
        #configuredBaseAgent = base-agent.outputs {
        #  inherit self nixpkgs flake-utils pip2nix pythonModule pythonPackagesFile;
        #};

      in
      {
        packages = rec {
          Agent4QZero-agent = Agent4QZero.outputs {
            inherit self nixpkgs flake-utils pip2nix;
            #base-agent = configuredBaseAgent;
          }.packages.${system}.default;
          ARCHITECT-agent = ARCHITECT.outputs {
            inherit self nixpkgs flake-utils pip2nix;
            #base-agent = configuredBaseAgent;
          }.packages.${system}.default;
          # No agent packages exposed directly here yet, will be done via nix/modules
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
#            configuredBaseAgent.pythonEnv.${system}
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

