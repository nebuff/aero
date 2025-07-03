#!/bin/sh
# Aero Installer Script
set -e


# Detect OS and install ncurses/curl/git/build tools if needed
if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y build-essential libncurses5-dev curl git
elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y ncurses-devel gcc make curl git
elif command -v yum >/dev/null 2>&1; then
    sudo yum install -y ncurses-devel gcc make curl git
elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy --noconfirm ncurses base-devel curl git
elif command -v zypper >/dev/null 2>&1; then
    sudo zypper install -y ncurses-devel gcc make curl git
elif command -v apk >/dev/null 2>&1; then
    sudo apk add ncurses-dev build-base curl git
elif command -v brew >/dev/null 2>&1; then
    brew install ncurses git curl
elif command -v pkg >/dev/null 2>&1; then
    sudo pkg install -y ncurses gcc gmake curl git
else
    echo "Please install ncurses development libraries, gcc, make, curl, and git manually."
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
sudo cp aero /usr/local/bin/
sudo chmod +x /usr/local/bin/aero

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
    mkdir -p "$HOME/.config/fish/conf.d"
    echo 'set -gx PATH /usr/local/bin $PATH' > "$HOME/.config/fish/conf.d/aero_path.fish"
    echo 'function aero; /usr/local/bin/aero $argv; end' > "$HOME/.config/fish/functions/aero.fish"
fi

echo 'If you still see "Unknown Command: aero", log out and back in, or run: export PATH="/usr/local/bin:$PATH"'
echo "Aero installed! You may need to open a new terminal window for the command to work."
echo 'If you still see "Unknown Command: aero", log out and back in, or run: export PATH="/usr/local/bin:$PATH"'
