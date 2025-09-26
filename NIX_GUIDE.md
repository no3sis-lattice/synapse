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

## Next Steps: Building the Modules

Now that we have a stable base environment, the next phase is to modularize the system.

We will create a `nix/modules` directory. For each agent in the project, we will create a corresponding `.nix` file (e.g., `nix/modules/architect.nix`). The main `flake.nix` will import these files to build and compose the entire system, package by package.
