__PLUGIN_VERSION__ = "2.0.1"

import os
import ssl
import sys
import urllib.request
import json
import shutil
import time

# --- Dynamic Core Imports (Relies on constants/functions defined in the main 'aero' script) ---
try:
    # Ensure the core script's directory is in path (it should be, but this adds robustness)
    AERO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(AERO_DIR)
    
    # Import utility functions and constants from the main 'aero' file
    from aero import (
        print_colored, LATEST_AERO_URL, REPO_ROOT_URL, PLUGINS_DIR, 
        LIB_DIR, REPO_PLUGINS_URL, REPO_LIBS_URL, 
        COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_CYAN, COLOR_RESET
    )

    # Use the GitHub API base for listing files
    GH_API_BASE = "https://api.github.com/repos/nebuff/aero/contents"

except ImportError as e:
    # Fallback/Error state if running outside the intended environment
    print(f"Error in updater.py import: {e}. Check main 'aero' file structure.")
    # Exit or define minimal constants to prevent crash (omitted for brevity here)


# ---------- Utility Functions ----------

def _fetch_github_dir_list(path_suffix):
    """Fetches a list of files in a directory via GitHub API."""
    url = f"{GH_API_BASE}/{path_suffix}"
    try:
        # Disable SSL verification for simple setup
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(url, context=context) as resp:
            data = json.loads(resp.read().decode())
            # Filter for Python files
            return [item['name'] for item in data if item['type'] == 'file' and item['name'].endswith('.py')]
    except Exception as e:
        print_colored(f"Error fetching directory list from {url}: {e}", "error")
        return []

def list_remote_plugins():
    """List all available plugins from the remote repository."""
    return _fetch_github_dir_list("plugins")

def list_remote_libs():
    """List all available lib files from the remote repository."""
    return _fetch_github_dir_list("lib")


def download_file(url, destination_path):
    """Downloads a file from a URL to a specified path."""
    try:
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(url, context=context) as response, open(destination_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        return True
    except Exception as e:
        print_colored(f"Error downloading {url}: {e}", "error")
        return False

# ---------- Update Logic Functions ----------

def update_aero_core(prompt_for_confirmation=True):
    """Downloads and replaces the main aero executable."""
    if prompt_for_confirmation:
        confirm = input(f"{COLOR_YELLOW}Are you sure you want to update the core Aero executable? (y/n): {COLOR_RESET}").strip().lower()
        if confirm != 'y':
            print_colored("Core update cancelled.", "warning")
            return False
    
    print_colored(f"Downloading latest Aero core from {LATEST_AERO_URL}...", "info")
    aero_path = os.path.join(AERO_DIR, 'aero')
    temp_file = os.path.join(AERO_DIR, 'aero.new')
    
    if download_file(LATEST_AERO_URL, temp_file):
        try:
            shutil.move(temp_file, aero_path)
            os.chmod(aero_path, 0o755) # Make it executable
            print_colored("Aero core updated successfully! Please restart Aero.", "success")
            return True
        except Exception as e:
            print_colored(f"Failed to replace old core file: {e}", "error")
            os.remove(temp_file) # Clean up temp file
            return False
    else:
        print_colored("Core update failed.", "error")
        return False

def update_lib(lib_name):
    """Update a single library file from the remote repository."""
    lib_file = f"{lib_name}.py"
    remote_url = f"{REPO_LIBS_URL}/{lib_file}"
    local_path = os.path.join(LIB_DIR, lib_file)
    
    print_colored(f"Updating lib file: {lib_file}...", "info")
    os.makedirs(LIB_DIR, exist_ok=True)
    
    if download_file(remote_url, local_path):
        print_colored(f"Library '{lib_name}' updated successfully!", "success")
        return True
    else:
        print_colored(f"Failed to update library '{lib_name}'.", "error")
        return False

def update_all_libs():
    """Download and update all lib files from GitHub."""
    print_colored(f"Updating all Aero libraries in {LIB_DIR}...", "cyan")
    libs = list_remote_libs()
    if not libs:
        print_colored(f"No library files found in the remote repository.", "warning")
        return False
        
    success_count = 0
    for lib_file in libs:
        lib_name = lib_file[:-3] # strip .py
        if update_lib(lib_name):
            success_count += 1
            
    print_colored(f"Finished updating libraries. {success_count}/{len(libs)} updated successfully.", "green")
    return success_count == len(libs)


def update_plugin(plugin_name):
    """Download and update a single plugin from the remote repository."""
    plugin_file = f"{plugin_name}.py"
    remote_url = f"{REPO_PLUGINS_URL}/{plugin_file}"
    local_path = os.path.join(PLUGINS_DIR, plugin_file)
    
    print_colored(f"Updating plugin file: {plugin_file}...", "info")
    os.makedirs(PLUGINS_DIR, exist_ok=True)
    
    if download_file(remote_url, local_path):
        print_colored(f"Plugin '{plugin_name}' updated successfully!", "success")
        return True
    else:
        print_colored(f"Failed to update plugin '{plugin_name}'.", "error")
        return False

def update_all_plugins():
    """Download and update all plugins from GitHub"""
    print_colored(f"Updating all official Aero plugins in {PLUGINS_DIR}...", "cyan")
    plugins = list_remote_plugins()
    if not plugins:
        print_colored(f"No official plugins found in the remote repository.", "warning")
        return False
        
    success_count = 0
    for plugin_file in plugins:
        plugin_name = plugin_file[:-3]  # strip .py
        if update_plugin(plugin_name):
            success_count += 1

    print_colored(f"Finished updating plugins. {success_count}/{len(plugins)} updated successfully. Run 'refresh' to reload them.", "green")
    return success_count == len(plugins)


def reinstall_no_config():
    """Reinstalls core, libs, and plugins while preserving configuration, themes, and existing plugins."""
    print_colored("--- Full Reinstallation (Preserving Configs, Plugins, Themes) ---", "header")
    print_colored("This will update the Aero core executable, all libraries, and all official plugins. Your config.json and custom files will be kept.", "warning")
    
    confirm = input(f"{COLOR_YELLOW}Proceed with full reinstall? (y/n): {COLOR_RESET}").strip().lower()
    if confirm != 'y':
        print_colored("Reinstallation cancelled.", "info")
        return

    # 1. Update Core (No prompt needed here)
    print_colored("\n--- Updating Aero Core ---", "subheader")
    update_aero_core(prompt_for_confirmation=False)

    # 2. Update Libraries
    print_colored("\n--- Updating Libraries ---", "subheader")
    update_all_libs()

    # 3. Update All Plugins (to update official plugins)
    print_colored("\n--- Updating Official Plugins ---", "subheader")
    update_all_plugins()
    
    print_colored("\nReinstallation complete! Please restart Aero to load the new core and libraries.", "success")


# ---------- Main Update Command ----------
def update_cmd(args):
    """Update Aero, its plugins, or libraries."""
    
    # --- NO ARGUMENTS: Default Update (Core + Libs) ---
    if not args:
        print_colored("--- Aero Core and Library Update ---", "header")
        print_colored("This will update the main 'aero' executable and all files in the 'lib/' directory.", "info")
        if update_aero_core():
            update_all_libs()
        return

    subcommand = args[0].lower()
    
    if subcommand in ("help", "-h", "--help"):
        print_help()
        return

    # --- Reinstall Command ---
    elif subcommand == "reinstall":
        reinstall_no_config()
        return

    # --- Core Command ---
    elif subcommand == "core":
        print_colored("--- Aero Core Update Only ---", "header")
        update_aero_core()
        return

    # --- Library Commands ---
    elif subcommand == "lib":
        if len(args) > 1:
            # update lib <name>: Update a specific library
            lib_name = args[1]
            print_colored(f"--- Updating specific library: {lib_name} ---", "header")
            update_lib(lib_name)
        else:
            # update lib: Update all libraries
            print_colored("--- Updating All Libraries ---", "header")
            update_all_libs()
        return
        
    # --- Plugin Commands ---
    elif subcommand == "plugins":
        update_all_plugins()
        return
        
    elif subcommand == "plugin":
        if len(args) < 2:
            print_colored("Usage: update plugin <name>", "error")
            return
        update_plugin(args[1])
        return

    # --- Fallback ---
    else:
        print_colored(f"Unknown update command: '{subcommand}'.", "error")
        print_colored("Run 'update help' for available options.", "info")
        return


# ---------- Help Function ----------
def print_help():
    print(f"{COLOR_YELLOW}Aero Update Command Help:{COLOR_RESET}")
    print(f"  {COLOR_GREEN}update{COLOR_RESET}             - Update the main core executable AND all libraries ('lib/') after confirmation.")
    print(f"  {COLOR_GREEN}update core{COLOR_RESET}        - Update ONLY the main core executable ('aero').")
    print(f"  {COLOR_GREEN}update lib [name]{COLOR_RESET}  - Update all libraries, or a specific library (e.g., 'update lib config_manager').")
    print(f"  {COLOR_GREEN}update plugins{COLOR_RESET}     - Update all official plugins to their latest remote versions.")
    print(f"  {COLOR_GREEN}update plugin <name>{COLOR_RESET} - Update a specific plugin (e.g. 'update plugin color').")
    print(f"  {COLOR_GREEN}update reinstall{COLOR_RESET}   - Reinstall core, libs, and plugins, preserving config/themes/custom plugins.")


def register(COMMANDS):
    COMMANDS["update"] = update_cmd
