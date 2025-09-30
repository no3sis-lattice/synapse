# Instructions and Tasks for Next Agents

This document provides context, current status, and a detailed set of tasks for subsequent AI agents (e.g., Claude Code agents) to continue the development of the `synapse-system` project, specifically focusing on Nix flake configuration and Python environment management.

## Project Context

The `synapse-system` project leverages Nix flakes to achieve reproducible development environments and consistent packaging. A foundational pattern has been established for managing Python environments:

*   A dedicated `base-agent` flake is responsible for defining, building, and exposing a self-contained Python environment.
*   Other agent-specific flakes (e.g., `Pneuma`, `architect`) consume this shared Python environment from the `base-agent` flake.
*   A strict Standard Operating Procedure (SOP) dictates that all inter-flake dependencies must be referenced using GitHub URLs (e.g., `github:owner/repo?dir=path/to/flake&ref=branch`), minimizing the use of local `path:` references.

## Current Status

As of this handover, the following has been achieved:

*   The `base-agent` flake (`nix/flakes/base-agent/flake.nix`) has been correctly configured to define and expose the project's primary Python environment.
*   The `Pneuma` agent flake (`nix/flakes/Pneuma/flake.nix`) has been successfully updated to consume the `base-agent`'s Python environment via its GitHub URL, adhering to the established pattern.
*   The main `flake.nix` at the project root is configured to orchestrate these dependencies and pass necessary inputs.
*   A documentation file, `docs/nix_python_pattern.md`, has been created to explain the established pattern in detail.
*   An executable script, `update_flake_lock.sh`, has been created to facilitate updating the `flake.lock` file.

## Goal for Next Agents

The primary goal is to systematically apply the established Nix Python environment management pattern across all remaining Python-based agent flakes within the project. This involves ensuring each agent flake correctly consumes the `base-agent`'s Python environment via GitHub URLs, thereby stabilizing the overall Nix build and ensuring full adherence to the defined SOPs.

## Detailed Set of Tasks

### Task 1: Apply Python Environment Pattern to `architect` Agent Flake

*   **Objective:** Modify `nix/flakes/architect/flake.nix` to correctly consume the `base-agent`'s Python environment using the established pattern.
*   **Steps:**
    1.  **Add `base-agent` as an input:** In `nix/flakes/architect/flake.nix`, add the following to the `inputs` section:
        ```nix
        base-agent.url = "github:meta-introspector/synapse-system?dir=nix/flakes/base-agent&ref=feature/base-agent-flake";
        ```
    2.  **Include `base-agent` in `outputs` arguments:** Ensure `base-agent` is present in the `outputs` function arguments:
        ```nix
        outputs = { self, nixpkgs, flake-utils, pip2nix, base-agent, ... }:
        ```
    3.  **Define `pythonEnv`:** In the `let` block of the `outputs` function, define `pythonEnv`:
        ```nix
        let
          # ...
          pythonEnv = base-agent.pythonEnv.${system};
        in
        ```
    4.  **Use `pythonEnv`:** In the `packages.default` definition, ensure the `architect_agent.py` script is executed using the `pythonEnv`:
        ```nix
        packages.default = pkgs.writeShellScriptBin "architect-agent" ''
          #!${pkgs.bash}/bin/bash
          ${pythonEnv}/bin/python ${./.synapse/agents/architect/architect_agent.py} "$@"
        '';
        ```
    5.  **Verify Build:** After making these changes, run `nix build` from the project root to confirm that the overall build remains successful.
    6.  **Commit Changes:** Commit the changes to `nix/flakes/architect/flake.nix` with a descriptive message (e.g., `feat: Configure architect agent to use base-agent via GitHub URL`).

### Task 2: Apply Python Environment Pattern to All Other Python-based Agent Flakes

*   **Objective:** Systematically identify and modify all other Python-based agent flakes located in `nix/flakes/` to adhere to the established pattern.
*   **Steps:**
    1.  **Identify Python Agent Flakes:** Use `glob` or directory listing tools to find all `flake.nix` files within the `nix/flakes/` directory that correspond to Python-based agents (e.g., `python-dev`, `python-specialist`, `code-hound`, `security-specialist`, etc.).
    2.  **For each identified flake:** Apply the same modification steps as detailed in Task 1 (adding `base-agent` input, including it in `outputs` arguments, defining `pythonEnv`, and using it for script execution).
    3.  **Verify Build:** After modifying each individual flake, run `nix build` from the project root to confirm the changes do not introduce new build errors.
    4.  **Commit Changes:** Commit changes for each modified flake with a descriptive message (e.g., `feat: Configure <agent-name> agent to use base-agent via GitHub URL`).

### Task 3: Review and Update Main `flake.nix` for Consistency

*   **Objective:** Ensure the main `flake.nix` at the project root consistently uses the established pattern for all agent flakes and is free of redundant or commented-out code.
*   **Steps:**
    1.  **Verify Agent Inputs:** Confirm that all agent flakes (including `AGENT1`, `ARCHITECT`, and any others modified in Task 2) are declared as inputs in the main `flake.nix` using their correct GitHub URLs.
    2.  **Verify `configuredBaseAgent` Usage:** Ensure `configuredBaseAgent` is correctly defined and passed as the `base-agent` input to all agent flakes when calling their `outputs` functions.
    3.  **Verify `devShells.default`:** Confirm that the `devShells.default` in the main `flake.nix` correctly uses `configuredBaseAgent.pythonEnv.${system}` for its `buildInputs`.
    4.  **Clean up Comments:** Remove any remaining commented-out or redundant lines from the main `flake.nix`.
    5.  **Verify Build:** Run `nix build` from the project root to confirm the overall build remains successful after cleanup.
    6.  **Commit Changes:** Commit with a descriptive message (e.g., `refactor: Clean up main flake.nix and ensure consistent agent consumption`).

### Task 4: Update `flake.lock` and Commit

*   **Objective:** Ensure the `flake.lock` file is fully up-to-date and accurately reflects all the changes made to the flake inputs.
*   **Steps:**
    1.  Execute the `./update_flake_lock.sh` script from the project root.
    2.  Commit the updated `flake.lock` file with a descriptive message (e.g., `chore: Update flake.lock after flake configuration changes`).

### Task 5: Review and Refine Documentation

*   **Objective:** Ensure the `docs/nix_python_pattern.md` documentation is accurate, comprehensive, and reflects the final implemented pattern across all flakes.
*   **Steps:**
    1.  Review the content of `docs/nix_python_pattern.md` to ensure it accurately describes the current state and best practices.
    2.  Add any further insights, clarifications, or examples gained during the implementation of the preceding tasks.
    3.  Commit any documentation updates with a descriptive message (e.g., `docs: Refine Nix Python pattern documentation`).
