{
  description = "UX Designer Agent with design tools and accessibility analysis";

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };

      pythonEnv = pkgs.python312.withPackages (ps: with ps; [
        asyncio-mqtt aiofiles rich pyyaml neo4j redis numpy requests
        pillow matplotlib seaborn
      ]);

      designEnv = pkgs.buildEnv {
        name = "ux-designer-env";
        paths = with pkgs; [
          git curl jq
          # Image and design tools
          imagemagick
          inkscape
          # Web development for prototyping
          nodejs_20
          nodePackages.prettier
          nodePackages.eslint
          # Accessibility tools
          pa11y
          # Color and design utilities
          pandoc
        ];
      };

      agentScript = pkgs.writeShellScript "ux-designer-script" ''
        AGENT_DIR="$HOME/.synapse-system/.synapse/agents/ux-designer"
        [[ -f "$AGENT_DIR/ux_designer_agent.py" ]] || { echo "Agent not found"; exit 1; }
        echo "🎨 Starting UX Designer Agent..."
        cd "$AGENT_DIR"
        export PATH="${designEnv}/bin:$PATH"
        exec ${pythonEnv}/bin/python ux_designer_agent.py "$@"
      '';

    in {
      packages.${system} = {
        ux-designer = pkgs.writeShellScriptBin "ux-designer" ''exec ${agentScript} "$@"'';
        default = self.packages.${system}.ux-designer;
      };
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [ designEnv pythonEnv ];
        shellHook = ''
          echo "🎨 UX Designer Development Environment"
          echo "Tools: imagemagick, inkscape, pa11y, prettier"
        '';
      };
      checks.${system}.ux-designer-build = self.packages.${system}.ux-designer;
    };
}
