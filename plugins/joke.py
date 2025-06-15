__PLUGIN_VERSION__ = "1.0.0"

import urllib.request
import json
import ssl

def joke_cmd(args):
    try:
        context = ssl._create_unverified_context()
        with urllib.request.urlopen("https://v2.jokeapi.dev/joke/Programming?type=single", context=context) as resp:
            data = json.loads(resp.read().decode())
            print(data.get("joke", "No joke found!"))
    except Exception as e:
        print(f"joke: {e}")

def register(COMMANDS):
    COMMANDS["joke"] = joke_cmd
