{
  description = "Python Specialist Agent with full development environment";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };

      # Python environment with all required packages for the agent
      pythonEnv = pkgs.python312.withPackages (ps: with ps; [
        # Core dependencies
        asyncio-mqtt
        aiofiles
        rich
        pyyaml

        # Code analysis tools
        flake8
        mypy
        black
        isort
        pylint
        bandit

        # Testing and coverage
        pytest
        pytest-asyncio
        pytest-cov
        coverage

        # Performance analysis
        cProfile
        memory-profiler
        py-spy

        # Type checking and documentation
        typing-extensions
        pydantic
        sphinx

        # Development utilities
        ipython
        jupyter

        # Neo4j and Redis for Synapse integration
        neo4j
        redis
        numpy
        requests
      ]);

      # Agent script that runs the actual Python implementation
      agentScript = pkgs.writeShellScript "python-specialist-runner" ''
        #!${pkgs.bash}/bin/bash
        set -euo pipefail

        AGENT_DIR="$HOME/.synapse-system/.synapse/agents/python-specialist"

        if [[ ! -f "$AGENT_DIR/python_specialist_agent.py" ]]; then
          echo "❌ Python specialist agent not found at $AGENT_DIR"
          echo "Please ensure the Synapse System is properly initialized."
          exit 1
        fi

        echo "🐍 Starting Python Specialist Agent..."
        cd "$AGENT_DIR"
        exec ${pythonEnv}/bin/python python_specialist_agent.py "$@"
      '';

    in
    {
      packages.${system} = {
        python-specialist = pkgs.writeShellScriptBin "python-specialist" ''
          exec ${agentScript} "$@"
        '';

        default = self.packages.${system}.python-specialist;

        # Development environment for Python work
        python-dev-env = pythonEnv;
      };

      # Development shell with full Python toolchain
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          pythonEnv

          # Python development tools
          python312Packages.pip
          python312Packages.setuptools
          python312Packages.wheel

          # Code formatting and linting
          ruff
          black

          # Language servers and editors
          python312Packages.python-lsp-server
          python312Packages.pylsp-mypy

          # Git and development utilities
          git
          curl
          jq
        ];

        shellHook = ''
          echo "🐍 Python Specialist Development Environment"
          echo "Python version: $(python --version)"
          echo "Available tools: black, ruff, mypy, pytest, pylint"
          echo ""
          echo "To run the agent: python-specialist"
          echo "To run tests: pytest"
          echo "To format code: black ."
          echo "To lint code: ruff check ."
        '';
      };

      # Checks to validate the agent
      checks.${system} = {
        python-specialist-build = self.packages.${system}.python-specialist;

        python-syntax-check = pkgs.runCommand "python-syntax-check" {
          buildInputs = [ pythonEnv ];
        } ''
          AGENT_DIR="$HOME/.synapse-system/.synapse/agents/python-specialist"
          if [[ -f "$AGENT_DIR/python_specialist_agent.py" ]]; then
            echo "Checking Python syntax..."
            python -m py_compile "$AGENT_DIR/python_specialist_agent.py"
            echo "✅ Python syntax check passed"
          else
            echo "⚠️  Agent file not found, skipping syntax check"
          fi
          touch $out
        '';
      };
    };
}
