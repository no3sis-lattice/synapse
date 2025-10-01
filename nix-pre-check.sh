#!/usr/bin/env bash
# Pre-installation Check for Nix Build Testing
# Verifies all prerequisites are in place before installing Nix

echo "========================================="
echo "Synapse Nix Pre-Installation Check"
echo "========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

CHECKS_PASSED=0
CHECKS_FAILED=0

# Check function
check() {
    local name="$1"
    local test_cmd="$2"
    local required="$3"  # "required" or "optional"

    echo -n "Checking: $name ... "

    if eval "$test_cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        ((CHECKS_PASSED++))
        return 0
    else
        if [ "$required" = "required" ]; then
            echo -e "${RED}✗ REQUIRED${NC}"
            ((CHECKS_FAILED++))
        else
            echo -e "${YELLOW}✗ optional${NC}"
        fi
        return 1
    fi
}

# Required checks
echo "Required Components:"
check "Mojo binary exists" "test -f .venv/bin/mojo" "required"
check "Mojo is executable" "test -x .venv/bin/mojo" "required"
check "Pattern search source exists" "test -f .synapse/neo4j/pattern_search_mojo.mojo" "required"
check "Message router source exists" "test -f .synapse/corpus_callosum/message_router.mojo" "required"
check "mojo-runtime flake.nix exists" "test -f nix/flakes/mojo-runtime/flake.nix" "required"
check "mojo-pattern-search flake.nix exists" "test -f nix/flakes/mojo-pattern-search/flake.nix" "required"
check "mojo-message-router flake.nix exists" "test -f nix/flakes/mojo-message-router/flake.nix" "required"
check "Root flake.nix exists" "test -f flake.nix" "required"

echo ""
echo "Optional Components:"
check "Git available" "command -v git" "optional"
check "Python available" "command -v python" "optional"
check "Make available" "command -v make" "optional"

echo ""
echo "File Size Verification:"
if [ -f .venv/bin/mojo ]; then
    mojo_size=$(stat -f%z .venv/bin/mojo 2>/dev/null || stat -c%s .venv/bin/mojo 2>/dev/null)
    echo "  Mojo binary: $mojo_size bytes"
fi

if [ -f .synapse/neo4j/pattern_search_mojo.mojo ]; then
    ps_size=$(stat -f%z .synapse/neo4j/pattern_search_mojo.mojo 2>/dev/null || stat -c%s .synapse/neo4j/pattern_search_mojo.mojo 2>/dev/null)
    echo "  Pattern search: $ps_size bytes ($(echo "scale=1; $ps_size/1024" | bc)KB)"
fi

if [ -f .synapse/corpus_callosum/message_router.mojo ]; then
    mr_size=$(stat -f%z .synapse/corpus_callosum/message_router.mojo 2>/dev/null || stat -c%s .synapse/corpus_callosum/message_router.mojo 2>/dev/null)
    echo "  Message router: $mr_size bytes ($(echo "scale=1; $mr_size/1024" | bc)KB)"
fi

echo ""
echo "Nix Installation Status:"
if command -v nix &> /dev/null; then
    echo -e "${GREEN}✓ Nix is already installed${NC}"
    nix --version

    if nix flake --help &> /dev/null 2>&1; then
        echo -e "${GREEN}✓ Flakes are enabled${NC}"
    else
        echo -e "${YELLOW}! Flakes may not be enabled${NC}"
        echo "  Enable with: echo 'experimental-features = nix-command flakes' >> ~/.config/nix/nix.conf"
    fi
else
    echo -e "${YELLOW}! Nix is not installed${NC}"
    echo "  Install with: curl -L https://nixos.org/nix/install | sh -s -- --daemon"
    echo "  See: NIX_INSTALL.md for detailed instructions"
fi

echo ""
echo "========================================="
echo "Summary"
echo "========================================="
echo ""
echo -e "Checks passed: ${GREEN}$CHECKS_PASSED${NC}"
echo -e "Checks failed: ${RED}$CHECKS_FAILED${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All required components are ready${NC}"
    echo ""

    if ! command -v nix &> /dev/null; then
        echo "Next steps:"
        echo "  1. Install Nix: See NIX_INSTALL.md"
        echo "  2. Run tests: ./nix-build-test.sh"
    else
        echo "Ready to test!"
        echo "  Run: ./nix-build-test.sh"
    fi
else
    echo -e "${RED}✗ Some required components are missing${NC}"
    echo ""
    echo "Fix issues and run this check again"
fi

echo ""
