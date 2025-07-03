# Aero App Center (TUI)

Aero is a terminal-based App Center for any computer with a shell. **All Aero data, configs, binaries, and package manager are stored in `/aero` on your drive.** Navigate with arrow keys, select with Enter, and quit with 'q'.


## Features
- TUI interface (ncurses)
- App browsing and selection
- Minimal dependencies
- Easy install via curl
- Auto-installs popular terminal apps and utilities (htop, nano, cmus, mpv, ranger, neofetch, btop, ncdu, lsd, bat, exa, fzf, ripgrep, fd, jq, tree, tldr, curl, wget, unzip, zip, etc.)
- Built-in package manager (pkm, stored in `/aero/pkm-main`)
- NPM support (installs npm and cli-pride-flags)
- Discord (TUI) client (Discordo, if Go is installed)
- Color and navigation customization


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
cp aero /aero/aero
```

## Usage
```sh
aero
```

**If you see 'command not found', add `/aero` to your PATH or use the provided alias.**



## App List Format & Data Location

All Aero data, configs, binaries, and package manager are stored in `/aero` at the root of your drive. This includes:

- `/aero/aero` (main binary)
- `/aero/app-list.txt` (JSON app list and settings)
- `/aero/pkm-main/` (built-in package manager)
- `/aero/pkm` (symlink to package manager)
- `/aero/.src/` (source code, if installed from git)

The app list is stored as a JSON file (`/aero/app-list.txt`) with entries like:
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

You can add or remove apps by editing `/aero/app-list.txt`.


### Special Notes
- If Go is installed, Discordo (TUI Discord client) will be built and installed automatically.
- NPM and the global package `cli-pride-flags` are installed if missing.
- Neofetch is always installed for system info.
- **All Aero files, configs, and binaries are in `/aero` (not in $HOME, /usr/local, or elsewhere).**

### Aero Data Location

**Everything Aero uses is now in `/aero`!**

- To launch: add `/aero` to your `PATH` (e.g. `export PATH="/aero:$PATH"`)
- To edit the app list: `nano /aero/app-list.txt`
- To update: run the installer again, or replace `/aero/aero`
- To use the package manager: run `pkm` (symlinked in `/aero`)

No files are stored in your home directory or `/usr/local`.

## License
MIT
