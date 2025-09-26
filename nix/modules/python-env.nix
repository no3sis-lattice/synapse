{
  pkgs,
  pip2nix,
  allRequirementsFile,
  pipLockFile,
}:

let
  # Define the Python environment using pip2nix and the generated pip.lock
  pythonEnv = pkgs.pip2nix.mkPythonEnv {
    src = ./.; # Reference the project root for context
    requirements = allRequirementsFile;
    pipLock = pipLockFile;
  };
in

{
  env = pythonEnv;
}
