__PLUGIN_VERSION__ = "1.2.0"

import urllib.request
import ssl

def weather_cmd(args):
    if not args:
        city = ""
        url = f"https://wttr.in/?format=3"
        try:
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(url, context=context) as resp:
                print(resp.read().decode())
        except Exception as e:
            print(f"weather: {e}")
        return

    # If user enters "canada", show weather for major Canadian cities
    if len(args) == 1 and args[0].lower() == "canada":
        cities = [
            "Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa",
            "Edmonton", "Winnipeg", "Quebec", "Halifax", "Victoria"
        ]
        print("Weather for major cities in Canada:")
        context = ssl._create_unverified_context()
        for city in cities:
            url = f"https://wttr.in/{city}?format=3"
            try:
                with urllib.request.urlopen(url, context=context) as resp:
                    print(resp.read().decode())
            except Exception as e:
                print(f"{city}: {e}")
        return

    # Otherwise, treat args as a location
    city = " ".join(args)
    url = f"https://wttr.in/{city}?format=3"
    try:
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(url, context=context) as resp:
            print(resp.read().decode())
    except Exception as e:
        print(f"weather: {e}")

def register(COMMANDS):
    COMMANDS["weather"] = weather_cmd
