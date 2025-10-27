import os

# --- Directory and Path Constants ---
# Assuming this file is in 'lib' subdirectory of the main aero directory
AERO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The directory where lib modules are located (AERO_DIR/lib)
LIB_DIR = os.path.join(AERO_DIR, "lib")

PLUGINS_DIR = os.path.join(AERO_DIR, "plugins")
CONFIG_PATH = os.path.join(AERO_DIR, "config.json")
COMMANDS_FILE = os.path.join(LIB_DIR, "core_commands.py")

# --- Repository URL Constants ---
REPO_ROOT_URL = "https://raw.githubusercontent.com/nebuff/aero/main"
REPO_PLUGINS_URL = f"{REPO_ROOT_URL}/plugins"

# --- General Constants ---
__AERO_VERSION__ = "aero-beta-0.1.8"


# --- Default Configuration ---
# This dictionary holds the default settings for the shell, 
# required by config_manager and core_commands before a user config is loaded.
DEFAULT_CONFIG = {
    "color": True,
    # Using a placeholder 'Aero-User' for the default username when this file is static
    "username": "Aero-User", 
    "prompt_template": "<green>{username}</green>@<blue>{hostname}</blue> <yellow>{short_pwd}</yellow> ❯ ",
    "time_format": "24",
    "colors": {
        "info": "\033[33m",
        "error": "\033[31m",
        "success": "\033[32m",
        "warning": "\033[33m",
        "header": "\033[1;36m",
        "subheader": "\033[1;33m",
        "data_primary": "\033[36m",
        "data_value": "\033[37m",
        "data_key": "\033[33m",
        "reset": "\033[0m"
    }
}
