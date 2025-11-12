#!/usr/bin/env bash
# Wrapper script for Podman Compose
# This ensures the correct socket is used

export DOCKER_HOST=unix:///run/user/1000/podman/podman.sock
podman compose "$@"
