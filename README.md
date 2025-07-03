# Aero App Center (TUI)

Aero is a terminal-based App Center for any computer with a shell. Navigate with arrow keys, select with Enter, and quit with 'q'.


## Features
- TUI interface (ncurses)
- App browsing and selection
- Minimal dependencies
- Easy install via curl
- Auto-installs popular terminal apps (htop, nano, cmus, mpv, ranger, neofetch, etc.)
- Built-in package manager (pkm)
- NPM support (installs npm and cli-pride-flags)
- Discord (TUI) client (Discordo, if Go is installed)
- Color and navigation customization


## Install (One-liner)
```sh
sudo curl -fsSL https://raw.githubusercontent.com/nebuff/aero/refs/heads/main/install.sh | sh
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
  {"name": "Resource Monitor", "alias": "htop"},
  {"name": "NPM Package Manager", "alias": "npm"},
  {"name": "NeoFetch", "alias": "neofetch"},
  {"name": "Discord (TUI)", "alias": "discordo"},
  {"name": "Pride Flag", "alias": "cli-pride-flags"}
]
```

You can add or remove apps by editing `app-list.txt`.

### Special Notes
- If Go is installed, Discordo (TUI Discord client) will be built and installed automatically.
- NPM and the global package `cli-pride-flags` are installed if missing.
- Neofetch is always installed for system info.

## License
MIT
