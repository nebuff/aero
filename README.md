# Aero App Center (TUI)

Aero is a terminal-based App Center for any computer with a shell. Navigate with arrow keys, select with Enter, and quit with 'q'.

## Features
- TUI interface (ncurses)
- App browsing and selection
- Minimal dependencies
- Easy install via curl

## Install (One-liner)
```sh
curl -fsSL https://raw.githubusercontent.com/nebuff/aero/refs/heads/main/install.sh | sh
```

## Build Manually
```sh
# Install dependencies
sudo apt-get install libncurses5-dev git curl build-essential  # or: brew install ncurses git curl on macOS

# Clone and build
git clone https://github.com/nebuff/aero.git
cd aero/src
make
sudo cp aero /usr/local/bin/
```

## Usage
```sh
aero
```

## App List Format
The app list is stored as a JSON file (`app-list.txt`) with entries like:
```json
[
  {"name": "Text Editor", "alias": "nano"},
  {"name": "Resource Monitor", "alias": "htop"}
]
```

## License
MIT
