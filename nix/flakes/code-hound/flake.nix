{
  description = "A flake for the code-hound agent.";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };
    in
    {
      packages.${system}.code-hound = pkgs.writeShellScriptBin "code-hound" ''
        echo "Hello from the code-hound agent!"
      '';
      packages.${system}.default = self.packages.${system}.code-hound;
    };
}
