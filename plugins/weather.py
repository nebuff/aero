__PLUGIN_VERSION__ = "1.2.1"

import urllib.request
import ssl

# Import core library functions
import config_manager as cm

def weather_cmd(args):
    """Fetches and displays weather information via wttr.in."""
    
    # Bypass SSL verification for wttr.in, which is common for command-line tools
    context = ssl._create_unverified_context()
    
    if not args:
        # Default: current location
        url = "https://wttr.in/?format=3"
        try:
            with urllib.request.urlopen(url, context=context) as resp:
                print(resp.read().decode())
        except Exception as e:
            cm.print_colored(f"weather: {e}", "error")
        return

    # If user enters "canada", show weather for major Canadian cities
    if len(args) == 1 and args[0].lower() == "canada":
        cities = [
            "Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa",
            "Edmonton", "Winnipeg", "Quebec", "Halifax", "Victoria"
        ]
        cm.print_colored("Weather for major cities in Canada:", "subheader")
        
        for city in cities:
            url = f"https://wttr.in/{city}?format=3"
            try:
                with urllib.request.urlopen(url, context=context) as resp:
                    # Print without color, as wttr.in handles its own ANSI coloring
                    print(resp.read().decode())
            except Exception as e:
                cm.print_colored(f"{city}: {e}", "error")
        return

    # Otherwise, treat args as a location
    city = " ".join(args)
    url = f"https://wttr.in/{city}?format=3"
    try:
        with urllib.request.urlopen(url, context=context) as resp:
            print(resp.read().decode())
    except Exception as e:
        cm.print_colored(f"weather: {e}", "error")

def register_plugin_commands(COMMANDS):
    """Registers the 'weather' command."""
    COMMANDS["weather"] = weather_cmd
