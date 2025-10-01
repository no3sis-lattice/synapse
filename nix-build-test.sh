#!/usr/bin/env bash
# Nix Build Test Suite for Synapse Mojo Components
# Run this after installing Nix with flakes enabled

set -e  # Exit on error

echo "========================================="
echo "Synapse Mojo Nix Build Test Suite"
echo "========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to run test
run_test() {
    local test_name="$1"
    local test_cmd="$2"

    echo -n "Testing: $test_name ... "

    if eval "$test_cmd" > /tmp/nix-test-output.log 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Error output:"
        cat /tmp/nix-test-output.log | head -20 | sed 's/^/    /'
        ((FAILED++))
        return 1
    fi
}

# Check Nix is installed
echo "Checking prerequisites..."
if ! command -v nix &> /dev/null; then
    echo -e "${RED}ERROR: Nix is not installed${NC}"
    echo ""
    echo "Install Nix with:"
    echo "  curl -L https://nixos.org/nix/install | sh -s -- --daemon"
    echo ""
    echo "Then enable flakes:"
    echo "  mkdir -p ~/.config/nix"
    echo "  echo 'experimental-features = nix-command flakes' >> ~/.config/nix/nix.conf"
    exit 1
fi

echo -e "${GREEN}✓ Nix is installed${NC}"

# Check flakes are enabled
if ! nix flake --help &> /dev/null; then
    echo -e "${YELLOW}WARNING: Nix flakes may not be enabled${NC}"
    echo "Enable with: echo 'experimental-features = nix-command flakes' >> ~/.config/nix/nix.conf"
fi

echo ""
echo "========================================="
echo "Phase 1: Individual Flake Validation"
echo "========================================="
echo ""

# Test 1: Mojo Runtime Flake Check
run_test "mojo-runtime flake check" \
    "nix flake check ./nix/flakes/mojo-runtime --no-write-lock-file"

# Test 2: Mojo Runtime Build
run_test "mojo-runtime build" \
    "nix build ./nix/flakes/mojo-runtime#default --no-link --no-write-lock-file"

# Test 3: Pattern Search Flake Check
run_test "mojo-pattern-search flake check" \
    "nix flake check ./nix/flakes/mojo-pattern-search --no-write-lock-file"

# Test 4: Pattern Search Build
run_test "mojo-pattern-search build" \
    "nix build ./nix/flakes/mojo-pattern-search#default --no-link --no-write-lock-file"

# Test 5: Message Router Flake Check
run_test "mojo-message-router flake check" \
    "nix flake check ./nix/flakes/mojo-message-router --no-write-lock-file"

# Test 6: Message Router Build
run_test "mojo-message-router build" \
    "nix build ./nix/flakes/mojo-message-router#default --no-link --no-write-lock-file"

echo ""
echo "========================================="
echo "Phase 2: Root Flake Integration"
echo "========================================="
echo ""

# Test 7: Root Flake Check
run_test "root flake check" \
    "nix flake check --no-write-lock-file"

# Test 8: Root Flake Show
run_test "root flake show" \
    "nix flake show --no-write-lock-file"

# Test 9: Build mojo-runtime from root
run_test "build .#mojo-runtime" \
    "nix build .#mojo-runtime --no-link --no-write-lock-file"

# Test 10: Build libpattern_search
run_test "build .#libpattern_search" \
    "nix build .#libpattern_search --no-link --no-write-lock-file"

# Test 11: Build libmessage_router
run_test "build .#libmessage_router" \
    "nix build .#libmessage_router --no-link --no-write-lock-file"

# Test 12: Build mojo-libraries (all)
run_test "build .#mojo-libraries" \
    "nix build .#mojo-libraries --no-link --no-write-lock-file"

echo ""
echo "========================================="
echo "Phase 3: FFI Export Verification"
echo "========================================="
echo ""

# Test 13: Verify pattern search FFI exports
if nix build .#libpattern_search --no-write-lock-file 2>/dev/null; then
    echo -n "Testing: pattern_search_ffi export ... "
    if nm -D result/lib/libpattern_search.so | grep -q "pattern_search_ffi"; then
        echo -e "${GREEN}PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Expected export 'pattern_search_ffi' not found"
        ((FAILED++))
    fi
    rm -f result
fi

# Test 14: Verify message router FFI exports
if nix build .#libmessage_router --no-write-lock-file 2>/dev/null; then
    echo -n "Testing: message router FFI exports ... "
    exports=$(nm -D result/lib/libmessage_router.so 2>/dev/null)
    missing=""

    for export in "create_router" "destroy_router" "route_message_ffi"; do
        if ! echo "$exports" | grep -q "$export"; then
            missing="$missing $export"
        fi
    done

    if [ -z "$missing" ]; then
        echo -e "${GREEN}PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Missing exports:$missing"
        ((FAILED++))
    fi
    rm -f result
fi

echo ""
echo "========================================="
echo "Phase 4: Development Shell Testing"
echo "========================================="
echo ""

# Test 15: Default devShell
run_test "default devShell" \
    "nix develop --command echo 'Shell works'"

# Test 16: Mojo devShell
run_test "mojo-dev devShell" \
    "nix develop .#mojo-dev --command echo 'Mojo shell works'"

# Test 17: Mojo version in devShell
echo -n "Testing: mojo --version in devShell ... "
if nix develop --command mojo --version &> /tmp/mojo-version.log; then
    version=$(cat /tmp/mojo-version.log | head -1)
    echo -e "${GREEN}PASS${NC}"
    echo "  Mojo version: $version"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    cat /tmp/mojo-version.log | sed 's/^/    /'
    ((FAILED++))
fi

echo ""
echo "========================================="
echo "Test Results Summary"
echo "========================================="
echo ""
echo "Total tests run: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review flake outputs: nix flake show"
    echo "  2. Enter dev shell: nix develop"
    echo "  3. Build all Mojo libs: nix build .#mojo-libraries"
    echo "  4. Test Python integration with ctypes"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Debug steps:"
    echo "  1. Check individual flake: nix flake check ./nix/flakes/mojo-runtime"
    echo "  2. Build with verbose: nix build .#mojo-runtime --print-build-logs"
    echo "  3. Check Mojo installation: ls -la .venv/bin/mojo"
    exit 1
fi
