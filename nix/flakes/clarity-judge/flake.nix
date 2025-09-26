{
  description = "A flake for the clarity-judge agent.";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };
    in
    {
      packages.${system}.clarity-judge = pkgs.writeShellScriptBin "clarity-judge" ''
        echo "Hello from the clarity-judge agent!"
      '';
      packages.${system}.default = self.packages.${system}.clarity-judge;
    };
}
