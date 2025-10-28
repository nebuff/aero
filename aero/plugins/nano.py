__PLUGIN_VERSION__ = "1.3.1"

import os
import subprocess

# Import core library functions
import config_manager as cm

def nano_cmd(args):
    """Simple text editor command"""
    if not args:
        cm.print_colored("nano: missing filename", "error")
        return

    filename = args[0]

    try:
        # Try to use system nano first
        if subprocess.run(['which', 'nano'], capture_output=True).returncode == 0:
            subprocess.run(['nano', filename])
        else:
            # Fallback to basic editing
            cm.print_colored("System nano not found. Using basic editor.", "warning")
            basic_edit(filename)
    except Exception as e:
        cm.print_colored(f"nano: {e}", "error")

def basic_edit(filename):
    """Basic text editor when nano is not available"""
    lines = []

    # Read existing file if it exists
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                lines = f.read().splitlines()
            cm.print_colored(f"Loaded {len(lines)} lines from {filename}", "success")
        except Exception as e:
            cm.print_colored(f"Error reading file: {e}", "error")
            return
    else:
        cm.print_colored(f"Creating new file: {filename}", "warning")

    cm.print_colored("Basic Editor - Enter text (type 'EOF' on a new line to save and exit):", "data_primary")

    while True:
        try:
            line = input()
            if line == "EOF":
                break
            lines.append(line)
        except KeyboardInterrupt:
            cm.print_colored("\nEdit cancelled", "warning")
            return

    # Save the file
    try:
        with open(filename, 'w') as f:
            f.write('\n'.join(lines))
        cm.print_colored(f"Saved {len(lines)} lines to {filename}", "success")
    except Exception as e:
        cm.print_colored(f"Error saving file: {e}", "error")

def register_plugin_commands(COMMANDS):
    """Registers the 'nano' command."""
    COMMANDS["nano"] = nano_cmd
