#!/bin/bash

# --- Configuration ---
# Target repository URL
REPO_URL="https://github.com/nebuff/aero.git"
# Specific commit hash containing the ready-to-use 'aero' directory
COMMIT_HASH="529793e612ff0dd89a94e0845a1c1f028ec86776"
# The subdirectory within the commit containing the Aero files
SUB_DIR="aero"
# The final installation directory
INSTALL_DIR="$HOME/aero"
# Temporary directory for cloning
TEMP_DIR="/tmp/aero_install_temp"

# Define colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

clear
echo -e "${CYAN}Aero Installer <-> By Nebuff${NC}"
echo

# --- Helper Functions ---

# Function to add the PATH export to shell config files
add_to_shell_config() {
    local config_file="$1"
    local shell_type="$2"
    local path_to_add="$INSTALL_DIR"

    if [ -f "$config_file" ] && grep -q "export PATH=\"$path_to_add:\$PATH\"" "$config_file" 2>/dev/null; then
        echo -e "${YELLOW}PATH already set in $config_file.${NC}"
    else
        echo -e "${YELLOW}Adding PATH to $config_file...${NC}"
        if [ "$shell_type" = "fish" ]; then
            cat <<-EOF >> "$config_file"
# Add Aero to PATH
set -gx PATH \$HOME/aero \$PATH
EOF
        else # bash/zsh
            cat <<-EOF >> "$config_file"

# Add Aero to PATH
export PATH="$path_to_add:\$PATH"
EOF
        fi
    fi
}

# --- Installation Logic ---
install_aero() {
    echo -e "${CYAN}--- Preparing Installation ---${NC}"

    # Check for Git
    if ! command -v git >/dev/null 2>&1; then
        echo -e "${RED}Error: Git is not installed. Please install Git to continue.${NC}"
        exit 1
    fi

    # Clean up previous installation directory
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}Removing existing installation in $INSTALL_DIR...${NC}"
        rm -rf "$INSTALL_DIR"
    fi

    # Clean up previous temporary directory
    rm -rf "$TEMP_DIR"
    mkdir -p "$INSTALL_DIR"

    echo -e "${YELLOW}Cloning repository and checking out specific commit ($COMMIT_HASH)...${NC}"

    # 1. Clone the repository minimally
    if ! git clone --depth 1 "$REPO_URL" "$TEMP_DIR"; then
        echo -e "${RED}Error: Failed to clone repository.${NC}"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
    
    # 2. Change into the temp directory and check out the specific commit
    cd "$TEMP_DIR" || exit 1

    # Ensure the commit is available locally
    git fetch origin "$COMMIT_HASH"

    if ! git checkout "$COMMIT_HASH" -- "$SUB_DIR"; then
        echo -e "${RED}CRITICAL ERROR: Failed to checkout directory '$SUB_DIR' from commit.${NC}"
        cd ~
        rm -rf "$TEMP_DIR"
        exit 1
    fi
    
    AERO_SOURCE_DIR="$TEMP_DIR/$SUB_DIR"
    
    # 3. Check if the subdirectory exists after checkout
    if [ ! -d "$AERO_SOURCE_DIR" ]; then
        echo -e "${RED}CRITICAL ERROR: Subdirectory '$SUB_DIR' not found after checkout. Please verify the structure.${NC}"
        cd ~
        rm -rf "$TEMP_DIR"
        exit 1
    fi

    # 4. Move contents of the subdirectory to the final install directory
    echo -e "${YELLOW}Moving contents from $AERO_SOURCE_DIR to $INSTALL_DIR...${NC}"
    # Move non-hidden files
    mv "$AERO_SOURCE_DIR"/* "$INSTALL_DIR"/
    # Move hidden files (like .gitignore) - suppress error if none exist
    mv "$AERO_SOURCE_DIR"/.* "$INSTALL_DIR"/ 2>/dev/null || true 
    
    # 5. Set executable permissions
    if [ ! -f "$INSTALL_DIR/aero" ]; then
        echo -e "${RED}CRITICAL ERROR: Main executable 'aero' not found in final directory.${NC}"
        cd ~
        rm -rf "$TEMP_DIR"
        exit 1
    fi
    echo -e "${YELLOW}Setting executable permissions on $INSTALL_DIR/aero...${NC}"
    chmod +x "$INSTALL_DIR/aero"
    
    echo
    echo -e "${CYAN}--- Contents of $INSTALL_DIR ---${NC}"
    ls -l "$INSTALL_DIR"
    echo -e "${CYAN}--------------------------------${NC}"

    # 6. Clean up temp directory
    cd ~
    rm -rf "$TEMP_DIR"
    
    echo -e "${GREEN}Installation files are now complete in $INSTALL_DIR.${NC}"
}

# Run the installation
install_aero

# --- Post-Installation & PATH Setup ---
echo
echo -e "${GREEN}Aero is installed in $INSTALL_DIR.${NC}"

# Add to shell configurations (bash/zsh)
for config in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$config" ] || [ "$config" = "$HOME/.bashrc" ] || [ "$config" = "$HOME/.zshrc" ]; then
        add_to_shell_config "$config" "posix"
    fi
done

# Handle Fish shell configuration
if command -v fish >/dev/null 2>&1; then
    FISH_CONFIG="$HOME/.config/fish/config.fish"
    mkdir -p "$(dirname "$FISH_CONFIG")" 2>/dev/null || true
    add_to_shell_config "$FISH_CONFIG" "fish"
fi

# Export PATH for current session
export PATH="$INSTALL_DIR:$PATH"

# Try to source the appropriate config for current shell
if [ -n "$ZSH_VERSION" ] && [ -f "$HOME/.zshrc" ]; then
    # shellcheck disable=SC1090
    . "$HOME/.zshrc" 2>/dev/null || true
elif [ -n "$BASH_VERSION" ] && [ -f "$HOME/.bashrc" ]; then
    # shellcheck disable=SC1090
    . "$HOME/.bashrc" 2>/dev/null || true
fi

echo -e "${CYAN}---${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "You can now run Aero by typing: ${GREEN}aero${NC}"
echo "Please start a new terminal session or run one of these commands if 'aero' is not recognized:"
echo -e "  ${YELLOW}source ~/.bashrc${NC}"
echo -e "  ${YELLOW}source ~/.zshrc${NC}"
