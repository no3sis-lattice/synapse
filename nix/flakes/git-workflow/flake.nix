{
  description = "A flake for the git-workflow agent.";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };
    in
    {
      packages.${system}.git-workflow = pkgs.writeShellScriptBin "git-workflow" ''
        echo "Hello from the git-workflow agent!"
      '';
      packages.${system}.default = self.packages.${system}.git-workflow;
    };
}
