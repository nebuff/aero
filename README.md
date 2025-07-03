# Aero App Center (TUI)

Aero is a terminal-based App Center for any computer with a shell. Navigate with arrow keys, select with Enter, and quit with 'q'.

## Features
- TUI interface (ncurses)
- App browsing and selection
- Minimal dependencies
- Easy install via curl

## Install (One-liner)
```sh
curl -fsSL https://raw.githubusercontent.com/yourrepo/aero-installer.sh | sh
```

## Build Manually
```sh
sudo apt-get install libncurses5-dev  # or brew install ncurses on macOS
cd src
make
sudo cp aero /usr/local/bin/
```

## Usage
```
aero
```

## License
MIT
