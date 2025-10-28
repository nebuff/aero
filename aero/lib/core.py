import os
import json
import sys
try:
    import psutil
except ImportError:
    psutil = None

# Import constants from our new constants file
from constants import PLUGINS_DIR, LIB_DIR, CONFIG_PATH, DEFAULT_CONFIG

# Define placeholder colors for initialization, in case config isn't loaded yet
COLOR_GREEN = "\033[32m"
COLOR_RED = "\033[31m"
COLOR_RESET = "\033[0m"

def initialize_aero():
    """Initialize Aero by creating required files and directories on first run"""
    # Create plugins directory if it doesn't exist
    os.makedirs(PLUGINS_DIR, exist_ok=True)
    
    # Create lib directory if it doesn't exist
    os.makedirs(LIB_DIR, exist_ok=True)
    
    # Create config.json if it doesn't exist
    if not os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            print(f"{COLOR_GREEN}Created config.json with default settings{COLOR_RESET}")
        except Exception as e:
            print(f"{COLOR_RED}Failed to create config.json: {e}{COLOR_RESET}", file=sys.stderr)
    
    # Create .gitignore if it doesn't exist
    gitignore_path = os.path.join(os.path.dirname(LIB_DIR), ".gitignore") # AERO_DIR
    if not os.path.exists(gitignore_path):
        gitignore_content = """# Aero files
.aero_history
config.json

# Python cache
__pycache__/
*.pyc
lib/__pycache__/
plugins/__pycache__/
"""
        try:
            with open(gitignore_path, "w") as f:
                f.write(gitignore_content)
            print(f"{COLOR_GREEN}Created .gitignore{COLOR_RESET}")
        except Exception as e:
            print(f"{COLOR_RED}Failed to create .gitignore: {e}{COLOR_RESET}", file=sys.stderr)

def get_battery_percent():
    """Get battery percentage for laptops"""
    if not psutil:
        return "N/A" # psutil not installed
    try:
        battery = psutil.sensors_battery()
        if battery:
            return f"{int(battery.percent)}%"
        return "N/A" # No battery found
    except Exception:
        return "N/A" # Error reading battery
