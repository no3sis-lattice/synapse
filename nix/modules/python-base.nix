# Python Base Environment
# Foundation module for all Synapse Python components
#
# Provides:
# - Python 3.12 interpreter
# - Core dependencies from all-requirements.txt
# - Shared utilities for all modules

{ pkgs, system }:

let
  # Core Python dependencies (from nix/all-requirements.txt)
  pythonPackages = ps: with ps; [
    # Neo4j and database
    neo4j

    # Redis
    redis

    # Scientific computing (for BGE-M3)
    numpy

    # Configuration
    python-dotenv

    # HTTP requests
    requests

    # Testing
    pytest
    pytest-snapshot

    # Testcontainers for integration tests
    # Note: These are optional, only needed for full test suite
    # testcontainers
    # testcontainers-neo4j
    # testcontainers-redis
  ];

  # Python environment with all core packages
  pythonEnv = pkgs.python312.withPackages pythonPackages;

in
{
  # Export the Python environment
  env = pythonEnv;

  # Export Python version for other modules
  python = pkgs.python312;

  # Export individual packages for selective imports
  packages = pythonPackages pkgs.python312Packages;

  # Utility function to create a Python package derivation
  mkPythonPackage = { pname, version, src, propagatedBuildInputs ? [], ... }@args:
    pkgs.python312Packages.buildPythonPackage ({
      inherit pname version src;
      propagatedBuildInputs = [ pythonEnv ] ++ propagatedBuildInputs;
      doCheck = false; # Skip tests by default, enable per-package
    } // (builtins.removeAttrs args [ "pname" "version" "src" "propagatedBuildInputs" ]));

  # Utility function to create a Python script wrapper
  mkPythonScript = { name, script, runtimeInputs ? [] }:
    pkgs.writeShellScriptBin name ''
      export PYTHONPATH="${pythonEnv}/${pythonEnv.sitePackages}:$PYTHONPATH"
      ${pkgs.lib.optionalString (runtimeInputs != []) ''
        export PATH="${pkgs.lib.makeBinPath runtimeInputs}:$PATH"
      ''}
      exec ${pythonEnv}/bin/python ${script} "$@"
    '';
}
