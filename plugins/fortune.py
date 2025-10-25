__PLUGIN_VERSION__ = "1.0.0"

import random

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
    print(random.choice(FORTUNES))

def register(COMMANDS):
    COMMANDS["fortune"] = fortune_cmd
