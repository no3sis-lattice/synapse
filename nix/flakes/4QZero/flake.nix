{
  description = "Nix flake for the 4QZero agent.";

  inputs = {
    nixpkgs.url = "github:meta-introspector/nixpkgs?ref=feature/CRQ-016-nixify";
    flake-utils.url = "github:numtide/flake-utils";
    # Reference the root synapse-system flake to get the shared Python environment
    # synapse-system.url = "github:meta-introspector/synapse-system?ref=feature/CRQ-001-NixFlakeModularization";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
        pythonEnv = pkgs.python3;
      in
      {
        packages.default = pkgs.writeShellScriptBin "4qzero-agent" ''
          #!${pkgs.bash}/bin/bash
          # The path to the agent script is relative to the current flake
          ${pythonEnv}/bin/python ${./.synapse/agents/4QZero/4qzero_agent.py} "$@"
        '';
      }
    );
}