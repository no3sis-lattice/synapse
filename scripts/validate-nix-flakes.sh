#!/usr/bin/env bash
#
# Nix Flakes Validation Script for Mojo Components
# Validates all 17 tests from MOJO_MIGRATION.md Implementation Checklist
#
# Usage: ./scripts/validate-nix-flakes.sh
#
# Refactored to comply with the Numogrammatic Codex:
# - TDD: Structured for testability with pure functions
# - KISS: Removed duplication, simplified control flow
# - SOLID: Single responsibility, abstraction, minimal interfaces
# - DRY: Extracted repeated patterns into reusable functions

set -euo pipefail

# =============================================================================
# CONSTANTS (Axiom: Remove magic numbers)
# =============================================================================
readonly MIN_LIBRARY_SIZE=1000
readonly MAX_LIBRARY_SIZE=1000000
readonly EXPECTED_FFI_EXPORTS=3
readonly EXPECTED_FFI_DEFINED=4
readonly EXPECTED_MOJO_LIBRARIES=3

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Results file
readonly RESULTS_FILE="nix/validation-results.txt"

# =============================================================================
# STATE ENCAPSULATION (Principle: Isolate global state)
# =============================================================================
declare -A TEST_STATE=(
    [total]=0
    [passed]=0
    [failed]=0
)

# =============================================================================
# ERROR HANDLING (Gate 1: Proper trap-based error handling)
# =============================================================================
error_handler() {
    local exit_code=$1
    local line_number=$2
    echo -e "${RED}ERROR: Command failed at line ${line_number} with exit code ${exit_code}${NC}" >&2
    # Don't exit - we want all tests to run even if some fail
    return 0
}

trap 'error_handler $? $LINENO' ERR

# =============================================================================
# PLATFORM ABSTRACTION (SOLID: Dependency Inversion)
# =============================================================================

# Abstract platform-specific file size retrieval
# Args: $1 - file path
# Returns: file size in bytes, or empty string on error
get_file_size() {
    local file_path="$1"

    if [[ ! -f "$file_path" ]]; then
        return 1
    fi

    case "$OSTYPE" in
        darwin*)
            stat -f%z "$file_path" 2>/dev/null || echo ""
            ;;
        *)
            stat -c%s "$file_path" 2>/dev/null || echo ""
            ;;
    esac
}

# =============================================================================
# NIX COMMAND ABSTRACTION (SOLID: Interface Segregation)
# =============================================================================

# Wrapper for nix commands with consistent --impure flag
# Args: $1 - subcommand, $@ - remaining arguments
# Returns: exit code of nix command
run_nix_command() {
    local subcommand="$1"
    shift
    nix "$subcommand" --impure "$@"
}

# =============================================================================
# DIRECTORY NAVIGATION (DRY: Eliminate repeated pushd/popd)
# =============================================================================

# Safe directory navigation with error handling
# Args: $1 - target directory, $2 - error message
# Returns: 0 on success, 1 on failure
pushd_safe() {
    local target_dir="$1"
    local error_msg="${2:-Cannot navigate to directory}"

    if ! pushd "$target_dir" > /dev/null 2>&1; then
        fail "$error_msg" "Directory: $target_dir"
        return 1
    fi
    return 0
}

# Safe return from directory
popd_safe() {
    popd > /dev/null 2>&1 || true
}

# =============================================================================
# OUTPUT & LOGGING (Single Responsibility)
# =============================================================================

# Initialize results file
init_results_file() {
    mkdir -p "$(dirname "$RESULTS_FILE")"
    {
        echo "Nix Flakes Validation Results - $(date)"
        echo "========================================="
        echo ""
    } > "$RESULTS_FILE"
}

# Print test phase header
# Args: $1 - header text
test_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
    {
        echo "$1"
        echo "-----------------------------------------------------------"
    } >> "$RESULTS_FILE"
}

# Register a new test case
# Args: $1 - test description
test_case() {
    TEST_STATE[total]=$((TEST_STATE[total] + 1))
    echo -e "${YELLOW}[TEST ${TEST_STATE[total]}]${NC} $1"
    echo "[TEST ${TEST_STATE[total]}] $1" >> "$RESULTS_FILE"
}

# Record test pass
# Args: $1 - success message
pass() {
    TEST_STATE[passed]=$((TEST_STATE[passed] + 1))
    echo -e "${GREEN}✓ PASS${NC}: $1"
    {
        echo "✓ PASS: $1"
        echo ""
    } >> "$RESULTS_FILE"
}

# Record test failure
# Args: $1 - failure message, $2 - error details
fail() {
    TEST_STATE[failed]=$((TEST_STATE[failed] + 1))
    echo -e "${RED}✗ FAIL${NC}: $1"
    {
        echo "✗ FAIL: $1"
        echo "Error: $2"
        echo ""
    } >> "$RESULTS_FILE"
}

# Print info message
# Args: $1 - info message
info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# =============================================================================
# FFI VERIFICATION (DRY: Extract repeated pattern)
# =============================================================================

# Verify FFI exports in a shared library
# Args: $1 - library path, $@ - expected export names
# Returns: 0 if all exports found, 1 otherwise
verify_ffi_exports() {
    local library_path="$1"
    shift
    local expected_exports=("$@")
    local exports_found=0

    if [[ ! -f "$library_path" ]]; then
        return 1
    fi

    for export_name in "${expected_exports[@]}"; do
        if nm -D "$library_path" 2>&1 | grep -q "$export_name"; then
            ((exports_found++))
        fi
    done

    if [[ $exports_found -eq ${#expected_exports[@]} ]]; then
        return 0
    else
        return 1
    fi
}

# Verify FFI exports are defined (not undefined symbols)
# Args: $1 - library path, $@ - expected export names
# Returns: count of defined exports
count_defined_ffi_exports() {
    local library_path="$1"
    shift
    local expected_exports=("$@")
    local defined_count=0

    if [[ ! -f "$library_path" ]]; then
        echo "0"
        return
    fi

    for export_name in "${expected_exports[@]}"; do
        # grep -v " U " excludes undefined symbols
        if nm -D "$library_path" 2>&1 | grep -v " U " | grep -q "$export_name"; then
            ((defined_count++))
        fi
    done

    echo "$defined_count"
}

# =============================================================================
# NIX BUILD VALIDATION (DRY: Extract build-test-verify pattern)
# =============================================================================

# Build a nix flake and validate result
# Args: $1 - flake reference (e.g., ".#mojo-runtime" or "path:./nix/flakes/...")
#       $2 - test description
# Returns: 0 on success, 1 on failure
validate_flake_build() {
    local flake_ref="$1"
    local description="$2"

    test_case "$description"

    # Disable exit on error temporarily for test evaluation
    set +e
    run_nix_command build "$flake_ref" --print-build-logs 2>&1 | tee -a "$RESULTS_FILE"
    local build_result=$?
    set -e

    if [[ $build_result -eq 0 ]]; then
        pass "$description succeeded"
        return 0
    else
        fail "$description failed" "See build logs above"
        return 1
    fi
}

# Validate a library flake with FFI exports
# Args: $1 - relative path to flake directory
#       $2 - flake name
#       $3 - library filename (e.g., libpattern_search.so)
#       $@ - expected FFI export names
# Returns: 0 on success, 1 on failure
validate_library_flake() {
    local flake_dir="$1"
    local flake_name="$2"
    local library_filename="$3"
    shift 3
    local ffi_exports=("$@")

    # Test: Build the flake
    test_case "nix build path:./$flake_dir"

    if ! pushd_safe "$flake_dir" "Cannot navigate to $flake_dir"; then
        # Skip FFI verification test
        TEST_STATE[total]=$((TEST_STATE[total] + 1))
        fail "Skipping FFI verification for $flake_name" "Directory not found"
        return 1
    fi

    # Disable exit on error temporarily for test evaluation
    set +e
    run_nix_command build --print-build-logs 2>&1 | tee -a "../../../$RESULTS_FILE"
    local build_result=$?
    set -e

    if [[ $build_result -ne 0 ]]; then
        fail "$flake_name build failed" "See build logs above"
        popd_safe

        # Skip FFI verification test
        TEST_STATE[total]=$((TEST_STATE[total] + 1))
        fail "Skipping FFI verification for $flake_name" "Build failed"
        return 1
    fi

    pass "$flake_name builds successfully"

    # Test: Verify FFI exports
    test_case "Verify $flake_name FFI exports"

    local library_path="result/lib/$library_filename"

    if verify_ffi_exports "$library_path" "${ffi_exports[@]}"; then
        pass "All ${#ffi_exports[@]} FFI exports found in $flake_name"
    else
        fail "FFI exports verification failed for $flake_name" "Expected exports: ${ffi_exports[*]}"
    fi

    popd_safe
    return 0
}

# =============================================================================
# DEV SHELL VALIDATION (DRY: Extract repeated dev shell tests)
# =============================================================================

# Test a development shell with a command
# Args: $1 - shell reference (e.g., "" for default, ".#mojo-dev" for named)
#       $2 - command to run in shell
#       $3 - test description
# Returns: 0 on success, 1 on failure
validate_dev_shell() {
    local shell_ref="$1"
    local test_command="$2"
    local description="$3"

    test_case "$description"

    # Disable exit on error temporarily for test evaluation
    set +e
    run_nix_command develop "$shell_ref" --command bash -c "$test_command 2>&1" | tee -a "$RESULTS_FILE"
    local shell_result=$?
    set -e

    if [[ $shell_result -eq 0 ]]; then
        pass "$description succeeded"
        return 0
    else
        fail "$description failed" "See error above"
        return 1
    fi
}

# =============================================================================
# PREREQUISITE VALIDATION (Best Practice: Fail fast)
# =============================================================================

# Verify required tools are available
# Returns: 0 if all tools present, exits script otherwise
validate_prerequisites() {
    local missing_tools=()

    if ! command -v nix &> /dev/null; then
        missing_tools+=("nix")
    fi

    if ! command -v jq &> /dev/null; then
        missing_tools+=("jq")
    fi

    if ! command -v nm &> /dev/null; then
        missing_tools+=("nm")
    fi

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        echo -e "${RED}ERROR: Missing required tools: ${missing_tools[*]}${NC}" >&2
        echo "Install missing tools before running this script." >&2
        exit 1
    fi

    return 0
}

# =============================================================================
# MAIN TEST SUITE (Open/Closed: Easy to extend with new test phases)
# =============================================================================

# Phase 1: Mojo Runtime Foundation
run_phase1_tests() {
    test_header "PHASE 1: Mojo Runtime Foundation"

    # Test 1: Build mojo-runtime
    validate_flake_build ".#mojo-runtime" "nix build .#mojo-runtime"

    # Test 2: Dev shell for mojo-runtime
    validate_dev_shell ".#mojo-runtime" "mojo --version" \
        "nix develop .#mojo-runtime --command mojo --version"

    # Test 3: Verify mojo executable exists in result
    test_case "Verify mojo executable in build output"
    if [[ -f "result/bin/mojo" ]] && [[ -x "result/bin/mojo" ]]; then
        pass "mojo executable found and is executable"
    else
        fail "mojo executable not found or not executable" "Expected result/bin/mojo"
    fi
}

# Phase 2: Library Flakes
run_phase2_tests() {
    test_header "PHASE 2: Library Flakes"

    # Test 4-5: Build mojo-pattern-search + verify FFI
    validate_library_flake \
        "nix/flakes/mojo-pattern-search" \
        "mojo-pattern-search" \
        "libpattern_search.so" \
        "pattern_search_ffi"

    # Test 6-7: Build mojo-message-router + verify FFI
    validate_library_flake \
        "nix/flakes/mojo-message-router" \
        "mojo-message-router" \
        "libmessage_router.so" \
        "create_router" "destroy_router" "route_message_ffi"
}

# Phase 3: Root Integration
run_phase3_tests() {
    test_header "PHASE 3: Root Integration"

    # Test 8: Build unified mojo-libraries package
    validate_flake_build ".#mojo-libraries" "nix build .#mojo-libraries"

    # Test 9: Test default devShell
    validate_dev_shell "" "mojo --version" \
        "nix develop --command bash -c 'mojo --version'"

    # Test 10: Test dedicated mojo-dev shell
    validate_dev_shell ".#mojo-dev" "mojo --version" \
        "nix develop .#mojo-dev --command bash -c 'mojo --version'"

    # Test 11: Verify MOJO_LIB_PATH is set
    test_case "Verify MOJO_LIB_PATH environment variable"
    set +e
    run_nix_command develop --command bash -c "echo \$MOJO_LIB_PATH" | grep -q "libpattern_search"
    local env_result=$?
    set -e

    if [[ $env_result -eq 0 ]]; then
        pass "MOJO_LIB_PATH is set and contains library paths"
    else
        fail "MOJO_LIB_PATH not set correctly" "Should contain paths to mojo libraries"
    fi

    # Test 12: nix flake check
    test_case "nix flake check"
    set +e
    run_nix_command flake check --print-build-logs 2>&1 | tee -a "$RESULTS_FILE"
    local check_result=$?
    set -e

    if [[ $check_result -eq 0 ]]; then
        pass "All flakes are valid (nix flake check passed)"
    else
        fail "nix flake check failed" "See errors above"
    fi
}

# Phase 4: Complete Validation
run_phase4_tests() {
    test_header "PHASE 4: Complete Validation"

    # Test 13: Verify library file sizes are reasonable
    test_case "Verify library file sizes"
    local library_path="result/lib/libpattern_search.so"

    if [[ -f "$library_path" ]]; then
        local size
        size=$(get_file_size "$library_path")

        if [[ -n "$size" ]] && [[ $size -gt $MIN_LIBRARY_SIZE ]] && [[ $size -lt $MAX_LIBRARY_SIZE ]]; then
            pass "libpattern_search.so size is reasonable ($size bytes)"
        else
            fail "libpattern_search.so size is unusual or could not be determined" \
                "Size: ${size:-unknown} bytes (expected: $MIN_LIBRARY_SIZE-$MAX_LIBRARY_SIZE)"
        fi
    else
        fail "libpattern_search.so not found in result" "Check build output"
    fi

    # Test 14: Verify FFI exports are properly defined (not undefined)
    test_case "Verify FFI exports are defined symbols"

    local pattern_defined
    pattern_defined=$(count_defined_ffi_exports "result/lib/libpattern_search.so" "pattern_search_ffi")

    local router_defined
    router_defined=$(count_defined_ffi_exports "result/lib/libmessage_router.so" \
        "create_router" "destroy_router" "route_message_ffi")

    local total_defined=$((pattern_defined + router_defined))

    if [[ $total_defined -eq $EXPECTED_FFI_DEFINED ]]; then
        pass "All FFI exports are properly defined ($total_defined/$EXPECTED_FFI_DEFINED)"
    else
        fail "Some FFI exports may be undefined" \
            "Found $total_defined/$EXPECTED_FFI_DEFINED defined FFI symbols"
    fi

    # Test 15: Verify build reproducibility
    test_case "Verify build reproducibility"
    info "Testing deterministic builds..."

    # Build and capture store path
    set +e
    local path1
    path1=$(run_nix_command build .#mojo-runtime --print-out-paths 2>/dev/null | tail -1)

    # Remove result symlink but keep store path
    rm -f result

    # Build again and capture store path
    local path2
    path2=$(run_nix_command build .#mojo-runtime --print-out-paths 2>/dev/null | tail -1)
    set -e

    if [[ -n "$path1" ]] && [[ "$path1" == "$path2" ]]; then
        pass "Builds are reproducible (identical store paths: $path1)"
    elif [[ -z "$path1" ]] || [[ -z "$path2" ]]; then
        fail "Build reproducibility test inconclusive" "Could not capture store paths"
    else
        fail "Builds are not reproducible" "Path1: $path1, Path2: $path2"
    fi

    # Test 16: Verify README files exist
    test_case "Verify documentation exists"
    local docs_found=0
    local expected_dirs=(
        "nix/flakes/mojo-runtime"
        "nix/flakes/mojo-pattern-search"
        "nix/flakes/mojo-message-router"
    )

    for dir in "${expected_dirs[@]}"; do
        if [[ -f "$dir/README.md" ]]; then
            ((docs_found++))
        fi
    done

    if [[ $docs_found -eq $EXPECTED_MOJO_LIBRARIES ]]; then
        pass "All $EXPECTED_MOJO_LIBRARIES flakes have README.md documentation"
    else
        fail "Only $docs_found/$EXPECTED_MOJO_LIBRARIES flakes have README.md" "Documentation incomplete"
    fi

    # Test 17: Verify flake metadata is correct
    test_case "Verify flake metadata"
    set +e
    run_nix_command flake metadata --json | jq -r '.description' | grep -q "Synapse"
    local metadata_result=$?
    set -e

    if [[ $metadata_result -eq 0 ]]; then
        pass "Flake metadata is correct"
    else
        fail "Flake metadata missing or incorrect" "Check flake.nix description"
    fi
}

# Print final summary
print_summary() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}VALIDATION SUMMARY${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"

    {
        echo "Total Tests: ${TEST_STATE[total]}"
        echo "Passed: ${TEST_STATE[passed]}"
        echo "Failed: ${TEST_STATE[failed]}"
        echo ""
    } | tee -a "$RESULTS_FILE"

    if [[ ${TEST_STATE[failed]} -eq 0 ]]; then
        echo -e "${GREEN}✓ All tests passed! Nix flakes are production-ready.${NC}" | tee -a "$RESULTS_FILE"
        echo "" | tee -a "$RESULTS_FILE"
        echo "Results saved to: $RESULTS_FILE"
        return 0
    else
        echo -e "${RED}✗ ${TEST_STATE[failed]} test(s) failed. Review results above.${NC}" | tee -a "$RESULTS_FILE"
        echo "" | tee -a "$RESULTS_FILE"
        echo "Results saved to: $RESULTS_FILE"
        return 1
    fi
}

# =============================================================================
# ENTRY POINT
# =============================================================================

main() {
    # Prerequisites
    validate_prerequisites

    # Initialize
    init_results_file

    info "Nix version: $(nix --version)"
    echo "Nix version: $(nix --version)" >> "$RESULTS_FILE"
    echo "" >> "$RESULTS_FILE"

    # Run test phases
    run_phase1_tests
    run_phase2_tests
    run_phase3_tests
    run_phase4_tests

    # Summary
    print_summary

    # Exit with appropriate code
    if [[ ${TEST_STATE[failed]} -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

# Execute main function
main "$@"
