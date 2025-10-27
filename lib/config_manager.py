import json
import os
import re
import sys
import datetime

# Import constants
from constants import CONFIG_PATH, DEFAULT_CONFIG
# Import core utilities
import core

# --- Module-level config variable ---
# This dictionary will hold the loaded configuration.
# All functions in this module will read from/write to this variable.
config = {}

def load_config():
    """Loads config.json into the module-level 'config' variable."""
    global config
    if not os.path.isfile(CONFIG_PATH):
        config = DEFAULT_CONFIG.copy()
        return
        
    try:
        with open(CONFIG_PATH, "r") as f:
            loaded_config = json.load(f)
        
        # Track if we need to save updated config
        config_updated = False
        
        # Ensure all default values exist
        for key, value in DEFAULT_CONFIG.items():
            if key not in loaded_config:
                loaded_config[key] = value
                config_updated = True
            if key == "colors" and isinstance(value, dict):
                if "colors" not in loaded_config:
                     loaded_config["colors"] = {}
                for color_key, color_value in value.items():
                    if color_key not in loaded_config["colors"]:
                        loaded_config["colors"][color_key] = color_value
                        config_updated = True
        
        config = loaded_config
        
        # Save updated config if new colors/keys were added
        if config_updated:
            try:
                with open(CONFIG_PATH, "w") as f:
                    json.dump(config, f, indent=2)
                print(f"{core.COLOR_GREEN}Updated config.json with new options{core.COLOR_RESET}")
            except Exception as e:
                print(f"{core.COLOR_RED}Failed to update config.json: {e}{core.COLOR_RESET}", file=sys.stderr)
                        
    except Exception:
        config = DEFAULT_CONFIG.copy()

def save_config():
    """Saves the current module-level 'config' variable to config.json."""
    global config
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Failed to save config: {e}", file=sys.stderr)

def get_config():
    """Returns the loaded configuration dictionary."""
    global config
    return config

# --- Color and Formatting Functions ---

def get_color(key):
    """Get a color code by key. Returns empty string if colors are disabled."""
    global config
    if config.get("color", True):
        return config.get("colors", {}).get(key, "")
    return ""

def colorize(text, color_key):
    """Colorize text with a specific color key."""
    if not config.get("color", True):
        return text
    color = get_color(color_key)
    reset = get_color("reset")
    return f"{color}{text}{reset}"

def print_colored(text, color_key):
    """Print text with a specific color."""
    print(colorize(text, color_key))

def get_color_palette():
    """Get all available color categories for plugins."""
    return {
        "core": ["prompt", "info", "error", "success", "warning", "reset"],
        "plugin": ["plugin", "plugin_output", "plugin_error", "plugin_success"],
        "ui": ["header", "subheader", "border", "highlight", "dim"],
        "data": ["data_primary", "data_secondary", "data_value", "data_key"],
        "status": ["status_online", "status_offline", "status_pending", "status_unknown"],
        "format": ["bold", "italic", "underline", "strikethrough"]
    }

def register_colors_for_plugins():
    """
    Register color functions in a way that plugins can import them.
    This injects them into the main script's global scope.
    """
    try:
        # This is a bit of Python magic. It gets the main script's
        # global scope and adds these functions to it.
        main_globals = sys.modules['__main__'].__dict__
        main_globals['aero_get_color'] = get_color
        main_globals['aero_colorize'] = colorize
        main_globals['aero_print_colored'] = print_colored
        main_globals['aero_get_color_palette'] = get_color_palette
    except Exception as e:
        print_colored(f"Warning: Could not register color functions for plugins: {e}", "warning")


def format_text(text):
    """Convert <color>text</color> tags to ANSI codes"""
    import re
    COLORS = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'aqua': '\033[36m',  # Add aqua as alias for cyan
        'white': '\033[37m',
        'bold': '\033[1m',
        'italic': '\033[3m',
        'underline': '\033[4m',
        'highlight': '\033[7m',  # Add highlight (reverse video)
        'reset': '\033[0m',
        'space': ' ',  
        'clear': '\033[0m'  # Add clear tag for resetting formatting
    }

    if not config.get("color", True):
        # If colors are off, just strip the tags
        text = re.sub(r'<[^>]+>', '', text)
        return text.replace('<space>', ' ')

    # Handle standalone clear tags first
    text = text.replace('<clear>', COLORS['clear'])
    
    # Use a non-greedy regex to find the innermost tags first
    while True:
        match = re.search(r'<([^>]+)>(.*?)</\1>', text, re.DOTALL)
        if not match:
            break
        
        start_tag, content = match.groups()
        
        # Check for nested tags (if so, process them first)
        if re.search(r'<[^>]+>', content):
             # Find a tag that is not the one we just matched
            nested_match = re.search(r'<(?!" + re.escape(start_tag) + r")[^>]+>(.*?)</[^>]+>', content, re.DOTALL)
            if nested_match:
                # Process inner tag first
                text = text.replace(content, format_text(content))
                continue # Re-run the outer loop

        formats = [f.strip() for f in start_tag.split(',')]
        replacement = ''
        for fmt in formats:
            if fmt in COLORS:
                replacement += COLORS[fmt]
        
        replacement += content + COLORS['reset']
        text = text[:match.start()] + replacement + text[match.end():]

    text = text.replace('<reset>', COLORS['reset'])
    text = text.replace('<space>', ' ')
    return text

def format_prompt(template):
    """Format prompt template with placeholders"""
    global config
    now = datetime.datetime.now()
    
    # Use 12-hour or 24-hour time based on config
    time_format_str = "%H:%M:%S"
    if config.get("time_format", "24") == "12":
        time_format_str = "%I:%M:%S %p"
        
    replacements = {
        "{time}": now.strftime(time_format_str),
        "{date}": now.strftime("%Y-%m-%d"),
        "{username}": config.get("username", "Aero-User"),
        "{hostname}": os.uname().nodename,
        "{pwd}": os.getcwd(),
        "{battery}": core.get_battery_percent(),
        "{short_pwd}": os.path.basename(os.getcwd())
    }
    
    result = template
    
    for key, value in replacements.items():
        result = result.replace(key, str(value))
    
    return format_text(result)
