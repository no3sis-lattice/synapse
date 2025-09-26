{
  description = "A flake for the golang-specialist agent.";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };
    in
    {
      packages.${system}.golang-specialist = pkgs.writeShellScriptBin "golang-specialist" ''
        echo "Hello from the golang-specialist agent!"
      '';
      packages.${system}.default = self.packages.${system}.golang-specialist;
    };
}
