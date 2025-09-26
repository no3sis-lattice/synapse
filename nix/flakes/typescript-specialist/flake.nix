{
  description = "A flake for the typescript-specialist agent.";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };
    in
    {
      packages.${system}.typescript-specialist = pkgs.writeShellScriptBin "typescript-specialist" ''
        echo "Hello from the typescript-specialist agent!"
      '';
      packages.${system}.default = self.packages.${system}.typescript-specialist;
    };
}
