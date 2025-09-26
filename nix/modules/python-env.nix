{
  pkgs,
  pythonPackagesFile,
}:

let
  # Import the generated python-packages.nix
  generatedPythonPackages = import pythonPackagesFile { inherit pkgs; };
  pythonEnv = generatedPythonPackages.env;

in

{
  env = pythonEnv;
}
