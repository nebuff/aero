__PLUGIN_VERSION__ = "1.2.0"

import os
import urllib.request
import ssl
import subprocess
import sys

# ANSI color codes
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_RED = "\033[31m"
COLOR_CYAN = "\033[36m"

def update_cmd(args):
    """Update Aero to the latest version"""
    if args and args[0] == "help":
        print(f"{COLOR_YELLOW}Update Command Help:{COLOR_RESET}")
        print(f"  {COLOR_GREEN}update{COLOR_RESET}        - Update Aero to the latest version")
        print(f"  {COLOR_GREEN}update check{COLOR_RESET}  - Check for updates without installing")
        print(f"  {COLOR_GREEN}update help{COLOR_RESET}   - Show this help")
        return
    
    if args and args[0] == "check":
        check_for_updates()
        return
    
    print(f"{COLOR_YELLOW}Checking for Aero updates...{COLOR_RESET}")
    
    try:
        # Get the current Aero directory
        aero_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        aero_script = os.path.join(aero_dir, "aero")
        
        # Download the latest version
        url = "https://raw.githubusercontent.com/nebuff/aero/main/aero"
        context = ssl._create_unverified_context()
        
        print(f"{COLOR_CYAN}Downloading latest version...{COLOR_RESET}")
        with urllib.request.urlopen(url, context=context) as response:
            new_content = response.read().decode()
        
        # Backup current version
        backup_file = f"{aero_script}.backup"
        with open(aero_script, 'r') as f:
            current_content = f.read()
        
        with open(backup_file, 'w') as f:
            f.write(current_content)
        
        # Write new version
        with open(aero_script, 'w') as f:
            f.write(new_content)
        
        # Make executable
        os.chmod(aero_script, 0o755)
        
        print(f"{COLOR_GREEN}Aero has been updated successfully!{COLOR_RESET}")
        print(f"{COLOR_YELLOW}Backup saved as: {backup_file}{COLOR_RESET}")
        print(f"{COLOR_CYAN}Use 'refresh' command to reload or restart Aero to see changes.{COLOR_RESET}")
        
    except Exception as e:
        print(f"{COLOR_RED}Failed to update Aero: {e}{COLOR_RESET}")

def check_for_updates():
    """Check if updates are available"""
    try:
        # This is a simplified check - in a real implementation you'd compare versions
        print(f"{COLOR_CYAN}Checking for updates...{COLOR_RESET}")
        url = "https://api.github.com/repos/nebuff/aero/commits/main"
        context = ssl._create_unverified_context()
        
        with urllib.request.urlopen(url, context=context) as response:
            import json
            data = json.loads(response.read().decode())
            
        commit_date = data['commit']['committer']['date']
        commit_msg = data['commit']['message']
        
        print(f"{COLOR_GREEN}Latest commit:{COLOR_RESET}")
        print(f"  Date: {commit_date}")
        print(f"  Message: {commit_msg}")
        
    except Exception as e:
        print(f"{COLOR_RED}Failed to check for updates: {e}{COLOR_RESET}")

def register(commands):
    """Register the update command with Aero"""
    commands['update'] = update_cmd
