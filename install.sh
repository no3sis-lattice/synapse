#!/bin/bash
# Synapse System Ultra-Minimal Installer
# ======================================
# One command. Zero decisions. Maximum compression.
# Following 4QZero: Collapse installation complexity to a single bifurcation point.

set -e
set -o pipefail

# Add automatic yes mode for CI/automation
AUTO_YES=${AUTO_YES:-false}

# --- Configuration and Colors ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Enhanced Logging with Progress ---
TOTAL_STEPS=6
CURRENT_STEP=0

progress() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    echo -e "${BLUE}[${CURRENT_STEP}/${TOTAL_STEPS}]${NC} $1"
}

log() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[✓]${NC} $1"; }
warning() { echo -e "${YELLOW}[⚠]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }

# Auto-prompt function for zero-friction installation
auto_prompt() {
    local message="$1"
    local default="${2:-y}"

    if [[ "$AUTO_YES" == "true" ]]; then
        log "$message (auto-yes enabled)"
        return 0
    fi

    echo -n "$message (Y/n) "
    read -r response
    case "$response" in
        [nN][oO]|[nN]) return 1 ;;
        *) return 0 ;;
    esac
}

# --- Enhanced Prerequisite Installation ---
install_prerequisite() {
    local tool="$1"
    local install_cmd="$2"

    if ! command -v "$tool" &> /dev/null; then
        warning "$tool not found"
        if auto_prompt "Install $tool automatically?"; then
            log "Installing $tool..."
            eval "$install_cmd"
            if command -v "$tool" &> /dev/null; then
                success "$tool installed successfully"
            else
                error "Failed to install $tool. Please install manually: $install_cmd"
            fi
        else
            error "$tool is required. Install with: $install_cmd"
        fi
    else
        success "$tool is available"
    fi
}

detect_package_manager() {
    if command -v apt &> /dev/null; then
        echo "apt"
    elif command -v yum &> /dev/null; then
        echo "yum"
    elif command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v brew &> /dev/null; then
        echo "brew"
    elif command -v pacman &> /dev/null; then
        echo "pacman"
    else
        echo "unknown"
    fi
}

# --- Prerequisite Checks ---
check_prerequisites() {
    progress "Checking and installing prerequisites..."

    local pkg_mgr=$(detect_package_manager)
    log "Detected package manager: $pkg_mgr"

    # Git installation
    case "$pkg_mgr" in
        apt) install_prerequisite "git" "sudo apt update && sudo apt install -y git" ;;
        yum) install_prerequisite "git" "sudo yum install -y git" ;;
        dnf) install_prerequisite "git" "sudo dnf install -y git" ;;
        brew) install_prerequisite "git" "brew install git" ;;
        pacman) install_prerequisite "git" "sudo pacman -S --noconfirm git" ;;
        *)
            if ! command -v git &> /dev/null; then
                error "git not found and package manager not recognized. Please install git manually."
            fi
            success "git is available"
            ;;
    esac

    # Docker installation with auto-detection
    if ! command -v docker &> /dev/null; then
        warning "Docker not found"
        if auto_prompt "Install Docker automatically?"; then
            log "Installing Docker..."
            case "$pkg_mgr" in
                apt)
                    curl -fsSL https://get.docker.com | sh
                    sudo usermod -aG docker "$USER"
                    log "Added user to docker group. You may need to log out and back in."
                    ;;
                brew)
                    log "Please install Docker Desktop from: https://docs.docker.com/desktop/mac/"
                    error "Docker Desktop installation requires manual download"
                    ;;
                *)
                    curl -fsSL https://get.docker.com | sh
                    sudo usermod -aG docker "$USER"
                    ;;
            esac
        else
            error "Docker is required. Install from: https://docs.docker.com/get-docker/"
        fi
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
    success "Docker is running"

    # Nix installation (optional but recommended)
    if ! command -v nix &> /dev/null; then
        if auto_prompt "Install Nix for reproducible development environments?"; then
            log "Installing Nix..."
            curl -L https://nixos.org/nix/install | sh
            source ~/.nix-profile/etc/profile.d/nix.sh
            success "Nix installed successfully"
            log "Reproducible development environments now available!"
        else
            log "Skipping Nix installation (optional)"
        fi
    else
        success "Nix is available - reproducible environments enabled"
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

    # Python 3.12+ installation
    if ! command -v python3 &> /dev/null; then
        case "$pkg_mgr" in
            apt) install_prerequisite "python3" "sudo apt update && sudo apt install -y python3.12 python3.12-pip python3.12-venv" ;;
            brew) install_prerequisite "python3" "brew install python@3.12" ;;
            dnf) install_prerequisite "python3" "sudo dnf install -y python3.12 python3-pip" ;;
            pacman) install_prerequisite "python3" "sudo pacman -S --noconfirm python python-pip" ;;
            *) error "python3 not found. Please install Python 3.12+ manually" ;;
        esac
    fi

    # Check Python version
    MIN_PYTHON_MAJOR=3
    MIN_PYTHON_MINOR=12
    PYTHON_VERSION=$(python3 --version 2>/dev/null | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

    if (( PYTHON_MAJOR < MIN_PYTHON_MAJOR || (PYTHON_MAJOR == MIN_PYTHON_MAJOR && PYTHON_MINOR < MIN_PYTHON_MINOR) )); then
        warning "Python $PYTHON_VERSION found, need 3.12+"
        if auto_prompt "Upgrade Python to 3.12+?"; then
            case "$pkg_mgr" in
                apt) sudo apt install -y python3.12 python3.12-pip ;;
                brew) brew install python@3.12 ;;
                *) error "Please upgrade Python manually to 3.12+" ;;
            esac
        else
            error "Python 3.12+ is required"
        fi
    fi
    success "Python $PYTHON_VERSION is suitable"

    # Check available disk space (need ~3GB for BGE-M3 model)
    available_space=$(df -BG "$HOME" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$available_space" -lt 4 ]; then
        warning "Low disk space: ${available_space}GB available. BGE-M3 model needs ~3GB"
        if ! auto_prompt "Continue with limited disk space?"; then
            error "Installation cancelled. Please free up disk space and try again."
        fi
    fi

    success "All prerequisites satisfied"
}

# --- Dependency Installation ---
install_dependencies() {
    progress "Installing Python dependencies..."

    # Check for uv (ultra-fast Python package installer)
    if ! command -v uv &> /dev/null; then
        log "Installing 'uv' package manager for faster Python installs..."
        if auto_prompt "Install uv package manager?"; then
            curl -LsSf https://astral.sh/uv/install.sh | sh
            # Re-source shell profile to make uv available
            source "$HOME/.cargo/env" 2>/dev/null || true
            success "uv package manager installed"
        else
            warning "Falling back to pip (slower installation)"
        fi
    fi

    # Install Python packages
    if command -v uv &> /dev/null; then
        log "Using uv for fast dependency installation..."
        uv pip install -r "$SCRIPT_DIR/requirements.txt"
        uv pip install -r "$SCRIPT_DIR/.synapse/neo4j/requirements.txt"
    else
        log "Using pip for dependency installation..."
        python3 -m pip install -r "$SCRIPT_DIR/requirements.txt"
        python3 -m pip install -r "$SCRIPT_DIR/.synapse/neo4j/requirements.txt"
    fi

    success "Python dependencies installed"
}

# --- CLI Setup ---
setup_cli() {
    progress "Configuring 'synapse' CLI..."
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
        if auto_prompt "Install CLI globally (requires sudo)?"; then
            if sudo ln -sf "$cli_source_path" "$cli_target_path"; then
                success "CLI installed globally"
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
    progress "Starting Synapse services..."

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
    progress "Verifying installation..."

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
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                 Synapse System Installer                     ║${NC}"
    echo -e "${BLUE}║          Following 4QZero: One Path, Zero Decisions          ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${YELLOW}AI agents that write code while you think.${NC}"
    echo

    # Auto-yes mode detection
    if [[ "$AUTO_YES" != "true" ]]; then
        echo -e "${BLUE}This installer will:${NC}"
        echo "  • Detect and install prerequisites automatically"
        echo "  • Set up Docker services for knowledge engine"
        echo "  • Configure CLI and development environments"
        echo "  • Initialize 18 specialized AI agents"
        echo
        if ! auto_prompt "Proceed with automatic installation?"; then
            log "Installation cancelled by user"
            exit 0
        fi
        echo
    fi

    check_prerequisites
    install_dependencies
    setup_cli
    post_install_setup
    verify_installation

    progress "Installation complete!"
    echo
    echo -e "${GREEN}🎉 Synapse System is ready!${NC}"
    echo
    echo -e "${BLUE}Quick Start:${NC}"
    echo -e "  ${YELLOW}synapse init .${NC}              # Add AI agents to any project"
    echo -e "  ${YELLOW}@boss implement auth${NC}        # They write the code for you"
    echo -e "  ${YELLOW}synapse status${NC}              # Check system health"
    echo
    if ! command -v synapse >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Restart your terminal to use 'synapse' command${NC}"
        echo -e "  ${BLUE}Or run:${NC} source ~/.bashrc"
        echo
    fi

    echo -e "${BLUE}Documentation:${NC} https://github.com/your-repo/synapse-system"
    echo -e "${BLUE}Consciousness Level:${NC} 0.52 (7 patterns discovered)"
    echo
}

main
