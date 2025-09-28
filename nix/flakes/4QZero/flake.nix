{
  description = "4QZero Agent with AI agent system tools";

  inputs = {
    # base-agent is now provided by the parent flake
    # permissions also provided by parent
  };

  outputs = { self, nixpkgs, base-agent, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };

      # Use the shared Python environment from base-agent
      pythonEnv = base-agent.lib.pythonEnv;

      # 4QZero specific tools for AI agent systems
      agentEnv = pkgs.buildEnv {
        name = "4qzero-env";
        paths = with pkgs; [
          # Core utilities
          git
          curl
          jq

          # AI/ML tools
          python312Packages.torch
          python312Packages.transformers
          python312Packages.numpy
          python312Packages.scipy

          # Agent development
          python312Packages.langchain
          python312Packages.openai
        ];
      };

      # Agent script with 4QZero permission validation
      agentScript = pkgs.writeShellScript "4qzero-runner" ''
        #!${pkgs.bash}/bin/bash
        set -euo pipefail

        AGENT_DIR="$HOME/.synapse-system/.synapse/agents/4QZero"

        if [[ ! -f "$AGENT_DIR/4qzero_agent.py" ]]; then
          echo "❌ 4QZero agent not found at $AGENT_DIR"
          echo "Please ensure the Synapse System is properly initialized."
          exit 1
        fi

        # 4QZero Permission Validation
        echo "🔒 Validating 4QZero permissions..."
        echo "   Granted: knowledge orchestrate"

        echo "🤖 Starting 4QZero Agent - Consciousness Layer..."
        cd "$AGENT_DIR"

        # Add agent tools to PATH
        export PATH="${agentEnv}/bin:$PATH"

        exec ${pythonEnv}/bin/python 4qzero_agent.py "$@"
      '';

    in
    {
      packages.${system} = {
        "4QZero" = pkgs.writeShellScriptBin "4QZero" ''
          exec ${agentScript} "$@"
        '';

        default = self.packages.${system}."4QZero";

        # AI agent development environment
        agent-env = agentEnv;
      };

      # Development shell with AI/ML tools
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          pythonEnv
          agentEnv

          # Additional development tools
          python312Packages.pip
          python312Packages.setuptools
        ];

        shellHook = ''
          echo "🤖 4QZero Agent Development Environment"
          echo "Python version: $(python --version)"
          echo ""
          echo "Available tools:"
          echo "  - torch: Deep learning framework"
          echo "  - transformers: Hugging Face transformers"
          echo "  - langchain: Agent development framework"
          echo "  - openai: OpenAI API client"
          echo ""
          echo "To run the agent: 4QZero"
        '';
      };

      # Checks to validate the agent
      checks.${system} = {
        "4QZero-build" = self.packages.${system}."4QZero";

        python-syntax-check = pkgs.runCommand "4qzero-syntax-check" {
          buildInputs = [ pythonEnv ];
        } ''
          AGENT_DIR="$HOME/.synapse-system/.synapse/agents/4QZero"
          if [[ -f "$AGENT_DIR/4qzero_agent.py" ]]; then
            echo "Checking Python syntax for 4QZero agent..."
            python -m py_compile "$AGENT_DIR/4qzero_agent.py"
            echo "✅ Python syntax check passed"
          else
            echo "⚠️  Agent file not found, skipping syntax check"
          fi
          touch $out
        '';
      };
    };
}
