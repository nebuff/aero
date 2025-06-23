__PLUGIN_VERSION__ = "1.0.0"

import json
import os
import getpass
import urllib.request
import urllib.parse
import ssl

# ANSI color codes
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_RED = "\033[31m"
COLOR_CYAN = "\033[36m"
COLOR_BLUE = "\033[34m"

# Gemini API configuration
DEFAULT_MODEL = "gemma-3-4B"
AVAILABLE_MODELS = [
    "gemma-3n-e4b-it",
    "gemma-3-1b-it",
    "gemma-3-4b-it",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-pro-preview",
    "gemini-2.5-flash-preview-06-17",
]

# Config file path - separate from main Aero config
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gemini_config.json")

def load_config():
    """Load Gemini plugin configuration"""
    default_config = {
        "model": DEFAULT_MODEL,
        "api_key": ""
    }
    
    if not os.path.exists(CONFIG_FILE):
        # Create config file with default values on first launch
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"{COLOR_GREEN}Created Gemini config file at {CONFIG_FILE}{COLOR_RESET}")
            print(f"{COLOR_YELLOW}Note: Run 'ai setkey' to set your Gemini API key{COLOR_RESET}")
        except Exception as e:
            print(f"{COLOR_RED}Warning: Could not create config file: {e}{COLOR_RESET}")
        return default_config
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        # Ensure all default keys exist
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
        return config
    except Exception:
        return default_config

def save_config(config):
    """Save Gemini plugin configuration"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"{COLOR_RED}Error saving config: {e}{COLOR_RESET}")

def send_to_gemini(message, model, api_key):
    """Send message to Gemini API and return response"""
    try:
        # Gemini API endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        # Prepare the request data
        data = {
            "contents": [{
                "parts": [{
                    "text": message
                }]
            }]
        }
        
        # Convert to JSON and encode
        json_data = json.dumps(data).encode('utf-8')
        
        # Create request
        request = urllib.request.Request(
            url,
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        
        # Create SSL context that doesn't verify certificates
        context = ssl._create_unverified_context()
        
        # Send request
        with urllib.request.urlopen(request, context=context) as response:
            result = json.loads(response.read().decode())
            
        # Extract the response text
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                return candidate['content']['parts'][0]['text']
        
        return "Sorry, I couldn't generate a response."
        
    except Exception as e:
        return f"Error communicating with Gemini API: {str(e)}"

def show_help():
    """Show AI command help"""
    config = load_config()
    print(f"{COLOR_YELLOW}AI Command Help:{COLOR_RESET}")
    
    # Show current settings
    print(f"{COLOR_CYAN}Current Settings:{COLOR_RESET}")
    model = config.get("model", DEFAULT_MODEL)
    api_key = config.get("api_key")
    if api_key:
        masked_key = f"...{api_key[-4:]}" if len(api_key) > 4 else "Set"
        print(f"  Model: {COLOR_GREEN}{model}{COLOR_RESET}")
        print(f"  API Key: {COLOR_GREEN}{masked_key}{COLOR_RESET}")
    else:
        print(f"  Model: {COLOR_GREEN}{model}{COLOR_RESET}")
        print(f"  API Key: {COLOR_RED}Not set{COLOR_RESET}")
    
    print(f"\n{COLOR_CYAN}Available Commands:{COLOR_RESET}")
    print(f"  {COLOR_GREEN}ai <message>{COLOR_RESET}           - Send a message to Gemini")
    print(f"  {COLOR_GREEN}ai help{COLOR_RESET}               - Show this help")
    print(f"  {COLOR_GREEN}ai model{COLOR_RESET}              - Show current model")
    print(f"  {COLOR_GREEN}ai set model <name>{COLOR_RESET}   - Change the AI model")
    print(f"  {COLOR_GREEN}ai setkey{COLOR_RESET}             - Set your Gemini API key")
    
    print(f"\n{COLOR_CYAN}Available Models:{COLOR_RESET}")
    for model_name in AVAILABLE_MODELS:
        marker = f"{COLOR_GREEN}*{COLOR_RESET}" if model_name == model else " "
        print(f"  {marker} {COLOR_BLUE}{model_name}{COLOR_RESET}")
    
    print(f"\n{COLOR_YELLOW}Setup Instructions:{COLOR_RESET}")
    print(f"1. Get a free API key from: https://aistudio.google.com/apikey")
    print(f"2. Run: {COLOR_GREEN}ai setkey{COLOR_RESET}")
    print(f"3. Start chatting: {COLOR_GREEN}ai Hello, how are you?{COLOR_RESET}")

def ai_cmd(args):
    """Main AI command handler"""
    config = load_config()
    
    if not args or args[0] == "help":
        show_help()
        return
        
    if args[0] == "model":
        model = config.get("model", DEFAULT_MODEL)
        print(f"{COLOR_CYAN}Current model: {COLOR_GREEN}{model}{COLOR_RESET}")
        return
        
    if args[0] == "set" and len(args) > 1 and args[1] == "model":
        if len(args) < 3:
            print(f"{COLOR_RED}Error: Please specify a model name{COLOR_RESET}")
            return
        
        model_name = args[2]
        if model_name not in AVAILABLE_MODELS:
            print(f"{COLOR_RED}Error: Unknown model '{model_name}'{COLOR_RESET}")
            print(f"{COLOR_YELLOW}Available models: {', '.join(AVAILABLE_MODELS)}{COLOR_RESET}")
            return
            
        config["model"] = model_name
        save_config(config)
        print(f"{COLOR_GREEN}Model changed to {model_name}{COLOR_RESET}")
        return
        
    if args[0] == "setkey":
        try:
            # Use getpass to hide input and prevent it from appearing in history
            api_key = getpass.getpass(f"{COLOR_YELLOW}Enter your Gemini API key (input hidden): {COLOR_RESET}")
            if api_key.strip():
                config["api_key"] = api_key.strip()
                save_config(config)
                print(f"{COLOR_GREEN}API key saved securely{COLOR_RESET}")
            else:
                print(f"{COLOR_RED}Error: Empty API key not saved{COLOR_RESET}")
        except KeyboardInterrupt:
            print(f"\n{COLOR_YELLOW}API key setup cancelled{COLOR_RESET}")
        except Exception as e:
            print(f"{COLOR_RED}Error setting API key: {str(e)}{COLOR_RESET}")
        return

    # Handle regular message
    api_key = config.get("api_key")
    if not api_key:
        print(f"{COLOR_RED}Error: No API key set. Run 'ai setkey' first.{COLOR_RESET}")
        return
    
    model = config.get("model", DEFAULT_MODEL)
    message = " ".join(args)
    
    print(f"{COLOR_CYAN}[{model}] Sending message: {message}{COLOR_RESET}")
    
    # Send to Gemini API
    response = send_to_gemini(message, model, api_key)
    
    # Display response
    print(f"\n{COLOR_GREEN}Response:{COLOR_RESET}")
    print(response)
    print()

def setmodel_cmd(args):
    """Quick command to change AI model"""
    if not args:
        config = load_config()
        model = config.get("model", DEFAULT_MODEL)
        print(f"{COLOR_CYAN}Current model: {COLOR_GREEN}{model}{COLOR_RESET}")
        print(f"{COLOR_YELLOW}Available models: {', '.join(AVAILABLE_MODELS)}{COLOR_RESET}")
        return
    
    model_name = args[0]
    config = load_config()
    
    if model_name not in AVAILABLE_MODELS:
        print(f"{COLOR_RED}Error: Unknown model '{model_name}'{COLOR_RESET}")
        print(f"{COLOR_YELLOW}Available models: {', '.join(AVAILABLE_MODELS)}{COLOR_RESET}")
        return
        
    config["model"] = model_name
    save_config(config)
    print(f"{COLOR_GREEN}Model changed to {model_name}{COLOR_RESET}")

def register(commands):
    """Register the AI command with Aero"""
    commands['ai'] = ai_cmd
    commands['setmodel'] = setmodel_cmd
