{
  pkgs ? import <nixpkgs> {},
}:

pkgs.mkShell {
  buildInputs = [
    pkgs.python3
    (pkgs.python3.withPackages (ps: [ ps.pip-tools ps.pipdeptree ]))
  ];
}
