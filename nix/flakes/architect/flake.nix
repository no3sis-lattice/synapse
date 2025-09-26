{
  description = "A flake for the architect agent.";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };
    in
    {
      packages.${system}.architect = pkgs.writeShellScriptBin "architect" ''
        echo "Hello from the architect agent!"
      '';
      packages.${system}.default = self.packages.${system}.architect;
    };
}
