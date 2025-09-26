{
  description = "A flake for the 4QZero agent.";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };
    in
    {
      packages.${system}."4QZero" = pkgs.writeShellScriptBin "4QZero" ''
        echo "Hello from the 4QZero agent!"
      '';
      packages.${system}.default = self.packages.${system}."4QZero";
    };
}
