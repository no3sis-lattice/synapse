{
  description = "Tool Runner Agent with comprehensive tool execution environment";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };

      pythonEnv = pkgs.python312.withPackages (ps: with ps; [
        asyncio-mqtt aiofiles rich pyyaml neo4j redis numpy requests
        subprocess-run psutil
      ]);

      toolEnv = pkgs.buildEnv {
        name = "tool-runner-env";
        paths = with pkgs; [
          # Core system tools
          bash zsh fish
          coreutils findutils
          git curl wget
          jq yq

          # Process and system monitoring
          htop btop
          lsof netstat
          strace

          # Archive and compression
          zip unzip
          gzip bzip2 xz
          tar

          # Text processing
          ripgrep fd
          sed awk

          # Network tools
          ping netcat
          dig nslookup
        ];
      };

      agentScript = pkgs.writeShellScript "tool-runner-script" ''
        AGENT_DIR="$HOME/.synapse-system/.synapse/agents/tool-runner"
        [[ -f "$AGENT_DIR/tool_runner_agent.py" ]] || { echo "Agent not found"; exit 1; }
        echo "🔧 Starting Tool Runner Agent..."
        cd "$AGENT_DIR"
        export PATH="${toolEnv}/bin:$PATH"
        exec ${pythonEnv}/bin/python tool_runner_agent.py "$@"
      '';

    in {
      packages.${system} = {
        tool-runner = pkgs.writeShellScriptBin "tool-runner" ''exec ${agentScript} "$@"'';
        default = self.packages.${system}.tool-runner;
      };
      devShells.${system}.default = pkgs.mkShell { buildInputs = [ toolEnv pythonEnv ]; };
      checks.${system}.tool-runner-build = self.packages.${system}.tool-runner;
    };
}
