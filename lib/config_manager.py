import json
import os
import datetime
import socket

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
# Global cache for color codes after loading config
COLOR_MAP = DEFAULT_COLORS.copy()


def load_config():
    """Loads configuration from config.json into the global CONFIG and COLOR_MAP."""
    global CONFIG, COLOR_MAP
    
    # Define a default configuration
    default_config = {
        "color": True,
        "username": os.getenv("USER", "Aero-User"),
        "time_format": "%H:%M:%S",
        "active_theme": "default",
        "prompt_template": "<green>{username}</green>@<blue>{hostname}</blue> <yellow>{short_pwd}</yellow> ❯ ",
        "colors": DEFAULT_COLORS
    }

    try:
        with open(CONFIG_PATH, 'r') as f:
            loaded_config = json.load(f)
            # Merge loaded config with defaults (in case new keys were added)
            CONFIG = default_config
            CONFIG.update(loaded_config)
            
    except FileNotFoundError:
        print(f"\033[33mWarning: {CONFIG_PATH} not found. Creating with default settings.\033[0m")
        CONFIG = default_config
        save_config(CONFIG)
    except json.JSONDecodeError:
        print(f"\033[31mError: {CONFIG_PATH} contains invalid JSON. Using default settings.\033[0m")
        CONFIG = default_config
        save_config(CONFIG)
    except Exception as e:
        print(f"\033[31mError loading config: {e}. Using default settings.\033[0m")
        CONFIG = default_config
        
    # Update the global COLOR_MAP from the loaded configuration
    COLOR_MAP = CONFIG.get("colors", DEFAULT_COLORS).copy()


def save_config(new_config=None):
    """Saves the current global configuration back to config.json."""
    global CONFIG
    if new_config:
        CONFIG = new_config
        
    try:
        with open(CONFIG_PATH, 'w') as f:
            # Ensure colors are written as plain strings (not string literals)
            json.dump(CONFIG, f, indent=2)
        return True
    except Exception as e:
        print_colored(f"Error saving config: {e}", "error")
        return False

def get_config(key=None):
    """Returns the entire config dictionary or a specific key's value."""
    if key:
        return CONFIG.get(key)
    return CONFIG

# --- Utility Functions ---

def colorize(text, color_key):
    """Applies ANSI color codes to text based on the color map."""
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
    full_pwd = os.getcwd()
    # Get the last component of the path for 'short_pwd'
    short_pwd = os.path.basename(full_pwd) or "/" 

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
        short_pwd=short_pwd
    )

    return formatted_prompt
    
# Initialize config on module load
load_config()
