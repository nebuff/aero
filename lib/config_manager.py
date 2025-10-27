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
    
    if not os.path.exists(CONFIG_PATH):
        # Fallback to defaults if file is missing (should be created by initialize_aero)
        from constants import DEFAULT_CONFIG # Import only when needed to avoid circular dep
        CONFIG = DEFAULT_CONFIG.copy()
        
    try:
        with open(CONFIG_PATH, 'r') as f:
            CONFIG.update(json.load(f))
    except Exception as e:
        print(f"Warning: Could not load config.json: {e}", file=sys.stderr)
        # If loading fails, ensure we still have a basic config
        if not CONFIG:
            from constants import DEFAULT_CONFIG
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
    except NameError:
        # Fallback if __AERO_VERSION__ is not defined
        CONFIG["aero_version"] = "unknown"

    return CONFIG


def get_config(key, default=None):
    """Retrieves a configuration value."""
    # Ensure config is loaded if this is the first call
    if not CONFIG:
        load_config()
    return CONFIG.get(key, default)


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

    # --- Start Fix: Handle PermissionError for os.getcwd() on systems like macOS TCC ---
    home_dir = os.path.expanduser("~")
    current_path_name = "/" # Default for short_pwd
    full_path = "/"
    
    try:
        # Get the current working directory. This is the line that can fail.
        full_path = os.getcwd()
        
        # Get the last component of the path for 'short_pwd' (original logic)
        current_path_name = os.path.basename(full_path) or "/"
        
        # If the full path is the home directory, show ~
        if full_path == home_dir:
            current_path_name = "~"
            
    except PermissionError:
        # Graceful fallback if os.getcwd() fails due to macOS TCC/PermissionError
        print_colored(
            "Warning: Operation not permitted. Check terminal permissions (macOS TCC). Prompt path will show as '[Denied]'.", 
            "warning"
        )
        current_path_name = "[Denied]"
        full_path = "[Denied]"
    except Exception as e:
        # General error handling
        print_colored(f"Warning: Failed to get CWD: {e}", "warning")
        current_path_name = "[Error]"
        full_path = "[Error]"

    # Map the results to the expected variables
    full_pwd = full_path
    short_pwd = current_path_name
    # --- End Fix ---

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
        # Get the last component of the path for 'short_pwd'
        short_pwd=short_pwd,
    )
    
    return formatted_prompt
