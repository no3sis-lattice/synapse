{
  description = "Rust Specialist Agent with full Rust development environment";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };

      # Python environment for the agent runner (agents are Python scripts)
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

      # Rust development environment with all necessary tools
      rustEnv = pkgs.buildEnv {
        name = "rust-specialist-env";
        paths = with pkgs; [
          # Rust toolchain
          rustc
          cargo
          rustfmt
          clippy
          rust-analyzer

          # Additional Rust tools
          cargo-edit
          cargo-watch
          cargo-audit
          cargo-deny
          cargo-outdated
          cargo-tree
          cargo-expand

          # Cross-compilation support
          cargo-cross

          # Testing and benchmarking
          cargo-tarpaulin
          cargo-criterion

          # Documentation
          mdbook
        ];
      };

      # Agent script that runs the actual Python implementation with Rust tools available
      agentScript = pkgs.writeShellScript "rust-specialist-runner" ''
        #!${pkgs.bash}/bin/bash
        set -euo pipefail

        AGENT_DIR="$HOME/.synapse-system/.synapse/agents/rust-specialist"

        if [[ ! -f "$AGENT_DIR/rust_specialist_agent.py" ]]; then
          echo "❌ Rust specialist agent not found at $AGENT_DIR"
          echo "Please ensure the Synapse System is properly initialized."
          exit 1
        fi

        echo "🦀 Starting Rust Specialist Agent..."
        cd "$AGENT_DIR"

        # Add Rust tools to PATH
        export PATH="${rustEnv}/bin:$PATH"

        # Set Rust environment variables
        export RUST_BACKTRACE=1
        export CARGO_HOME="$HOME/.cargo"
        export RUSTUP_HOME="$HOME/.rustup"

        exec ${pythonEnv}/bin/python rust_specialist_agent.py "$@"
      '';

    in
    {
      packages.${system} = {
        rust-specialist = pkgs.writeShellScriptBin "rust-specialist" ''
          exec ${agentScript} "$@"
        '';

        default = self.packages.${system}.rust-specialist;

        # Full Rust development environment
        rust-dev-env = rustEnv;
      };

      # Development shell with complete Rust toolchain
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          pythonEnv
          rustEnv

          # Development utilities
          git
          curl
          jq
          pkg-config
          openssl

          # System libraries commonly needed for Rust development
          sqlite
          postgresql
        ];

        shellHook = ''
          echo "🦀 Rust Specialist Development Environment"
          echo "Rust version: $(rustc --version)"
          echo "Cargo version: $(cargo --version)"
          echo ""
          echo "Available tools:"
          echo "  - cargo: Build system and package manager"
          echo "  - rustfmt: Code formatter"
          echo "  - clippy: Linter and code analysis"
          echo "  - rust-analyzer: Language server"
          echo "  - cargo-edit: Add/remove dependencies"
          echo "  - cargo-watch: Watch for changes and rebuild"
          echo "  - cargo-audit: Security vulnerability database"
          echo ""
          echo "To run the agent: rust-specialist"
          echo "To create a new Rust project: cargo new my-project"
          echo "To format code: cargo fmt"
          echo "To run lints: cargo clippy"
          echo "To run tests: cargo test"
        '';

        # Set environment variables for Rust development
        RUST_BACKTRACE = "1";
        RUST_LOG = "debug";
      };

      # Checks to validate the agent and Rust environment
      checks.${system} = {
        rust-specialist-build = self.packages.${system}.rust-specialist;

        rust-toolchain-check = pkgs.runCommand "rust-toolchain-check" {
          buildInputs = [ rustEnv ];
        } ''
          echo "Checking Rust toolchain..."
          rustc --version
          cargo --version
          rustfmt --version
          cargo clippy --version
          echo "✅ Rust toolchain check passed"
          touch $out
        '';

        python-syntax-check = pkgs.runCommand "rust-agent-syntax-check" {
          buildInputs = [ pythonEnv ];
        } ''
          AGENT_DIR="$HOME/.synapse-system/.synapse/agents/rust-specialist"
          if [[ -f "$AGENT_DIR/rust_specialist_agent.py" ]]; then
            echo "Checking Python syntax for Rust agent..."
            python -m py_compile "$AGENT_DIR/rust_specialist_agent.py"
            echo "✅ Python syntax check passed"
          else
            echo "⚠️  Agent file not found, skipping syntax check"
          fi
          touch $out
        '';
      };
    };
}
