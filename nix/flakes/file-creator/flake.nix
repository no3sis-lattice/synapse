{
  description = "File Creator Agent with template generation and file manipulation tools";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };

      pythonEnv = pkgs.python312.withPackages (ps: with ps; [
        asyncio-mqtt aiofiles rich pyyaml neo4j redis numpy requests
        jinja2 cookiecutter pathlib2
      ]);

      fileEnv = pkgs.buildEnv {
        name = "file-creator-env";
        paths = with pkgs; [
          git curl jq yq
          tree fd
          cookiecutter
          nodePackages.yo  # Yeoman generator
        ];
      };

      agentScript = pkgs.writeShellScript "file-creator-script" ''
        AGENT_DIR="$HOME/.synapse-system/.synapse/agents/file-creator"
        [[ -f "$AGENT_DIR/file_creator_agent.py" ]] || { echo "Agent not found"; exit 1; }
        echo "📁 Starting File Creator Agent..."
        cd "$AGENT_DIR"
        export PATH="${fileEnv}/bin:$PATH"
        exec ${pythonEnv}/bin/python file_creator_agent.py "$@"
      '';

    in {
      packages.${system} = {
        file-creator = pkgs.writeShellScriptBin "file-creator" ''exec ${agentScript} "$@"'';
        default = self.packages.${system}.file-creator;
      };
      devShells.${system}.default = pkgs.mkShell { buildInputs = [ fileEnv pythonEnv ]; };
      checks.${system}.file-creator-build = self.packages.${system}.file-creator;
    };
}
