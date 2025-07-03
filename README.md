# Aero Shell

Aero is a blazing-fast, cross-platform shell for Linux, macOS, and Windows, written in C. It features a modern component/add-on system, customizable prompts, and a simple installer for instant setup.

## Quick Start

1. **Run the installer:**
   ```sh
   curl -fsSL https://raw.githubusercontent.com/nebuff/aero/main/install.sh | sh
   ```
   This will:
   - Install a C compiler (if needed)
   - Download and build Aero
   - Download all official Aero components
   - Add the `aero` command to your shell (Bash, Zsh, Fish, PowerShell)

2. **Start Aero:**
   ```sh
   aero
   ```

## Features
- Fast, native C shell
- Built-in commands: `cd`, `ls`, `mkdir`, `rmdir`, `rm`, `touch`, `cat`, `pwd`, `echo`, `clear`, and more
- Component system: extend Aero with add-ons (like plugins)
- Customizable prompt (like Fish's tide)
- Easy to install and update

## Project Structure
- `src/`         — Shell source code
- `components/`  — Official Aero components (add-ons)
- `install.sh`   — One-step installer script

## Components
- Add-ons live in `components/` and can be listed/used with `list` and `run <component>` inside Aero.
- Example: `aero run hello_world` or `aero run set_prompt "[\u@\h \w]$ "`

## License
MIT
