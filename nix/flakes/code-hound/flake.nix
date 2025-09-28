{
  description = "Code Hound Agent with advanced code search and analysis tools";

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

        # Code analysis and parsing
        tree-sitter
        pygments
        ast-monitor

        # Search and indexing
        whoosh
      ]);

      # Code search and analysis tools
      codeHoundEnv = pkgs.buildEnv {
        name = "code-hound-env";
        paths = with pkgs; [
          # Core utilities
          git
          curl
          jq

          # Advanced search tools
          ripgrep
          fd
          fzf
          the_silver_searcher

          # Code analysis
          tree-sitter
          universal-ctags
          global

          # Language-specific tools
          ast-grep

          # File processing
          bat
          exa
          hexyl

          # Code metrics
          cloc
          scc
          tokei

          # Git tools
          git-delta
          difftastic

          # JSON/YAML processing
          jq
          yq
        ];
      };

      # Agent script that runs the actual Python implementation with code search tools
      agentScript = pkgs.writeShellScript "code-hound-runner" ''
        #!${pkgs.bash}/bin/bash
        set -euo pipefail

        AGENT_DIR="$HOME/.synapse-system/.synapse/agents/code-hound"

        if [[ ! -f "$AGENT_DIR/code_hound_agent.py" ]]; then
          echo "❌ Code Hound agent not found at $AGENT_DIR"
          echo "Please ensure the Synapse System is properly initialized."
          exit 1
        fi

        echo "🔍 Starting Code Hound Agent..."
        cd "$AGENT_DIR"

        # Add code search tools to PATH
        export PATH="${codeHoundEnv}/bin:$PATH"

        # Set environment variables for search tools
        export FZF_DEFAULT_COMMAND="fd --type f --hidden --follow --exclude .git"
        export RIPGREP_CONFIG_PATH="$HOME/.ripgreprc"

        exec ${pythonEnv}/bin/python code_hound_agent.py "$@"
      '';

    in
    {
      packages.${system} = {
        code-hound = pkgs.writeShellScriptBin "code-hound" ''
          exec ${agentScript} "$@"
        '';

        default = self.packages.${system}.code-hound;

        # Code search tools environment
        code-search-env = codeHoundEnv;
      };

      # Development shell with complete code search toolchain
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          pythonEnv
          codeHoundEnv

          # Additional development tools
          python312Packages.pip
          python312Packages.setuptools
        ];

        shellHook = ''
          echo "🔍 Code Hound Development Environment"
          echo "Python version: $(python --version)"
          echo ""
          echo "Available search tools:"
          echo "  - ripgrep (rg): Ultra-fast text search"
          echo "  - fd: Fast file finder"
          echo "  - fzf: Fuzzy file finder"
          echo "  - ag: The Silver Searcher"
          echo "  - ctags: Source code indexing"
          echo "  - global: Source code tagging"
          echo "  - ast-grep: AST-based code search"
          echo ""
          echo "Code analysis tools:"
          echo "  - cloc/scc/tokei: Code line counting"
          echo "  - bat: Syntax-highlighted cat"
          echo "  - delta: Git diff viewer"
          echo "  - difftastic: Structural diff tool"
          echo ""
          echo "To run the agent: code-hound"
          echo "To search code: rg 'pattern' ."
          echo "To find files: fd 'filename'"
          echo "To fuzzy search: fzf"
          echo "To view file with syntax: bat file.py"
          echo "To generate tags: ctags -R ."
        '';

        # Set environment variables for code search
        FZF_DEFAULT_COMMAND = "fd --type f --hidden --follow --exclude .git";
      };

      # Checks to validate the agent and code search environment
      checks.${system} = {
        code-hound-build = self.packages.${system}.code-hound;

        search-tools-check = pkgs.runCommand "search-tools-check" {
          buildInputs = [ codeHoundEnv ];
        } ''
          echo "Checking code search tools..."
          rg --version
          fd --version
          fzf --version
          ag --version
          ctags --version
          cloc --version
          bat --version
          echo "✅ Code search tools check passed"
          touch $out
        '';

        python-syntax-check = pkgs.runCommand "code-hound-syntax-check" {
          buildInputs = [ pythonEnv ];
        } ''
          AGENT_DIR="$HOME/.synapse-system/.synapse/agents/code-hound"
          if [[ -f "$AGENT_DIR/code_hound_agent.py" ]]; then
            echo "Checking Python syntax for Code Hound agent..."
            python -m py_compile "$AGENT_DIR/code_hound_agent.py"
            echo "✅ Python syntax check passed"
          else
            echo "⚠️  Agent file not found, skipping syntax check"
          fi
          touch $out
        '';
      };
    };
}
