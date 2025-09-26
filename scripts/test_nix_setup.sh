#!/usr/bin/env bash

# Execute nix flake check and capture output
nix flake check
exit $?