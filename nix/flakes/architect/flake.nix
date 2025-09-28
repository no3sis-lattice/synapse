{
  description = "Architect Agent with design and architecture tools";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };

      # Python environment for the agent runner
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

        # Architecture and design analysis
        pydot
        graphviz
        matplotlib
        networkx

        # Documentation and diagramming
        sphinx
        jinja2
      ]);

      # Architecture and design tools
      architectEnv = pkgs.buildEnv {
        name = "architect-env";
        paths = with pkgs; [
          # Core utilities
          git
          curl
          jq

          # Diagramming and visualization
          graphviz
          plantuml
          mermaid-cli

          # Documentation tools
          pandoc
          texlive.combined.scheme-medium

          # Code analysis and metrics
          cloc
          scc
          tokei

          # File processing
          yq
          jq
          xmlstarlet

          # Architecture validation
          shellcheck
          yamllint
        ];
      };

      # Agent script that runs the actual Python implementation with architecture tools
      agentScript = pkgs.writeShellScript "architect-runner" ''
        #!${pkgs.bash}/bin/bash
        set -euo pipefail

        AGENT_DIR="$HOME/.synapse-system/.synapse/agents/architect"

        if [[ ! -f "$AGENT_DIR/architect_agent.py" ]]; then
          echo "❌ Architect agent not found at $AGENT_DIR"
          echo "Please ensure the Synapse System is properly initialized."
          exit 1
        fi

        echo "🏗️ Starting Architect Agent..."
        cd "$AGENT_DIR"

        # Add architecture tools to PATH
        export PATH="${architectEnv}/bin:$PATH"

        # Set environment variables for diagram generation
        export PLANTUML_JAR="${pkgs.plantuml}/lib/plantuml.jar"
        export GRAPHVIZ_DOT="${pkgs.graphviz}/bin/dot"

        exec ${pythonEnv}/bin/python architect_agent.py "$@"
      '';

    in
    {
      packages.${system} = {
        architect = pkgs.writeShellScriptBin "architect" ''
          exec ${agentScript} "$@"
        '';

        default = self.packages.${system}.architect;

        # Architecture tools environment
        architect-env = architectEnv;
      };

      # Development shell with complete architecture toolchain
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          pythonEnv
          architectEnv

          # Additional development tools
          python312Packages.pip
          python312Packages.setuptools
        ];

        shellHook = ''
          echo "🏗️ Architect Development Environment"
          echo "Python version: $(python --version)"
          echo ""
          echo "Available tools:"
          echo "  - graphviz: Graph visualization (dot)"
          echo "  - plantuml: UML diagram creation"
          echo "  - mermaid: Diagram and flowchart creation"
          echo "  - pandoc: Universal document converter"
          echo "  - cloc/scc: Code line counting and analysis"
          echo "  - shellcheck: Shell script analysis"
          echo "  - yamllint: YAML validation"
          echo ""
          echo "To run the agent: architect"
          echo "To create PlantUML diagram: plantuml diagram.puml"
          echo "To create Graphviz diagram: dot -Tpng graph.dot -o graph.png"
          echo "To count code lines: cloc ."
          echo "To validate shell scripts: shellcheck script.sh"
        '';

        # Set environment variables for architecture work
        PLANTUML_JAR = "${pkgs.plantuml}/lib/plantuml.jar";
        GRAPHVIZ_DOT = "${pkgs.graphviz}/bin/dot";
      };

      # Checks to validate the agent and architecture environment
      checks.${system} = {
        architect-build = self.packages.${system}.architect;

        architecture-tools-check = pkgs.runCommand "architecture-tools-check" {
          buildInputs = [ architectEnv ];
        } ''
          echo "Checking architecture tools..."
          dot -V
          plantuml -version
          mermaid --version
          pandoc --version
          cloc --version
          echo "✅ Architecture tools check passed"
          touch $out
        '';

        python-syntax-check = pkgs.runCommand "architect-syntax-check" {
          buildInputs = [ pythonEnv ];
        } ''
          AGENT_DIR="$HOME/.synapse-system/.synapse/agents/architect"
          if [[ -f "$AGENT_DIR/architect_agent.py" ]]; then
            echo "Checking Python syntax for Architect agent..."
            python -m py_compile "$AGENT_DIR/architect_agent.py"
            echo "✅ Python syntax check passed"
          else
            echo "⚠️  Agent file not found, skipping syntax check"
          fi
          touch $out
        '';
      };
    };
}
