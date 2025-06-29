__COMPONENT_VERSION__ = "1.0.0"
__COMPONENT_NAME__ = "sysinfo"
__COMPONENT_DESCRIPTION__ = "System information - ps, top, df, free, etc."

import os
import subprocess
import sys
import platform

COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_RED = "\033[31m"
COLOR_CYAN = "\033[36m"

def ps_cmd(args):
    """Process status"""
    if args and args[0] == "help":
        print(f"{COLOR_YELLOW}PS Command Help:{COLOR_RESET}")
        print(f"  {COLOR_GREEN}ps{COLOR_RESET}                    - Show processes")
        print(f"  {COLOR_GREEN}ps aux{COLOR_RESET}               - Show all processes with details")
        return
    
    try:
        if not args:
            args = []
        cmd = ['ps'] + args
        subprocess.run(cmd)
    except Exception as e:
        print(f"{COLOR_RED}ps: {e}{COLOR_RESET}")

def top_cmd(args):
    """Display running processes"""
    try:
        subprocess.run(['top'] + (args or []))
    except KeyboardInterrupt:
        print(f"\n{COLOR_YELLOW}Top interrupted{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_RED}top: {e}{COLOR_RESET}")

def df_cmd(args):
    """Display filesystem disk space usage"""
    if args and args[0] == "help":
        print(f"{COLOR_YELLOW}DF Command Help:{COLOR_RESET}")
        print(f"  {COLOR_GREEN}df{COLOR_RESET}                    - Show disk usage")
        print(f"  {COLOR_GREEN}df -h{COLOR_RESET}                 - Show in human readable format")
        return
    
    try:
        cmd = ['df'] + (args or [])
        subprocess.run(cmd)
    except Exception as e:
        print(f"{COLOR_RED}df: {e}{COLOR_RESET}")

def free_cmd(args):
    """Display memory usage"""
    if platform.system() == "Darwin":  # macOS
        try:
            print(f"{COLOR_CYAN}Memory Usage (macOS):{COLOR_RESET}")
            subprocess.run(['vm_stat'])
        except Exception as e:
            print(f"{COLOR_RED}free: {e}{COLOR_RESET}")
    else:
        try:
            cmd = ['free'] + (args or [])
            subprocess.run(cmd)
        except Exception as e:
            print(f"{COLOR_RED}free: {e}{COLOR_RESET}")

def uname_cmd(args):
    """System information"""
    if args and args[0] == "help":
        print(f"{COLOR_YELLOW}Uname Command Help:{COLOR_RESET}")
        print(f"  {COLOR_GREEN}uname{COLOR_RESET}                 - Show system name")
        print(f"  {COLOR_GREEN}uname -a{COLOR_RESET}              - Show all system info")
        return
    
    try:
        if not args:
            print(platform.system())
        else:
            subprocess.run(['uname'] + args)
    except Exception as e:
        print(f"{COLOR_RED}uname: {e}{COLOR_RESET}")

def whoami_cmd(args):
    """Display current username"""
    try:
        result = subprocess.run(['whoami'], capture_output=True, text=True)
        print(result.stdout.strip())
    except Exception as e:
        print(f"{COLOR_RED}whoami: {e}{COLOR_RESET}")

def register(commands):
    commands['ps'] = ps_cmd
    commands['top'] = top_cmd
    commands['df'] = df_cmd
    commands['free'] = free_cmd
    commands['uname'] = uname_cmd
    commands['whoami'] = whoami_cmd
