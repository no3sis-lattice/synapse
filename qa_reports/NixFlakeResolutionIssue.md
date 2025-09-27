# QA Report: Nix Flake Resolution Issue with Sub-Flakes and Modules

**CRQ ID:** CRQ-001-NixFlakeModularization

## 1. Problem Description

When attempting to modularize a Nix flake project by breaking it into smaller sub-flakes and passing Nix modules (functions) as arguments between them, a persistent `nix flake update` and `nix build` error occurs. The error manifests as `error: cannot find flake 'flake:python-env-module' in the flake registries` or similar, even when `python-env-module` is correctly defined as a module and passed as an argument.

The core issue seems to stem from Nix's inability to correctly interpret and resolve a Nix module (a function returning a derivation) when it's passed as an argument between flakes, treating it instead as a flake input that needs to be found in the flake registries. This leads to a circular dependency or an incorrect resolution path.

## 2. Expected Behavior

When a Nix module (e.g., `python-env.nix` which exports a function) is imported in a root flake and then passed as an argument to a sub-flake, the sub-flake should be able to call this module (function) directly with its required arguments (e.g., `pythonModule = python-env-module { inherit pkgs; ... };`). Nix should not attempt to resolve `python-env-module` as a flake from its registries.

## 3. Actual Behavior

The `nix flake update` and `nix build` commands consistently fail with errors such as:
`error: cannot find flake 'flake:python-env-module' in the flake registries`
`error: getting status of '/nix/store/...-source/self': No such file or directory`
`error: flake reference '_4qzero' is not an absolute path`

These errors occur despite ensuring:
*   All flake inputs are absolute `github:` URLs with correct `ref` and `dir` attributes, or `path:` references for local sub-flakes.
*   The `python-env-module` is correctly imported in the root flake and passed as an argument to sub-flakes.
*   The sub-flakes correctly receive `python-env-module` as an argument and attempt to call it as a function.

## 4. Minimal Reproducible Test Case

To reproduce this issue, create the following file structure:

```
.
├── flake.nix
├── nix/
│   ├── modules/
│   │   └── python-env.nix
│   ├── python-packages.nix
│   └── flakes/
│       └── agent/
│           └── flake.nix
```

**`flake.nix` (Root Flake):**
```nix
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
```

**`nix/modules/python-env.nix`:**
```nix
{
  pkgs,
  pythonPackagesFile,
}:

let
  packageOverrides = pkgs.callPackage pythonPackagesFile { };
  pythonWithOverrides = pkgs.python3.override { inherit packageOverrides; };
  pythonEnv = pythonWithOverrides.withPackages (ps: builtins.attrValues ps);
in
pythonEnv
```

**`nix/python-packages.nix`:**
```nix
# This file would contain your Python package definitions, e.g.:
{ pkgs }: {
  # example:
  # requests = pkgs.python3Packages.requests;
}
```

**`nix/flakes/agent/flake.nix`:**
```nix
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
```

**Steps to Reproduce:**

1.  Clone the repository.
2.  Navigate to the root directory.
3.  Run `nix flake update`.
4.  Run `nix build .#test-agent`.

**Expected Result:**
`nix flake update` should succeed, and `nix build .#test-agent` should successfully build the `test-agent` derivation.

**Actual Result:**
`nix flake update` fails with `error: cannot find flake 'flake:pythonEnv' in the flake registries` or similar errors related to `pythonEnv` not being a flake.

---
