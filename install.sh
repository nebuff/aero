# Install Discordo (TUI Discord client)
if ! command -v discordo >/dev/null 2>&1; then
    echo "Installing Discordo..."
    if command -v go >/dev/null 2>&1; then
        git clone https://github.com/ayn2op/discordo /tmp/discordo-inst
        cd /tmp/discordo-inst
        go build .
        sudo mv discordo /usr/local/bin/
        cd ..
        rm -rf /tmp/discordo-inst
    else
        echo "Go is not installed. Please install Go to use Discordo."
    fi
else
    echo "Discordo already installed."
fi
#!/bin/sh

# Aero Installer Script
set -e

# Ensure /aero exists at the very start
if [ ! -d /aero ]; then
    mkdir -p /aero
fi


# Detect OS and install ncurses/curl/git/build tools if needed
if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y build-essential libncurses5-dev curl git nano fish sudo
elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y ncurses-devel gcc make curl git nano fish sudo
elif command -v yum >/dev/null 2>&1; then
    sudo yum install -y ncurses-devel gcc make curl git nano fish sudo
elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy --noconfirm ncurses base-devel curl git nano fish sudo
elif command -v zypper >/dev/null 2>&1; then
    sudo zypper install -y ncurses-devel gcc make curl git nano fish sudo
elif command -v apk >/dev/null 2>&1; then
    sudo apk add ncurses-dev build-base curl git nano fish sudo
elif command -v brew >/dev/null 2>&1; then
    brew install ncurses git curl nano fish sudo
elif command -v pkg >/dev/null 2>&1; then
    sudo pkg install -y ncurses gcc gmake curl git nano fish sudo
else
    echo "Please install ncurses development libraries, gcc, make, curl, git, fish, and sudo manually."
    exit 1
fi



# Clone or update Aero
if [ ! -d "$HOME/.aero-src" ]; then
    git clone https://github.com/nebuff/aero.git "$HOME/.aero-src"
else
    cd "$HOME/.aero-src"
    git pull
fi

cd "$HOME/.aero-src/src"
make

# Install all apps listed in app-list.txt (if available)
APP_LIST_FILE="../app-list.txt"
if [ ! -f "$APP_LIST_FILE" ]; then
    APP_LIST_FILE="app-list.txt"
fi
if [ -f "$APP_LIST_FILE" ]; then
    echo "\nInstalling apps from app-list.txt..."
    # Extract all aliases from the app-list (skip Package Manager, Notes, and commands with ~ or /)
    APPS_TO_INSTALL=$(grep '"alias"' "$APP_LIST_FILE" | sed 's/.*"alias"[ ]*:[ ]*"\([^"]*\)".*/\1/' | grep -vE 'pkm|nano |~|/|^$')
    # Always add extra utilities to the install list if not present
    for util in neofetch btop ncdu lsd bat exa fzf ripgrep fd jq tree tldr curl wget unzip zip ranger; do
        if ! echo "$APPS_TO_INSTALL" | grep -qw "$util"; then
            APPS_TO_INSTALL="$APPS_TO_INSTALL $util"
        fi
    done
    for app in $APPS_TO_INSTALL; do
        if ! command -v "$app" >/dev/null 2>&1; then
            echo "Installing $app..."
            if [ "$app" = "npm" ]; then
                # Try to install npm (and node if needed)
                if command -v apt-get >/dev/null 2>&1; then
                    sudo apt-get install -y npm
                elif command -v dnf >/dev/null 2>&1; then
                    sudo dnf install -y npm
                elif command -v yum >/dev/null 2>&1; then
                    sudo yum install -y npm
                elif command -v pacman >/dev/null 2>&1; then
                    sudo pacman -Sy --noconfirm npm
                elif command -v zypper >/dev/null 2>&1; then
                    sudo zypper install -y npm
                elif command -v apk >/dev/null 2>&1; then
                    sudo apk add npm
                elif command -v brew >/dev/null 2>&1; then
                    brew install npm
                elif command -v pkg >/dev/null 2>&1; then
                    sudo pkg install -y npm
                else
                    echo "Please install npm manually."
                fi
                # After npm install, install cli-pride-flags globally
                if command -v npm >/dev/null 2>&1; then
                    echo "Installing cli-pride-flags globally with npm..."
                    sudo npm i -g cli-pride-flags || npm i -g cli-pride-flags
                fi
            else
                if command -v apt-get >/dev/null 2>&1; then
                    sudo apt-get install -y "$app"
                elif command -v dnf >/dev/null 2>&1; then
                    sudo dnf install -y "$app"
                elif command -v yum >/dev/null 2>&1; then
                    sudo yum install -y "$app"
                elif command -v pacman >/dev/null 2>&1; then
                    sudo pacman -Sy --noconfirm "$app"
                elif command -v zypper >/dev/null 2>&1; then
                    sudo zypper install -y "$app"
                elif command -v apk >/dev/null 2>&1; then
                    sudo apk add "$app"
                elif command -v brew >/dev/null 2>&1; then
                    brew install "$app"
                elif command -v pkg >/dev/null 2>&1; then
                    sudo pkg install -y "$app"
                else
                    echo "Please install $app manually."
                fi
            fi
        else
            echo "$app already installed."
        fi
    done
fi

# All Aero files, configs, and binaries will be stored in /aero

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
        # Add alias for aero in /aero
        echo 'alias aero="/aero/aero"' >> "$shellrc"
    fi
done

# Remove any existing fish function for aero
if [ -d "$HOME/.config/fish/functions" ]; then
    rm -f "$HOME/.config/fish/functions/aero.fish"
    echo -e "function aero\n    /aero/aero\nend" > "$HOME/.config/fish/functions/aero.fish"
fi

# Ensure the binary is executable
chmod +x aero
cp -f aero /aero/aero
chmod +x /aero/aero

# Copy app-list.txt to /aero, or create a default one if missing
mkdir -p /aero
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

# For fish shell
if [ -d "$HOME/.config/fish" ]; then
    # Add PATH and alias to config.fish if not present
    if ! grep -q '/aero' "$HOME/.config/fish/config.fish" 2>/dev/null; then
        echo 'set -gx PATH /aero $PATH' >> "$HOME/.config/fish/config.fish"
    fi
fi

echo
echo "Aero installed! You may need to open a new terminal window for the command to work."
echo 'If you still see "Unknown Command: aero", log out and back in, or run: export PATH="/aero:$PATH"'
echo
echo "Troubleshooting:"
echo "- If you see 'Failed to load app-list.txt':"
echo "    1. Make sure /aero/app-list.txt exists:"
echo "         ls -l /aero/app-list.txt"
echo "    2. If missing, re-run the installer."
echo "    3. Make sure you are running the latest aero binary:"
echo "         which aero"
echo "         ls -l /aero/aero"
echo "    4. If you built manually, run:"
echo "         cd /aero/.aero-src/src && make && cp aero /aero/aero"
echo "    5. Try running 'aero' from your home directory."
