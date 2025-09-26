{
  description = "A flake for the docs-writer agent.";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };
    in
    {
      packages.${system}.docs-writer = pkgs.writeShellScriptBin "docs-writer" ''
        echo "Hello from the docs-writer agent!"
      '';
      packages.${system}.default = self.packages.${system}.docs-writer;
    };
}
