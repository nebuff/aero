#!/usr/bin/env python3
import os
import sys
import shlex
import subprocess
import shutil
import importlib.util
import urllib.request
import json
import datetime
import readline
import socket # Used for hostname

# --- 1. CORE PATH SETUP ---
# Determine the root directory of the Aero application
AERO_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(AERO_DIR, "lib")

# Add the 'lib' directory to the Python path so we can import internal modules.
if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)

# --- 2. CORE MODULE IMPORTS ---
# These imports rely on LIB_DIR being in sys.path
try:
    # We use a try/except block specifically to provide a clean error message 
    # if any core library is missing or misconfigured.
    from constants import (
        __AERO_VERSION__, PLUGINS_DIR, CONFIG_PATH, COMMANDS_FILE, REPO_PLUGINS_URL
    )
    import config_manager as cm
    from core_commands import register_core_commands
    # Note: 'core' must be imported later as it might have external dependencies
except ImportError as e:
    # Note: config_manager might not be loaded yet, so we use print() and raw ANSI codes 
    # for the most basic error reporting here.
    RED = "\033[31m"
    RESET = "\033[0m"
    print(f"{RED}[Aero Fatal Error] Failed to import core libraries from 'lib/' directory.{RESET}")
    print(f"{RED}Error: {e}{RESET}")
    print(f"{RED}Please ensure the '{LIB_DIR}' directory is correctly structured and files like 'constants.py' and 'config_manager.py' exist.{RESET}")
    sys.exit(1)


# Global dictionary for all commands (core and plugin)
COMMANDS = {}

def load_plugins():
    """Dynamically loads and registers commands from all plugins in the plugins/ directory."""
    cm.print_colored("Loading plugins...", "info")
    loaded_count = 0
    
    # Ensure plugins directory exists
    os.makedirs(PLUGINS_DIR, exist_ok=True)
    
    # Add plugins directory to path for imports
    if PLUGINS_DIR not in sys.path:
        sys.path.append(PLUGINS_DIR)

    for filename in os.listdir(PLUGINS_DIR):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            filepath = os.path.join(PLUGINS_DIR, filename)
            
            try:
                spec = importlib.util.spec_from_file_location(module_name, filepath)
                if spec is None:
                    continue
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Plugin module must have a register_plugin_commands function
                if hasattr(module, 'register_plugin_commands'):
                    module.register_plugin_commands(COMMANDS)
                    loaded_count += 1
                else:
                    cm.print_colored(f"Warning: Plugin '{module_name}' is missing 'register_plugin_commands' function.", "warning")

            except Exception as e:
                cm.print_colored(f"[Aero Error] Failed to load plugin {filename}: {e}", "error")

    cm.print_colored(f"Loaded {loaded_count} plugin(s)", "success")


def initialize_aero():
    """Initialize Aero by creating required files and directories on first run."""
    
    # Create required directories
    os.makedirs(PLUGINS_DIR, exist_ok=True)
    os.makedirs(LIB_DIR, exist_ok=True)
    
    # Ensure config.json exists and is loaded
    if not os.path.exists(CONFIG_PATH):
        # The config_manager handles creating the default config if it's missing
        cm.load_config() 
    else:
        cm.load_config()


def main():
    """Main execution loop for the Aero Shell."""
    
    # Run initialization steps
    initialize_aero()
    
    # Register core commands (defined in lib/core_commands.py)
    register_core_commands(COMMANDS)
    
    # Load commands from plugins
    load_plugins()

    # Initial welcome message
    username = cm.get_config('username')
    display_username = username if username else 'Aero-User' # Determine display name with default fallback
    
    cm.print_colored(f"{display_username} Shell {__AERO_VERSION__}", "header")
    cm.print_colored(f"Welcome, {cm.colorize(display_username, 'data_primary')}! Type {cm.colorize('help', 'info')} for commands.", "success")

    while True:
        try:
            # Format the prompt using config_manager
            prompt = cm.format_prompt(cm.get_config('prompt_template'))
            
            # Readline history is automatically managed by the 'readline' module
            cmd_input = input(prompt).strip()
            if not cmd_input:
                continue

            parts = shlex.split(cmd_input)
            cmd = parts[0]
            args = parts[1:]

            if cmd in ("exit", "quit"):
                cm.print_colored("Exiting Aero Shell...", "warning")
                break

            # Command execution logic
            if cmd in COMMANDS:
                COMMANDS[cmd](args)
            else:
                # External command fallback
                if shutil.which(cmd):
                    try:
                        # Use subprocess.run for external commands
                        subprocess.run(parts, check=True) # Run parts directly without shell=True for security/robustness
                    except subprocess.CalledProcessError as e:
                        cm.print_colored(f"External command failed with return code {e.returncode}.", "error")
                    except Exception as e:
                        cm.print_colored(f"Error running command: {e}", "error")
                else:
                    cm.print_colored(f"aero: command not found: {cmd}", "error")

        except KeyboardInterrupt:
            cm.print_colored("\nUse 'exit' or 'quit' to close Aero.", "warning")
        except EOFError:
            cm.print_colored("\nGoodbye!", "warning")
            break
        except Exception as e:
            cm.print_colored(f"Uncaught Error: {e}", "error")

if __name__ == "__main__":
    main()
