#!/usr/bin/env bash

SCRIPT_NAME="test_nix_setup.sh"
LOG_DIR="logs"
REPORT_DIR="qa_reports"

mkdir -p "$LOG_DIR"
mkdir -p "$REPORT_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/${SCRIPT_NAME%.sh}_${TIMESTAMP}.log"
REPORT_FILE="$REPORT_DIR/QA_Report_${TIMESTAMP}.md"

# --- Logging Function --- #
log_message() {
    local type="$1"
    local message="$2"
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] [$type] $message" | tee -a "$LOG_FILE"
}

# --- Test Execution --- #
log_message INFO "Starting Nix setup meta-test..."
log_message INFO "Running: nix flake check"

START_TIME=$(date +%s)

# Execute nix flake check and capture output
NIX_STDOUT=$(nix flake check 2>&1)
NIX_EXIT_CODE=$?

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

log_message INFO "Nix flake check completed with exit code: $NIX_EXIT_CODE"
log_message DEBUG "Nix flake check STDOUT/STDERR:\n$NIX_STDOUT"

# --- QA Report Generation --- #
REPORT_CONTENT="# QA Report: Nix Flake Setup - ${TIMESTAMP}\n\n"
REPORT_CONTENT+="## Test: Nix Flake Check\n\n"
REPORT_CONTENT+="*   **Date/Time:** $(date)\n"
REPORT_CONTENT+="*   **Duration:** ${DURATION} seconds\n"
REPORT_CONTENT+="*   **Command:** `nix flake check`\n"
REPORT_CONTENT+="*   **Exit Code:** ${NIX_EXIT_CODE}\n\n"

if [[ $NIX_EXIT_CODE -eq 0 ]]; then
    REPORT_CONTENT+="## Result: ✅ PASS\n\n"
    REPORT_CONTENT+="The Nix flake setup appears to be functional.\n\n"
else
    REPORT_CONTENT+="## Result: ❌ FAIL\n\n"
    REPORT_CONTENT+="The Nix flake setup encountered an error. This is likely due to the persistent `path:` input issue as described in `NIXIFICATION_PLAN.md`.\n\n"
fi

REPORT_CONTENT+="### Full Output (STDOUT/STDERR):\n\n```\n${NIX_STDOUT}\n```\n\n"

echo -e "$REPORT_CONTENT" > "$REPORT_FILE"

log_message INFO "QA Report generated: $REPORT_FILE"

exit $NIX_EXIT_CODE
