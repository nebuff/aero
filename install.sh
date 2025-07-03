#!/bin/sh
# Aero Installer Script
# Installs C compiler and dependencies, downloads latest main.c and components, builds Aero, and adds 'aero' alias to common shells

REPO_URL="https://raw.githubusercontent.com/nebuff/aero/73ed7534a6e863b87eda16f6bbb7a4f753ad475d/main.c"
COMPONENTS_URL="https://github.com/nebuff/aero/archive/refs/heads/main.zip"
INSTALL_DIR="$HOME/aero"
SRC_DIR="$INSTALL_DIR/src"
COMPONENTS_DIR="$INSTALL_DIR/components"
BIN_PATH="$INSTALL_DIR/aero"

# Detect OS and install C compiler if missing
install_compiler() {
    if command -v cc >/dev/null 2>&1 || command -v gcc >/dev/null 2>&1 || command -v clang >/dev/null 2>&1; then
        echo "C compiler found."
        return
    fi
    echo "No C compiler found. Attempting to install..."
    UNAME=$(uname)
    if [ "$UNAME" = "Darwin" ]; then
        # macOS
        if ! xcode-select -p >/dev/null 2>&1; then
            echo "Installing Xcode Command Line Tools..."
            xcode-select --install
            echo "Please rerun this script after installation completes."
            exit 1
        fi
    elif [ "$UNAME" = "Linux" ]; then
        if command -v apt-get >/dev/null 2>&1; then
            sudo apt-get update && sudo apt-get install -y build-essential unzip curl
        elif command -v dnf >/dev/null 2>&1; then
            sudo dnf install -y gcc unzip curl
        elif command -v yum >/dev/null 2>&1; then
            sudo yum install -y gcc unzip curl
        elif command -v pacman >/dev/null 2>&1; then
            sudo pacman -Sy --noconfirm base-devel unzip curl
        else
            echo "Unsupported Linux package manager. Please install gcc, unzip, and curl manually."
            exit 1
        fi
    elif [ "$UNAME" = "MINGW"* ] || [ "$UNAME" = "MSYS"* ] || [ "$UNAME" = "CYGWIN"* ]; then
        echo "Please install a C compiler (e.g., TDM-GCC or MSYS2), unzip, and curl manually on Windows."
        exit 1
    else
        echo "Unknown OS. Please install a C compiler, unzip, and curl manually."
        exit 1
    fi
}

install_compiler

mkdir -p "$SRC_DIR"
echo "Downloading Aero main.c..."
curl -fsSL "$REPO_URL" -o "$SRC_DIR/main.c"
if [ ! -f "$SRC_DIR/main.c" ]; then
    echo "Failed to download main.c from $REPO_URL"
    exit 1
fi

# Download and extract components
mkdir -p "$COMPONENTS_DIR"
echo "Downloading Aero components..."
tmpzip="/tmp/aero_components.zip"
curl -fsSL -o "$tmpzip" "$COMPONENTS_URL"
unzip -o -q "$tmpzip" -d /tmp/aero_repo
cp -r /tmp/aero_repo/aero-main/components/* "$COMPONENTS_DIR" 2>/dev/null || cp -r /tmp/aero_repo-main/components/* "$COMPONENTS_DIR" 2>/dev/null
rm -rf /tmp/aero_repo /tmp/aero_repo-main "$tmpzip"

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
