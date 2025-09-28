{
  description = "Golang Specialist Agent with full Go development environment";

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

      # Go development environment with all necessary tools
      golangEnv = pkgs.buildEnv {
        name = "golang-specialist-env";
        paths = with pkgs; [
          # Go toolchain
          go
          gopls  # Go language server

          # Development tools
          gotools  # Contains goimports, godoc, etc.
          go-tools # Contains staticcheck, etc.
          golangci-lint
          gosec
          go-critic

          # Testing and benchmarking
          gotestsum
          go-junit-report

          # Code generation
          protobuf
          protoc-gen-go
          protoc-gen-go-grpc

          # Build and deployment tools
          goreleaser
          ko

          # Debug tools
          delve

          # Documentation
          godoc

          # Package management utilities
          go-mod-outdated
        ];
      };

      # Agent script that runs the actual Python implementation with Go tools available
      agentScript = pkgs.writeShellScript "golang-specialist-runner" ''
        #!${pkgs.bash}/bin/bash
        set -euo pipefail

        AGENT_DIR="$HOME/.synapse-system/.synapse/agents/golang-specialist"

        if [[ ! -f "$AGENT_DIR/golang_specialist_agent.py" ]]; then
          echo "❌ Golang specialist agent not found at $AGENT_DIR"
          echo "Please ensure the Synapse System is properly initialized."
          exit 1
        fi

        echo "🐹 Starting Golang Specialist Agent..."
        cd "$AGENT_DIR"

        # Add Go tools to PATH
        export PATH="${golangEnv}/bin:$PATH"

        # Set Go environment variables
        export GOPATH="$HOME/go"
        export GOBIN="$GOPATH/bin"
        export GO111MODULE=on
        export GOPROXY=https://proxy.golang.org,direct
        export GOSUMDB=sum.golang.org

        # Ensure GOPATH exists
        mkdir -p "$GOPATH/src" "$GOPATH/bin" "$GOPATH/pkg"

        exec ${pythonEnv}/bin/python golang_specialist_agent.py "$@"
      '';

    in
    {
      packages.${system} = {
        golang-specialist = pkgs.writeShellScriptBin "golang-specialist" ''
          exec ${agentScript} "$@"
        '';

        default = self.packages.${system}.golang-specialist;

        # Full Go development environment
        golang-dev-env = golangEnv;
      };

      # Development shell with complete Go toolchain
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          pythonEnv
          golangEnv

          # Development utilities
          git
          curl
          jq

          # Additional development tools
          gnumake
          gcc  # For CGO
        ];

        shellHook = ''
          echo "🐹 Golang Specialist Development Environment"
          echo "Go version: $(go version)"
          echo ""
          echo "Available tools:"
          echo "  - go: Go compiler and toolchain"
          echo "  - gopls: Go language server"
          echo "  - goimports: Import formatter"
          echo "  - golangci-lint: Comprehensive linter"
          echo "  - gosec: Security checker"
          echo "  - delve: Debugger"
          echo "  - goreleaser: Release automation"
          echo "  - protoc: Protocol buffer compiler"
          echo ""
          echo "To run the agent: golang-specialist"
          echo "To create a new Go module: go mod init example.com/module"
          echo "To format code: go fmt ./..."
          echo "To run lints: golangci-lint run"
          echo "To run tests: go test ./..."
          echo "To build: go build"
          echo "To run security check: gosec ./..."
        '';

        # Set environment variables for Go development
        GOPATH = "$HOME/go";
        GO111MODULE = "on";
        CGO_ENABLED = "1";
      };

      # Checks to validate the agent and Go environment
      checks.${system} = {
        golang-specialist-build = self.packages.${system}.golang-specialist;

        golang-toolchain-check = pkgs.runCommand "golang-toolchain-check" {
          buildInputs = [ golangEnv ];
        } ''
          echo "Checking Go toolchain..."
          go version
          gopls version
          golangci-lint --version
          gosec --version
          echo "✅ Go toolchain check passed"
          touch $out
        '';

        python-syntax-check = pkgs.runCommand "golang-agent-syntax-check" {
          buildInputs = [ pythonEnv ];
        } ''
          AGENT_DIR="$HOME/.synapse-system/.synapse/agents/golang-specialist"
          if [[ -f "$AGENT_DIR/golang_specialist_agent.py" ]]; then
            echo "Checking Python syntax for Golang agent..."
            python -m py_compile "$AGENT_DIR/golang_specialist_agent.py"
            echo "✅ Python syntax check passed"
          else
            echo "⚠️  Agent file not found, skipping syntax check"
          fi
          touch $out
        '';
      };
    };
}
