#!/bin/bash
# Synapse System Installer
# ========================
# This script automates the global installation of the Synapse CLI.

set -e
set -o pipefail

# --- Configuration and Colors ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Logging Functions ---
log() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# --- Prerequisite Checks ---
check_prerequisites() {
    log "Checking for prerequisites..."

    # Check for git
    if ! command -v git &> /dev/null; then
        error "git is not installed. Install with: sudo apt install git (Ubuntu/Debian) or brew install git (macOS)"
    fi
    success "git is installed."

    # Check for Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Get it from: https://docs.docker.com/get-docker/"
    fi

    # Check Docker daemon and try to start if needed
    if ! docker info &> /dev/null; then
        warning "Docker daemon is not running. Attempting to start..."
        if command -v systemctl &> /dev/null; then
            sudo systemctl start docker 2>/dev/null || true
        fi
        sleep 2
        if ! docker info &> /dev/null; then
            error "Docker daemon failed to start. Please start Docker manually and re-run this script."
        fi
    fi
    success "Docker is running."

    # Check for Nix (optional enhancement)
    if command -v nix &> /dev/null; then
        log "Nix detected! For a reproducible development environment, consider using:"
        echo "  cd ~/.synapse-system && nix develop"
        echo "  This provides all tools with guaranteed version consistency."
        echo ""
    fi

    # Check for docker-compose
    if ! command -v docker-compose &> /dev/null; then
        warning "docker-compose not found. Checking if docker compose (v2) is available..."
        if ! docker compose version &> /dev/null; then
            error "Neither docker-compose nor 'docker compose' is available. Please install Docker Compose."
        fi
        # Create alias for compatibility
        alias docker-compose='docker compose'
        success "Using 'docker compose' (v2)."
    else
        success "docker-compose is installed."
    fi

    # Check for Python 3.12+
    if ! command -v python3 &> /dev/null; then
        error "python3 not found. Install with: sudo apt install python3.12 (Ubuntu) or brew install python@3.12 (macOS)"
    fi

    MIN_PYTHON_MAJOR=3
    MIN_PYTHON_MINOR=12
    PYTHON_VERSION=$(python3 --version 2>/dev/null | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

    if (( PYTHON_MAJOR < MIN_PYTHON_MAJOR || (PYTHON_MAJOR == MIN_PYTHON_MAJOR && PYTHON_MINOR < MIN_PYTHON_MINOR) )); then
        error "Python $PYTHON_VERSION found. Need 3.12+. Install with: sudo apt install python3.12 or brew install python@3.12"
    fi
    success "Python $PYTHON_VERSION is installed."

    # Check available disk space (need ~3GB for BGE-M3 model)
    available_space=$(df -BG "$HOME" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$available_space" -lt 4 ]; then
        warning "Low disk space: ${available_space}GB available. BGE-M3 model needs ~3GB."
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error "Installation cancelled. Please free up disk space and try again."
        fi
    fi

    log "All prerequisites are met."
}

# --- Dependency Installation ---
install_dependencies() {
    log "Installing Python dependencies..."

    # Check for uv
    if ! command -v uv &> /dev/null; then
        warning "'uv' package manager not found."
        read -p "May I install it system-wide using 'curl -LsSf https://astral.sh/uv/install.sh | sh'? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            curl -LsSf https://astral.sh/uv/install.sh | sh
            # Re-source shell profile to make uv available
            source "$HOME/.cargo/env"
            success "'uv' has been installed."
        else
            error "Cannot proceed without 'uv'. Please install it manually and run this script again."
        fi
    fi

    log "Found 'uv'. Installing packages..."
    uv pip install -r "$SCRIPT_DIR/requirements.txt"
    uv pip install -r "$SCRIPT_DIR/.synapse/neo4j/requirements.txt"

    success "All Python dependencies are installed."
}

# --- CLI Setup ---
setup_cli() {
    log "Configuring 'synapse' CLI..."
    local cli_source_path="$SCRIPT_DIR/bin/synapse"
    local cli_target_dir="/usr/local/bin"
    local cli_target_path="$cli_target_dir/synapse"

    # Try global install first
    if [[ -d "$cli_target_dir" && -w "$cli_target_dir" ]]; then
        ln -sf "$cli_source_path" "$cli_target_path"
        success "CLI symlink created in $cli_target_path."
        return 0
    fi

    # Ask for sudo if needed
    if [[ -d "$cli_target_dir" ]]; then
        warning "Admin privileges needed for global installation."
        read -p "Use sudo to install globally? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if sudo ln -sf "$cli_source_path" "$cli_target_path"; then
                success "CLI installed globally with sudo."
                return 0
            fi
        fi
    fi

    # Fallback: Add to user's shell profile
    log "Setting up user-local installation..."
    local shell_profile=""

    if [[ -n "$ZSH_VERSION" ]] || [[ "$SHELL" == *"zsh"* ]]; then
        shell_profile="$HOME/.zshrc"
    elif [[ -n "$BASH_VERSION" ]] || [[ "$SHELL" == *"bash"* ]]; then
        shell_profile="$HOME/.bashrc"
    elif [[ "$SHELL" == *"fish"* ]]; then
        shell_profile="$HOME/.config/fish/config.fish"
    else
        shell_profile="$HOME/.profile"
    fi

    # Add to PATH if not already there
    local export_line="export PATH=\"$SCRIPT_DIR/bin:\$PATH\""
    if [[ "$SHELL" == *"fish"* ]]; then
        export_line="set -gx PATH $SCRIPT_DIR/bin \$PATH"
    fi

    if ! grep -q "$SCRIPT_DIR/bin" "$shell_profile" 2>/dev/null; then
        echo "" >> "$shell_profile"
        echo "# Synapse CLI" >> "$shell_profile"
        echo "$export_line" >> "$shell_profile"
        success "Added synapse to PATH in $shell_profile"
        log "Restart your terminal or run: source $shell_profile"
    else
        success "synapse already in PATH via $shell_profile"
    fi

    # Create convenience alias as backup
    echo "alias synapse='$cli_source_path'" >> "$shell_profile"
    log "Created synapse alias as backup"
}

# --- Post-Install Setup ---
post_install_setup() {
    log "Starting Synapse services..."

    # Start services
    cd "$SCRIPT_DIR/.synapse/neo4j"
    if docker-compose up -d; then
        success "Docker services started successfully"

        # Wait for services to be ready
        log "Waiting for services to initialize..."
        sleep 5

        # Test connectivity
        local max_attempts=12
        local attempt=1
        while [ $attempt -le $max_attempts ]; do
            if curl -f http://localhost:7474 >/dev/null 2>&1; then
                success "Neo4j is ready"
                break
            fi
            log "Waiting for Neo4j... (attempt $attempt/$max_attempts)"
            sleep 5
            ((attempt++))
        done

        if [ $attempt -gt $max_attempts ]; then
            warning "Neo4j may take longer to start. Check with: synapse status"
        fi
    else
        warning "Failed to start services. You can start them manually with: synapse start"
    fi

    cd "$SCRIPT_DIR"
}

# --- Verification ---
verify_installation() {
    log "Verifying installation..."

    # Test CLI availability
    if command -v synapse >/dev/null 2>&1 || [ -x "$SCRIPT_DIR/bin/synapse" ]; then
        success "Synapse CLI is accessible"
    else
        warning "Synapse CLI not in PATH. Use full path: $SCRIPT_DIR/bin/synapse"
    fi

    # Test basic functionality
    log "Running health check..."
    if "$SCRIPT_DIR/bin/synapse" status >/dev/null 2>&1; then
        success "Basic functionality verified"
    else
        log "Note: Some services may still be starting up"
    fi
}

# --- Main Function ---
main() {
    echo -e "${BLUE}===========================${NC}"
    echo -e "${BLUE}  Synapse System Installer ${NC}"
    echo -e "${BLUE}===========================${NC}"
    echo

    check_prerequisites
    echo
    install_dependencies
    echo
    setup_cli
    echo
    post_install_setup
    echo
    verify_installation
    echo

    success "Synapse installation complete!"
    echo
    log "Quick start:"
    echo -e "  ${YELLOW}synapse status${NC}     # Check system health"
    echo -e "  ${YELLOW}synapse init .${NC}     # Initialize a project"
    echo -e "  ${YELLOW}synapse search \"test\"${NC}  # Test search functionality"
    echo
    log "If synapse command not found, restart terminal or run:"
    echo -e "  ${YELLOW}source ~/.bashrc${NC}   # (or ~/.zshrc for zsh)"
    echo
}

main
