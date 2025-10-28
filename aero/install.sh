#!/bin/bash

# Configuration
REPO_OWNER="nebuff"
REPO_NAME="aero"
REPO_ROOT_URL="https://raw.githubusercontent.com/$REPO_OWNER/$REPO_NAME/main"
REPO_LIB_URL="$REPO_ROOT_URL/lib"
REPO_PLUGINS_URL="$REPO_ROOT_URL/plugins"

INSTALL_DIR="$HOME/aero"
AERO_TMP="/tmp/aero_tmp_exec"

clear
echo "Aero Installer <-> By Nebuff"
echo

# Prevent running from inside the install directory
case "$PWD" in
    "$INSTALL_DIR"*)
        echo "Please run this installer from outside the $INSTALL_DIR directory."
        exit 1
        ;;
esac

# Function to detect Python
detect_python() {
    local python_cmd=""
    
    # Try different Python commands in order of preference
    for cmd in python3 python python3.13 python3.12 python3.11 python3.10; do
        if command -v "$cmd" >/dev/null 2>&1; then
            python_cmd="$cmd"
            break
        fi
    done
    
    if [ -z "$python_cmd" ]; then
        echo "Python not found. Please install Python 3.x first."
        echo "Visit: https://www.python.org/downloads/"
        exit 1
    fi
    
    # Verify Python version is 3.x
    if ! "$python_cmd" -c "import sys; sys.exit(0 if sys.version_info.major == 3 else 1)" 2>/dev/null; then
        echo "Python 3.x is required. Found: $($python_cmd --version 2>&1)"
        exit 1
    fi
    
    echo "$python_cmd"
}

# Function to add $HOME/aero to shell config files
add_to_shell_config() {
    local config_file="$1"
    local shell_type="$2"
    local config_line
    
    # Determine the export command based on shell type
    if [ "$shell_type" = "fish" ]; then
        config_line="set -gx PATH \"\$HOME/aero\" \$PATH"
    else
        config_line='export PATH="$HOME/aero:$PATH"'
    fi

    # Check if the path is already set
    if grep -qF "$config_line" "$config_file"; then
        return
    fi

    # Add the path to the config file
    echo "" >> "$config_file"
    echo "# --- Added by Aero Shell Installer ---" >> "$config_file"
    echo "$config_line" >> "$config_file"
    echo "# -------------------------------------" >> "$config_file"
    
    echo "Added \$HOME/aero to PATH in $config_file"
}

# --- Download Core Libraries ---
download_core_libs() {
    local LIB_DIR="$INSTALL_DIR/lib"
    
    # The list of all refactored files
    local CORE_LIBS=(
        "constants.py"
        "core.py"
        "config_manager.py"
        "plugin_manager.py"
        "core_commands.py"
    )

    echo "Creating library directory: $LIB_DIR"
    mkdir -p "$LIB_DIR"

    echo "Downloading core library files..."
    for file in "${CORE_LIBS[@]}"; do
        echo "  -> Fetching $file"
        # Use curl to download the file directly into the lib directory
        if ! curl -fsSL "$REPO_LIB_URL/$file" -o "$LIB_DIR/$file"; then
            echo "FATAL: Failed to download $file. Check network and repo name."
            exit 1
        fi
    done
    echo "Library files successfully downloaded."
}

# --- Main Installation Steps ---

# 1. Detect Python
PYTHON_CMD=$(detect_python)
echo "Using Python executable: $PYTHON_CMD"
echo

# 2. Confirm installation path
echo "Installation Directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/plugins" # Ensure plugins folder exists too

# 3. Download the main executable ('aero')
echo "Downloading main 'aero' executable..."
if ! curl -fsSL "$REPO_ROOT_URL/aero" -o "$AERO_TMP"; then
    echo "FATAL: Failed to download the main 'aero' executable."
    exit 1
fi

# 4. Download Core Libraries (NEW STEP)
download_core_libs

# 5. Create default config.json if it doesn't exist
CONFIG_PATH="$INSTALL_DIR/config.json"
if [ ! -f "$CONFIG_PATH" ]; then
    echo "Creating default config.json..."
    cat > "$CONFIG_PATH" <<-EOF
{
  "color": true,
  "username": "$(whoami)",
  "prompt_template": "<green>{username}</green>@<blue>{hostname}</blue> <yellow>{short_pwd}</yellow> ❯ ",
  "time_format": "24",
  "colors": {
    "info": "\033[33m",
    "error": "\033[31m",
    "success": "\033[32m",
    "warning": "\033[33m",
    "header": "\033[1;36m",
    "subheader": "\033[1;33m",
    "data_primary": "\033[36m",
    "data_value": "\033[37m",
    "data_key": "\033[33m",
    "reset": "\033[0m"
  }
}
EOF
fi

# 6. Move executable back and rename to 'aero'
mv "$AERO_TMP" "$INSTALL_DIR/aero"
chmod +x "$INSTALL_DIR/aero"

echo
echo "Aero installed in $INSTALL_DIR as 'aero'."
echo "You can run it with: $INSTALL_DIR/aero"
echo

# 7. Add to shell configurations
for config in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$config" ] || [ "$config" = "$HOME/.bashrc" ] || [ "$config" = "$HOME/.zshrc" ]; then
        add_to_shell_config "$config" "posix"
    fi
done

# Handle Fish shell configuration
if command -v fish >/dev/null 2>&1; then
    FISH_CONFIG="$HOME/.config/fish/config.fish"
    mkdir -p "$(dirname "$FISH_CONFIG")"
    add_to_shell_config "$FISH_CONFIG" "fish"
fi

# Export PATH for current session
export PATH="$HOME/aero:$PATH"

# Try to source the appropriate config for current shell
if [ -n "$ZSH_VERSION" ] && [ -f "$HOME/.zshrc" ]; then
    # shellcheck disable=SC1090
    . "$HOME/.zshrc" 2>/dev/null || true
elif [ -n "$BASH_VERSION" ] && [ -f "$HOME/.bashrc" ]; then
    # shellcheck disable=SC1090
    . "$HOME/.bashrc" 2>/dev/null || true
fi

echo "Reloaded shell config. You should be able to run 'aero' from a new terminal session."
echo "You can also run it now by typing: $INSTALL_DIR/aero"
