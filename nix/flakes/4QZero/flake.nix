{
  description = "Nix flake for the 4QZero agent.";

  inputs = {
    nixpkgs.url = "github:meta-introspector/nixpkgs?ref=feature/CRQ-016-nixify";
    flake-utils.url = "github:meta-introspector/flake-utils?ref=feature/CRQ-016-nixify";
  };

#${pythonEnv}/bin/python .synapse/agents/4QZero/4qzero_agent.py "$@"
        #pythonEnv = synapse-system.pythonEnv.${system};
  outputs = { self, nixpkgs, flake-utils,  ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
        # Access the shared Python environment from the root flake

      in
      {
        packages.default = pkgs.writeShellScriptBin "4qzero-agent" ''
          #!${pkgs.bash}/bin/bash
          # The path to the agent script is relative to the root of the synapse-system flake
          
        '';
      }
    );
}