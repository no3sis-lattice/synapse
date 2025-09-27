{
  description = "Nix flake for the 4QZero agent.";

  inputs = {
    nixpkgs.url = "github:meta-introspector/nixpkgs?ref=feature/CRQ-016-nixify";
    flake-utils.url = "github:meta-introspector/flake-utils?ref=feature/CRQ-016-nixify";
    pip2nix.url = "github:meta-introspector/pip2nix?ref=master";
    base-agent.url = "path:../../base-agent"; # Reference the base agent flake
  };

  outputs = { self, nixpkgs, flake-utils, pip2nix, base-agent, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        pythonEnv = base-agent.pythonEnv.${system};
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