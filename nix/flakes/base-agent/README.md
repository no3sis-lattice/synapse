./vendor/nix/mach-nix/mach_nix/nix/lib.nix
          pythonModule = python;
./vendor/nix/mach-nix/mach_nix/nix/mk-python-derivation-overlay.nix
            pkg_pyver = l.get_py_ver p.pythonModule;
                ${p.pname} from 'packagesExtra' is built with python ${p.pythonModule.version},
      ) (filter (p: l.is_src p || p ? pythonModule) packagesExtra);
      extra_pkgs_other = filter (p: ! (p ? rCommand || p ? pythonModule || l.is_src p)) packagesExtra;
./vendor/nix/mach-nix/mach_nix/nix/mkPython.nix
              #pythonModule,
     #   pythonEnv = pythonModule { inherit pkgs pythonPackagesFile; };
