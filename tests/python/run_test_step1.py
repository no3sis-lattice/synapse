import subprocess
import os

def run_command(command, cwd):
    print(f"Running command: {command} in {cwd}")
    process = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        capture_output=True,
        text=True
    )
    print(f"Stdout:\n{process.stdout}")
    print(f"Stderr:\n{process.stderr}")
    print(f"Exit Code: {process.returncode}")
    return process.returncode, process.stdout, process.stderr

def test_minimal_flake_case():
    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "step1"))
    print(f"Starting test for minimal flake case in: {test_dir}")

    # Step 1: nix flake update
    print("\n--- Running nix flake update ---")
    exit_code_update, stdout_update, stderr_update = run_command("nix flake update", test_dir)

    if exit_code_update != 0:
        print("\n!!! nix flake update FAILED !!!")
        return False

    print("\n--- Running nix build .#test-agent ---")
    exit_code_build, stdout_build, stderr_build = run_command("nix build .#test-agent", test_dir)

    if exit_code_build != 0:
        print("\n!!! nix build .#test-agent FAILED !!!")
        return False

    print("\n--- Test PASSED ---")
    return True

if __name__ == "__main__":
    if test_minimal_flake_case():
        print("Minimal flake test case executed successfully.")
    else:
        print("Minimal flake test case FAILED.")
