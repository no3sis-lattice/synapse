{
  description = "Mojo SDK runtime for Synapse System";

  inputs = {
    nixpkgs.url = "github:meta-introspector/nixpkgs?ref=feature/CRQ-016-nixify";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        # Note: Using local Mojo installation as src initially
        # TODO: Migrate to fetchurl from Modular servers after validation
        mojoVersion = "0.25.7";

        mojoRuntime = pkgs.stdenv.mkDerivation {
          pname = "mojo-runtime";
          version = mojoVersion;

          # Use existing local installation
          src = /home/m0xu/.synapse-system/.venv;

          nativeBuildInputs = with pkgs; [
            autoPatchelfHook
            makeWrapper
          ];

          buildInputs = with pkgs; [
            stdenv.cc.cc.lib
            zlib
            python312
          ];

          dontUnpack = true;
          dontBuild = true;

          installPhase = ''
            mkdir -p $out/bin
            mkdir -p $out/lib/python3.12/site-packages

            # Copy mojo binary
            cp -r $src/bin/mojo $out/bin/
            chmod +x $out/bin/mojo

            # Copy mojo Python package
            cp -r $src/lib/python3.12/site-packages/mojo* $out/lib/python3.12/site-packages/
          '';

          # Fix interpreter paths and PYTHONPATH
          postFixup = ''
            patchShebangs $out/bin/mojo
            wrapProgram $out/bin/mojo \
              --prefix PATH : ${pkgs.lib.makeBinPath [ pkgs.python312 ]} \
              --prefix PYTHONPATH : $out/lib/python3.12/site-packages
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
      })) // {
      # Expose lib at top level (not system-specific)
      lib = {
        mojoPath = system: "${self.packages.${system}.default}/bin/mojo";
      };
    };
}
