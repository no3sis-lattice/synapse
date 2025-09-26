{
  description = "A flake for the synapse-project-manager agent.";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };
    in
    {
      packages.${system}.synapse-project-manager = pkgs.writeShellScriptBin "synapse-project-manager" ''
        echo "Hello from the synapse-project-manager agent!"
      '';
      packages.${system}.default = self.packages.${system}.synapse-project-manager;
    };
}
