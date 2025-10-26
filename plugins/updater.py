__PLUGIN_VERSION__ = "1.4.0"

import os
import ssl
import sys
import urllib.request
import json
import shutil

# ANSI colors
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_RED = "\033[31m"
COLOR_CYAN = "\033[36m"

VERSIONS_API = "https://api.github.com/repos/nebuff/aero/contents/versions"
RAW_BASE_URL = "https://raw.githubusercontent.com/nebuff/aero/main/versions"
PLUGINS_API = "https://api.github.com/repos/nebuff/aero/contents/plugins"
PLUGINS_RAW_URL = "https://raw.githubusercontent.com/nebuff/aero/main/plugins"


# ---------- Main Update Command ----------
def update_cmd(args):
    """Update Aero or its plugins"""
    if args and args[0] == "help":
        print_help()
        return

    if not args:
        # No args: show available Aero versions
        versions = list_versions()
        if not versions:
            print(f"{COLOR_RED}No versions found in repository.{COLOR_RESET}")
            return

        print()
        print(f"{COLOR_YELLOW}Type the version name you want to install (e.g. aero-beta-2.1.3):{COLOR_RESET}")
        selected = input("> ").strip()
        if not selected:
            print(f"{COLOR_RED}Update cancelled.{COLOR_RESET}")
            return

        update_to_version(selected)
        return

    # Handle subcommands
    sub = args[0].lower()
    if sub == "check":
        list_versions(show_only=True)
    elif sub == "plugins":
        update_all_plugins()
    elif sub == "plugin" and len(args) > 1:
        update_plugin(args[1])
    else:
        # Maybe a version name
        update_to_version(sub)


# ---------- Helpers for Updating Aero ----------
def list_versions(show_only=False):
    """Fetch and list available Aero versions from GitHub"""
    print(f"{COLOR_CYAN}Checking available Aero versions...{COLOR_RESET}")
    context = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(VERSIONS_API, context=context) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"{COLOR_RED}Failed to fetch versions list: {e}{COLOR_RESET}")
        return []

    # Sort and categorize
    versions = [f["name"] for f in data if f["name"].startswith("aero-")]
    pre = [v for v in versions if "pre" in v]
    beta = [v for v in versions if "beta" in v]
    stable = [v for v in versions if "stable" in v]

    print()
    print(f"{COLOR_YELLOW}- Pre Release -{COLOR_RESET}")
    for v in pre or ["(none)"]:
        print(f"  {COLOR_CYAN}{v}{COLOR_RESET}")
    print(f"{COLOR_YELLOW}- Beta -{COLOR_RESET}")
    for v in beta or ["(none)"]:
        print(f"  {COLOR_CYAN}{v}{COLOR_RESET}")
    print(f"{COLOR_YELLOW}- Stable (Recommended) -{COLOR_RESET}")
    for v in stable or ["(none)"]:
        print(f"  {COLOR_CYAN}{v}{COLOR_RESET}")

    if show_only:
        return []
    return versions


def update_to_version(version_name):
    """Download and replace Aero with selected version"""
    print(f"{COLOR_YELLOW}Preparing to install {version_name}...{COLOR_RESET}")

    home = os.path.expanduser("~")
    aero_dir = os.path.join(home, "aero")
    aero_script = os.path.join(aero_dir, "aero")
    plugins_dir = os.path.join(aero_dir, "plugins")
    config_path = os.path.join(aero_dir, "config.json")

    url = f"{RAW_BASE_URL}/{version_name}"
    tmp_path = "/tmp/aero_update_tmp"

    os.makedirs(plugins_dir, exist_ok=True)

    # Download selected version
    try:
        print(f"{COLOR_CYAN}Downloading {url}...{COLOR_RESET}")
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(url, context=context) as resp:
            new_code = resp.read()
        with open(tmp_path, "wb") as f:
            f.write(new_code)
    except Exception as e:
        print(f"{COLOR_RED}Failed to download version: {e}{COLOR_RESET}")
        return

    # Backup current Aero
    backup_path = f"{aero_script}.backup"
    try:
        if os.path.isfile(aero_script):
            shutil.copy2(aero_script, backup_path)
            print(f"{COLOR_GREEN}Backup saved as {backup_path}{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_RED}Failed to backup current Aero: {e}{COLOR_RESET}")

    # Replace executable safely
    try:
        shutil.move(tmp_path, aero_script)
        os.chmod(aero_script, 0o755)
        print(f"{COLOR_GREEN}Aero successfully updated to {version_name}!{COLOR_RESET}")
        print(f"{COLOR_CYAN}Your plugins and config.json have been preserved.{COLOR_RESET}")
        print(f"{COLOR_YELLOW}Restart Aero to use the new version.{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_RED}Failed to replace Aero executable: {e}{COLOR_RESET}")


# ---------- Plugin Update Section ----------
def list_remote_plugins():
    """Return list of plugins available in GitHub"""
    context = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(PLUGINS_API, context=context) as resp:
            data = json.loads(resp.read().decode())
        return [f["name"] for f in data if f["name"].endswith(".py")]
    except Exception as e:
        print(f"{COLOR_RED}Failed to fetch plugin list: {e}{COLOR_RESET}")
        return []


def update_plugin(plugin_name):
    """Update a single plugin by name"""
    print(f"{COLOR_YELLOW}Updating plugin: {plugin_name}{COLOR_RESET}")
    home = os.path.expanduser("~")
    plugin_path = os.path.join(home, "aero", "plugins", f"{plugin_name}.py")
    url = f"{PLUGINS_RAW_URL}/{plugin_name}.py"
    context = ssl._create_unverified_context()

    try:
        with urllib.request.urlopen(url, context=context) as resp:
            code = resp.read()
        os.makedirs(os.path.dirname(plugin_path), exist_ok=True)
        with open(plugin_path, "wb") as f:
            f.write(code)
        print(f"{COLOR_GREEN}Updated plugin '{plugin_name}' successfully!{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_RED}Failed to update plugin '{plugin_name}': {e}{COLOR_RESET}")


def update_all_plugins():
    """Download and update all plugins from GitHub"""
    print(f"{COLOR_CYAN}Updating all Aero plugins...{COLOR_RESET}")
    plugins = list_remote_plugins()
    if not plugins:
        print(f"{COLOR_RED}No plugins found in the remote repository.{COLOR_RESET}")
        return

    for plugin_file in plugins:
        plugin_name = plugin_file[:-3]  # strip .py
        update_plugin(plugin_name)
    print(f"{COLOR_GREEN}All plugins updated! Restart Aero or run 'refresh' to reload them.{COLOR_RESET}")


# ---------- Utility ----------
def print_help():
    print(f"{COLOR_YELLOW}Aero Update Command Help:{COLOR_RESET}")
    print(f"  {COLOR_GREEN}update{COLOR_RESET}             - List available versions and update interactively")
    print(f"  {COLOR_GREEN}update <version>{COLOR_RESET}   - Install a specific version (e.g. aero-beta-2.1.3)")
    print(f"  {COLOR_GREEN}update check{COLOR_RESET}       - Show available versions only")
    print(f"  {COLOR_GREEN}update plugins{COLOR_RESET}     - Update all installed plugins")
    print(f"  {COLOR_GREEN}update plugin <name>{COLOR_RESET} - Update a specific plugin (e.g. update plugin color)")
    print(f"  {COLOR_GREEN}update help{COLOR_RESET}        - Show this help message")


# ---------- Register ----------
def register(commands):
    commands["update"] = update_cmd
