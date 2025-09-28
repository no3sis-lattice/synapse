{
  description = "Documentation Writer Agent with comprehensive documentation tools";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };

      # Python environment for the agent runner
      pythonEnv = pkgs.python312.withPackages (ps: with ps; [
        # Core agent dependencies
        asyncio-mqtt aiofiles rich pyyaml
        neo4j redis numpy requests

        # Documentation tools
        sphinx sphinx-rtd-theme
        mkdocs mkdocs-material
        jupyter-book
        myst-parser
      ]);

      # Documentation tools environment
      docsEnv = pkgs.buildEnv {
        name = "docs-writer-env";
        paths = with pkgs; [
          # Core utilities
          git curl jq

          # Markdown tools
          pandoc
          mdbook
          zola

          # Diagram generation
          graphviz
          plantuml
          mermaid-cli

          # LaTeX for PDF generation
          texlive.combined.scheme-medium

          # Node.js documentation tools
          nodejs_20
          nodePackages.doctoc
          nodePackages.markdownlint-cli

          # API documentation
          openapi-generator-cli
        ];
      };

      agentScript = pkgs.writeShellScript "docs-writer-script" ''
        #!${pkgs.bash}/bin/bash
        set -euo pipefail

        AGENT_DIR="$HOME/.synapse-system/.synapse/agents/docs-writer"

        if [[ ! -f "$AGENT_DIR/docs_writer_agent.py" ]]; then
          echo "❌ Docs Writer agent not found"
          exit 1
        fi

        echo "📝 Starting Documentation Writer Agent..."
        cd "$AGENT_DIR"

        export PATH="${docsEnv}/bin:$PATH"
        exec ${pythonEnv}/bin/python docs_writer_agent.py "$@"
      '';

    in
    {
      packages.${system} = {
        docs-writer = pkgs.writeShellScriptBin "docs-writer" ''
          exec ${agentScript} "$@"
        '';
        default = self.packages.${system}.docs-writer;
      };

      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [ docsEnv pythonEnv ];
        shellHook = ''
          echo "📝 Documentation Writer Environment"
          echo "Tools: sphinx, mkdocs, pandoc, mdbook"
        '';
      };

      checks.${system}.docs-writer-build = self.packages.${system}.docs-writer;
    };
}
