__PLUGIN_VERSION__ = "1.3.1"

import os
import tempfile
import subprocess

# ANSI color codes
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_RED = "\033[31m"

def nano_cmd(args):
    """Simple text editor command"""
    if not args:
        print(f"{COLOR_RED}nano: missing filename{COLOR_RESET}")
        return
    
    filename = args[0]
    
    try:
        # Try to use system nano first
        if subprocess.run(['which', 'nano'], capture_output=True).returncode == 0:
            subprocess.run(['nano', filename])
        else:
            # Fallback to basic editing
            print(f"{COLOR_YELLOW}System nano not found. Using basic editor.{COLOR_RESET}")
            basic_edit(filename)
    except Exception as e:
        print(f"{COLOR_RED}nano: {e}{COLOR_RESET}")

def basic_edit(filename):
    """Basic text editor when nano is not available"""
    lines = []
    
    # Read existing file if it exists
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                lines = f.read().splitlines()
            print(f"{COLOR_GREEN}Loaded {len(lines)} lines from {filename}{COLOR_RESET}")
        except Exception as e:
            print(f"{COLOR_RED}Error reading file: {e}{COLOR_RESET}")
            return
    else:
        print(f"{COLOR_YELLOW}Creating new file: {filename}{COLOR_RESET}")
    
    print(f"{COLOR_CYAN}Basic Editor - Enter text (type 'EOF' on a new line to save and exit):{COLOR_RESET}")
    
    while True:
        try:
            line = input()
            if line == "EOF":
                break
            lines.append(line)
        except KeyboardInterrupt:
            print(f"\n{COLOR_YELLOW}Edit cancelled{COLOR_RESET}")
            return
    
    # Save the file
    try:
        with open(filename, 'w') as f:
            f.write('\n'.join(lines))
        print(f"{COLOR_GREEN}Saved {len(lines)} lines to {filename}{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_RED}Error saving file: {e}{COLOR_RESET}")

def register(commands):
    """Register the nano command with Aero"""
    commands['nano'] = nano_cmd
