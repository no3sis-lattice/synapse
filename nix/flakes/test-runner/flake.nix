{
  description = "A flake for the test-runner agent.";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };
    in
    {
      packages.${system}.test-runner = pkgs.writeShellScriptBin "test-runner" ''
        echo "Hello from the test-runner agent!"
      '';
      packages.${system}.default = self.packages.${system}.test-runner;
    };
}
