# Nix Python Environment Management Pattern

This document outlines the established pattern for managing Python environments across our Nix flakes, ensuring adherence to the "all references are to GitHub" SOP and promoting modularity, reusability, and reproducibility.

## Core Principles

1.  **Single Source of Truth for Python Environment:** A dedicated `base-agent` flake is responsible for defining and exposing the project's primary Python environment.
2.  **GitHub-Only References:** All inter-flake dependencies are expressed using GitHub URLs, eliminating `path:` references where possible.
3.  **Modular Design:** Each flake has a clear, well-defined responsibility, contributing to a maintainable and scalable architecture.
4.  **Explicit Input/Output Contracts:** Flakes clearly define what inputs they expect and what outputs they provide.

## The Pattern

### 1. `base-agent` Flake (The Python Environment Provider)

This flake is responsible for constructing and exposing the shared Python environment.

*   **Location:** `nix/flakes/base-agent/flake.nix`
*   **Inputs to `outputs` function:**
    *   `self`: Reference to the flake itself.
    *   `nixpkgs`: The pinned Nixpkgs instance.
    *   `flake-utils`: The `flake-utils` library.
    *   `pip2nix`: The `pip2nix` tool.
    *   `pythonModule`: The function imported from `nix/modules/python-env.nix`.
    *   `pythonPackagesFile`: The path to `nix/python-packages.nix`.
*   **Internal Logic:** Within its `let` block, it calls the `pythonModule` function with `pkgs` (derived from `nixpkgs`) and `pythonPackagesFile` to construct the `pythonEnv`.
    ```nix
    # In nix/flakes/base-agent/flake.nix
    outputs = { self, nixpkgs, flake-utils, pip2nix, pythonModule, pythonPackagesFile, ... }:
      flake-utils.lib.eachDefaultSystem (system:
        let
          pkgs = import nixpkgs { inherit system; };
          pythonEnv = pythonModule { inherit pkgs pythonPackagesFile; };
        in
        {
          pythonEnv = pythonEnv; # Expose the Python environment
        }
      );
    ```
*   **Outputs:** Exposes the fully configured `pythonEnv` as an attribute in its output set (e.g., `base-agent.pythonEnv.${system}`).

### 2. Consumer Flakes (e.g., `Pneuma`, `architect`)

These flakes depend on and utilize the shared Python environment provided by `base-agent`.

*   **Location:** `nix/flakes/Pneuma/flake.nix`, `nix/flakes/architect/flake.nix`
*   **Inputs:**
    *   Declares `base-agent` as an input using its **GitHub URL**.
        ```nix
        # In nix/flakes/Pneuma/flake.nix
        inputs = {
          # ... other inputs ...
          base-agent.url = "github:meta-introspector/synapse-system?dir=nix/flakes/base-agent&ref=feature/base-agent-flake";
        };
        ```
*   **`outputs` Function Arguments:** Includes `base-agent` in its `outputs` function arguments.
    ```nix
    # In nix/flakes/Pneuma/flake.nix
    outputs = { self, nixpkgs, flake-utils, pip2nix, base-agent, ... }:
      # ...
    ```
*   **Consumption:** Accesses the shared Python environment via `pythonEnv = base-agent.pythonEnv.${system};` within its `let` block.
*   **Usage:** Utilizes this `pythonEnv` to run Python scripts (e.g., `${pythonEnv}/bin/python`) or includes it in `buildInputs` for specific packages or development shells.

### 3. Main `flake.nix` (The Orchestrator)

This is the top-level flake that orchestrates the entire system, defining the overall structure and passing necessary inputs.

*   **Location:** `flake.nix` (root of the project)
*   **Inputs:**
    *   Declares `AGENT1`, `ARCHITECT`, and `base-agent` as inputs using their respective **GitHub URLs**.
        ```nix
        # In main flake.nix
        inputs = {
          # ... other inputs ...
          AGENT1.url = "github:meta-introspector/synapse-system?dir=nix/flakes/Pneuma&ref=feature/base-agent-flake";
          ARCHITECT.url = "github:meta-introspector/synapse-system?dir=nix/flakes/architect&ref=feature/base-agent-flake";
          base-agent.url = "github:meta-introspector/synapse-system?dir=nix/flakes/base-agent&ref=feature/base-agent-flake";
        };
        ```
*   **Internal Logic (within `outputs`' `let` block):**
    *   Defines `pythonModule = import ./nix/modules/python-env.nix;` and `pythonPackagesFile = ./nix/python-packages.nix;`.
    *   Calls `base-agent.outputs { inherit self nixpkgs flake-utils pip2nix pythonModule pythonPackagesFile; }` to get the *configured* `base-agent` outputs (including the `pythonEnv`). This result is stored in `configuredBaseAgent`.
*   **Consumption:**
    *   Calls `AGENT1.outputs { inherit self nixpkgs flake-utils pip2nix; base-agent = configuredBaseAgent; }` and `ARCHITECT.outputs { inherit self nixpkgs flake-utils pip2nix; base-agent = configuredBaseAgent; }` to pass the *configured* `base-agent` to these consumer flakes.
    *   **`devShells.default`:** Uses `configuredBaseAgent.pythonEnv.${system}` for its `buildInputs` to provide a consistent development environment.

## Benefits of this Pattern

*   **Strict Adherence to SOP:** All inter-flake dependencies are explicitly GitHub URLs.
*   **Self-Contained Environment:** The Python environment is fully defined and managed within our project's flakes, with no external dependencies for the environment itself.
*   **Modularity and Reusability:** Each flake has a clear, well-defined responsibility, promoting a clean and maintainable architecture.
*   **Reproducibility:** Leveraging Nix flakes ensures that the environment is reproducible across different systems and times.
*   **Clarity and Consistency:** The explicit passing of inputs and outputs makes the data flow transparent and consistent.
