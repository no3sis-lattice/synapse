# New User's Guide to the Nix Environment

This document explains how to use the Nix-based development environment for this project.

## What is this?

This project uses [Nix](https://nixos.org/) to create a reproducible development environment. This ensures that all developers have the exact same versions of all tools and dependencies, eliminating "works on my machine" problems.

The entire environment is defined in the `flake.nix` file in the root of this project.

## Getting Started

### Prerequisites

Before you begin, you must have Nix installed on your system with support for flakes enabled. If you do not, please follow the [official installation guide](https://nixos.org/download.html).

### Step 1: Enter the Environment

To activate the development environment, navigate to the root directory of this project in your terminal and run the following command:

```bash
nix develop
```

Nix will automatically download all the specified dependencies and place you into a new shell session. This might take some time on the first run. You'll know you are in the environment when you see your shell prompt change.

### Step 2: Verify the Environment

Once inside the shell, you can verify that everything is working correctly.

1.  **Check the Python version:**

    ```bash
    which python
    ```

    This should point to a path inside the `/nix/store`, not your system's default Python.

2.  **Check that Python packages are available:**

    The environment automatically includes all packages from `requirements.txt`. You can test this by trying to import `redis`:

    ```bash
    python -c "import redis; print('Successfully imported redis')"
    ```

    You should see the success message with no import errors.

## What's Included?

The development shell currently provides:

- A specific version of Python.
- All Python packages defined in `requirements.txt` (currently `redis`).
- A set of core utilities for development, including `bash`, `coreutils`, and `nix` itself.

## Agent Flake Architecture

The Synapse System uses a modular flake architecture where each agent is its own independent flake:

```
nix/flakes/
├── architect/flake.nix           # System design agent
├── rust-specialist/flake.nix     # Rust language expert
├── python-specialist/flake.nix   # Python language expert
├── typescript-specialist/flake.nix
├── golang-specialist/flake.nix
├── synapse-project-manager/flake.nix
├── code-hound/flake.nix         # Code quality
├── devops-engineer/flake.nix     # Infrastructure
└── ... (17 total agents)
```

Each agent flake exports a package that can be built independently or composed together via the main `flake.nix`.

## Hybrid Architecture: Docker + Nix

The system uses a hybrid approach for optimal development and deployment:

- **Docker**: Stateful services (Neo4j, Redis) for data persistence
- **Nix**: Stateless tools, agents, and build environment for reproducibility

This gives you the best of both worlds:
- Database services remain easy to manage with `docker-compose`
- Development tools are completely reproducible with Nix
- No dependency conflicts between Python, Rust, Go components

## Practical Usage

```bash
# Enter development environment
nix develop

# Build specific agent
nix build .#rust-specialist

# Build all agents
nix build

# See all available packages
nix flake show
```
