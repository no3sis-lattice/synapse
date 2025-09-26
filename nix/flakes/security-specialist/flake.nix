{
  description = "A flake for the security-specialist agent.";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };
    in
    {
      packages.${system}.security-specialist = pkgs.writeShellScriptBin "security-specialist" ''
        echo "Hello from the security-specialist agent!"
      '';
      packages.${system}.default = self.packages.${system}.security-specialist;
    };
}
