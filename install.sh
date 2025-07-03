#!/bin/sh

# Aero Installer Script
set -e




# Detect OS and install ncurses/curl/git/build tools if needed
if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y build-essential libncurses5-dev curl git nano fish
elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y ncurses-devel gcc make curl git nano fish
elif command -v yum >/dev/null 2>&1; then
    sudo yum install -y ncurses-devel gcc make curl git nano fish
elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy --noconfirm ncurses base-devel curl git nano fish
elif command -v zypper >/dev/null 2>&1; then
    sudo zypper install -y ncurses-devel gcc make curl git nano fish
elif command -v apk >/dev/null 2>&1; then
    sudo apk add ncurses-dev build-base curl git nano fish
elif command -v brew >/dev/null 2>&1; then
    brew install ncurses git curl nano fish
elif command -v pkg >/dev/null 2>&1; then
    sudo pkg install -y ncurses gcc gmake curl git nano fish
else
    echo "Please install ncurses development libraries, gcc, make, curl, git, and fish manually."
    exit 1
fi

# Clone or update Aero

# Use the official repo
if [ ! -d "$HOME/.aero-src" ]; then
    git clone https://github.com/nebuff/aero.git "$HOME/.aero-src"
else
    cd "$HOME/.aero-src"
    git pull
fi

cd "$HOME/.aero-src/src"
make


# Remove any existing aliases for 'aero' in common shell config files
for shellrc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile" "$HOME/.bash_profile"; do
    if [ -f "$shellrc" ]; then
        sed -i.bak '/alias[[:space:]]\+aero=/d' "$shellrc" 2>/dev/null || true
        rm -f "$shellrc.bak"
    fi
done

# Remove any existing fish function for aero
if [ -d "$HOME/.config/fish/functions" ]; then
    rm -f "$HOME/.config/fish/functions/aero.fish"
fi





# Ensure the binary is executable
chmod +x aero
# If /usr/local/bin/aero is running, move to temp then overwrite
if [ -f /usr/local/bin/aero ]; then
    # Try to copy with overwrite, fallback to move if needed
    cp -f aero /usr/local/bin/aero 2>/dev/null || {
        tmpfile="/usr/local/bin/aero.$$.tmp"
        cp aero "$tmpfile" && mv -f "$tmpfile" /usr/local/bin/aero
    }
else
    cp aero /usr/local/bin/aero
fi
chmod +x /usr/local/bin/aero

# Copy app-list.txt to a shared location, or create a default one if missing
sudo mkdir -p /usr/local/share/aero
if [ -f ../app-list.txt ]; then
    sudo cp ../app-list.txt /usr/local/share/aero/app-list.txt
elif [ -f app-list.txt ]; then
    sudo cp app-list.txt /usr/local/share/aero/app-list.txt
elif [ ! -f /usr/local/share/aero/app-list.txt ]; then
    sudo tee /usr/local/share/aero/app-list.txt > /dev/null <<EOF
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

# Ensure /usr/local/bin is in PATH and create an alias for all users and shells
for shellrc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile" "$HOME/.bash_profile"; do
    if [ -f "$shellrc" ]; then
        if ! grep -q '/usr/local/bin' "$shellrc"; then
            echo 'export PATH="/usr/local/bin:$PATH"' >> "$shellrc"
        fi
        # Add alias for aero if not present
        if ! grep -q 'alias aero=' "$shellrc"; then
            echo 'alias aero="/usr/local/bin/aero"' >> "$shellrc"
        fi
    fi
done


# For fish shell
if [ -d "$HOME/.config/fish" ]; then
    # Add PATH and alias to config.fish if not present
    if ! grep -q '/usr/local/bin' "$HOME/.config/fish/config.fish" 2>/dev/null; then
        echo 'set -gx PATH /usr/local/bin $PATH' >> "$HOME/.config/fish/config.fish"
    fi
    if ! grep -q 'function aero' "$HOME/.config/fish/config.fish" 2>/dev/null; then
        echo 'function aero; /usr/local/bin/aero $argv; end' >> "$HOME/.config/fish/config.fish"
    fi
fi

echo
echo "Aero installed! You may need to open a new terminal window for the command to work."
echo 'If you still see "Unknown Command: aero", log out and back in, or run: export PATH="/usr/local/bin:$PATH"'
echo
echo "Troubleshooting:"
echo "- If you see 'Failed to load app-list.txt':"
echo "    1. Make sure /usr/local/share/aero/app-list.txt exists:"
echo "         ls -l /usr/local/share/aero/app-list.txt"
echo "    2. If missing, re-run the installer."
echo "    3. Make sure you are running the latest aero binary:"
echo "         which aero"
echo "         ls -l /usr/local/bin/aero"
echo "    4. If you built manually, run:"
echo "         cd /Users/holden/aero/src && make && sudo cp aero /usr/local/bin/"
echo "    5. Try running 'aero' from your home directory."
