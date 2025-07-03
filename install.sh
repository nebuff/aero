#!/bin/sh
# Aero Installer Script
# Downloads latest main.c, builds Aero, and adds 'aero' alias to common shells

REPO_URL="https://raw.githubusercontent.com/nebuff/aero/main/src/main.c"
INSTALL_DIR="$HOME/aero"
SRC_DIR="$INSTALL_DIR/src"
BIN_PATH="$INSTALL_DIR/aero"

mkdir -p "$SRC_DIR"
echo "Downloading latest Aero main.c..."
curl -fsSL "$REPO_URL" -o "$SRC_DIR/main.c"

echo "Building Aero..."
cc "$SRC_DIR/main.c" -o "$BIN_PATH"
if [ $? -ne 0 ]; then
    echo "Build failed. Please ensure you have a C compiler installed."
    exit 1
fi

add_alias() {
    SHELL_RC="$1"
    if [ -f "$SHELL_RC" ]; then
        if ! grep -q "alias aero=" "$SHELL_RC"; then
            echo "alias aero=\"$BIN_PATH\"" >> "$SHELL_RC"
            echo "Added alias to $SHELL_RC"
        else
            echo "Alias already exists in $SHELL_RC"
        fi
    fi
}

# Bash
add_alias "$HOME/.bashrc"
# Zsh
add_alias "$HOME/.zshrc"
# Fish
if [ -d "$HOME/.config/fish" ]; then
    FISH_CONFIG="$HOME/.config/fish/config.fish"
    if ! grep -q "alias aero" "$FISH_CONFIG" 2>/dev/null; then
        echo "alias aero $BIN_PATH" >> "$FISH_CONFIG"
        echo "Added alias to $FISH_CONFIG"
    else
        echo "Alias already exists in $FISH_CONFIG"
    fi
fi
# PowerShell
POWERSHELL_PROFILE="$HOME/Documents/PowerShell/Microsoft.PowerShell_profile.ps1"
if [ -f "$POWERSHELL_PROFILE" ]; then
    if ! grep -q "function aero" "$POWERSHELL_PROFILE"; then
        echo "function aero { & \"$BIN_PATH\" $args }" >> "$POWERSHELL_PROFILE"
        echo "Added function to $POWERSHELL_PROFILE"
    else
        echo "Function already exists in $POWERSHELL_PROFILE"
    fi
fi

echo "Installation complete. Restart your shell or source your config file to use 'aero' command."
