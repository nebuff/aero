import os

# --- Core Version ---
__AERO_VERSION__ = "aero-beta-0.1.4"  # Change this string for your version

# --- Core Paths ---
# We are in lib/, so AERO_DIR is one level up
AERO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
PLUGINS_DIR = os.path.join(AERO_DIR, "plugins")
LIB_DIR = os.path.join(AERO_DIR, "lib")
REPO_PLUGINS_URL = "https://raw.githubusercontent.com/nebuff/aero/main/plugins"
CONFIG_PATH = os.path.join(AERO_DIR, "config.json")

# --- Default Configuration ---
# This is the default config.json structure
DEFAULT_CONFIG = {
    "color": True,
    "username": "Aero-User",
    "time_format": "24",
    "prompt_template": "<green>{username}@{hostname}</green> <blue>{short_pwd}</blue> > ",
    "colors": {
        # Core system colors
        "prompt": "\033[32m",
        "info": "\033[36m",
        "error": "\033[31m",
        "success": "\033[32m",
        "warning": "\033[33m",
        "reset": "\033[0m",
        
        # Plugin-specific colors
        "plugin": "\033[36m",
        "plugin_output": "\033[37m",
        "plugin_error": "\033[91m",
        "plugin_success": "\033[92m",
        
        # UI element colors
        "header": "\033[1;36m",
        "subheader": "\033[1;33m",
        "border": "\033[90m",
        "highlight": "\033[1;37m",
        "dim": "\033[2;37m",
        
        # Data display colors
        "data_primary": "\033[36m",
        "data_secondary": "\033[35m",
        "data_value": "\033[37m",
        "data_key": "\033[33m",
        
        # Status colors
        "status_online": "\033[92m",
        "status_offline": "\033[91m",
        "status_pending": "\033[93m",
        "status_unknown": "\033[90m",
        
        # Special formatting
        "bold": "\033[1m",
        "italic": "\033[3m",
        "underline": "\033[4m",
        "strikethrough": "\033[9m",
        "highlight_format": "\033[7m"
    }
}
