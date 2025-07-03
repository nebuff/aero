#!/bin/sh

# Aero Installer Script
set -e

# Relaunch with sudo if not root
if [ "$(id -u)" -ne 0 ]; then
    echo "[Aero Installer] Re-running with sudo..."
    exec sudo /bin/sh "$0" "$@"
fi

# Ensure /aero exists and is owned by the user
if [ ! -d /aero ]; then
    mkdir -p /aero
    chown "$SUDO_USER" /aero 2>/dev/null || chown "$USER" /aero 2>/dev/null || true
fi

# Clone or update Aero source into /aero/.aero-src
if [ ! -d /aero/.aero-src ]; then
    git clone https://github.com/nebuff/aero.git /aero/.aero-src
else
    cd /aero/.aero-src
    git pull
fi

cd /aero/.aero-src/src
make

# Install the Aero binary to /aero
cp -f aero /aero/aero
chmod +x /aero/aero

# Copy app-list.txt to /aero, or create a default one if missing
if [ -f ../app-list.txt ]; then
    cp ../app-list.txt /aero/app-list.txt
elif [ -f app-list.txt ]; then
    cp app-list.txt /aero/app-list.txt
elif [ ! -f /aero/app-list.txt ]; then
    tee /aero/app-list.txt > /dev/null <<EOF
{"settings": {
  "nav_mode": "letters",
  "app_fg": "cyan",
  "app_bg": "black",
  "sel_fg": "black",
  "sel_bg": "yellow"
}},
[
  {"name": "Text Editor", "alias": "nano"},
  {"name": "Web Browser", "alias": "lynx"},
  {"name": "Terminal", "alias": "bash"},
  {"name": "File Manager", "alias": "mc"},
  {"name": "Music Player", "alias": "cmus"},
  {"name": "Video Player", "alias": "mpv"},
  {"name": "Image Viewer", "alias": "fim"},
  {"name": "Calculator", "alias": "bc"},
  {"name": "Notes", "alias": "nano ~/notes.txt"},
  {"name": "Resource Monitor", "alias": "htop"}
]
EOF
fi

# Install Aero's built-in pkm-main as the Package Manager
if [ -d "$PWD/pkm-main" ]; then
    mkdir -p /aero/pkm-main
    cp -r "$PWD/pkm-main/"* /aero/pkm-main/
    chmod +x /aero/pkm-main/pkm
    ln -sf /aero/pkm-main/pkm /aero/pkm
else
    echo "Warning: pkm-main folder not found in workspace, skipping built-in package manager install."
fi

# Remove any existing aliases for 'aero' in common shell config files
for shellrc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile" "$HOME/.bash_profile"; do
    if [ -f "$shellrc" ]; then
        sed -i.bak '/alias[[:space:]]\+aero=/d' "$shellrc" 2>/dev/null || true
        rm -f "$shellrc.bak"
        echo 'alias aero="/aero/aero"' >> "$shellrc"
    fi
done

# Remove any existing fish function for aero
if [ -d "$HOME/.config/fish/functions" ]; then
    rm -f "$HOME/.config/fish/functions/aero.fish"
    echo -e "function aero\n    /aero/aero\nend" > "$HOME/.config/fish/functions/aero.fish"
fi

# For fish shell PATH
if [ -d "$HOME/.config/fish" ]; then
    if ! grep -q '/aero' "$HOME/.config/fish/config.fish" 2>/dev/null; then
        echo 'set -gx PATH /aero $PATH' >> "$HOME/.config/fish/config.fish"
    fi
fi

echo
ls -l /aero
ls -l /aero/app-list.txt || true
ls -l /aero/aero || true
echo

echo "Aero installed in /aero! You may need to open a new terminal window for the command to work."
echo 'If you still see "Unknown Command: aero", log out and back in, or run: export PATH="/aero:$PATH"'
echo
