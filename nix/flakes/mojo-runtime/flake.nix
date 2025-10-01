{
  description = "Mojo SDK runtime for Synapse System";

  inputs = {
    nixpkgs.url = "github:meta-introspector/nixpkgs?ref=feature/CRQ-016-nixify";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        # Note: Using local Mojo installation as src initially
        # TODO: Migrate to fetchurl from Modular servers after validation
        mojoVersion = "0.25.7";

        mojoRuntime = pkgs.stdenv.mkDerivation {
          pname = "mojo-runtime";
          version = mojoVersion;

          # Use existing local installation
          src = /home/m0xu/.synapse-system/.venv/bin;

          buildInputs = with pkgs; [
            autoPatchelfHook
            stdenv.cc.cc.lib
            zlib
          ];

          dontBuild = true;

          installPhase = ''
            mkdir -p $out/bin
            cp -r $src/mojo $out/bin/
            chmod +x $out/bin/mojo
          '';

          meta = with pkgs.lib; {
            description = "Mojo programming language compiler and runtime";
            homepage = "https://www.modular.com/mojo";
            license = licenses.unfree;
            platforms = [ "x86_64-linux" "aarch64-linux" ];
          };
        };

      in {
        packages = {
          default = mojoRuntime;
          mojo = mojoRuntime;
        };

        # Expose mojo path for dependent flakes
        lib = {
          mojoPath = "${mojoRuntime}/bin/mojo";
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [ mojoRuntime ];

          shellHook = ''
            echo "🔥 Mojo Runtime Environment"
            echo "Mojo version: $(mojo --version 2>&1 | head -n1 || echo 'Not available')"
            echo ""
            echo "Available commands:"
            echo "  mojo --version    - Check Mojo version"
            echo "  mojo run <file>   - Run Mojo program"
            echo "  mojo build <file> - Compile Mojo to binary/library"
          '';
        };
      });
}
