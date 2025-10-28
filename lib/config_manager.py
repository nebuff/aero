import json
import os
import datetime
import socket
import sys  # <-- FIX 1: Added missing import

# Attempt to import constants from the new location
try:
    # We must try/except here for local testing, though in runtime it should work
    from constants import CONFIG_PATH, __AERO_VERSION__
except ImportError:
    # Fallback if constants is not yet defined (just for robustness)
    CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")


# Global cache for configuration settings
CONFIG = {}
# Default ANSI color codes mapped to configuration keys
DEFAULT_COLORS = {
    "reset": "\033[0m",
    # Main UI elements
    "success": "\033[32m",      # Green
    "warning": "\033[33m",      # Yellow
    "error": "\033[31m",        # Red
    "info": "\033[36m",         # Cyan
    "header": "\033[1;36m",     # Bold Cyan
    "subheader": "\033[1;33m",  # Bold Yellow
    "dim": "\033[2;37m",        # Dim White
    # Prompt and data
    "data_primary": "\033[34m", # Blue
    "data_secondary": "\033[35m", # Magenta
    "data_value": "\033[37m",   # White
    "prompt_text": "\033[92m",  # Light Green
}
# Global cache for color codes after loading config.
COLOR_MAP = DEFAULT_COLORS


# --- Configuration Loading ---

def load_config():
    """
    Loads configuration from config.json into the global CONFIG dictionary
    and updates the COLOR_MAP.
    """
    global CONFIG
    global COLOR_MAP
    
    # Import here to avoid circular dependencies
    from constants import DEFAULT_CONFIG 

    try:
        # Try to open and read the config file
        with open(CONFIG_PATH, 'r') as f:
            config_data = json.load(f)
            # If json.load(f) returns None or {}, it's considered empty/invalid
            if not config_data:
                raise json.JSONDecodeError("Config file is empty.", "", 0)
        CONFIG.update(config_data)
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # --- FIX 2: Handle missing, empty, or corrupt config file ---
        print(f"Warning: config.json not found or is corrupt/empty ({e}). Loading defaults.", file=sys.stderr)
        CONFIG = DEFAULT_CONFIG.copy()
        try:
            # Save the default config back to the file to fix it
            with open(CONFIG_PATH, 'w') as f:
                json.dump(CONFIG, f, indent=2)
            print("Created default config.json.", file=sys.stderr)
        except Exception as save_e:
            print(f"Error: Could not write default config: {save_e}", file=sys.stderr)
            
    except Exception as e:
        # Catchall for other unexpected errors
        print(f"Warning: Could not load config.json: {e}", file=sys.stderr)
        if not CONFIG: # Ensure config is not empty
            CONFIG = DEFAULT_CONFIG.copy()

    # Update color map if color config is present
    if CONFIG.get("color", True) and "colors" in CONFIG:
        # Merge defaults and user defined colors
        COLOR_MAP = DEFAULT_COLORS.copy()
        COLOR_MAP.update(CONFIG["colors"])
        
    # Ensure all required core keys are present for fallback safety
    if "reset" not in COLOR_MAP:
        COLOR_MAP["reset"] = "\033[0m"
    if "warning" not in COLOR_MAP:
        COLOR_MAP["warning"] = DEFAULT_COLORS["warning"]

    # Add the current Aero version to the config cache
    try:
        from constants import __AERO_VERSION__
        CONFIG["aero_version"] = __AERO_VERSION__
    except ImportError:
        # Fallback if __AERO_VERSION__ is not defined
        CONFIG["aero_version"] = "unknown"

    return CONFIG


def get_config(key=None, default=None):
    """
    Retrieves a specific configuration value by key,
    or returns the entire config dictionary if no key is provided.
    """
    # Ensure config is loaded if this is the first call
    if not CONFIG:
        load_config()
    
    if key:
        return CONFIG.get(key, default)
    return CONFIG


# --- Utility Functions ---

def colorize(text, color_key="info"):
    """Wraps text with ANSI color codes based on color_key."""
    # Ensure config is loaded
    if not CONFIG:
        load_config()
        
    if not CONFIG.get("color", True):
        return text
    
    color_code = COLOR_MAP.get(color_key, COLOR_MAP["reset"])
    reset_code = COLOR_MAP["reset"]
    return f"{color_code}{text}{reset_code}"

def print_colored(text, color_key="info"):
    """Prints text with the specified color."""
    print(colorize(text, color_key))

def format_prompt(template):
    """Formats the prompt template with dynamic values and color tags."""
    
    # 1. Prepare dynamic values
    username = CONFIG.get("username", "user")
    time_str = datetime.datetime.now().strftime(CONFIG.get("time_format", "%H:%M:%S"))
    hostname = socket.gethostname().split('.')[0]
    
    # --- Robust Path Handling ---
    try:
        full_pwd = os.getcwd()
        # Get the last component of the path for 'short_pwd'
        short_pwd = os.path.basename(full_pwd) or "/"
        # Replace home dir with ~
        home_dir = os.path.expanduser("~")
        if full_pwd.startswith(home_dir):
            full_pwd = "~" + full_pwd[len(home_dir):]
            if full_pwd == "~":
                 short_pwd = "~" # Special case for home
            
    except Exception as e:
        print_colored(f"Warning: Could not get current directory: {e}", "error")
        full_pwd = "[error_pwd]"
        short_pwd = "[error_pwd]"
    
    # 2. Prepare color replacement map
    # This uses a simple regex-like replacement for tags like <color>text</color>
    
    colored_template = template
    
    # Replace <color> tags with ANSI codes
    for color_name, color_code in COLOR_MAP.items():
        # Open tag replacement: <color> -> ANSI code
        colored_template = colored_template.replace(f"<{color_name}>", color_code)
        # Close tag replacement: </color> -> RESET code
        colored_template = colored_template.replace(f"</{color_name}>", COLOR_MAP["reset"])

    # 3. Apply dynamic values
    formatted_prompt = colored_template.format(
        username=username,
        time_str=time_str,
        hostname=hostname,
        full_pwd=full_pwd,
        short_pwd=short_pwd,
    )
    
    return formatted_prompt

def get_color(key):
    """Get a raw color code by key."""
    return COLOR_MAP.get(key, "")

def get_color_palette():
    """Get all available color categories for plugins."""
    # This can be expanded with more categories later
    return {
        "core": ["success", "warning", "error", "info", "header", "subheader", "dim", "reset"],
        "data": ["data_primary", "data_secondary", "data_value"],
        "prompt": ["prompt_text"]
    }

def save_config():
    """Saves the current CONFIG cache back to config.json."""
    global CONFIG
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(CONFIG, f, indent=2)
    except Exception as e:
        print_colored(f"Failed to save config: {e}", "error")

