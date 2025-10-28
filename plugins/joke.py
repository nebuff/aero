__PLUGIN_VERSION__ = "1.0.4"

import random

# Import core library functions
import config_manager as cm

# Collection of programming jokes
JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why don't programmers like nature? It has too many bugs.",
    "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
    "Why do Java developers wear glasses? Because they can't C#!",
    "What's a programmer's favorite hangout place? Foo Bar.",
    "Why did the programmer quit his job? He didn't get arrays.",
    "What do you call a programmer from Finland? Nerdic!",
    "Why do programmers hate nature? It has too many trees and not enough documentation.",
    "What's the object-oriented way to become wealthy? Inheritance.",
    "Why did the developer go broke? Because he used up all his cache!",
    "What do you call 8 hobbits? A hobbyte!",
    "Why don't programmers like to go outside? The sunlight causes too many reflections.",
    "What's a programmer's favorite type of music? Algo-rhythms!",
    "Why did the programmer bring a ladder to work? To reach the high-level programming!",
    "What do you call a programmer who doesn't comment their code? A monster!"
]

def joke_cmd(args):
    """Tell a random programming joke"""
    if args and args[0] == "help":
        cm.print_colored("Joke Command Help:", "subheader")
        print(f"  {cm.colorize('joke', 'success'):<10} - Tell a random programming joke")
        print(f"  {cm.colorize('joke help', 'success'):<10} - Show this help")
        return

    # Pick a random joke
    joke = random.choice(JOKES)
    cm.print_colored("Here's a joke for you:", "data_primary")
    cm.print_colored(joke, "data_value")

def register_plugin_commands(COMMANDS):
    """Registers the 'joke' command."""
    COMMANDS["joke"] = joke_cmd
