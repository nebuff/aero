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
echo

# Add to PATH and alias in both .zshrc and .bashrc (permanent for all new terminals)
for RC in "$HOME/.zshrc" "$HOME/.bashrc"; do
    # Ensure the file exists
    touch "$RC"
    # Ensure PATH is set (add only if not present and not commented out)
    if ! grep -E '^[^#]*export PATH="\$HOME/aero:\$PATH"' "$RC" > /dev/null; then
        echo 'export PATH="$HOME/aero:$PATH"' >> "$RC"
        echo "Added Aero to your PATH in $RC"
    fi
    # Remove any existing aero alias (even if commented out)
    sed -i.bak '/alias aero=/d' "$RC"
    # Add the correct alias
    echo "alias aero='$PYTHON_PATH $INSTALL_DIR/aero'" >> "$RC"
    echo "Added or updated alias 'aero' in $RC"
done

# Export PATH for current session
export PATH="$HOME/aero:$PATH"
# shellcheck disable=SC1090
if [ -n "$ZSH_VERSION" ]; then
    source "$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    source "$HOME/.bashrc"
fi
echo "Reloaded your shell configs so the 'aero' alias is available now."

echo
echo "---------------------------------------------"
echo "To use the 'aero' command, open a NEW terminal"
echo "window or tab, or run: source ~/.zshrc or source ~/.bashrc"
echo "Then you can type: aero"
echo "---------------------------------------------"
echo
