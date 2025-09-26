#!/usr/bin/env bash

# Function to log script execution
log_execution() {
    local script_name="$1"
    local function_name="$2"
    local log_file="$3"
    local status="$4"
    local stdout_content="$5"
    local stderr_content="$6"
    local start_time="$7"
    local end_time="$8"

    echo "--- Log Start: $(date) ---" >> "$log_file"
    echo "Script: $script_name" >> "$log_file"
    echo "Function: $function_name" >> "$log_file"
    echo "Start Time: $start_time" >> "$log_file"
    echo "End Time: $end_time" >> "$log_file"
    echo "Duration: $((end_time - start_time)) seconds" >> "$log_file"
    echo "Status: $status" >> "$log_file"
    echo "--- STDOUT ---" >> "$log_file"
    echo "$stdout_content" >> "$log_file"
    echo "--- STDERR ---" >> "$log_file"
    echo "$stderr_content" >> "$log_file"
    echo "--- Log End ---" >> "$log_file"
    echo "" >> "$log_file"
}
