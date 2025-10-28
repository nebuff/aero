import os
import json
import urllib.request
import ssl
from collections import defaultdict

# Import core library functions
import config_manager as cm
from constants import REPO_ROOT_URL, AERO_DIR

# --- Plugin Metadata ---
__PLUGIN_NAME__ = "theme"
__PLUGIN_VERSION__ = "1.0.0"

# --- Constants ---
THEMES_DIR = os.path.join(AERO_DIR, "themes")
REPO_THEMES_URL = f"{REPO_ROOT_URL}/themes"
THEME_EXTENSION = ".theme"

# --- Utility Functions ---

def _get_local_themes():
    """Gets a dictionary of locally installed themes {name: path}."""
    if not os.path.isdir(THEMES_DIR):
        return {}
    themes = {}
    for filename in os.listdir(THEMES_DIR):
        if filename.endswith(THEME_EXTENSION):
            name = filename[:-len(THEME_EXTENSION)]
            themes[name] = os.path.join(THEMES_DIR, filename)
    return themes

def _get_remote_themes():
    """Fetches a list of available theme names from the GitHub repo."""
    # Ensure REPO_ROOT_URL is accessible for this network call
    if not REPO_ROOT_URL:
        cm.print_colored("Error: REPO_ROOT_URL is missing. Cannot fetch remote themes.", "error")
        return []

    try:
        # Construct the API URL to list the contents of the themes directory
        api_url = f"https://api.github.com/repos/nebuff/aero/contents/themes"
        
        # Create an unverified SSL context for simplicity
        context = ssl._create_unverified_context()
        
        with urllib.request.urlopen(api_url, context=context, timeout=5) as resp:
            data = resp.read().decode()
            
        files = json.loads(data)
        remote_themes = set()
        for f in files:
            name = f.get("name", "")
            if name.endswith(THEME_EXTENSION):
                remote_themes.add(name[:-len(THEME_EXTENSION)])
        return sorted(list(remote_themes))
    except Exception as e:
        cm.print_colored(f"Could not fetch available themes from repo: {e}", "error")
        return []

def _load_theme_file(theme_path):
    """Loads and returns the content of a .theme JSON file."""
    try:
        with open(theme_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        cm.print_colored(f"Error: Theme file not found at {theme_path}", "error")
        return None
    except json.JSONDecodeError:
        cm.print_colored(f"Error: Invalid JSON format in theme file: {theme_path}", "error")
        return None
    except Exception as e:
        cm.print_colored(f"Error reading theme file: {e}", "error")
        return None

# --- Core Theme Commands ---

def cmd_theme_list(args):
    """Lists all installed and available themes."""
    local_themes = _get_local_themes()
    remote_themes = _get_remote_themes()
    config = cm.get_config()
    active_theme = config.get("active_theme", "default")
    
    # 1. Local Themes
    cm.print_colored("\nInstalled Themes (aero/themes/):", "header")
    if local_themes:
        for name in sorted(local_themes.keys()):
            status = cm.colorize("[ACTIVE]", "success") if name == active_theme else ""
            print(f"  {cm.colorize(name.ljust(20), 'data_primary')} {status}")
    else:
        cm.print_colored("  No local themes installed. Use 'theme download <name>' to get one.", "warning")

    # 2. Remote Themes
    cm.print_colored("\nAvailable Remote Themes (GitHub):", "header")
    if remote_themes:
        for name in remote_themes:
            # Mark themes that are already installed locally
            mark = cm.colorize("[INSTALLED]", "info") if name in local_themes else ""
            print(f"  {cm.colorize(name.ljust(20), 'data_primary')} {mark}")
        cm.print_colored("\nUse 'theme download <name>' to install a remote theme.", "info")
    else:
        cm.print_colored("  Could not retrieve remote themes list. Check network connectivity or REPO_ROOT_URL.", "error")


def cmd_theme_set(args):
    """Sets the active theme by merging its configuration into config.json."""
    if not args:
        cm.print_colored("Usage: theme set <theme_name>", "error")
        return

    theme_name = args[0]
    local_themes = _get_local_themes()
    
    if theme_name not in local_themes:
        cm.print_colored(f"Error: Theme '{theme_name}' not found locally. Use 'theme list' or 'theme download'.", "error")
        return
        
    theme_path = local_themes[theme_name]
    theme_data = _load_theme_file(theme_path)
    
    if not theme_data:
        return # Error handled in _load_theme_file

    config = cm.get_config()
    
    # Create a theme-applied config map by starting with the current config
    new_config = config.copy()
    
    # Update prompt_template and colors (the only things a theme should change)
    if 'prompt_template' in theme_data:
        new_config['prompt_template'] = theme_data['prompt_template']
        
    if 'colors' in theme_data and isinstance(theme_data['colors'], dict):
        # Only merge the colors dictionary, preserving other config keys
        new_config.setdefault('colors', {}).update(theme_data['colors'])
        
    # Set the active theme marker
    new_config['active_theme'] = theme_name
    
    # Save the merged configuration
    cm.save_config(new_config)
    
    # Reload config manager to update prompt/color functions immediately
    cm.load_config() 
    
    cm.print_colored(f"Theme '{theme_name}' applied successfully. Config and colors updated.", "success")


def cmd_theme_download(args):
    """Downloads a theme file from the GitHub repo."""
    if not args:
        cm.print_colored("Usage: theme download <theme_name>", "error")
        return

    theme_name = args[0]
    theme_file = f"{theme_name}{THEME_EXTENSION}"
    url = f"{REPO_THEMES_URL}/{theme_file}"
    dest = os.path.join(THEMES_DIR, theme_file)

    os.makedirs(THEMES_DIR, exist_ok=True)
    
    try:
        context = ssl._create_unverified_context()
        cm.print_colored(f"Downloading theme '{theme_name}' from {url} ...", "info")
        
        # Check if remote file exists (by checking response status)
        with urllib.request.urlopen(url, context=context, timeout=5) as response:
            if response.getcode() != 200:
                raise Exception(f"Theme not found (HTTP {response.getcode()})")
            
            # Write content to local file
            with open(dest, "wb") as out_file:
                out_file.write(response.read())

        cm.print_colored(f"Installed theme '{theme_name}' to {dest}. Use 'theme set {theme_name}' to apply.", "success")
    except Exception as e:
        cm.print_colored(f"Failed to install theme '{theme_name}': {e}", "error")


def cmd_theme_create(args):
    """Creates a theme template file for editing."""
    if not args:
        cm.print_colored("Usage: theme create <new_theme_name>", "error")
        return

    theme_name = args[0]
    theme_file = f"{theme_name}{THEME_EXTENSION}"
    dest = os.path.join(THEMES_DIR, theme_file)

    if os.path.exists(dest):
        cm.print_colored(f"Error: Theme '{theme_name}' already exists at {dest}", "error")
        return

    os.makedirs(THEMES_DIR, exist_ok=True)
    
    # Fetch current colors for the template
    current_config = cm.get_config()
    current_colors = current_config.get('colors', {})
    
    # Base template structure
    template_data = {
        "theme_name": theme_name,
        "prompt_template": "<green>{username}</green>@<blue>{hostname}</blue> <yellow>{short_pwd}</yellow> ❯ ",
        "colors": current_colors # Use current colors as a starting point
    }
    
    try:
        with open(dest, 'w') as f:
            json.dump(template_data, f, indent=2)
            
        cm.print_colored(f"Theme template '{theme_name}' created at {dest}", "success")
        cm.print_colored("Edit the file to customize, then use 'theme set {}' to apply.".format(theme_name), "info")
    except Exception as e:
        cm.print_colored(f"Error creating theme file: {e}", "error")


def cmd_theme_help(args):
    """Displays help for the theme command."""
    cm.print_colored("Aero Theme Manager - Commands:", "header")
    help_text = {
        "theme list": "Lists all installed themes and available remote themes.",
        "theme set <name>": "Applies a local theme. Reloads prompt and colors.",
        "theme download <name>": "Downloads a remote theme file to your local themes directory.",
        "theme create <name>": "Creates a new theme template file for you to edit.",
    }
    
    for cmd, desc in help_text.items():
        print(f"  {cm.colorize(cmd, 'data_primary'):<25} - {desc}")

def cmd_theme(args):
    """Main entry point for the 'theme' command."""
    if not args:
        cmd_theme_help([])
        return
        
    subcommand = args[0].lower()
    sub_args = args[1:]
    
    if subcommand == "list":
        cmd_theme_list(sub_args)
    elif subcommand == "set":
        cmd_theme_set(sub_args)
    elif subcommand == "download":
        cmd_theme_download(sub_args)
    elif subcommand == "create":
        cmd_theme_create(sub_args)
    elif subcommand in ("help", "-h", "--help"):
        cmd_theme_help(sub_args)
    else:
        cm.print_colored(f"Unknown theme subcommand: {subcommand}", "error")
        cmd_theme_help([])

# --- Command Registration for Plugin Manager ---

def register_plugin_commands(COMMANDS):
    """Registers the 'theme' command."""
    COMMANDS['theme'] = cmd_theme
