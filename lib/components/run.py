__COMPONENT_VERSION__ = "1.0.0"
__COMPONENT_NAME__ = "run"
__COMPONENT_DESCRIPTION__ = "Execute files and scripts - alternative to ./ prefix"

import os
import subprocess
import sys

def run_cmd(args):
    """Execute a file or script - like the . command in other shells"""
    if not args:
        print(f"{COLOR_RED}run: missing filename{COLOR_RESET}")
        print(f"{COLOR_YELLOW}Usage: run <filename> [arguments...]{COLOR_RESET}")
        print(f"{COLOR_CYAN}Example: run install.sh{COLOR_RESET}")
        return
    
    filename = args[0]
    script_args = args[1:] if len(args) > 1 else []
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"{COLOR_RED}run: {filename}: No such file or directory{COLOR_RESET}")
        return
    
    # Check if file is executable
    if not os.access(filename, os.X_OK):
        print(f"{COLOR_YELLOW}run: {filename} is not executable. Making it executable...{COLOR_RESET}")
        try:
            os.chmod(filename, 0o755)
            print(f"{COLOR_GREEN}Made {filename} executable{COLOR_RESET}")
        except Exception as e:
            print(f"{COLOR_RED}run: Failed to make {filename} executable: {e}{COLOR_RESET}")
            return
    
    # Prepare the command
    if filename.startswith('./'):
        # Already has ./ prefix
        cmd = [filename] + script_args
    elif filename.startswith('/'):
        # Absolute path
        cmd = [filename] + script_args
    else:
        # Relative path - add ./
        cmd = [f'./{filename}'] + script_args
    
    try:
        print(f"{COLOR_CYAN}Running: {' '.join(cmd)}{COLOR_RESET}")
        
        # Execute the command
        result = subprocess.run(cmd, check=False)
        
        # Report exit status
        if result.returncode == 0:
            print(f"{COLOR_GREEN}Command completed successfully{COLOR_RESET}")
        else:
            print(f"{COLOR_YELLOW}Command exited with code {result.returncode}{COLOR_RESET}")
            
    except FileNotFoundError:
        print(f"{COLOR_RED}run: {filename}: command not found{COLOR_RESET}")
    except PermissionError:
        print(f"{COLOR_RED}run: {filename}: Permission denied{COLOR_RESET}")
    except KeyboardInterrupt:
        print(f"\n{COLOR_YELLOW}Interrupted by user{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_RED}run: Error executing {filename}: {e}{COLOR_RESET}")

def register(commands):
    """Register the run command with Aero"""
    commands['run'] = run_cmd
