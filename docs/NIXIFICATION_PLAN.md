## Nixification Plan Summary

This document summarizes the current plan and progress for Nixifying the project.

### 1. Initial Goal & Challenges

*   **Goal:** Create a "lattice of Nix flakes," with one flake per module, to compose the Synapse system step-by-step.
*   **Initial Attempt:** We tried creating separate `flake.nix` files for each agent in `nix/flakes/` and referencing them via `path:` URLs in the root `flake.nix`.
*   **Result:** This approach consistently failed with a `flake.nix: No such file or directory` error during `nix flake check`. This suggested an environmental issue with how Nix handles local flake inputs in this specific setup.

### 2. Revised Strategy (Proposed Workaround)

Due to the persistent local flake input issue, we proposed a "**Monolithic Flake with Modular Structure**." This involves:

*   A single, top-level `flake.nix` that acts as the main entry point.
*   Modular `.nix` files (e.g., `nix/modules/architect.nix`) that define individual components (agents, libraries, etc.). These files are then *imported* into the main `flake.nix`.
*   **Benefit:** This approach avoids the problematic `path:` URL references for sub-flakes while still providing modularity and code organization.

### 3. Project Review & Analysis

A thorough review of the project's components was conducted:

*   **Python Components:**
    *   **Agents:** Located in `.synapse/agents/`, each with a main `*_agent.py` file and `tools/` submodules.
    *   **CLI Entry Point:** `bin/synapse` (Python script) imports `lib/cli.py`.
    *   **Shared Libraries:** `lib/` contains Python utility modules.
    *   **Neo4j Integration:** `.synapse/neo4j/` contains numerous Python scripts and its own `requirements.txt` files.
    *   **Health Check:** `synapse_health_check.py` (standalone Python script).
*   **Dependencies:**
    *   `requirements.txt` (root), `requirements-dev.txt` (root).
    *   `.synapse/neo4j/requirements.txt`, `.synapse/neo4j/requirements-minimal.txt`.
*   **Bash Scripts:** Top-level `install.sh`, `setup.sh`, `synapse.sh`, `setup-claude-code.sh`. Also, `scripts/architect.sh` and `scripts/utils.sh` (currently present).
*   **Configuration/Metadata:** `.synapse/AGENTS_MANIFEST.json`, `.synapse/tool-mapping.json`, agent `config.yml` files, `.env` files.

### 4. Current Progress

*   **Consolidated Dependencies:** All Python dependencies from various `requirements.txt` files have been merged into a single `nix/all-requirements.txt`.
*   **Updated Base `flake.nix`:** The root `flake.nix` has been modified to:
    *   Use `nix/all-requirements.txt` with `pip2nix` to create the core Python environment.
    *   Include development tools in the default `devShell`.
*   **GitHub Action:** A GitHub Action (`.github/workflows/nix-build.yml`) has been created and configured to use `meta-introspector` forks of actions, testing the Nix flake build on push/pull requests to `master`.
*   **Documentation:** `NIX_GUIDE.md` provides a new user onboarding guide.
*   **Existing Files:** Due to explicit user instruction, no files have been deleted. This means the `nix/flakes/` directory (with the old agent flakes) and the `scripts/` directory (with Bash scripts) are still present.
*   **Directory Created:** `nix/modules/` directory has been created.

### 5. Next Steps (Pending Clarification)

The last instruction was to "continue creating the lattice of flakes to mirror the python dependencesi. first lets make the foundational python flake. then we create a graph of modules, one flake per module, adding it into a new flake in the lattice."

Before proceeding, clarification is needed on the exact approach for modularity:

*   **Option A (Separate Flakes):** Do you intend to retry creating separate `flake.nix` files in subdirectories (e.g., `nix/flakes/architect/flake.nix`) and referencing them with `path:` URLs in the main `flake.nix`? (This approach previously failed).
*   **Option B (Modular `.nix` Files):** Or should I proceed with the proposed workaround of creating modular `.nix` files (e.g., `nix/modules/architect.nix`) that are *imported* into a single top-level `flake.nix`? (This avoids the local flake input issue while still providing modularity).

Your guidance on this choice is crucial to avoid repeating past issues.