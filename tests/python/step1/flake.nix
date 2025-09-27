{
  description = "A minimal reproducible test case for Nix flake resolution issue.";

  inputs = {
    nixpkgs.url = "github:meta-introspector/nixpkgs?ref=feature/CRQ-016-nixify";
    flake-utils.url = "github:meta-introspector/flake-utils?ref=feature/CRQ-016-nixify";
    pip2nix.url = "github:meta-introspector/pip2nix?ref=master";
    agent.url = "path:./nix/flakes/agent"; # Reference the sub-flake
  };

  outputs = { self, nixpkgs, flake-utils, pip2nix, agent, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        pythonModule = import ./nix/modules/python-env.nix {
          inherit pkgs;
          pythonPackagesFile = ./nix/python-packages.nix;
        };
        pythonEnv = pythonModule;

      in
      {
        packages = rec {
          test-agent = (import agent {
            inherit self nixpkgs flake-utils;
            pythonEnv = pythonEnv; # Pass pythonEnv derivation directly
          }).packages.${system}.default;
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
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
