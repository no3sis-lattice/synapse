{
  description = "Test Runner Agent with multi-language testing frameworks";

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

        # Python testing frameworks
        pytest
        pytest-asyncio
        pytest-cov
        pytest-xdist
        coverage
        hypothesis
        tox
      ]);

      # Multi-language testing tools
      testEnv = pkgs.buildEnv {
        name = "test-runner-env";
        paths = with pkgs; [
          # Core utilities
          git
          curl
          jq

          # Python testing
          pythonEnv

          # Node.js testing
          nodejs_20
          nodePackages.jest
          nodePackages.mocha
          nodePackages.vitest

          # Rust testing
          rustc
          cargo
          cargo-tarpaulin

          # Go testing
          go
          gotestsum

          # Generic test tools
          bats  # Bash testing

          # Coverage and reporting
          lcov
          gcovr

          # Performance testing
          wrk
          k6
        ];
      };

      # Agent script that runs the actual Python implementation
      agentScript = pkgs.writeShellScript "test-runner-script" ''
        #!${pkgs.bash}/bin/bash
        set -euo pipefail

        AGENT_DIR="$HOME/.synapse-system/.synapse/agents/test-runner"

        if [[ ! -f "$AGENT_DIR/test_runner_agent.py" ]]; then
          echo "❌ Test Runner agent not found at $AGENT_DIR"
          echo "Please ensure the Synapse System is properly initialized."
          exit 1
        fi

        echo "🧪 Starting Test Runner Agent..."
        cd "$AGENT_DIR"

        # Add testing tools to PATH
        export PATH="${testEnv}/bin:$PATH"

        exec ${pythonEnv}/bin/python test_runner_agent.py "$@"
      '';

    in
    {
      packages.${system} = {
        test-runner = pkgs.writeShellScriptBin "test-runner" ''
          exec ${agentScript} "$@"
        '';

        default = self.packages.${system}.test-runner;
        test-env = testEnv;
      };

      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [ testEnv ];

        shellHook = ''
          echo "🧪 Test Runner Development Environment"
          echo "Available testing frameworks:"
          echo "  - Python: pytest, coverage, tox"
          echo "  - Node.js: jest, mocha, vitest"
          echo "  - Rust: cargo test, tarpaulin"
          echo "  - Go: go test, gotestsum"
          echo "  - Bash: bats"
          echo "  - Performance: wrk, k6"
          echo ""
          echo "To run the agent: test-runner"
        '';
      };

      checks.${system} = {
        test-runner-build = self.packages.${system}.test-runner;
      };
    };
}
