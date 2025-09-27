{
  pkgs,
  pythonPackagesFile,
}:

let
  # Import the generated python-packages.nix using pkgs.callPackage
  packageOverrides = pkgs.callPackage pythonPackagesFile { };
  pythonWithOverrides = pkgs.python3.override { inherit packageOverrides; };
  pythonEnv = pythonWithOverrides.withPackages (ps: builtins.attrValues ps);
in
pythonEnv
