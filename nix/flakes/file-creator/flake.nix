{
  description = "A flake for the file-creator agent.";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };
    in
    {
      packages.${system}.file-creator = pkgs.writeShellScriptBin "file-creator" ''
        echo "Hello from the file-creator agent!"
      '';
      packages.${system}.default = self.packages.${system}.file-creator;
    };
}
