#!/bin/bash

REPO_URL="https://github.com/nebuff/aero.git"
INSTALL_DIR="$HOME/aero"
VERSIONS_DIR="$INSTALL_DIR/versions"
AERO_TMP="/tmp/aero_tmp_exec"

clear
echo "Aero Installer <-> By Holden"
echo

# Prevent running from inside the install directory
if [[ "$PWD" == "$INSTALL_DIR"* ]]; then
    echo "Please run this installer from outside the $INSTALL_DIR directory."
    exit 1
fi

# Check for existing install
if [ -d "$INSTALL_DIR" ]; then
    echo "Looks like theres Already a Aero Install, Want to Reinstall or Update? (y/n)"
    read -r yn
    if [ "$yn" != "y" ]; then
        echo "Exiting installer."
        exit 0
    fi
    # No need to move script, just continue
fi

# Clone the repo
git clone "$REPO_URL" "$INSTALL_DIR" || { echo "Failed to clone repo."; exit 1; }

# Find available versions
cd "$VERSIONS_DIR" || { echo "No versions directory found."; exit 1; }

echo
echo "- Pre Release -"
ls aero-pre-* 2>/dev/null
echo
echo "- Beta -"
ls aero-beta-* 2>/dev/null
echo
echo "- Stables (Recomended) -"
ls aero-stable-* 2>/dev/null
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

# Recreate versions directory if needed
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

# Always use the working Python path for Aero
PYTHON_PATH="/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"

echo
echo "Aero installed in $INSTALL_DIR as 'aero'."
echo "You can run it with: $INSTALL_DIR/aero"
echo "To make it available everywhere, add this line to your ~/.zshrc or ~/.bashrc:"
echo "export PATH=\"\$HOME/aero:\$PATH\""
echo

# Add to PATH if not already present
SHELL_RC=""
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
    if ! grep -q 'export PATH="\$HOME/aero:\$PATH"' "$SHELL_RC"; then
        echo 'export PATH="$HOME/aero:$PATH"' >> "$SHELL_RC"
        echo "Added Aero to your PATH in $SHELL_RC"
    fi
fi

# Print Python version info
echo "Python used by Aero (double-click):"
"$PYTHON_PATH" --version 2>/dev/null || echo "Could not detect Python version."

echo
echo "To always use the same Python in your terminal, run:"
echo "\"$PYTHON_PATH\" \"$INSTALL_DIR/aero\""
echo "Or add an alias to your shell config:"
echo "alias aero='$PYTHON_PATH $INSTALL_DIR/aero'"
echo

# Add alias to shell config (always append or update)
if [ -n "$SHELL_RC" ]; then
    # Remove any existing aero alias
    grep -v "^alias aero=" "$SHELL_RC" > "${SHELL_RC}.tmp" && mv "${SHELL_RC}.tmp" "$SHELL_RC"
    # Add the correct alias
    echo "alias aero='$PYTHON_PATH $INSTALL_DIR/aero'" >> "$SHELL_RC"
    echo "Added or updated alias 'aero' in $SHELL_RC"
fi

echo
echo "---------------------------------------------"
echo "To use the 'aero' command, open a NEW terminal"
echo "window or tab, or run: source $SHELL_RC"
echo "Then you can type: aero"
echo "---------------------------------------------"
echo
echo "Open a new terminal window or tab, or type: source $SHELL_RC"
echo "Then you can run: aero"
fi
