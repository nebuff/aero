#!/bin/sh
# Aero Installer Script
set -e

# Detect OS and install ncurses if needed
if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y build-essential libncurses5-dev curl git
elif command -v brew >/dev/null 2>&1; then
    brew install ncurses
else
    echo "Please install ncurses development libraries manually."
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
