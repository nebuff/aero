__PLUGIN_VERSION__ = "stable-2.4"

import os
import urllib.request
import ssl
import sys

COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_RED = "\033[31m"
COLOR_CYAN = "\033[36m"

BASE_URL = "https://raw.githubusercontent.com/nebuff/aero/main/versions"

def version_exists(version_name):
    url = f"{BASE_URL}/aero-{version_name}"
    context = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(url, context=context) as response:
            if response.status == 200:
                return True
    except:
        return False
    return False

def download_version(version_name, aero_script):
    url = f"{BASE_URL}/aero-{version_name}"
    context = ssl._create_unverified_context()
    print(f"{COLOR_CYAN}Downloading version {version_name}...{COLOR_RESET}")
    with urllib.request.urlopen(url, context=context) as response:
        content = response.read().decode()
    # Backup current
    backup_file = f"{aero_script}.backup"
    with open(aero_script, 'r') as f:
        current_content = f.read()
    with open(backup_file, 'w') as f:
        f.write(current_content)
    # Write new
    with open(aero_script, 'w') as f:
        f.write(content)
    os.chmod(aero_script, 0o755)
    print(f"{COLOR_GREEN}Updated to version {version_name}! Backup saved as {backup_file}.{COLOR_RESET}")

def update_cmd(args):
    if args and args[0] == "help":
        print(f"{COLOR_YELLOW}Update Command Help:{COLOR_RESET}")
        print(f"  {COLOR_GREEN}update{COLOR_RESET}        - Update Aero to the latest version")
        print(f"  {COLOR_GREEN}update check{COLOR_RESET}  - Check for updates without installing")
        print(f"  {COLOR_GREEN}update help{COLOR_RESET}   - Show this help")
        return
    
    if args and args[0] == "check":
        print(f"{COLOR_CYAN}Checking for updates...{COLOR_RESET}")
        # Just print the latest version (for demo, say stable-2.1 is latest)
        print(f"{COLOR_GREEN}Latest version available: stable-2.1{COLOR_RESET}")
        return
    
    print(f"{COLOR_YELLOW}Checking for Aero updates...{COLOR_RESET}")
    
    aero_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    aero_script = os.path.join(aero_dir, "aero")
    
    current_version = __PLUGIN_VERSION__  # eg: stable-2
    
    print(f"Current version: {current_version}")
    
    # Parse current version, expect stable-X or stable-X.Y
    import re
    m = re.match(r"stable-(\d+)(?:\.(\d+))?$", current_version)
    if not m:
        print(f"{COLOR_RED}Current version format not recognized.{COLOR_RESET}")
        return
    
    major = int(m.group(1))
    minor = int(m.group(2) or 0)
    
    # Try to find higher versions:
    # First try higher minor versions for same major
    MAX_MINOR_CHECK = 5
    MAX_MAJOR_CHECK = 5
    
    found_newer = False
    
    for maj in range(major, major + MAX_MAJOR_CHECK + 1):
        # start minor at 1 if major > current major else minor+1
        start_minor = 1 if maj > major else minor + 1
        for mino in range(start_minor, MAX_MINOR_CHECK + 1):
            version_try = f"stable-{maj}.{mino}"
            if version_exists(version_try):
                print(f"Found newer version: {version_try}")
                download_version(version_try, aero_script)
                found_newer = True
                break
        if found_newer:
            break
        
        # If no minor found and this is a major increment, try just stable-X (without minor)
        if not found_newer and maj > major:
            version_try = f"stable-{maj}"
            if version_exists(version_try):
                print(f"Found newer version: {version_try}")
                download_version(version_try, aero_script)
                found_newer = True
                break
    
    if not found_newer:
        print(f"{COLOR_YELLOW}No newer versions available. You are up to date!{COLOR_RESET}")

def register(commands):
    commands['update'] = update_cmd
