{
  description = "TypeScript Specialist Agent with full Node.js/TypeScript development environment";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };

      # Python environment for the agent runner
      pythonEnv = pkgs.python312.withPackages (ps: with ps; [
        asyncio-mqtt
        aiofiles
        rich
        pyyaml
        neo4j
        redis
        numpy
        requests
      ]);

      # Node.js environment with TypeScript tools
      nodejsEnv = pkgs.buildEnv {
        name = "typescript-specialist-env";
        paths = with pkgs; [
          # Node.js runtime and package manager
          nodejs_20
          npm
          yarn
          pnpm

          # TypeScript toolchain
          typescript
          nodePackages.typescript-language-server

          # Development tools
          nodePackages.eslint
          nodePackages.prettier
          nodePackages.ts-node
          nodePackages.nodemon

          # Testing frameworks
          nodePackages.jest
          nodePackages.mocha
          nodePackages.vitest

          # Build tools
          nodePackages.webpack
          nodePackages.vite
          nodePackages.rollup
          nodePackages.esbuild

          # Package management utilities
          nodePackages.npm-check-updates
          nodePackages.depcheck

          # Documentation
          nodePackages.typedoc
        ];
      };

      # Agent script that runs the actual Python implementation with Node.js tools available
      agentScript = pkgs.writeShellScript "typescript-specialist-runner" ''
        #!${pkgs.bash}/bin/bash
        set -euo pipefail

        AGENT_DIR="$HOME/.synapse-system/.synapse/agents/typescript-specialist"

        if [[ ! -f "$AGENT_DIR/typescript_specialist_agent.py" ]]; then
          echo "❌ TypeScript specialist agent not found at $AGENT_DIR"
          echo "Please ensure the Synapse System is properly initialized."
          exit 1
        fi

        echo "📘 Starting TypeScript Specialist Agent..."
        cd "$AGENT_DIR"

        # Add Node.js tools to PATH
        export PATH="${nodejsEnv}/bin:$PATH"

        # Set Node.js environment variables
        export NODE_ENV=development
        export NPM_CONFIG_PREFIX="$HOME/.npm-global"

        exec ${pythonEnv}/bin/python typescript_specialist_agent.py "$@"
      '';

    in
    {
      packages.${system} = {
        typescript-specialist = pkgs.writeShellScriptBin "typescript-specialist" ''
          exec ${agentScript} "$@"
        '';

        default = self.packages.${system}.typescript-specialist;

        # Full TypeScript/Node.js development environment
        typescript-dev-env = nodejsEnv;
      };

      # Development shell with complete TypeScript/Node.js toolchain
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          pythonEnv
          nodejsEnv

          # Development utilities
          git
          curl
          jq

          # Additional development tools
          nodePackages.serve
          nodePackages.http-server
        ];

        shellHook = ''
          echo "📘 TypeScript Specialist Development Environment"
          echo "Node.js version: $(node --version)"
          echo "npm version: $(npm --version)"
          echo "TypeScript version: $(tsc --version)"
          echo ""
          echo "Available tools:"
          echo "  - tsc: TypeScript compiler"
          echo "  - ts-node: TypeScript execution environment"
          echo "  - eslint: JavaScript/TypeScript linter"
          echo "  - prettier: Code formatter"
          echo "  - jest/vitest: Testing frameworks"
          echo "  - webpack/vite: Build tools"
          echo "  - npm/yarn/pnpm: Package managers"
          echo ""
          echo "To run the agent: typescript-specialist"
          echo "To create a new TypeScript project: npm init -y && npm install typescript @types/node"
          echo "To compile TypeScript: tsc"
          echo "To run TypeScript directly: ts-node file.ts"
          echo "To format code: prettier --write ."
          echo "To lint code: eslint ."
          echo "To run tests: npm test"
        '';

        # Set environment variables for Node.js development
        NODE_ENV = "development";
      };

      # Checks to validate the agent and TypeScript environment
      checks.${system} = {
        typescript-specialist-build = self.packages.${system}.typescript-specialist;

        nodejs-toolchain-check = pkgs.runCommand "nodejs-toolchain-check" {
          buildInputs = [ nodejsEnv ];
        } ''
          echo "Checking Node.js toolchain..."
          node --version
          npm --version
          tsc --version
          eslint --version
          prettier --version
          echo "✅ Node.js/TypeScript toolchain check passed"
          touch $out
        '';

        python-syntax-check = pkgs.runCommand "typescript-agent-syntax-check" {
          buildInputs = [ pythonEnv ];
        } ''
          AGENT_DIR="$HOME/.synapse-system/.synapse/agents/typescript-specialist"
          if [[ -f "$AGENT_DIR/typescript_specialist_agent.py" ]]; then
            echo "Checking Python syntax for TypeScript agent..."
            python -m py_compile "$AGENT_DIR/typescript_specialist_agent.py"
            echo "✅ Python syntax check passed"
          else
            echo "⚠️  Agent file not found, skipping syntax check"
          fi
          touch $out
        '';
      };
    };
}
