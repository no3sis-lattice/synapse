{
  description = "A flake for the devops-engineer agent.";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };
    in
    {
      packages.${system}.devops-engineer = pkgs.writeShellScriptBin "devops-engineer" ''
        echo "Hello from the devops-engineer agent!"
      '';
      packages.${system}.default = self.packages.${system}.devops-engineer;
    };
}
