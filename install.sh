#!/bin/bash

REPO_URL="https://github.com/nebuff/aero.git"
INSTALL_DIR="$HOME/aero"
VERSIONS_DIR="$INSTALL_DIR/versions"
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

# Function to add to shell config
add_to_shell_config() {
    local config_file="$1"
    local shell_type="$2"
    
    # Ensure the file exists
    touch "$config_file"
    
    case "$shell_type" in
        "fish")
            # Fish shell configuration
            if ! grep -q "set -gx PATH \$HOME/aero \$PATH" "$config_file" 2>/dev/null; then
                echo "set -gx PATH \$HOME/aero \$PATH" >> "$config_file"
                echo "Added Aero to PATH in $config_file"
            fi
            # Remove existing alias and add new one
            sed -i.bak '/alias aero/d' "$config_file" 2>/dev/null || true
            echo "alias aero='$PYTHON_PATH $INSTALL_DIR/aero'" >> "$config_file"
            ;;
        *)
            # Bash/Zsh configuration
            if ! grep -E '^[^#]*export PATH="\$HOME/aero:\$PATH"' "$config_file" >/dev/null 2>&1; then
                echo 'export PATH="$HOME/aero:$PATH"' >> "$config_file"
                echo "Added Aero to PATH in $config_file"
            fi
            # Remove existing alias and add new one
            sed -i.bak '/alias aero=/d' "$config_file" 2>/dev/null || true
            echo "alias aero='$PYTHON_PATH $INSTALL_DIR/aero'" >> "$config_file"
            ;;
    esac
    
    echo "Updated alias in $config_file"
}

# Check for existing install
if [ -d "$INSTALL_DIR" ]; then
    echo "Looks like theres Already a Aero Install, Want to Reinstall or Update? (y/n)"
    read -r yn
    if [ "$yn" != "y" ]; then
        echo "Exiting installer."
        exit 0
    fi
fi

# Detect Python before proceeding
PYTHON_PATH=$(detect_python)
echo "Using Python: $PYTHON_PATH"

# Clone the repo
git clone "$REPO_URL" "$INSTALL_DIR" || { echo "Failed to clone repo."; exit 1; }

# Find available versions
cd "$VERSIONS_DIR" || { echo "No versions directory found."; exit 1; }

echo
echo "- Pre Release -"
ls aero-pre-* 2>/dev/null | head -10
echo
echo "- Beta -"
ls aero-beta-* 2>/dev/null | head -10
echo
echo "- Stables (Recomended) -"
ls aero-stable-* 2>/dev/null | head -10
echo

echo "Type the version you want to install (e.g. aero-stable-1.0):"
read -r version

if [ ! -f "$version" ]; then
    echo "Version not found."
    exit 1
fi

# Move selected executable to /tmp
cp "$version" "$AERO_TMP"

# Remove everything in aero folder
cd "$HOME"
rm -rf "$INSTALL_DIR"/*

# Recreate directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/plugins"

# Create default config.json if not exists
if [ ! -f "$INSTALL_DIR/config.json" ]; then
    cat > "$INSTALL_DIR/config.json" <<EOF
{
  "color": true,
  "username": "Aero-User",
  "colors": {
    "prompt": "\\u001b[32m",
    "info": "\\u001b[33m",
    "error": "\\u001b[31m",
    "plugin": "\\u001b[36m",
    "reset": "\\u001b[0m"
  }
}
EOF
fi

# Move executable back and rename to 'aero'
mv "$AERO_TMP" "$INSTALL_DIR/aero"
chmod +x "$INSTALL_DIR/aero"

echo
echo "Aero installed in $INSTALL_DIR as 'aero'."
echo "You can run it with: $INSTALL_DIR/aero"
echo

# Add to shell configurations
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

echo "Reloaded shell configs where possible."
echo
echo "---------------------------------------------"
echo "To use the 'aero' command:"
echo "1. Open a NEW terminal window/tab, OR"
echo "2. Run one of these commands:"
echo "   - Bash: source ~/.bashrc"
echo "   - Zsh:  source ~/.zshrc" 
echo "   - Fish: source ~/.config/fish/config.fish"
echo "Then you can type: aero"
echo "---------------------------------------------"
echo
