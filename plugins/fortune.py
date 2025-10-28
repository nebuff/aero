__PLUGIN_VERSION__ = "1.0.0"

import random

# Import core library functions
import config_manager as cm

FORTUNES = [
    "You will write bug-free code today!",
    "A good commit is worth a thousand lines.",
    "Keep calm and code on.",
    "Refactor fearlessly.",
    "The best debugger is a good night's sleep.",
    "Your next project will be a success!",
    "Don't forget to push your changes.",
    "Aero loves you."
]

def fortune_cmd(args):
    """Prints a random fortune cookie message."""
    cm.print_colored(random.choice(FORTUNES), "data_primary")

def register_plugin_commands(COMMANDS):
    """Registers the 'fortune' command."""
    COMMANDS["fortune"] = fortune_cmd
