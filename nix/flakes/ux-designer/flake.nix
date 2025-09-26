{
  description = "A flake for the ux-designer agent.";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };
    in
    {
      packages.${system}.ux-designer = pkgs.writeShellScriptBin "ux-designer" ''
        echo "Hello from the ux-designer agent!"
      '';
      packages.${system}.default = self.packages.${system}.ux-designer;
    };
}
