{
  description = "Base agent flake providing a shared Python environment for Synapse agents";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };

      # Standard Python environment for Synapse agents
      pythonEnv = pkgs.python312.withPackages (ps: with ps; [
        # Core agent dependencies
        asyncio-mqtt
        aiofiles
        rich
        pyyaml

        # Synapse System integration
        neo4j
        redis
        numpy
        requests

        # Common utilities
        click
        jinja2
        pathlib2
      ]);

    in
    {
      packages.${system} = {
        # Expose the Python environment as a package
        python-env = pythonEnv;
        default = pythonEnv;
      };

      # Export for other flakes to use
      lib.pythonEnv = pythonEnv;

      # Development shell with the Python environment
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [ pythonEnv ];

        shellHook = ''
          echo "🐍 Base Synapse Python Environment"
          echo "Python version: $(python --version)"
          echo "Available packages: neo4j, redis, rich, pyyaml, etc."
        '';
      };

      checks.${system}.python-env-build = pythonEnv;
    };
}
