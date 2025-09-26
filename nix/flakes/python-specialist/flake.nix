{
  description = "A flake for the python-specialist agent.";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };
    in
    {
      packages.${system}.python-specialist = pkgs.writeShellScriptBin "python-specialist" ''
        echo "Hello from the python-specialist agent!"
      '';
      packages.${system}.default = self.packages.${system}.python-specialist;
    };
}
