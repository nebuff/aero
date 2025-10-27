__PLUGIN_VERSION__ = "1.2.6"

import json
import os
import getpass
import urllib.request
import urllib.parse
import ssl

# Import core library functions for printing and coloring
import config_manager as cm

# Gemini API configuration
DEFAULT_MODEL = "gemma-3n-e4b-it"
AVAILABLE_MODELS = [
    "gemma-3n-e4b-it",
    "gemma-3-1b-it",
    "gemma-3-4b-it",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-pro-preview",
    "gemini-2.5-flash-preview-06-17",
]

# Config file path - separate from main Aero config for API key
# We will use the Aero directory as a base for safety
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gemini_config.json")

def load_config():
    """Load Gemini plugin configuration from its separate file."""
    default_config = {
        "model": DEFAULT_MODEL,
        "api_key": ""
    }
    
    if not os.path.exists(CONFIG_FILE):
        # Create config file with default values on first launch
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config
        except Exception as e:
            cm.print_colored(f"Error creating Gemini config file: {e}", "error")
            return default_config
    else:
        # Load existing config
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            cm.print_colored(f"Error loading Gemini config file: {e}", "error")
            return default_config

def save_config(config):
    """Save Gemini plugin configuration to its separate file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        cm.print_colored(f"Error saving Gemini config file: {e}", "error")

def send_to_gemini(message, model, api_key):
    """Sends a message to the Gemini API and returns the text response."""
    # The API URL format depends on your hosting setup. Using a placeholder for direct access.
    # In a real shell, this would need a proxy or a full API call wrapper.
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    payload = {
        "contents": [{"parts": [{"text": message}]}],
    }
    
    # Bypass SSL for network calls (standard practice in many embedded shells)
    context = ssl._create_unverified_context()
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(API_URL, data=data, headers=headers)
        
        with urllib.request.urlopen(req, context=context, timeout=30) as response:
            result = json.loads(response.read().decode())
            
            # Extract the text content
            if result.get('candidates') and result['candidates'][0].get('content'):
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return "API returned no text content."
                
    except urllib.error.HTTPError as e:
        return f"HTTP Error: {e.code} - API Key or Model may be invalid."
    except Exception as e:
        return f"Network or API Call Error: {e}"


# --- Command Handlers ---

def help_cmd(args):
    """Displays help for the AI command."""
    cm.print_colored("Gemini AI Commands:", "header")
    help_text = {
        "ai <prompt>": "Sends a message to the currently configured Gemini model.",
        "ai setkey": "Sets your Google AI API key (from environment variable or prompt).",
        "ai setmodel <name>": "Changes the default AI model.",
        "ai help": "Shows this help message.",
    }
    for cmd, desc in help_text.items():
        print(f"  {cm.colorize(cmd, 'data_primary'):<25} - {desc}")
    cm.print_colored(f"\nNote: Key is stored in {CONFIG_FILE}", "warning")


def setkey_cmd(args):
    """Sets the API key for the Gemini plugin."""
    config = load_config()
    
    if args and args[0].lower() == "env":
        # Check environment variable
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            cm.print_colored("Error: Environment variable GEMINI_API_KEY is not set.", "error")
            return
        cm.print_colored("Using key from GEMINI_API_KEY environment variable.", "info")
    elif args:
        # Key provided as argument (discouraged, but supported)
        api_key = args[0]
        cm.print_colored("Key set from argument.", "info")
    else:
        # Prompt for key
        try:
            api_key = getpass.getpass(cm.colorize("Enter your Google AI API Key: ", "data_key")).strip()
        except Exception as e:
            cm.print_colored(f"Key input failed: {e}", "error")
            return

    if not api_key:
        cm.print_colored("API key cannot be empty.", "error")
        return

    config['api_key'] = api_key
    save_config(config)
    cm.print_colored("Gemini API key set successfully.", "success")


def setmodel_cmd(args):
    """Quick command to change AI model"""
    config = load_config()

    if not args:
        model = config.get("model", DEFAULT_MODEL)
        cm.print_colored(f"Current model: {cm.colorize(model, 'success')}", "data_primary")
        cm.print_colored(f"Available models: {', '.join(AVAILABLE_MODELS)}", "info")
        return

    model_name = args[0]
    
    if model_name not in AVAILABLE_MODELS:
        cm.print_colored(f"Error: Unknown model '{model_name}'", "error")
        cm.print_colored(f"Available models: {', '.join(AVAILABLE_MODELS)}", "info")
        return
        
    config['model'] = model_name
    save_config(config)
    cm.print_colored(f"Model successfully set to {cm.colorize(model_name, 'success')}", "success")


def gemini_cmd(args):
    """Main entry point for the 'ai' command."""
    if not args or args[0].lower() in ("help", "-h", "--help"):
        help_cmd([])
        return
        
    # Check for setkey or setmodel subcommands
    if args[0].lower() == "setkey":
        setkey_cmd(args[1:])
        return
    elif args[0].lower() == "setmodel":
        setmodel_cmd(args[1:])
        return
    
    # Handle regular message
    config = load_config()
    api_key = config.get("api_key")
    if not api_key:
        cm.print_colored("Error: No API key set. Run 'ai setkey' first.", "error")
        return
    
    model = config.get("model", DEFAULT_MODEL)
    message = " ".join(args)
    
    cm.print_colored(f"[{model}] Sending message: {message}", "data_primary")
    
    # Send to Gemini API
    response = send_to_gemini(message, model, api_key)
    
    # Display response
    cm.print_colored("\nResponse:", "header")
    print(response) # Print raw response, let the user's terminal handle format/newlines
    print()

def register_plugin_commands(COMMANDS):
    """Registers the 'ai' command and its subcommands."""
    # We register the top-level command 'ai' which handles all subcommands internally
    COMMANDS["ai"] = gemini_cmd
    # Also register the subcommands directly for tab-completion/help if needed
    COMMANDS["ai setkey"] = setkey_cmd
    COMMANDS["ai setmodel"] = setmodel_cmd
    COMMANDS["ai help"] = help_cmd
