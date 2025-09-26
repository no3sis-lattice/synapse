{
  description = "A flake for the tool-runner agent.";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };
    in
    {
      packages.${system}.tool-runner = pkgs.writeShellScriptBin "tool-runner" ''
        echo "Hello from the tool-runner agent!"
      '';
      packages.${system}.default = self.packages.${system}.tool-runner;
    };
}
