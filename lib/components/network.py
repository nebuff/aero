__COMPONENT_VERSION__ = "1.0.0"
__COMPONENT_NAME__ = "network"
__COMPONENT_DESCRIPTION__ = "Network utilities - ping, wget, curl functionality"

import os
import subprocess
import urllib.request
import ssl
import sys

COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_RED = "\033[31m"
COLOR_CYAN = "\033[36m"

def ping_cmd(args):
    """Ping network hosts"""
    if not args or args[0] == "help":
        print(f"{COLOR_YELLOW}Ping Command Help:{COLOR_RESET}")
        print(f"  {COLOR_GREEN}ping host{COLOR_RESET}             - Ping a host")
        print(f"  {COLOR_GREEN}ping -c count host{COLOR_RESET}    - Ping with specific count")
        return
    
    try:
        cmd = ['ping'] + args
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print(f"\n{COLOR_YELLOW}Ping interrupted{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_RED}ping: {e}{COLOR_RESET}")

def wget_cmd(args):
    """Download files from URLs"""
    if not args or args[0] == "help":
        print(f"{COLOR_YELLOW}Wget Command Help:{COLOR_RESET}")
        print(f"  {COLOR_GREEN}wget url{COLOR_RESET}              - Download file")
        print(f"  {COLOR_GREEN}wget -O filename url{COLOR_RESET}  - Download to specific filename")
        return
    
    url = None
    output_file = None
    
    i = 0
    while i < len(args):
        if args[i] == "-O" and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        else:
            url = args[i]
            i += 1
    
    if not url:
        print(f"{COLOR_RED}wget: no URL specified{COLOR_RESET}")
        return
    
    try:
        if not output_file:
            output_file = os.path.basename(url.split('?')[0]) or "index.html"
        
        print(f"{COLOR_CYAN}Downloading {url}...{COLOR_RESET}")
        
        context = ssl._create_unverified_context()
        urllib.request.urlretrieve(url, output_file)
        
        file_size = os.path.getsize(output_file)
        print(f"{COLOR_GREEN}Downloaded {output_file} ({file_size} bytes){COLOR_RESET}")
        
    except Exception as e:
        print(f"{COLOR_RED}wget: {e}{COLOR_RESET}")

def curl_cmd(args):
    """Make HTTP requests"""
    if not args or args[0] == "help":
        print(f"{COLOR_YELLOW}Curl Command Help:{COLOR_RESET}")
        print(f"  {COLOR_GREEN}curl url{COLOR_RESET}              - GET request, print response")
        print(f"  {COLOR_GREEN}curl -o file url{COLOR_RESET}      - Save response to file")
        print(f"  {COLOR_GREEN}curl -I url{COLOR_RESET}           - HEAD request (headers only)")
        return
    
    url = None
    output_file = None
    head_only = False
    
    i = 0
    while i < len(args):
        if args[i] == "-o" and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif args[i] == "-I":
            head_only = True
            i += 1
        else:
            url = args[i]
            i += 1
    
    if not url:
        print(f"{COLOR_RED}curl: no URL specified{COLOR_RESET}")
        return
    
    try:
        context = ssl._create_unverified_context()
        
        if head_only:
            req = urllib.request.Request(url, method='HEAD')
        else:
            req = urllib.request.Request(url)
        
        with urllib.request.urlopen(req, context=context) as response:
            if head_only:
                print(f"HTTP/{response.version} {response.status} {response.reason}")
                for header, value in response.headers.items():
                    print(f"{header}: {value}")
            else:
                content = response.read().decode('utf-8', errors='ignore')
                if output_file:
                    with open(output_file, 'w') as f:
                        f.write(content)
                    print(f"{COLOR_GREEN}Response saved to {output_file}{COLOR_RESET}")
                else:
                    print(content)
                    
    except Exception as e:
        print(f"{COLOR_RED}curl: {e}{COLOR_RESET}")

def register(commands):
    commands['ping'] = ping_cmd
    commands['wget'] = wget_cmd
    commands['curl'] = curl_cmd
