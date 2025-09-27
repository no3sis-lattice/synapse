{
  description = "Nix flake for a test agent.";

  inputs = {
    nixpkgs.url = "github:meta-introspector/nixpkgs?ref=feature/CRQ-016-nixify";
    flake-utils.url = "github:meta-introspector/flake-utils?ref=feature/CRQ-016-nixify";
  };

  outputs = { self, nixpkgs, flake-utils, pythonEnv, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
      in
      {
        packages.default = pkgs.writeShellScriptBin "test-agent" ''
          #!${pkgs.bash}/bin/bash
          ${pythonEnv}/bin/python -c "print('Hello from test agent!')"
        '';
      }
    );
}
