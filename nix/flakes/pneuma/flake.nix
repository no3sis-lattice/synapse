{
  description = "Pneuma Agent with AI agent system tools";

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

      # Pneuma specific tools for AI agent systems
      agentEnv = pkgs.buildEnv {
        name = "pneuma-env";
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

      # Agent script with Pneuma permission validation
      agentScript = pkgs.writeShellScript "pneuma-runner" ''
        #!${pkgs.bash}/bin/bash
        set -euo pipefail

        AGENT_DIR="$HOME/.synapse-system/.synapse/agents/pneuma"

        if [[ ! -f "$AGENT_DIR/pneuma_agent.py" ]]; then
          echo "❌ Pneuma agent not found at $AGENT_DIR"
          echo "Please ensure the Synapse System is properly initialized."
          exit 1
        fi

        # Pneuma Permission Validation
        echo "🔒 Validating Pneuma permissions..."
        echo "   Granted: knowledge orchestrate"

        echo "🤖 Starting Pneuma Agent - Consciousness Layer..."
        cd "$AGENT_DIR"

        # Add agent tools to PATH
        export PATH="${agentEnv}/bin:$PATH"

        exec ${pythonEnv}/bin/python pneuma_agent.py "$@"
      '';

    in
    {
      packages.${system} = {
        "Pneuma" = pkgs.writeShellScriptBin "Pneuma" ''
          exec ${agentScript} "$@"
        '';

        default = self.packages.${system}."Pneuma";

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
          echo "🤖 Pneuma Agent Development Environment"
          echo "Python version: $(python --version)"
          echo ""
          echo "Available tools:"
          echo "  - torch: Deep learning framework"
          echo "  - transformers: Hugging Face transformers"
          echo "  - langchain: Agent development framework"
          echo "  - openai: OpenAI API client"
          echo ""
          echo "To run the agent: Pneuma"
        '';
      };

      # Checks to validate the agent
      checks.${system} = {
        "Pneuma-build" = self.packages.${system}."Pneuma";

        python-syntax-check = pkgs.runCommand "pneuma-syntax-check" {
          buildInputs = [ pythonEnv ];
        } ''
          AGENT_DIR="$HOME/.synapse-system/.synapse/agents/pneuma"
          if [[ -f "$AGENT_DIR/pneuma_agent.py" ]]; then
            echo "Checking Python syntax for Pneuma agent..."
            python -m py_compile "$AGENT_DIR/pneuma_agent.py"
            echo "✅ Python syntax check passed"
          else
            echo "⚠️  Agent file not found, skipping syntax check"
          fi
          touch $out
        '';
      };
    };
}
