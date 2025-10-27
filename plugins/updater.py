__PLUGIN_VERSION__ = "1.4.1"

import os
import ssl
import sys
import urllib.request
import json
import shutil
import subprocess

# Import core library functions
import config_manager as cm
from constants import AERO_DIR, PLUGINS_DIR, __AERO_VERSION__
# Note: REPO_ROOT_URL is needed for full update logic, assume it's imported in constants
# For now, hardcode API URLs as they were in the original snippet, but should ideally use constants

VERSIONS_API = "https://api.github.com/repos/nebuff/aero/contents/versions"
RAW_BASE_URL = "https://raw.githubusercontent.com/nebuff/aero/main/versions"
PLUGINS_API = "https://api.github.com/repos/nebuff/aero/contents/plugins"
PLUGINS_RAW_URL = "https://raw.githubusercontent.com/nebuff/aero/main/plugins"

# --- Utility Functions ---

def list_versions():
    """Lists available Aero versions from the GitHub API."""
    context = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(VERSIONS_API, context=context) as response:
            data = json.loads(response.read().decode())
            versions = [item['name'] for item in data if item['type'] == 'file' and item['name'].endswith('.sh')]
            # Remove '.sh' extension for display
            return [v[:-3] for v in versions]
    except Exception as e:
        cm.print_colored(f"Error listing versions: {e}", "error")
        return []

def list_remote_plugins():
    """Lists all plugin files available in the remote repository."""
    context = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(PLUGINS_API, context=context) as response:
            data = json.loads(response.read().decode())
            return [item['name'] for item in data if item['type'] == 'file' and item['name'].endswith('.py')]
    except Exception as e:
        cm.print_colored(f"Error listing remote plugins: {e}", "error")
        return []

def update_aero_core(version):
    """Downloads and replaces the main 'aero' executable with a specific version."""
    cm.print_colored(f"Starting core update to version {version}...", "info")
    
    # Note: This is an incomplete function as the core update logic is complex, 
    # but the structure is preserved for the new standard.
    
    # 1. Download the new version installer
    raw_url = f"{RAW_BASE_URL}/{version}.sh"
    temp_installer_path = os.path.join(AERO_DIR, f"temp_{version}.sh")
    
    cm.print_colored(f"Fetching installer from {raw_url}", "info")
    try:
        context = ssl._create_unverified_context()
        urllib.request.urlretrieve(raw_url, temp_installer_path, context=context)
        os.chmod(temp_installer_path, 0o755)
    except Exception as e:
        cm.print_colored(f"Failed to download installer: {e}", "error")
        return
        
    cm.print_colored("Installer downloaded. Running update script...", "warning")
    
    try:
        # Execute the new installer script to replace core files
        # NOTE: Running an external script within a shell command can be tricky.
        # This assumes the script handles file replacement safely.
        subprocess.run([sys.executable, temp_installer_path], check=True, cwd=AERO_DIR)
        
        cm.print_colored(f"Aero successfully updated to {version}.", "success")
        cm.print_colored("Please restart the shell to use the new version.", "warning")
        
    except subprocess.CalledProcessError as e:
        cm.print_colored(f"Update script failed with return code {e.returncode}.", "error")
    except Exception as e:
        cm.print_colored(f"Error executing update script: {e}", "error")
    finally:
        # Clean up the temporary installer
        if os.path.exists(temp_installer_path):
            os.remove(temp_installer_path)


def update_plugin(plugin_name):
    """Downloads and replaces a single plugin file."""
    plugin_file = f"{plugin_name}.py"
    raw_url = f"{PLUGINS_RAW_URL}/{plugin_file}"
    local_path = os.path.join(PLUGINS_DIR, plugin_file)
    
    cm.print_colored(f"Updating plugin '{plugin_name}'...", "info")
    
    try:
        context = ssl._create_unverified_context()
        urllib.request.urlretrieve(raw_url, local_path, context=context)
        cm.print_colored(f"Plugin '{plugin_name}' updated successfully!", "success")
    except Exception as e:
        cm.print_colored(f"Failed to update plugin '{plugin_name}': {e}", "error")


def update_all_plugins():
    """Download and update all plugins from GitHub"""
    cm.print_colored("Updating all Aero plugins...", "data_primary")
    plugins = list_remote_plugins()
    if not plugins:
        cm.print_colored("No plugins found in the remote repository.", "error")
        return

    for plugin_file in plugins:
        plugin_name = plugin_file[:-3]  # strip .py
        update_plugin(plugin_name)
        
    cm.print_colored("All plugins updated! Restart Aero or run 'refresh' to reload them.", "success")


# ---------- Main Update Command ----------
def update_cmd(args):
    """Update Aero or its plugins"""
    if args and args[0] in ("help", "-h", "--help"):
        print_help()
        return

    if not args or args[0] == "check":
        # No args or 'check': show available Aero versions
        versions = list_versions()
        if not versions:
            cm.print_colored("No versions found in repository.", "error")
            return

        cm.print_colored("Available Aero Versions (Current: {cm.colorize(__AERO_VERSION__, 'success')}):", "header")
        for v in versions:
            cm.print_colored(f"  - {v}", "info")
        
        if args and args[0] == "check":
            return
            
        print()
        cm.print_colored("Type the version name you want to install (e.g. aero-beta-2.1.3):", "data_primary")
        selected = input("> ").strip()
        if not selected:
            cm.print_colored("Update cancelled.", "warning")
            return
        
        if selected in versions:
            update_aero_core(selected)
        else:
            cm.print_colored(f"Error: Unknown version '{selected}'.", "error")

    elif args[0].lower() == "plugins":
        update_all_plugins()
        
    elif args[0].lower() == "plugin" and len(args) > 1:
        update_plugin(args[1])
        
    elif len(args) == 1 and args[0].startswith("aero-"):
        # Specific version requested
        update_aero_core(args[0])
        
    else:
        cm.print_colored(f"Unknown update command or arguments: {' '.join(args)}", "error")
        print_help()


# ---------- Utility ----------
def print_help():
    """Displays help for the updater command."""
    cm.print_colored("Aero Update Command Help:", "subheader")
    help_text = {
        "update": "List available versions and update interactively.",
        "update <version>": "Install a specific core version (e.g. aero-beta-2.1.3).",
        "update check": "Show available versions only.",
        "update plugins": "Update all installed plugins.",
        "update plugin <name>": "Update a specific plugin (e.g. update plugin color).",
    }
    
    for cmd, desc in help_text.items():
        print(f"  {cm.colorize(cmd, 'data_primary'):<25} - {desc}")

def register_plugin_commands(COMMANDS):
    """Registers the 'update' command."""
    COMMANDS["update"] = update_cmd
