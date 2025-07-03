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
sudo cp aero /usr/local/bin/

echo "\nAero installed! Run 'aero' to start."
