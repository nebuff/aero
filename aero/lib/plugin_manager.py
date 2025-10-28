import os
import importlib.util
import sys

# Import constants and config functions
from constants import PLUGINS_DIR
try:
    from config_manager import print_colored
except ImportError:
    # Fallback if config_manager isn't fully loaded yet
    def print_colored(text, color_key):
        colors = {"success": "\033[32m", "error": "\033[31m", "reset": "\033[0m"}
        print(f"{colors.get(color_key, '')}{text}{colors['reset']}")


def load_plugins(COMMANDS):
    """
    Loads all .py files from the PLUGINS_DIR and registers their commands.
    
    Args:
        COMMANDS (dict): The main command dictionary to populate.
    """
    if not os.path.isdir(PLUGINS_DIR):
        return
    
    loaded = 0
    for fname in os.listdir(PLUGINS_DIR):
        if fname.endswith(".py") and not fname.startswith("_"):
            fpath = os.path.join(PLUGINS_DIR, fname)
            try:
                # Create a module spec from the file path
                spec = importlib.util.spec_from_file_location(fname[:-3], fpath)
                # Create a module from the spec
                mod = importlib.util.module_from_spec(spec)
                # Add module to sys.modules to allow relative imports within plugins
                sys.modules[spec.name] = mod
                # Execute the module's code
                spec.loader.exec_module(mod)
                
                # Look for a 'register' function in the loaded module
                if hasattr(mod, "register"):
                    # Call the register function, passing it the COMMANDS dict
                    mod.register(COMMANDS)
                
                loaded += 1
            except Exception as e:
                print_colored(f"Failed to load plugin {fname}: {e}", "error")
                
    if loaded > 0:
        print_colored(f"Loaded {loaded} plugin(s)", "success")
