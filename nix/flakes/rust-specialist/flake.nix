{
  description = "A flake for the rust-specialist agent.";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };
    in
    {
      packages.${system}.rust-specialist = pkgs.writeShellScriptBin "rust-specialist" ''
        echo "Hello from the rust-specialist agent!"
      '';
      packages.${system}.default = self.packages.${system}.rust-specialist;
    };
}
